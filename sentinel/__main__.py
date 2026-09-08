"""Entry point: python -m sentinel <scan|backtest|optimize|live> [...]"""
from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
