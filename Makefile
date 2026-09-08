.PHONY: install build test smoke backtest live-dry lint clean lines

install:
	pip install -e ".[all]"

build:
	python scripts/codegen_megabuild.py

test:
	python -m pytest tests -q

smoke:
	PYTHONPATH=. python scripts/smoke.py

backtest:
	python -m sentinel backtest --config configs/default.yaml

live-dry:
	python -m sentinel live --dry-run --config configs/default.yaml

optimize:
	python -m sentinel optimize --config configs/default.yaml --trials 50

lint:
	ruff check sentinel tests scripts || true

lines:
	find sentinel tests scripts configs docs examples -type f | xargs wc -l | tail -3

clean:
	find . -name "__pycache__" -type d -prune -exec rm -rf {} + 2>/dev/null; true
