#!/usr/bin/env python3
"""Build the original Jinja portfolio into static HTML for GitHub Pages.

Only Jinja2 is needed during the build. The published files have no Python runtime.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import shutil
from urllib.parse import urlparse

from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src"
TEMPLATES = SOURCE / "templates"
DATA = SOURCE / "data"
ASSETS = SOURCE / "assets"


def load_json(name: str):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def normalize_base_path(value: str) -> str:
    """Return '/' or '/repo/'; Pages provides '' or '/repo' for base_path."""
    value = value.strip().replace("\\", "/")
    if not value or value == "/":
        return "/"
    if value.startswith("//") or not re.fullmatch(r"/[A-Za-z0-9._/-]+/?", value):
        raise ValueError("Base path must look like /repository-name, or /")
    parts = value.strip("/").split("/")
    if any(part in ("", ".", "..") for part in parts):
        raise ValueError("Base path cannot contain empty, '.' or '..' segments")
    return "/" + "/".join(parts) + "/"


def url_with_prefix(path: str, prefix: str) -> str:
    if not path.startswith("/") or path.startswith("//"):
        raise ValueError(f"Not a site-root path: {path!r}")
    return prefix + path.lstrip("/")


def validate_data(site: dict, pages: list[dict], projects: list[dict], skills: list[dict]) -> None:
    email = site.get("email", "").strip()
    if email and not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
        raise ValueError("src/data/site.json: email must be valid, or empty")
    for link in site["social_links"]:
        if link["url"]:
            parsed = urlparse(link["url"])
            if parsed.scheme != "https" or not parsed.netloc:
                raise ValueError(f"Social URL for {link['label']} must be https://...")
    keys = [page["key"] for page in pages]
    if len(keys) != len(set(keys)):
        raise ValueError("src/data/pages.json: duplicate page keys")
    outputs = [page["output"] for page in pages]
    if len(outputs) != len(set(outputs)):
        raise ValueError("src/data/pages.json: duplicate output paths")
    for page in pages:
        output = Path(page["output"])
        if output.is_absolute() or ".." in output.parts or not page["output"].endswith(".html"):
            raise ValueError(f"Unsafe output path: {page['output']}")
        if not page["url"].startswith("/") or not page["url"].endswith("/"):
            raise ValueError(f"Page URL must begin and end with '/': {page['url']}")
    for project in projects:
        filename = project["image"]
        if Path(filename).name != filename or not (ASSETS / "images" / filename).is_file():
            raise ValueError(f"Missing or invalid project image: {filename}")
    for skill in skills:
        if not isinstance(skill["level"], int) or not 0 <= skill["level"] <= 100:
            raise ValueError(f"Skill percentage must be an integer 0..100: {skill!r}")


def build(output: Path, base_path: str = "/") -> list[Path]:
    prefix = normalize_base_path(base_path)
    site, pages, projects, skills = (
        load_json("site.json"),
        load_json("pages.json"),
        load_json("projects.json"),
        load_json("skills.json"),
    )
    validate_data(site, pages, projects, skills)

    route_map = {page["key"]: page["url"] for page in pages}

    def route(key: str) -> str:
        return url_with_prefix(route_map[key], prefix)

    def asset(path: str) -> str:
        # Only local assets are permitted; prevent accidental '../' paths.
        if not path or path.startswith("/") or ".." in Path(path).parts:
            raise ValueError(f"Unsafe asset path: {path!r}")
        return url_with_prefix("/assets/" + path, prefix)

    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES)),
        autoescape=select_autoescape(enabled_extensions=("html",), default_for_string=True),
        undefined=StrictUndefined,
        keep_trailing_newline=True,
    )
    env.globals.update(route=route, asset=asset)

    output = output.resolve()
    if output in (ROOT, SOURCE, TEMPLATES, DATA, ASSETS) or SOURCE in output.parents:
        raise ValueError("Refusing to overwrite the project sources")
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    shutil.copytree(ASSETS, output / "assets")
    (output / ".nojekyll").write_text("", encoding="utf-8")

    context = {
        "site": site,
        "projects": projects,
        "skills": skills,
        "navigation": pages,
        "year": datetime.now(timezone.utc).year,
    }
    written = []
    for page in pages:
        rendered = env.get_template(page["template"]).render(**context, page=page)
        destination = output / page["output"]
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(rendered, encoding="utf-8")
        written.append(destination)

    not_found = {
        "key": "404",
        "label": "Page not found",
        "description": "The requested page could not be found.",
    }
    (output / "404.html").write_text(
        env.get_template("pages/404.html").render(**context, page=not_found),
        encoding="utf-8",
    )
    written.append(output / "404.html")
    return written


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "dist", help="Directory for generated HTML")
    parser.add_argument("--base-path", default="/", help="GitHub Pages base path: / or /repo-name")
    args = parser.parse_args()
    files = build(args.output, args.base_path)
    print(f"Built {len(files)} HTML pages and copied assets into {args.output.resolve()}")
    print(f"Base path: {normalize_base_path(args.base_path)}")


if __name__ == "__main__":
    main()
