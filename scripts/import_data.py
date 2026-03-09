# ruff: noqa: PGH003

import sys
from pathlib import Path

import openpyxl

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from app import create_app
from app.db.models import Material
from app.db.session import db


def import_xlsx() -> None:
    app = create_app()
    with app.app_context():
        # Truncate table (SQLite does not support TRUNCATE, so we use DELETE)
        db.session.query(Material).delete()
        db.session.commit()
        print("Tabela 'materials' limpa.")  # noqa: T201

        xlsx_path = Path(app.root_path).parent / "data" / "imports" / "materials.xlsx"
        if not xlsx_path.exists():
            print(f"Arquivo XLSX não encontrado: {xlsx_path}")  # noqa: T201
            return

        wb = openpyxl.load_workbook(xlsx_path)
        ws = wb.active

        if not ws:
            print("Planilha vazia")  # noqa: T201
            return

        count = 0
        headers = [str(cell.value) if cell.value else "" for cell in ws[1]]

        for row in ws.iter_rows(min_row=2, values_only=True):
            if not row or not row[0]:
                continue

            row_dict = dict(zip(headers, row, strict=False))

            # Tratar vazios
            for k, v in row_dict.items():
                if v == "" or v is None:
                    row_dict[k] = None

            material = Material()
            material.id = int(row_dict["id"])  # type: ignore
            material.type = str(row_dict["type"]) if row_dict["type"] else ""
            material.title = str(row_dict["title"]) if row_dict["title"] else ""
            material.module = str(row_dict["module"]) if row_dict["module"] else ""
            material.theme = str(row_dict["theme"]) if row_dict.get("theme") else None
            material.subtheme = (
                str(row_dict["subtheme"]) if row_dict.get("subtheme") else None
            )
            material.subsubtheme = (
                str(row_dict["subsubtheme"]) if row_dict.get("subsubtheme") else None
            )
            material.keywords = (
                str(row_dict["keywords"]) if row_dict.get("keywords") else None
            )
            material.summary = (
                str(row_dict["summary"]) if row_dict.get("summary") else None
            )
            material.source_url = (
                str(row_dict["source_url"]) if row_dict.get("source_url") else None
            )
            material.blob_path = (
                str(row_dict["blob_path"]) if row_dict.get("blob_path") else None
            )

            db.session.add(material)
            count += 1

        db.session.commit()
        print(f"Importação concluída: {count} registros inseridos.")  # noqa: T201


if __name__ == "__main__":
    import_xlsx()
