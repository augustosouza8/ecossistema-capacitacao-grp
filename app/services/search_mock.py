from typing import Any

from sqlalchemy import or_

from app.db.models import Material
from app.db.session import db
from app.services.search_provider import SearchProvider


class SearchMock(SearchProvider):
    def search(self, query: str, top_k: int = 10) -> list[Any]:
        if not query:
            return []

        search_term = f"%{query}%"

        # Simple match in title, keywords, or summary
        return (
            db.session.query(Material)
            .filter(Material.is_active)
            .filter(
                or_(
                    Material.title.ilike(search_term),
                    Material.keywords.ilike(search_term),
                    Material.summary.ilike(search_term),
                )
            )
            .limit(top_k)
            .all()
        )

    def rag_search(self, query: str, top_k: int = 3) -> dict[str, Any]:
        results = self.search(query, top_k=top_k)

        if not results:
            return {
                "generated_text": (
                    "Não encontrei materiais suficientes no catálogo local para "
                    "responder à sua dúvida. Por favor, reformule a pergunta."
                ),
                "sources": [],
            }

        # Simula resposta RAG baseando-se no summary do melhor material
        best_match = results[0]
        generated_text = (
            f"Esta é uma resposta simulada baseada no material '{best_match.title}'. "
            f"O procedimento envolve: {best_match.summary}. "
            "Siga os passos detalhados no documento ou vídeo para completar a ação."
        )

        return {"generated_text": generated_text, "sources": results}
