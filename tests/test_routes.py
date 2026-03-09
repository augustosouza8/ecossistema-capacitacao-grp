from flask.testing import FlaskClient


def test_index_route(client: FlaskClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert b"Testes de Usabilidade (MVP)" in response.data


def test_repo_linear_route(client: FlaskClient) -> None:
    response = client.get("/1_repo_linear")
    assert response.status_code == 200


def test_tree_accordion_route(client: FlaskClient) -> None:
    response = client.get("/2_tree_accordion")
    assert response.status_code == 200


def test_semantic_trad_route(client: FlaskClient) -> None:
    response = client.get("/6_ai_semantic_trad")
    assert response.status_code == 200


def test_rag_trad_route(client: FlaskClient) -> None:
    response = client.get("/8_rag_trad")
    assert response.status_code == 200
