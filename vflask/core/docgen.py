"""Documentation generation helpers for vflask modules."""

from __future__ import annotations

import re
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape

TEMPLATE_ROOT = Path(__file__).resolve().parents[1] / "templates"


class DocGenerator:
    """Generate markdown documentation for module folders."""

    def __init__(self, project_root: str | Path):
        self.project_root = Path(project_root).expanduser().resolve()
        self.env = Environment(
            loader=FileSystemLoader(str(TEMPLATE_ROOT)),
            autoescape=select_autoescape(["html", "xml", "md"]),
            trim_blocks=True,
            lstrip_blocks=True,
            undefined=StrictUndefined,
        )

    def generate_for_module(self, module_dir: str | Path) -> Path:
        module_path = Path(module_dir).expanduser().resolve()
        module_name = module_path.name
        class_name = "".join(part.capitalize() for part in re.split(r"[_-]+", module_name))
        roles = ["admin"]
        template = self.env.get_template("module/docs.md.j2")
        content = template.render(
            module={
                "name": module_name,
                "class_name": class_name,
                "table_name": module_name,
                "plural_class": class_name,
                "singular": module_name.rstrip("s"),
                "url_prefix": f"/api/v1/{module_name}",
            },
            fields=[],
            roles=roles,
        )
        output = module_path / "docs.md"
        output.write_text(content, encoding="utf-8")
        return output


__all__ = ["DocGenerator"]
