#!/usr/bin/env python3

import argparse
import json
import shutil
import subprocess
import sys
from fractions import Fraction
from pathlib import Path
from typing import Optional


def parse_rate(value: Optional[str]) -> Optional[float]:
    if not value or value in {"0/0", "N/A"}:
        return None
    try:
        return round(float(Fraction(value)), 3)
    except (ValueError, ZeroDivisionError):
        return None


def inspect_media(path: Path) -> dict:
    command = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration,format_name,size,bit_rate",
        "-show_entries",
        "stream=index,codec_type,codec_name,width,height,pix_fmt,avg_frame_rate,r_frame_rate,duration",
        "-of",
        "json",
        str(path),
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "ffprobe could not inspect the file")

    payload = json.loads(result.stdout)
    format_info = payload.get("format", {})
    streams = []
    for stream in payload.get("streams", []):
        item = {
            "index": stream.get("index"),
            "type": stream.get("codec_type"),
            "codec": stream.get("codec_name"),
        }
        if stream.get("codec_type") == "video":
            item.update(
                {
                    "width": stream.get("width"),
                    "height": stream.get("height"),
                    "pixel_format": stream.get("pix_fmt"),
                    "average_fps": parse_rate(stream.get("avg_frame_rate")),
                    "reported_fps": parse_rate(stream.get("r_frame_rate")),
                }
            )
        streams.append(item)

    return {
        "path": str(path.resolve()),
        "container": format_info.get("format_name"),
        "duration_seconds": round(float(format_info["duration"]), 3)
        if format_info.get("duration")
        else None,
        "size_bytes": int(format_info["size"]) if format_info.get("size") else None,
        "bit_rate": int(format_info["bit_rate"])
        if format_info.get("bit_rate")
        else None,
        "streams": streams,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Inspect local video or image media for a particle-field implementation."
    )
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args()

    if shutil.which("ffprobe") is None:
        print("Error: ffprobe is required but was not found on PATH.", file=sys.stderr)
        return 2

    reports = []
    for path in args.paths:
        if not path.is_file():
            print(f"Error: media file does not exist: {path}", file=sys.stderr)
            return 2
        try:
            reports.append(inspect_media(path))
        except (RuntimeError, json.JSONDecodeError) as error:
            print(f"Error: {path}: {error}", file=sys.stderr)
            return 1

    print(json.dumps(reports[0] if len(reports) == 1 else reports, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
