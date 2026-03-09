from typing import Any

from app.db.models import Material
from app.db.session import db


class CatalogService:
    @staticmethod
    def get_all_materials_linear(
        query: str | None = None, page: int = 1, per_page: int = 20
    ) -> dict[str, Any]:
        qs = db.session.query(Material).filter(Material.is_active)

        if query:
            # Busca no backend com ILIKE no título (case-insensitive sqlite)
            search_term = f"%{query}%"
            qs = qs.filter(Material.title.ilike(search_term))

        qs = qs.order_by(Material.id.asc())

        # Paginação manual simples
        total = qs.count()
        items = qs.offset((page - 1) * per_page).limit(per_page).all()

        return {
            "items": items,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page,
        }

    @staticmethod
    def get_materials_tree() -> dict[str, Any]:
        materials = (
            db.session.query(Material)
            .filter(Material.is_active)
            .order_by(Material.id.asc())
            .all()
        )

        tree: dict[str, Any] = {}
        for m in materials:
            mod = m.module
            thm = m.theme or ""
            sub = m.subtheme or ""
            ssub = m.subsubtheme or ""

            if mod not in tree:
                tree[mod] = {}
            if thm not in tree[mod]:
                tree[mod][thm] = {}
            if sub not in tree[mod][thm]:
                tree[mod][thm][sub] = {}
            if ssub not in tree[mod][thm][sub]:
                tree[mod][thm][sub][ssub] = []

            tree[mod][thm][sub][ssub].append(m)

        return tree
