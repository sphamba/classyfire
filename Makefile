install:
	pip install pre-commit
	pre-commit install --install-hooks
	uv venv
	uv pip install -e .[dev]
	touch .env

lint:
	pre-commit run --all-files

run:
	uv run streamlit run classyfire/main.py --server.headless true
