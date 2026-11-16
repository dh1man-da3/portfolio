"""Zero-extra-test-dependency checks for GitHub Pages compatibility."""

from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build as build_module
from build import (  # noqa: E402
    build,
    load_json,
    normalize_base_path,
    url_with_prefix,
    validate_data,
)


class AssetLinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links: list[str] = []
        self.active_links = 0
        self.images = 0
        self.form_fields: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag in {"a", "link"} and attributes.get("href"):
            self.links.append(attributes["href"])
        if tag in {"img", "script"} and attributes.get("src"):
            self.links.append(attributes["src"])
        if tag == "img":
            self.images += 1
            assert attributes.get("alt"), "All images should have descriptive alt text"
        if tag == "a" and attributes.get("aria-current") == "page":
            self.active_links += 1
        if tag in {"input", "textarea"} and attributes.get("name"):
            self.form_fields.add(attributes["name"])


class StaticBuildTests(unittest.TestCase):
    def test_base_path_normalization(self):
        for raw, expected in (("", "/"), ("/", "/"), ("/repo", "/repo/"), ("/repo/", "/repo/")):
            self.assertEqual(normalize_base_path(raw), expected)
        for bad in ("repo", "/../no", "/repo/../bad", "https://example.com", "//evil.example"):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                normalize_base_path(bad)
        self.assertEqual(url_with_prefix("/projects/", "/repo/"), "/repo/projects/")
        self.assertEqual(url_with_prefix("/", "/repo/"), "/repo/")

    def test_data_is_valid(self):
        validate_data(load_json("site.json"), load_json("pages.json"),
                      load_json("projects.json"), load_json("skills.json"))
        self.assertEqual(len(load_json("projects.json")), 4)
        self.assertEqual(len(load_json("skills.json")), 6)

    def test_root_and_repository_paths(self):
        pages = load_json("pages.json")
        for prefix in ("/", "/physics-portfolio/"):
            with self.subTest(prefix=prefix), TemporaryDirectory() as directory:
                output = Path(directory) / "built"
                generated = build(output, prefix)
                self.assertEqual(len(generated), 6)  # five originals plus 404
                self.assertTrue((output / ".nojekyll").exists())
                self.assertFalse((output / "app.py").exists())
                self.assertFalse((output / "requirements-build.txt").exists())

                for page in [*pages, {"key": "404", "output": "404.html"}]:
                    html = (output / page["output"]).read_text()
                    self.assertIn("<!DOCTYPE html>", html)
                    self.assertIn("<main", html)
                    self.assertIn("<footer", html)
                    self.assertNotIn("{{", html)
                    self.assertNotIn("{%", html)
                    self.assertNotIn("dhiman.physics@example.com", html)
                    self.assertNotIn('href="#"', html)
                    parsed = AssetLinkParser()
                    parsed.feed(html)
                    self.assertEqual(parsed.active_links, 0 if page["key"] == "404" else 1)
                    for link in parsed.links:
                        if not link.startswith("/"):
                            continue  # external links and mailto: are not local assets
                        self.assertTrue(link.startswith(prefix), (page["key"], link, prefix))
                        local = link[len(prefix):].split("#", 1)[0].split("?", 1)[0]
                        path = output / local
                        if link.endswith("/"):
                            path /= "index.html"
                        self.assertTrue(path.is_file(), (page["key"], link, path))

                project_html = (output / "projects/index.html").read_text()
                self.assertEqual(project_html.count('class="project-card"'), len(load_json("projects.json")))
                skills_html = (output / "skills/index.html").read_text()
                self.assertEqual(skills_html.count('class="skill-card"'), len(load_json("skills.json")))
                contact_html = (output / "contact/index.html").read_text()
                parsed = AssetLinkParser()
                parsed.feed(contact_html)
                self.assertEqual(parsed.form_fields, {"name", "email", "subject", "message"})
                self.assertIn("data-contact-form", contact_html)
                self.assertIn("Not configured yet", contact_html)

    def test_configured_email_produces_real_mailto_link(self):
        real_load_json = build_module.load_json

        def configured_json(filename):
            value = real_load_json(filename)
            if filename == "site.json":
                value["email"] = "hello@example.org"
            return value

        with TemporaryDirectory() as directory, patch.object(build_module, "load_json", configured_json):
            build(Path(directory) / "site", "/")
            rendered = (Path(directory) / "site/contact/index.html").read_text()
            self.assertIn('href="mailto:hello@example.org"', rendered)
            self.assertIn('data-recipient="hello@example.org"', rendered)
            self.assertNotIn("Not configured yet", rendered)

    def test_template_preservation(self):
        # The main CSS stylesheet starts with the original unchanged rules.
        original = ROOT.parent / "source/physics_portfolio/static/css/style.css"
        if original.exists():
            self.assertTrue((ROOT / "src/assets/css/style.css").read_bytes().startswith(original.read_bytes()))
        for filename in ("index", "about", "projects", "skills", "contact"):
            self.assertTrue((ROOT / f"src/templates/pages/{filename}.html").is_file())


if __name__ == "__main__":
    unittest.main()
