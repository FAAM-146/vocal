"""Launch a web-based compliance checker."""

import time
import webbrowser
import threading

import uvicorn


def main() -> None:
    def _start_browser_in_thread() -> None:
        time.sleep(1)
        webbrowser.open_new_tab("http://127.0.0.1:8088")
    # Use a new thread to open the browser in 1 second, lauch server immediately
    threading.Thread(target=_start_browser_in_thread).start()
    uvicorn.run("vocal.web:app", host="127.0.0.1", port=8088, log_level="info", reload=True)