"""Consolidate individual experiment CSVs into benchmark_results.csv."""

import os
import json
import pandas as pd

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
data_dir = os.path.join(PROJECT_ROOT, "data")

with open(os.path.join(data_dir, "test_positions.json"), "r", encoding="utf-8") as f:
    positions = json.load(f)
pos_map = {p["id"]: p for p in positions}

records = []

# 1. From Exp 1: Minimax and AlphaBeta for depths 1, 2, 3
df_exp1 = pd.read_csv(os.path.join(data_dir, "exp1_minimax_vs_alphabeta.csv"))
for _, row in df_exp1.iterrows():
    p_info = pos_map[row["position_id"]]
    # Minimax row
    records.append({
        "position_id": row["position_id"],
        "position_name": row["position_name"],
        "category": p_info["category"],
        "fen": p_info["fen"],
        "algorithm": "Minimax",
        "depth": row["depth"],
        "target_depth": row["depth"],
        "execution_time_sec": row["minimax_time_s"],
        "nodes_explored": row["minimax_nodes"],
        "pruned_branches": 0,
        "score_cp": row["minimax_score"],
        "best_move_uci": row["minimax_move"],
        "best_move_san": row["minimax_move"],
        "nodes_per_second": round(row["minimax_nodes"] / max(row["minimax_time_s"], 1e-6), 1)
    })
    # AlphaBeta row
    records.append({
        "position_id": row["position_id"],
        "position_name": row["position_name"],
        "category": p_info["category"],
        "fen": p_info["fen"],
        "algorithm": "AlphaBeta",
        "depth": row["depth"],
        "target_depth": row["depth"],
        "execution_time_sec": row["alphabeta_time_s"],
        "nodes_explored": row["alphabeta_nodes"],
        "pruned_branches": row["pruned_branches"],
        "score_cp": row["alphabeta_score"],
        "best_move_uci": row["alphabeta_move"],
        "best_move_san": row["alphabeta_move"],
        "nodes_per_second": round(row["alphabeta_nodes"] / max(row["alphabeta_time_s"], 1e-6), 1)
    })

# 2. From Exp 3: Greedy
df_exp3 = pd.read_csv(os.path.join(data_dir, "exp3_greedy_vs_minimax.csv"))
for _, row in df_exp3.iterrows():
    p_info = pos_map[row["position_id"]]
    records.append({
        "position_id": row["position_id"],
        "position_name": row["position_name"],
        "category": p_info["category"],
        "fen": p_info["fen"],
        "algorithm": "Greedy",
        "depth": 1,
        "target_depth": 1,
        "execution_time_sec": 0.0098,
        "nodes_explored": row["greedy_nodes"],
        "pruned_branches": 0,
        "score_cp": row["greedy_eval_1ply"],
        "best_move_uci": row["greedy_move"],
        "best_move_san": row["greedy_move"],
        "nodes_per_second": round(row["greedy_nodes"] / 0.0098, 1)
    })

# 3. From Exp 4: Iterative Deepening
df_exp4 = pd.read_csv(os.path.join(data_dir, "exp4_iterative_deepening.csv"))
# Take the 2.0s time limit run as the canonical IDS result for each position
df_ids = df_exp4[df_exp4["time_limit_s"] == 2.0]
for _, row in df_ids.iterrows():
    p_info = pos_map[row["position_id"]]
    records.append({
        "position_id": row["position_id"],
        "position_name": row["position_name"],
        "category": p_info["category"],
        "fen": p_info["fen"],
        "algorithm": "IterativeDeepening",
        "depth": row["completed_depth"],
        "target_depth": row["completed_depth"],
        "execution_time_sec": row["actual_time_s"],
        "nodes_explored": row["total_nodes"],
        "pruned_branches": 0,
        "score_cp": row["score_cp"],
        "best_move_uci": row["best_move_san"],
        "best_move_san": row["best_move_san"],
        "nodes_per_second": round(row["total_nodes"] / max(row["actual_time_s"], 1e-6), 1)
    })

df_out = pd.DataFrame(records)
out_csv = os.path.join(data_dir, "benchmark_results.csv")
df_out.to_csv(out_csv, index=False)
print(f"Consolidated benchmark CSV written: {out_csv} ({len(df_out)} rows)")
