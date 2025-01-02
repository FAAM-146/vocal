import os

from fastapi import FastAPI, HTTPException, Request, File, UploadFile, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from vocal.utils.registry import Registry
from vocal.application.fetch import fetch_project
from vocal.web.utils import check_upload

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
async def add_project_get(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request=request, name="add-project.html")


@app.post("/projects/add", response_class=RedirectResponse)
async def add_project_post(request: Request) -> RedirectResponse:
    form = await request.form()
    url = form.get("url")

    if not url:
        raise HTTPException(
            detail="No URL provided", status_code=status.HTTP_400_BAD_REQUEST
        )

    if not isinstance(url, str):
        raise HTTPException(
            detail="Invalid URL provided", status_code=status.HTTP_400_BAD_REQUEST
        )

    try:
        fetch_project(url, git=False)
    except Exception as e:
        raise HTTPException(
            detail=f"Error fetching project: {e}",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

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
        return templates.TemplateResponse(request=request, name="no-projects.html")

    return templates.TemplateResponse(request=request, name="checker.html")


@app.post("/", response_class=JSONResponse)
async def upload(request: Request, file: UploadFile = File(...)) -> HTMLResponse:

    context = await check_upload(file)

    return templates.TemplateResponse(
        request=request, name="checked.html", context=context.model_dump()
    )
