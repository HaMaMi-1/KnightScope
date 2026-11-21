"""Benchmarking framework for KnightScope.
Conducts reproducible experiments across selected chess positions.
Measures execution time (median of repeats), nodes explored, scores, and pruning efficiency.
Saves actual empirical data to CSV.
"""

import os
import sys

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import json
import time
from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np
import chess

from engine.board_utils import create_board
from engine.minimax import minimax_search
from engine.alphabeta import alphabeta_search
from engine.greedy import greedy_search
from engine.iterative_deepening import iterative_deepening_search


def load_test_positions(file_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Load benchmark positions from JSON file."""
    if file_path is None:
        file_path = os.path.join(
            os.path.dirname(__file__), "..", "data", "test_positions.json"
        )
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def benchmark_position(
    fen: str,
    depth: int = 3,
    repeats: int = 3,
    algorithms: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """Benchmark specified algorithms on a single chess position.
    Repeats execution to report median timing.
    """
    if algorithms is None:
        algorithms = ["Minimax", "AlphaBeta", "Greedy", "IterativeDeepening"]

    board = create_board(fen)
    results = []

    # 1. Minimax
    if "Minimax" in algorithms:
        times = []
        res = None
        for _ in range(repeats):
            b_copy = board.copy()
            res = minimax_search(b_copy, depth=depth, use_move_ordering=True)
            times.append(res["execution_time"])
        results.append({
            "algorithm": "Minimax",
            "depth": depth,
            "execution_time": float(np.median(times)),
            "nodes_explored": res["nodes_explored"],
            "pruned_branches": res["pruned_branches"],
            "score": res["score"],
            "best_move": res["best_move"].uci() if res["best_move"] else None,
            "best_move_san": res["best_move_san"],
            "nodes_per_second": res["nodes_explored"] / max(np.median(times), 1e-6)
        })

    # 2. Alpha-Beta
    if "AlphaBeta" in algorithms:
        times = []
        res = None
        for _ in range(repeats):
            b_copy = board.copy()
            res = alphabeta_search(b_copy, depth=depth, use_move_ordering=True)
            times.append(res["execution_time"])
        results.append({
            "algorithm": "AlphaBeta",
            "depth": depth,
            "execution_time": float(np.median(times)),
            "nodes_explored": res["nodes_explored"],
            "pruned_branches": res["pruned_branches"],
            "score": res["score"],
            "best_move": res["best_move"].uci() if res["best_move"] else None,
            "best_move_san": res["best_move_san"],
            "nodes_per_second": res["nodes_explored"] / max(np.median(times), 1e-6)
        })

    # 3. Greedy (strictly 1-ply baseline)
    if "Greedy" in algorithms:
        times = []
        res = None
        for _ in range(repeats):
            b_copy = board.copy()
            res = greedy_search(b_copy)
            times.append(res["execution_time"])
        results.append({
            "algorithm": "Greedy",
            "depth": 1,
            "execution_time": float(np.median(times)),
            "nodes_explored": res["nodes_explored"],
            "pruned_branches": 0,
            "score": res["score"],
            "best_move": res["best_move"].uci() if res["best_move"] else None,
            "best_move_san": res["best_move_san"],
            "nodes_per_second": res["nodes_explored"] / max(np.median(times), 1e-6)
        })

    # 4. Iterative Deepening
    if "IterativeDeepening" in algorithms:
        times = []
        res = None
        for _ in range(repeats):
            b_copy = board.copy()
            res = iterative_deepening_search(b_copy, max_depth=depth, time_limit=5.0)
            times.append(res["execution_time"])
        results.append({
            "algorithm": "IterativeDeepening",
            "depth": res["completed_depth"],
            "execution_time": float(np.median(times)),
            "nodes_explored": res["nodes_explored"],
            "pruned_branches": res["pruned_branches"],
            "score": res["score"],
            "best_move": res["best_move"].uci() if res["best_move"] else None,
            "best_move_san": res["best_move_san"],
            "nodes_per_second": res["nodes_explored"] / max(np.median(times), 1e-6)
        })

    return results


def run_full_benchmark(
    output_csv_path: Optional[str] = None,
    repeats: int = 3,
    max_depth: int = 3
) -> pd.DataFrame:
    """Execute complete benchmark suite across all test positions and depths 1 to max_depth."""
    positions = load_test_positions()
    records = []

    print(f"Starting KnightScope Benchmark across {len(positions)} positions (repeats={repeats})...")

    for pos in positions:
        pos_id = pos["id"]
        pos_name = pos["name"]
        fen = pos["fen"]
        category = pos["category"]
        print(f"Benchmarking [{pos_id}] {pos_name}...")

        # Test depths 1, 2, 3 (and 4 for AlphaBeta if fast)
        for d in range(1, max_depth + 1):
            res_list = benchmark_position(
                fen=fen,
                depth=d,
                repeats=repeats,
                algorithms=["Minimax", "AlphaBeta", "Greedy", "IterativeDeepening"]
            )
            for entry in res_list:
                # If Greedy, only include once at depth 1 to avoid duplicating 1-ply data
                if entry["algorithm"] == "Greedy" and d > 1:
                    continue
                records.append({
                    "position_id": pos_id,
                    "position_name": pos_name,
                    "category": category,
                    "fen": fen,
                    "algorithm": entry["algorithm"],
                    "depth": entry["depth"],
                    "target_depth": d,
                    "execution_time_sec": round(entry["execution_time"], 5),
                    "nodes_explored": entry["nodes_explored"],
                    "pruned_branches": entry["pruned_branches"],
                    "score_cp": entry["score"],
                    "best_move_uci": entry["best_move"],
                    "best_move_san": entry["best_move_san"],
                    "nodes_per_second": round(entry["nodes_per_second"], 1)
                })

    df = pd.DataFrame(records)

    if output_csv_path is None:
        output_csv_path = os.path.join(
            os.path.dirname(__file__), "..", "data", "benchmark_results.csv"
        )
    os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)
    df.to_csv(output_csv_path, index=False)
    print(f"Benchmark finished. Stored {len(df)} records to {output_csv_path}")
    return df
