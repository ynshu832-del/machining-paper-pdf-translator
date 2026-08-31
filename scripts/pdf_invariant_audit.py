#!/usr/bin/env python3
"""Compare source and translated PDFs for structural layout invariants."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import fitz


def inspect_pdf(path: Path) -> dict:
    doc = fitz.open(path)
    pages = []
    total_cjk = 0
    for index, page in enumerate(doc):
        text = page.get_text("text")
        cjk_count = sum("\u3400" <= char <= "\u9fff" for char in text)
        total_cjk += cjk_count
        pages.append(
            {
                "page": index + 1,
                "width_pt": round(page.rect.width, 3),
                "height_pt": round(page.rect.height, 3),
                "rotation": page.rotation,
                "image_count": len(page.get_images(full=True)),
                "text_chars": len(text),
                "cjk_chars": cjk_count,
            }
        )
    result = {
        "path": str(path.resolve()),
        "page_count": doc.page_count,
        "file_size_bytes": path.stat().st_size,
        "total_cjk_chars": total_cjk,
        "pages": pages,
    }
    doc.close()
    return result


def compare(source: dict, output: dict, tolerance: float) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    if source["page_count"] != output["page_count"]:
        errors.append(
            f"Page count differs: source={source['page_count']}, output={output['page_count']}"
        )
        return errors, warnings

    for src, dst in zip(source["pages"], output["pages"]):
        number = src["page"]
        if abs(src["width_pt"] - dst["width_pt"]) > tolerance or abs(
            src["height_pt"] - dst["height_pt"]
        ) > tolerance:
            errors.append(
                f"Page {number}: geometry differs "
                f"({src['width_pt']}x{src['height_pt']} -> "
                f"{dst['width_pt']}x{dst['height_pt']} pt)"
            )
        if src["rotation"] != dst["rotation"]:
            errors.append(
                f"Page {number}: rotation differs "
                f"({src['rotation']} -> {dst['rotation']})"
            )
        if src["image_count"] != dst["image_count"]:
            warnings.append(
                f"Page {number}: image object count differs "
                f"({src['image_count']} -> {dst['image_count']}); inspect visually"
            )
        if src["text_chars"] >= 80 and dst["cjk_chars"] == 0:
            warnings.append(
                f"Page {number}: source has substantial text but output exposes no CJK text; "
                "check translation coverage or text extraction"
            )

    if output["total_cjk_chars"] == 0:
        warnings.append("Output exposes no extractable CJK text; verify font embedding and visibility")
    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit page geometry, rotation, image counts, and visible CJK text."
    )
    parser.add_argument("source", type=Path, help="Original PDF")
    parser.add_argument("output", type=Path, help="Translated PDF")
    parser.add_argument(
        "--tolerance",
        type=float,
        default=0.25,
        help="Allowed page-size difference in points (default: 0.25)",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args()

    for path in (args.source, args.output):
        if not path.is_file():
            parser.error(f"PDF not found: {path}")

    try:
        source = inspect_pdf(args.source)
        output = inspect_pdf(args.output)
    except Exception as exc:
        print(f"Failed to inspect PDF: {exc}", file=sys.stderr)
        return 2

    errors, warnings = compare(source, output, args.tolerance)
    report = {
        "source": source,
        "output": output,
        "errors": errors,
        "warnings": warnings,
        "passed": not errors,
    }

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        status = "PASS" if not errors else "FAIL"
        print(f"{status}: {source['page_count']} source pages, {output['page_count']} output pages")
        for message in errors:
            print(f"ERROR: {message}")
        for message in warnings:
            print(f"WARNING: {message}")
        if not warnings and not errors:
            print("No structural differences detected.")

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
