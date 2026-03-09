# Regras Absolutas de Desenvolvimento
SEMPRE rode `uv run ruff format && uv run ruff check --fix && uv run mypy . && uv run pytest` até todos passarem sem erros antes de considerar uma tarefa pronta. 
Nunca pare até que todos passem (formatador, linter, typechecker, testes)! 
Nunca, em hipótese alguma, desabilite regras de lint, adicione ignoradores de tipo (como `# type: ignore`), ou modifique a configuração de quais regras estão habilitadas no `pyproject.toml`. Se o comando falhar, o código está errado. Conserte o código.
