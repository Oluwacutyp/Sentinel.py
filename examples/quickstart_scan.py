"""Quickstart: scan synthetic data with the full QuantumEngine pipeline."""
from __future__ import annotations

from sentinel.core.engine import QuantumEngine
from sentinel.data.feed import make_synthetic


def main():
    df = make_synthetic(1500, seed=42)
    engine = QuantumEngine("configs/default.yaml")
    print("fitting ML gate on first half…")
    info = engine.fit_ml(df.iloc[:750])
    print("ml:", {k: v for k, v in info.items() if k != "importance"})
    report = engine.scan(df, symbol="SYNTH")
    print(report.summary())
    print("stops:", report.stops)
    print("top5:\n", report.ranked[["sharpe", "score"]].head())


if __name__ == "__main__":
    main()
