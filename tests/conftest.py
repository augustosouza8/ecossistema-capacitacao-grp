from collections.abc import Generator
from pathlib import Path
from typing import TYPE_CHECKING, cast

import pytest
from flask import Flask
from flask.testing import FlaskClient, FlaskCliRunner
from openpyxl import Workbook

from app import create_app

if TYPE_CHECKING:
    from openpyxl.worksheet.worksheet import Worksheet


@pytest.fixture
def catalog_workbook_path(tmp_path: Path) -> Path:
    workbook = Workbook()
    worksheet = cast("Worksheet", workbook.active)
    worksheet.append(
        [
            "id",
            "type",
            "title",
            "module",
            "theme",
            "subtheme",
            "subsubtheme",
            "keywords",
            "summary",
            "source_url",
            "blob_path",
        ]
    )
    worksheet.append(
        [
            1,
            "POP",
            "Empenho guia",
            "Empenho",
            "Inclusao",
            "Ordinario",
            None,
            "guia; empenho",
            "Passo a passo de empenho guia.",
            None,
            "POP_101__empenho-inclusao-ordinario.docx",
        ]
    )
    worksheet.append(
        [
            2,
            "VIDEO",
            "Video liquidacao",
            "Liquidacao",
            "Conceitos",
            None,
            None,
            "liquidacao; tutorial",
            "Video de liquidacao tutorial.",
            "https://example.com/video-liquidacao",
            None,
        ]
    )

    workbook_path = tmp_path / "materials.xlsx"
    workbook.save(workbook_path)
    workbook.close()
    return workbook_path


@pytest.fixture
def app(
    monkeypatch: pytest.MonkeyPatch, catalog_workbook_path: Path
) -> Generator[Flask]:
    monkeypatch.setenv("CATALOG_XLSX_PATH", str(catalog_workbook_path))
    monkeypatch.setenv("SEARCH_PROVIDER", "local")
    monkeypatch.setenv("AZURE_SEARCH_ENDPOINT", "https://example.search.windows.net")
    monkeypatch.setenv("AZURE_SEARCH_INDEX_NAME", "idx-eco-grp-v1")
    monkeypatch.setenv("AZURE_SEARCH_API_KEY", "test-api-key")
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://example.openai.azure.com")
    monkeypatch.setenv("AZURE_OPENAI_API_VERSION", "2024-02-01")
    monkeypatch.setenv(
        "AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT",
        "text-embedding-3-small",
    )

    app = create_app()
    app.config.update({"TESTING": True})

    with app.app_context():
        yield app


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    return app.test_client()


@pytest.fixture
def runner(app: Flask) -> FlaskCliRunner:
    return app.test_cli_runner()
