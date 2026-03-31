import os
from pathlib import Path
from typing import cast

from azure.core.exceptions import ClientAuthenticationError
from flask import (
    Blueprint,
    current_app,
    jsonify,
    redirect,
    render_template,
    request,
    send_from_directory,
)
from openai import OpenAIError
from werkzeug.wrappers import Response

from app.catalog.service import CatalogService
from app.search.azure_text_search import AzureTextSearchService
from app.search.provider import SearchProvider
from app.services.storage_service import get_blob_sas_url

ui_bp = Blueprint("ui", __name__)


def get_catalog_service() -> CatalogService:
    return cast("CatalogService", current_app.extensions["catalog_service"])


def get_search_provider() -> SearchProvider:
    return cast("SearchProvider", current_app.extensions["search_provider"])


def get_azure_text_search_service() -> AzureTextSearchService:
    return cast(
        "AzureTextSearchService",
        current_app.extensions["azure_text_search_service"],
    )


def get_catalog_metadata() -> dict[str, object]:
    repository = get_catalog_service().repository
    return dict(repository.get_metadata())


@ui_bp.route("/download/<path:filename>")
def download_file(filename: str) -> Response:
    if os.environ.get("FLASK_ENV") == "production" or os.environ.get(
        "AZURE_STORAGE_ACCOUNT_URL"
    ):
        sas_url = get_blob_sas_url(filename)
        return redirect(sas_url)

    docs_dir = Path(current_app.root_path).parent / "data" / "docs"
    return send_from_directory(docs_dir, filename, as_attachment=True)


@ui_bp.route("/")
def index() -> str:
    return render_template("index.html", catalog_metadata=get_catalog_metadata())


@ui_bp.route("/search")
def search_documents() -> Response | tuple[Response, int]:
    query = request.args.get("q", "").strip()
    top = _normalize_top(request.args.get("top", 5, type=int), default=5)
    if not query:
        return jsonify({"error": "O parametro q e obrigatorio."}), 400

    service = get_azure_text_search_service()
    results = service.search_text(query, top=top)
    return jsonify(
        {
            "query": query,
            "count": len(results),
            "results": [result.to_dict() for result in results],
        }
    )


@ui_bp.route("/search/hybrid")
def search_documents_hybrid() -> Response | tuple[Response, int]:
    query = request.args.get("q", "").strip()
    top = _normalize_top(request.args.get("top", 10, type=int), default=10)
    if not query:
        return jsonify({"error": "O parametro q e obrigatorio."}), 400

    service = get_azure_text_search_service()
    try:
        results = service.search_hybrid(query, top=top)
    except ClientAuthenticationError as exc:
        return jsonify({"error": str(exc)}), 502
    except OpenAIError as exc:
        return jsonify({"error": str(exc)}), 502

    return jsonify(
        {
            "query": query,
            "count": len(results),
            "results": [result.to_dict() for result in results],
        }
    )


@ui_bp.route("/1_indice_geral")
@ui_bp.route("/1_repo_linear")
def route_1() -> str:
    query = request.args.get("q", "").strip()
    page = request.args.get("page", 1, type=int)

    result = get_catalog_service().get_all_materials_linear(query=query, page=page)
    return render_template(
        "1_repo_linear.html",
        materials=result.items,
        query=query,
        page=result.page,
        total_pages=result.total_pages,
    )


@ui_bp.route("/2_arvore_navegacao")
@ui_bp.route("/2_tree_accordion")
def route_2() -> str:
    tree = get_catalog_service().get_materials_tree()
    return render_template("2_tree_accordion.html", tree=tree)


@ui_bp.route("/3_busca_semantica")
@ui_bp.route("/6_ai_semantic_trad")
def route_3() -> str:
    query = request.args.get("q", "").strip()
    provider = get_search_provider()

    resultados = provider.search(query, top_k=10) if query else []

    return render_template(
        "6_ai_semantic_trad.html",
        resultados=resultados,
        query=query,
    )


@ui_bp.route("/4_busca_rag")
@ui_bp.route("/8_rag_trad")
def route_4() -> str:
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


def _normalize_top(raw_top: int | None, *, default: int) -> int:
    if raw_top is None:
        return default

    return min(max(raw_top, 1), 50)
