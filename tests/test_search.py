from flask import Flask

from app.db.models import Material
from app.db.session import db
from app.services.search_mock import SearchMock


def test_search_contract(app: Flask) -> None:
    with app.app_context():
        # Setup mock data
        m1 = Material()
        m1.id = 1
        m1.type = "POP"
        m1.title = "Empenho mock"
        m1.module = "Empenho"
        m1.is_active = True

        m2 = Material()
        m2.id = 2
        m2.type = "VIDEO"
        m2.title = "Video liquidacao"
        m2.module = "Liquidação"
        m2.summary = "liquidacao mock"
        m2.is_active = True

        db.session.add_all([m1, m2])
        db.session.commit()

        provider = SearchMock()

        # Test basic search
        results = provider.search("mock")
        assert isinstance(results, list)
        assert len(results) == 2
        assert all(hasattr(r, "id") and hasattr(r, "title") for r in results)

        # Test RAG search
        rag_res = provider.rag_search("empenho")
        assert isinstance(rag_res, dict)
        assert "generated_text" in rag_res
        assert "sources" in rag_res
        assert len(rag_res["sources"]) == 1
        assert "Empenho mock" in rag_res["generated_text"]
