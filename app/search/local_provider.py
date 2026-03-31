import re

from app.catalog.models import CatalogMaterial
from app.catalog.repository import CatalogRepository
from app.search.provider import RagResult, SearchProvider


class LocalCatalogSearchProvider(SearchProvider):
    def __init__(self, repository: CatalogRepository) -> None:
        self._repository = repository

    def search(self, query: str, top_k: int = 10) -> list[CatalogMaterial]:
        normalized_query = query.strip()
        if not normalized_query:
            return []

        safe_top_k = max(top_k, 1)
        ranked_materials = sorted(
            self._ranked_matches(normalized_query),
            key=lambda match: (-match[0], match[1].id),
        )
        return [material for _, material in ranked_materials[:safe_top_k]]

    def rag_search(self, query: str, top_k: int = 3) -> RagResult:
        sources = self.search(query, top_k=top_k)
        if not sources:
            return {
                "generated_text": (
                    "Nao encontrei materiais suficientes no catalogo atual "
                    "para responder "
                    "a sua pergunta. Tente reformular a busca com termos mais diretos."
                ),
                "sources": [],
            }

        primary_source = sources[0]
        generated_text = self._build_generated_text(query=query, sources=sources)
        if not generated_text:
            generated_text = (
                f"Encontrei materiais relacionados a '{query}'. O item mais aderente e "
                f"'{primary_source.title}'. Consulte as fontes listadas para seguir o "
                "procedimento completo."
            )

        return {"generated_text": generated_text, "sources": sources}

    def _ranked_matches(self, query: str) -> list[tuple[int, CatalogMaterial]]:
        tokens = self._tokenize(query)
        normalized_query = query.casefold()
        ranked_matches: list[tuple[int, CatalogMaterial]] = []

        for material in self._repository.list_materials():
            score = self._score_material(material, normalized_query, tokens)
            if score > 0:
                ranked_matches.append((score, material))

        return ranked_matches

    def _score_material(
        self,
        material: CatalogMaterial,
        normalized_query: str,
        tokens: list[str],
    ) -> int:
        title = material.title.casefold()
        keywords = (material.keywords or "").casefold()
        summary = (material.summary or "").casefold()
        module = material.module.casefold()

        score = 0
        if normalized_query in title:
            score += 12
        if normalized_query in keywords:
            score += 8
        if normalized_query in summary:
            score += 6
        if normalized_query in module:
            score += 4

        for token in tokens:
            if token in title:
                score += 5
            if token in keywords:
                score += 3
            if token in summary:
                score += 2
            if token in module:
                score += 1

        searchable_chunks = [title, keywords, summary, module]
        if tokens and all(
            any(token in chunk for chunk in searchable_chunks) for token in tokens
        ):
            score += 5

        return score

    def _build_generated_text(
        self,
        query: str,
        sources: list[CatalogMaterial],
    ) -> str:
        primary_source = sources[0]
        primary_summary = (
            primary_source.summary
            or "Consulte o material principal para ver o procedimento completo."
        )

        if len(sources) == 1:
            return (
                f"Resumo local do catalogo para '{query}': {primary_summary} "
                f"O material mais aderente e '{primary_source.title}', no modulo "
                f"{primary_source.module}."
            )

        supporting_titles = ", ".join(source.title for source in sources[1:])
        return (
            f"Resumo local do catalogo para '{query}': {primary_summary} "
            f"Comece por '{primary_source.title}' e, se precisar de contexto "
            "adicional, "
            f"consulte tambem: {supporting_titles}."
        )

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        return re.findall(r"\w+", text.casefold())
