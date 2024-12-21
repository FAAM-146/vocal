import os
import tempfile

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from starlette import status
from fastapi import FastAPI, File, UploadFile


from vocal.application.check import load_matching_definitions, load_matching_projects
from vocal.checking import ProductChecker
from vocal.core import register_defaults_module
from vocal.netcdf.writer import NetCDFReader
from vocal.utils import get_error_locs, import_project
from vocal.utils.registry import Registry
from vocal.application.fetch import fetch_project

app = FastAPI()

app.mount(
    "/static",
    StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")),
    name="static",
)
templates = Jinja2Templates(
    directory=os.path.join(os.path.dirname(__file__), "templates")
)


@app.get("/projects/add", response_class=HTMLResponse)
async def add_project(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request, name="add-project.html"
    )

@app.post("/projects/add", response_class=RedirectResponse)
async def add_project(request: Request) -> RedirectResponse:
    form = await request.form()
    url = form.get("url")

    try:
        fetch_project(url, git=False)
    except Exception as e:
        pass  # TODO: handle error

    return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

@app.get("/projects", response_class=HTMLResponse)
async def projects(request: Request) -> HTMLResponse:
    with Registry.open() as registry:
        projects = registry.projects

    return templates.TemplateResponse(
        request=request, name="projects.html", context={"projects": projects}
    )

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):

    try:
        with Registry.open() as registry:
            num_projects = len(registry.projects)
    except FileNotFoundError:
        num_projects = 0

    if num_projects == 0:
        return templates.TemplateResponse(
            request=request, name="no-projects.html"
        )
    
    return templates.TemplateResponse(
        request=request, name="checker.html"
    )

@app.post("/", response_class=JSONResponse)
def upload(request: Request, file: UploadFile = File(...)):
    context = {
        "projects": {},
        "definitions": {}
    }

    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = os.path.join(temp_dir, file.filename)
        with open(file_path, "wb") as f:
            f.write(file.file.read())
        file.file.close()

        projects = load_matching_projects(file_path)
        definitions = load_matching_definitions(file_path)

        for project in projects:
            try:
                project_mod = import_project(project)
                context["projects"][project_mod.__name__] = {
                    "passed": True,
                    "errors": []
                }
            except Exception as e:
                context["errors"].append(f"Error loading project {project}: {e}")

            register_defaults_module(project_mod.defaults)

            nc = NetCDFReader(file_path)
            try:
                nc_noval = nc.to_model(project_mod.models.Dataset, validate=False)
                nc.to_model(project_mod.models.Dataset)

            except ValidationError as err:
                error_locs = get_error_locs(err, nc_noval)
                context["projects"][project_mod.__name__]["passed"] = False
                for loc, msg in zip(*error_locs):
                    context["projects"][project_mod.__name__]["errors"].append({
                        "loc": loc,
                        "msg": msg
                    })

        for definition in definitions:
            context["definitions"][os.path.basename(definition)] = {
                "passed": True,
                "warnings": False,
                "comments": False,
                "checks": []
            }

            pc = ProductChecker(definition)
            pc.check(file_path)

            context["definitions"][os.path.basename(definition)]["passed"] = (
                all([r.passed for r in pc.checks])
            )

            for check in pc.checks:
                _check = {
                    "description": check.description,
                }

                if check.passed:
                    if check.has_comment and check.comment:
                        context["definitions"][os.path.basename(definition)]["comments"] = True
                        _check["comment"] = check.comment
                    else:
                        _check["comment"] = None

                    if check.has_warning and check.warning:
                        context["definitions"][os.path.basename(definition)]["warnings"] = True
                        _check["warning"] = check.warning
                    else:
                        _check["warning"] = None
                elif check.error:
                    _check["error"] = check.error
                    print(check.error)
                


                context["definitions"][os.path.basename(definition)]["checks"].append(_check)
        
    return templates.TemplateResponse(
        request=request, name="checked.html", context=context
    )