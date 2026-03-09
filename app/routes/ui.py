from pathlib import Path

from flask import Blueprint, current_app, render_template, request, send_from_directory
from werkzeug.wrappers import Response

from app.services.catalog_service import CatalogService
from app.services.search_mock import SearchMock
from app.services.search_provider import SearchProvider

ui_bp = Blueprint("ui", __name__)


def get_search_provider() -> SearchProvider:
    return SearchMock()


@ui_bp.route("/download/<path:filename>")
def download_file(filename: str) -> Response:
    docs_dir = Path(current_app.root_path).parent / "data" / "docs"
    return send_from_directory(docs_dir, filename, as_attachment=True)


@ui_bp.route("/")
def index() -> str:
    return render_template("index.html")


@ui_bp.route("/1_repo_linear")
def route_1() -> str:
    query = request.args.get("q", "").strip()
    page = request.args.get("page", 1, type=int)

    result = CatalogService.get_all_materials_linear(query=query, page=page)
    return render_template(
        "1_repo_linear.html",
        materials=result["items"],
        query=query,
        page=result["page"],
        total_pages=result["total_pages"],
    )


@ui_bp.route("/2_tree_accordion")
def route_2() -> str:
    tree = CatalogService.get_materials_tree()
    return render_template("2_tree_accordion.html", tree=tree)


@ui_bp.route("/6_ai_semantic_trad")
def route_6() -> str:
    query = request.args.get("q", "").strip()
    provider = get_search_provider()

    resultados = provider.search(query, top_k=10) if query else []

    return render_template(
        "6_ai_semantic_trad.html",
        resultados=resultados,
        query=query,
    )


@ui_bp.route("/8_rag_trad")
def route_8() -> str:
    query = request.args.get("q", "").strip()
    provider = get_search_provider()

    resultados = []
    texto_gerado = None

    if query:
        rag_res = provider.rag_search(query, top_k=3)
        resultados = rag_res["sources"]
        texto_gerado = rag_res["generated_text"]

    return render_template(
        "8_rag_trad.html",
        resultados=resultados,
        texto_gerado=texto_gerado,
        query=query,
    )
