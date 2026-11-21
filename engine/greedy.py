"""Greedy Best-First Search baseline algorithm.
Evaluates immediate resulting positions (1-ply lookahead) and picks the move
with the highest immediate heuristic score from the perspective of the side to move.

Limitations:
Does not perform adversarial lookahead.
Fails to foresee opponent counter-attacks, tactical traps, and sacrifices.
Serves as an empirical baseline to highlight the critical role of search depth in AI.
"""

import time
from typing import Dict, Any, Optional, List
import chess
from .evaluation import evaluate_board
from .board_utils import get_move_san


def greedy_search(
    board: chess.Board,
    depth: int = 1,  # Kept as parameter for API signature consistency; Greedy is strictly 1-ply
    weights: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    """Perform Greedy Best-First Search (single-ply candidate evaluation)."""
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
            "depth": 1,
            "candidate_moves": [],
            "principal_variation": [],
            "pv_san": [],
            "nodes_per_second": 1.0 / max(elapsed, 1e-6),
            "algorithm_type": "Greedy (1-ply heuristic)",
            "explanation": "No legal moves available."
        }

    is_white = (board.turn == chess.WHITE)
    candidate_moves: List[Dict[str, Any]] = []

    for move in legal_moves:
        board.push(move)
        score = evaluate_board(board, 1, weights)
        board.pop()

        san = get_move_san(board, move)
        candidate_moves.append({
            "move": move,
            "uci": move.uci(),
            "san": san,
            "score": score
        })

    # Sort candidates
    candidate_moves.sort(
        key=lambda x: x["score"],
        reverse=is_white
    )

    best_cand = candidate_moves[0]
    best_move = best_cand["move"]
    best_score = best_cand["score"]
    nodes_explored = len(legal_moves)
    elapsed = time.perf_counter() - start_time

    explanation = (
        f"Greedy selected {best_cand['san']} with immediate heuristic score {best_score}. "
        "Notice: Greedy evaluates only the immediate next state and does not model opponent replies."
    )

    return {
        "best_move": best_move,
        "best_move_san": best_cand["san"],
        "score": best_score,
        "nodes_explored": nodes_explored,
        "pruned_branches": 0,
        "execution_time": elapsed,
        "depth": 1,
        "candidate_moves": candidate_moves[:3],
        "all_candidates": candidate_moves,
        "principal_variation": [best_move],
        "pv_san": [best_cand["san"]],
        "nodes_per_second": nodes_explored / max(elapsed, 1e-6),
        "algorithm_type": "Greedy (1-ply heuristic)",
        "explanation": explanation
    }
