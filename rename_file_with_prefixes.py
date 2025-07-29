#!/usr/bin/env python3
import os
import argparse
from pathlib import Path
from datetime import datetime

def format_millis(ts: float) -> str:
    dt = datetime.fromtimestamp(ts)
    ms = int((ts - int(ts)) * 1000)
    return dt.strftime(f"%Y%m%d_%H%M%S{ms:03d}")

def rename_files_with_datetime(path: str, extension: str):
    p = Path(path)
    if not p.exists() or not p.is_dir():
        print(f"Error: '{path}' is not a valid directory.")
        return

    files = [f for f in p.iterdir() if f.is_file() and f.suffix == extension]
    if not files:
        print(f"No files with extension '{extension}' found in '{path}'.")
        return

    for file in files:
        mtime = file.stat().st_mtime
        prefix = format_millis(mtime)
        new_name = f"{prefix}_{file.name}"
        new_path = file.with_name(new_name)
        print(f"Renaming: {file.name} → {new_name}")
        file.rename(new_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prefix files with datetime to milliseconds.")
    parser.add_argument("path", help="Directory path containing files")
    parser.add_argument("extension", help="File extension (e.g., .txt, .log, .py)")

    args = parser.parse_args()
    rename_files_with_datetime(args.path, args.extension)