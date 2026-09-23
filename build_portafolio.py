"""Genera Portafolio.ipynb y Portafolio1.ipynb fusionando TODO el contenido del proyecto."""
import copy
import json
import uuid
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EXCLUDE = {"portafolio.ipynb", "portafolio1.ipynb"}


def new_cell_id() -> str:
    return uuid.uuid4().hex[:8]


def extract_title(notebook_path: Path) -> str:
    try:
        nb = json.loads(notebook_path.read_text(encoding="utf-8"))
        for cell in nb.get("cells", []):
            if cell.get("cell_type") != "markdown":
                continue
            for line in "".join(cell.get("source", [])).splitlines():
                line = line.strip()
                if line.startswith("# ") and not line.startswith("## "):
                    return line[2:].strip()
    except Exception:
        pass
    return notebook_path.stem


def collect_notebooks() -> list[dict]:
    seen: set[str] = set()
    items: list[dict] = []

    for path in ROOT.glob("*.ipynb"):
        key = path.name.lower()
        if key in EXCLUDE or key in seen:
            continue
        seen.add(key)

        stat = path.stat()
        items.append(
            {
                "path": path,
                "file": path.name,
                "title": extract_title(path),
                "created": datetime.fromtimestamp(stat.st_ctime),
            }
        )

    items.sort(key=lambda x: x["created"])
    return items


def build_table_markdown(items: list[dict]) -> str:
    lines = [
        "## Proyectos del portafolio (orden cronológico)\n",
        "\n",
        "Listado de todos los notebooks `.ipynb` del repositorio, "
        "desde el primero creado hasta el último.\n",
        "\n",
        "| # | Fecha creación | Notebook | Título |\n",
        "|---|----------------|----------|--------|\n",
    ]

    for index, item in enumerate(items, start=1):
        date_str = item["created"].strftime("%d/%m/%Y")
        link = f"[{item['file']}](#proyecto-{index})"
        lines.append(f"| {index} | {date_str} | {link} | {item['title']} |\n")

    lines.append(f"\n**Total de proyectos:** {len(items)}\n")
    return "".join(lines)


def normalize_output(output: dict) -> dict:
    out = copy.deepcopy(output)
    output_type = out.get("output_type")

    if output_type == "stream" and "name" not in out:
        out["name"] = "stdout"

    if output_type in {"execute_result", "display_data"} and "metadata" not in out:
        out["metadata"] = {}

    if output_type == "execute_result" and "execution_count" not in out:
        out["execution_count"] = None

    return out


def normalize_cell(cell: dict) -> dict:
    new_cell = copy.deepcopy(cell)
    new_cell["id"] = new_cell_id()
    if new_cell.get("cell_type") == "code":
        new_cell["execution_count"] = None
        if new_cell.get("outputs"):
            new_cell["outputs"] = [normalize_output(o) for o in new_cell["outputs"]]
    return new_cell


def build_portfolio_cells(items: list[dict], portfolio_title: str) -> list[dict]:
    cells: list[dict] = [
        {
            "cell_type": "markdown",
            "id": new_cell_id(),
            "metadata": {},
            "source": [
                '<img src="img/logoitqv1.jpg" width="500">\n',
                "<br>\n",
                "\n",
                f"# {portfolio_title}\n",
                "\n",
                "## Machine Learning — Jesús Viera\n",
                "<br>\n",
                "\n",
                '<img src="img/python_logo.png" width="300">\n',
                "<br>\n",
                "\n",
                "*Jesús Viera* https://github.com/Vierita23/machinelearning\n",
                "\n",
                "---\n",
                "\n",
                "Este notebook reúne **toda la materia** del curso: el contenido completo "
                "de cada proyecto, en orden cronológico, desde el primero hasta el último.\n",
            ],
        },
        {
            "cell_type": "markdown",
            "id": new_cell_id(),
            "metadata": {},
            "source": [build_table_markdown(items)],
        },
    ]

    for index, item in enumerate(items, start=1):
        nb = json.loads(item["path"].read_text(encoding="utf-8"))
        date_str = item["created"].strftime("%d/%m/%Y")

        cells.append(
            {
                "cell_type": "markdown",
                "id": new_cell_id(),
                "metadata": {},
                "source": [
                    f'<a id="proyecto-{index}"></a>\n',
                    "\n",
                    "---\n",
                    "\n",
                    f"# Proyecto {index}: {item['file']}\n",
                    "\n",
                    f"**Fecha de creación:** {date_str}  \n",
                    f"**Título:** {item['title']}\n",
                    "\n",
                    "---\n",
                ],
            }
        )

        for cell in nb.get("cells", []):
            cells.append(normalize_cell(cell))

    return cells


def write_notebook(path: Path, cells: list[dict]) -> None:
    notebook = {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "name": "python",
                "pygments_lexer": "ipython3",
            },
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(notebook, ensure_ascii=False, indent=1), encoding="utf-8")
    size_mb = path.stat().st_size / (1024 * 1024)
    print(f"Escrito: {path} ({size_mb:.1f} MB)")


def main() -> None:
    items = collect_notebooks()
    targets = [
        (ROOT / "Portafolio.ipynb", ROOT / ".ipynb_checkpoints" / "Portafolio-checkpoint.ipynb", "Portafolio de Proyectos"),
        (ROOT / "Portafolio1.ipynb", ROOT / ".ipynb_checkpoints" / "Portafolio1-checkpoint.ipynb", "Portafolio de Proyectos 1"),
    ]

    for main_path, checkpoint_path, title in targets:
        cells = build_portfolio_cells(items, title)
        write_notebook(main_path, cells)
        write_notebook(checkpoint_path, cells)

    print(f"Proyectos fusionados: {len(items)}")
    print(f"Celdas totales por portafolio: {len(cells)}")


if __name__ == "__main__":
    main()
