"""Execution script for all 4 formal experiments defined in academic specification:
Experiment 1: Minimax vs Alpha-Beta (Equivalence & Pruning Efficiency)
Experiment 2: Search Depth Analysis (Computational Complexity Scaling)
Experiment 3: Greedy vs Minimax (Tactical Blindspots & Horizon Effects)
Experiment 4: Iterative Deepening (Time-Budget Resource Allocation)
"""

import os
import sys

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import json
import time
import pandas as pd
import numpy as np
import chess

from engine.board_utils import create_board
from engine.minimax import minimax_search
from engine.alphabeta import alphabeta_search
from engine.greedy import greedy_search
from engine.iterative_deepening import iterative_deepening_search
from analysis.benchmark import load_test_positions, run_full_benchmark


def run_experiment_1_minimax_vs_alphabeta(positions: list, depths=(1, 2, 3)) -> pd.DataFrame:
    """Experiment 1: Verify Minimax and Alpha-Beta produce identical scores and best moves,

    while measuring node reduction and speedup.
    """
    rows = []
    for pos in positions:
        board = create_board(pos["fen"])
        for d in depths:
            res_mm = minimax_search(board.copy(), depth=d, use_move_ordering=True)
            res_ab = alphabeta_search(board.copy(), depth=d, use_move_ordering=True)

            score_diff = abs(res_mm["score"] - res_ab["score"])
            same_best_move = (res_mm["best_move"] == res_ab["best_move"])
            node_reduction = (
                (res_mm["nodes_explored"] - res_ab["nodes_explored"]) / res_mm["nodes_explored"] * 100.0
                if res_mm["nodes_explored"] > 0 else 0.0
            )
            speedup = (
                res_mm["execution_time"] / res_ab["execution_time"]
                if res_ab["execution_time"] > 0 else 1.0
            )

            rows.append({
                "experiment": "Exp1_Minimax_vs_AlphaBeta",
                "position_id": pos["id"],
                "position_name": pos["name"],
                "depth": d,
                "minimax_time_s": round(res_mm["execution_time"], 5),
                "alphabeta_time_s": round(res_ab["execution_time"], 5),
                "speedup": round(speedup, 2),
                "minimax_nodes": res_mm["nodes_explored"],
                "alphabeta_nodes": res_ab["nodes_explored"],
                "pruned_branches": res_ab["pruned_branches"],
                "node_reduction_pct": round(node_reduction, 2),
                "minimax_score": res_mm["score"],
                "alphabeta_score": res_ab["score"],
                "score_match": (score_diff == 0),
                "minimax_move": res_mm["best_move_san"],
                "alphabeta_move": res_ab["best_move_san"],
                "move_match": same_best_move
            })
    return pd.DataFrame(rows)


def run_experiment_2_search_depth(positions: list, depths=(1, 2, 3, 4)) -> pd.DataFrame:
    """Experiment 2: Measure scaling of search metrics across depth 1..4."""
    rows = []
    for pos in positions:
        board = create_board(pos["fen"])
        for d in depths:
            res_ab = alphabeta_search(board.copy(), depth=d, use_move_ordering=True)
            rows.append({
                "experiment": "Exp2_Search_Depth",
                "position_id": pos["id"],
                "position_name": pos["name"],
                "depth": d,
                "execution_time_s": round(res_ab["execution_time"], 5),
                "nodes_explored": res_ab["nodes_explored"],
                "pruned_branches": res_ab["pruned_branches"],
                "score_cp": res_ab["score"],
                "best_move_san": res_ab["best_move_san"],
                "pv_san": " ".join(res_ab["pv_san"])
            })
    return pd.DataFrame(rows)


def run_experiment_3_greedy_vs_minimax(positions: list) -> pd.DataFrame:
    """Experiment 3: Contrast Greedy 1-ply heuristic choice against Minimax adversarial lookahead (depth 3).

    Specifically highlights tactical blind spots.
    """
    rows = []
    for pos in positions:
        board = create_board(pos["fen"])
        res_greedy = greedy_search(board.copy())
        res_mm = alphabeta_search(board.copy(), depth=3)

        move_agreement = (res_greedy["best_move"] == res_mm["best_move"])
        score_diff = abs(res_greedy["score"] - res_mm["score"])

        rows.append({
            "experiment": "Exp3_Greedy_vs_Adversarial",
            "position_id": pos["id"],
            "position_name": pos["name"],
            "category": pos["category"],
            "greedy_move": res_greedy["best_move_san"],
            "greedy_eval_1ply": res_greedy["score"],
            "adversarial_move_d3": res_mm["best_move_san"],
            "adversarial_eval_d3": res_mm["score"],
            "moves_agree": move_agreement,
            "greedy_nodes": res_greedy["nodes_explored"],
            "adversarial_nodes": res_mm["nodes_explored"],
            "tactical_divergence_noted": not move_agreement
        })
    return pd.DataFrame(rows)


def run_experiment_4_iterative_deepening(positions: list, time_limits=(0.2, 0.5, 1.0, 2.0)) -> pd.DataFrame:
    """Experiment 4: Evaluate Iterative Deepening across varying time budgets."""
    rows = []
    for pos in positions:
        board = create_board(pos["fen"])
        for tl in time_limits:
            res_ids = iterative_deepening_search(board.copy(), max_depth=6, time_limit=tl)
            rows.append({
                "experiment": "Exp4_Iterative_Deepening",
                "position_id": pos["id"],
                "position_name": pos["name"],
                "time_limit_s": tl,
                "completed_depth": res_ids["completed_depth"],
                "actual_time_s": round(res_ids["execution_time"], 4),
                "total_nodes": res_ids["nodes_explored"],
                "score_cp": res_ids["score"],
                "best_move_san": res_ids["best_move_san"],
                "timed_out": res_ids["timed_out"]
            })
    return pd.DataFrame(rows)


def run_all_experiments() -> None:
    """Run all 4 experiments and save results to CSV and markdown documentation."""
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    doc_dir = os.path.join(os.path.dirname(__file__), "..", "documentation")
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(doc_dir, exist_ok=True)

    positions = load_test_positions()

    print("Running Experiment 1: Minimax vs Alpha-Beta...")
    df_exp1 = run_experiment_1_minimax_vs_alphabeta(positions)
    df_exp1.to_csv(os.path.join(data_dir, "exp1_minimax_vs_alphabeta.csv"), index=False)

    print("Running Experiment 2: Search Depth Scaling...")
    df_exp2 = run_experiment_2_search_depth(positions)
    df_exp2.to_csv(os.path.join(data_dir, "exp2_search_depth.csv"), index=False)

    print("Running Experiment 3: Greedy vs Minimax...")
    df_exp3 = run_experiment_3_greedy_vs_minimax(positions)
    df_exp3.to_csv(os.path.join(data_dir, "exp3_greedy_vs_minimax.csv"), index=False)

    print("Running Experiment 4: Iterative Deepening...")
    df_exp4 = run_experiment_4_iterative_deepening(positions)
    df_exp4.to_csv(os.path.join(data_dir, "exp4_iterative_deepening.csv"), index=False)

    # Also run the full multi-algorithm benchmark CSV
    print("Running Consolidated Benchmark...")
    run_full_benchmark(os.path.join(data_dir, "benchmark_results.csv"), repeats=3, max_depth=3)

    print("All experiments completed successfully!")


if __name__ == "__main__":
    run_all_experiments()
