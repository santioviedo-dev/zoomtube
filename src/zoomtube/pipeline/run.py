from zoomtube.pipeline import download, upload
from zoomtube.clients import zoom_api, youtube_api

import sys
from datetime import datetime, timedelta
from argparse import ArgumentParser
from pathlib import Path

from zoomtube.pipeline import download, upload

def main():
    p = ArgumentParser(prog="zoomtube")
    p.add_argument("--action", choices=["download", "upload", "all"], default="all")
    p.add_argument("--folder")
    p.add_argument("--file")
    p.add_argument("--date")
    p.add_argument("--title")
    p.add_argument("--min-duration", type=int, default=10)
    p.add_argument("--output-path")
    args = p.parse_args()

    date = args.date or (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    if args.action == "download":
        download.main([
            "--date", date,
            *(["--min-duration", str(args["min_duration"])] if args.min_duration else []),
            *(["--output-path", args.output_path] if args.output_path else []),
        ])
    elif args.action == "upload":
        if not (args.folder or args.file or args.date):
            p.error("provide --folder or --file or --date")
        upload.main([
            *(["--folder", args.folder] if args.folder else []),
            *(["--file", args.file] if args.file else []),
            *(["--title", args.title] if (args.title and args.file) else []),
        ])
    else:
        # all
        dl_args = ["--date", date, "--min-duration", str(args.min_duration)]
        if args.output_path: dl_args += ["--output-path", args.output_path]
        download.main(dl_args)
        up_folder = args.folder or (args.output_path or str(Path("data/recordings")/date))
        upload.main(["--folder", up_folder])

if __name__ == "__main__":
    main()
