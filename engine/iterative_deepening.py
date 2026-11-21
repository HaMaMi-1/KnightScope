"""Iterative Deepening Search (IDS).
Progressive deepening search strategy executing depth-limited Alpha-Beta search
at increasing depth levels (d = 1, 2, 3, ...).

Supports configurable time limits.
Preserves the best result from the last completed iteration.
Records the progression across all completed iterations.
"""

import time
from typing import Dict, Any, Optional, List
import chess
from .alphabeta import alphabeta_search
from .evaluation import evaluate_board
from .board_utils import get_move_san


def iterative_deepening_search(
    board: chess.Board,
    max_depth: int = 5,
    time_limit: float = 2.0,
    use_move_ordering: bool = True,
    weights: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    """Perform Iterative Deepening Search with time-limiting and history logging."""
    start_time = time.perf_counter()
    legal_moves = list(board.legal_moves)

    if not legal_moves:
        elapsed = time.perf_counter() - start_time
        eval_score = evaluate_board(board, 0, weights)
        return {
            "best_move": None,
            "best_move_san": None,
            "score": eval_score,
            "nodes_explored": 1,
            "pruned_branches": 0,
            "execution_time": elapsed,
            "depth": 0,
            "max_depth": max_depth,
            "time_limit": time_limit,
            "candidate_moves": [],
            "principal_variation": [],
            "pv_san": [],
            "iterations": [],
            "completed_depth": 0,
            "timed_out": False
        }

    iterations = []
    total_nodes = 0
    total_pruned = 0
    last_completed_result = None
    timed_out = False

    for current_depth in range(1, max_depth + 1):
        depth_start = time.perf_counter()

        # Check if we already exceeded time limit before starting this iteration
        if (depth_start - start_time) >= time_limit:
            timed_out = True
            break

        # Run Alpha-Beta at current_depth
        result = alphabeta_search(
            board=board,
            depth=current_depth,
            use_move_ordering=use_move_ordering,
            weights=weights
        )

        depth_elapsed = time.perf_counter() - depth_start
        total_elapsed = time.perf_counter() - start_time
        total_nodes += result["nodes_explored"]
        total_pruned += result["pruned_branches"]

        iteration_entry = {
            "depth": current_depth,
            "best_move": result["best_move"],
            "best_move_san": result["best_move_san"],
            "score": result["score"],
            "nodes_explored": result["nodes_explored"],
            "cumulative_nodes": total_nodes,
            "pruned_branches": result["pruned_branches"],
            "iteration_time": depth_elapsed,
            "elapsed_time": total_elapsed,
            "principal_variation": result["principal_variation"],
            "pv_san": result["pv_san"]
        }
        iterations.append(iteration_entry)
        last_completed_result = result

        # Check if time limit reached or if search found a forced checkmate
        if total_elapsed >= time_limit:
            timed_out = True
            break
        if abs(result["score"]) >= 19000:
            # Found forced checkmate; further deepening unnecessary
            break

    total_time = time.perf_counter() - start_time

    if last_completed_result is None:
        # Fallback to depth 1 if somehow timed out immediately
        last_completed_result = alphabeta_search(board, 1, use_move_ordering, weights)

    return {
        "best_move": last_completed_result["best_move"],
        "best_move_san": last_completed_result["best_move_san"],
        "score": last_completed_result["score"],
        "nodes_explored": total_nodes,
        "pruned_branches": total_pruned,
        "execution_time": total_time,
        "completed_depth": len(iterations),
        "max_depth_target": max_depth,
        "time_limit": time_limit,
        "timed_out": timed_out,
        "candidate_moves": last_completed_result["candidate_moves"],
        "all_candidates": last_completed_result.get("all_candidates", []),
        "principal_variation": last_completed_result["principal_variation"],
        "pv_san": last_completed_result["pv_san"],
        "iterations": iterations,
        "nodes_per_second": total_nodes / max(total_time, 1e-6)
    }
