from flask.testing import FlaskClient

from app.search.azure_models import AzureSearchDocument


class StubAzureTextSearchService:
    def search_text(self, query: str, top: int = 5) -> list[AzureSearchDocument]:
        assert query == "empenho"
        assert top == 2
        return [
            AzureSearchDocument(
                id="abc-123",
                metadata_storage_name="POP_101__empenho-inclusao-ordinario.docx",
                metadata_storage_path="https://storage/path.docx",
                content="Passo a passo do empenho.",
                search_score=1.5,
            )
        ]

    def search_hybrid(self, query: str, top: int = 10) -> list[AzureSearchDocument]:
        assert query == "empenho"
        assert top == 2
        return [
            AzureSearchDocument(
                id="hybrid-123",
                metadata_storage_name="POP_105__empenho-reforco.docx",
                metadata_storage_path="https://storage/hybrid.docx",
                content="Instrucoes para reforco de empenho.",
                search_score=3.15,
            )
        ]


def test_index_route(client: FlaskClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Testes de Usabilidade (MVP)" in html
    assert "1. Índice Geral (Repositório Linear)" in html


def test_repo_linear_route(client: FlaskClient) -> None:
    response = client.get("/1_indice_geral")
    assert response.status_code == 200
    assert "Empenho guia" in response.get_data(as_text=True)


def test_tree_accordion_route(client: FlaskClient) -> None:
    response = client.get("/2_arvore_navegacao")
    assert response.status_code == 200
    assert "Empenho" in response.get_data(as_text=True)


def test_semantic_trad_route(client: FlaskClient) -> None:
    response = client.get("/3_busca_semantica?q=guia")
    assert response.status_code == 200
    assert "Empenho guia" in response.get_data(as_text=True)


def test_rag_trad_route(client: FlaskClient) -> None:
    response = client.get("/4_busca_rag?q=empenho")
    assert response.status_code == 200
    assert "Resumo local do catalogo" in response.get_data(as_text=True)


def test_legacy_routes_remain_available(client: FlaskClient) -> None:
    for legacy_route in (
        "/1_repo_linear",
        "/2_tree_accordion",
        "/6_ai_semantic_trad?q=guia",
        "/8_rag_trad?q=empenho",
    ):
        response = client.get(legacy_route)
        assert response.status_code == 200


def test_search_json_route(client: FlaskClient) -> None:
    client.application.extensions["azure_text_search_service"] = (
        StubAzureTextSearchService()
    )

    response = client.get("/search?q=empenho&top=2")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload == {
        "query": "empenho",
        "count": 1,
        "results": [
            {
                "id": "abc-123",
                "metadata_storage_name": "POP_101__empenho-inclusao-ordinario.docx",
                "metadata_storage_path": "https://storage/path.docx",
                "content": "Passo a passo do empenho.",
                "search_score": 1.5,
            }
        ],
    }


def test_search_json_route_requires_query(client: FlaskClient) -> None:
    response = client.get("/search")

    assert response.status_code == 400
    assert response.get_json() == {"error": "O parametro q e obrigatorio."}


def test_search_hybrid_json_route(client: FlaskClient) -> None:
    client.application.extensions["azure_text_search_service"] = (
        StubAzureTextSearchService()
    )

    response = client.get("/search/hybrid?q=empenho&top=2")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload == {
        "query": "empenho",
        "count": 1,
        "results": [
            {
                "id": "hybrid-123",
                "metadata_storage_name": "POP_105__empenho-reforco.docx",
                "metadata_storage_path": "https://storage/hybrid.docx",
                "content": "Instrucoes para reforco de empenho.",
                "search_score": 3.15,
            }
        ],
    }


def test_search_hybrid_json_route_requires_query(client: FlaskClient) -> None:
    response = client.get("/search/hybrid")

    assert response.status_code == 400
    assert response.get_json() == {"error": "O parametro q e obrigatorio."}
