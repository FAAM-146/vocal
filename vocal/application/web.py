"""Launch a web-based checker GUI."""

import sys
import time
import webbrowser
import threading

import uvicorn

from vocal.application import parser_factory


def main() -> None:
    """
    The main function for the vocal web command.
    """

    def _start_browser_in_thread(host: str, port: int) -> None:
        """
        Start a web browser in a new thread.

        Args:
            host: The host to bind to.
            port: The port to bind to.
        """
        time.sleep(1)
        webbrowser.open_new_tab(f"http://{host}:{port}")

    parser = parser_factory(
        file=__file__, description="Launch a web-based checker GUI."
    )

    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        metavar="HOST",
        help="The host to bind to.",
    )

    parser.add_argument(
        "--port",
        type=int,
        default=8088,
        metavar="PORT",
        help="The port to bind to.",
    )

    args = parser.parse_args(sys.argv[2:])

    # Use a new thread to open the browser in 1 second, launch server immediately
    threading.Thread(target=_start_browser_in_thread, args=(args.host, args.port)).start()
    uvicorn.run(
        "vocal.web:app", host=args.host, port=args.port, log_level="info", reload=True
    )
