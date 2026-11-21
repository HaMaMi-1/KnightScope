"""Statistical aggregation and metric calculations for experimental data."""

from typing import List, Dict, Any
import pandas as pd
import numpy as np


def calculate_speedup(minimax_time: float, alphabeta_time: float) -> float:
    """Calculate speedup factor of Alpha-Beta over Minimax."""
    if alphabeta_time <= 0:
        return 1.0
    return round(minimax_time / alphabeta_time, 2)


def calculate_pruning_efficiency(minimax_nodes: int, alphabeta_nodes: int) -> float:
    """Calculate percentage reduction in nodes explored achieved by Alpha-Beta."""
    if minimax_nodes <= 0:
        return 0.0
    reduction = (minimax_nodes - alphabeta_nodes) / minimax_nodes * 100.0
    return round(max(0.0, reduction), 2)


def summarize_benchmark_dataframe(df: pd.DataFrame) -> Dict[str, Any]:
    """Generate statistical summary of benchmark experiments."""
    summary = {}
    if df.empty:
        return summary

    summary["total_runs"] = len(df)
    summary["algorithms"] = df["algorithm"].unique().tolist() if "algorithm" in df.columns else []

    if "execution_time" in df.columns:
        summary["avg_time_by_algo"] = df.groupby("algorithm")["execution_time"].mean().to_dict()
        summary["median_time_by_algo"] = df.groupby("algorithm")["execution_time"].median().to_dict()

    if "nodes_explored" in df.columns:
        summary["avg_nodes_by_algo"] = df.groupby("algorithm")["nodes_explored"].mean().to_dict()

    return summary
