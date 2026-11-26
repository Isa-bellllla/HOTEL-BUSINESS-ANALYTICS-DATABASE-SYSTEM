import argparse
import subprocess
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
sys.path[:0] = [str(PROJECT_DIR / "vendor"), str(PROJECT_DIR)]

from werkzeug.serving import make_server

from app import app


def main():
    parser = argparse.ArgumentParser(description="Start The Haven Los Angeles on this Mac.")
    parser.add_argument("--no-browser", action="store_true", help="Start without opening the browser.")
    parser.add_argument("--check", action="store_true", help="Check the bundled app without starting a server.")
    options = parser.parse_args()
    if options.check:
        with app.test_client() as client:
            for url in ("/", "/suites", "/login", "/static/images/terrace.webp"):
                response = client.get(url)
                if response.status_code != 200:
                    raise RuntimeError(f"{url} returned {response.status_code}")
        print("The Haven is ready.")
        return

    with make_server("127.0.0.1", 0, app, threaded=True) as server:
        address = f"http://127.0.0.1:{server.server_port}/"
        print(f"The Haven Los Angeles · {address}", flush=True)
        print("请保留此终端窗口。按 Control+C 停止网站。", flush=True)
        if not options.no_browser:
            subprocess.Popen(["/usr/bin/open", address])
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
