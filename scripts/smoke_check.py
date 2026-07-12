#!/usr/bin/env python3
"""Run repository checks that do not require robot hardware."""

import ast
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
SKIP_PARTS = {".git", "__pycache__"}
STALE_SCAN_ROOTS = (
    ROOT / "README.md",
    ROOT / "docs" / "workshop",
    ROOT / "docs" / "setup",
    ROOT / "docs" / "support",
    ROOT / "skills",
)
STALE_PATTERNS = {
    "python3 app.py": "retired robotic-arm web command",
    ":5000/servo": "retired robotic-arm web URL",
    "tag36h11_singles.pdf": "missing retired AprilTag PDF",
    "Run on Buddy": "retired robot name",
    "apriltag_nav.py": "missing retired AprilTag implementation",
    "calibrate_camera.py": "missing retired camera calibration script",
    "pick_place_template.py": "missing retired arm template",
}
EMOJI_MARKERS = tuple(chr(codepoint) for codepoint in (0x2705, 0x274C, 0x26A0, 0x2753, 0x2713, 0x2717))
MARKDOWN_LINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)|!\[[^\]]*\]\(([^)]+)\)")
HTML_IMAGE = re.compile(r'<img\s+[^>]*src="([^"]+)"')
PYTHON_COMMAND = re.compile(r"python3\s+([A-Za-z0-9_./-]+\.py)")
INLINE_SCRIPT = re.compile(r"<script(?:\s[^>]*)?>(.*?)</script>", re.DOTALL | re.IGNORECASE)


def active_files(suffix):
    for path in ROOT.rglob(f"*{suffix}"):
        if SKIP_PARTS.intersection(path.parts):
            continue
        if "docs" in path.parts and "archive" in path.parts:
            continue
        yield path


def stale_scan_files():
    for start in STALE_SCAN_ROOTS:
        if start.is_file():
            yield start
            continue
        for path in start.rglob("*"):
            if path.is_file() and path.suffix.lower() in {".md", ".py", ".yaml", ".html"}:
                yield path


def check_python(errors):
    checked = 0
    for path in active_files(".py"):
        try:
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            checked += 1
        except (SyntaxError, UnicodeDecodeError) as error:
            errors.append(f"Python syntax: {path.relative_to(ROOT)}: {error}")
    return checked


def local_target(source, target):
    target = target.strip("<>")
    if not target or target.startswith(("http://", "https://", "mailto:", "#")):
        return None
    path_text = unquote(target.split("#", 1)[0])
    return (source.parent / path_text).resolve() if path_text else None


def check_markdown(errors):
    checked = 0
    for path in active_files(".md"):
        text = path.read_text(encoding="utf-8")
        checked += 1
        for match in MARKDOWN_LINK.finditer(text):
            target = match.group(1) or match.group(2)
            resolved = local_target(path, target)
            if resolved is not None and not resolved.exists():
                errors.append(f"Broken link: {path.relative_to(ROOT)} -> {target}")
        for target in HTML_IMAGE.findall(text):
            resolved = local_target(path, target)
            if resolved is not None and not resolved.exists():
                errors.append(f"Broken image: {path.relative_to(ROOT)} -> {target}")
        for command_path in PYTHON_COMMAND.findall(text):
            if command_path.startswith("/") or command_path.startswith("../"):
                continue
            if "/" in command_path and not (ROOT / command_path).exists():
                errors.append(f"Missing command file: {path.relative_to(ROOT)} -> {command_path}")
    return checked


def check_stale_text(errors):
    checked = 0
    for path in stale_scan_files():
        text = path.read_text(encoding="utf-8")
        checked += 1
        for pattern, description in STALE_PATTERNS.items():
            if pattern in text:
                errors.append(f"Stale text ({description}): {path.relative_to(ROOT)}")
        for marker in EMOJI_MARKERS:
            if marker in text:
                errors.append(f"Emoji marker: {path.relative_to(ROOT)} contains {marker}")
    return checked


def check_javascript(errors):
    node = shutil.which("node")
    if node is None:
        return "skipped (node not installed)"

    checked = 0
    for path in active_files(".html"):
        text = path.read_text(encoding="utf-8")
        for index, script in enumerate(INLINE_SCRIPT.findall(text), start=1):
            if not script.strip():
                continue
            with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as handle:
                handle.write(script)
                temp_path = Path(handle.name)
            try:
                result = subprocess.run(
                    [node, "--check", str(temp_path)],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if result.returncode:
                    detail = (result.stderr or result.stdout).strip()
                    errors.append(f"JavaScript syntax: {path.relative_to(ROOT)} script {index}: {detail}")
                checked += 1
            finally:
                temp_path.unlink(missing_ok=True)
    return str(checked)


def main():
    errors = []
    python_count = check_python(errors)
    markdown_count = check_markdown(errors)
    text_count = check_stale_text(errors)
    javascript_count = check_javascript(errors)

    print("Pathfinder2026 smoke check")
    print(f"  Python files: {python_count}")
    print(f"  Markdown files: {markdown_count}")
    print(f"  Current text files: {text_count}")
    print(f"  Inline JavaScript blocks: {javascript_count}")

    if errors:
        print(f"\nFAILED: {len(errors)} issue(s)")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("\nPASS: no hardware-free repository issues found")
    return 0


if __name__ == "__main__":
    sys.exit(main())
