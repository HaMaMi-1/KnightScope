"""Adversarial Minimax Search Algorithm.
Full depth-limited minimax search without pruning.
Explores all possible future positions up to depth d.

Max player: White (maximizing evaluation score)
Min player: Black (minimizing evaluation score)
"""

import time
from typing import Dict, Any, Optional, List, Tuple
import chess
from .evaluation import evaluate_board, CHECKMATE_SCORE, STALEMATE_SCORE
from .move_ordering import order_moves
from .board_utils import get_move_san


class MinimaxSearcher:
    """Minimax searcher maintaining statistics and search tree information."""

    def __init__(self, use_move_ordering: bool = True):
        self.nodes_explored = 0
        self.use_move_ordering = use_move_ordering
        self.start_time = 0.0

    def search(
        self,
        board: chess.Board,
        depth: int,
        weights: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """Perform Minimax search from the current board state."""
        self.nodes_explored = 0
        self.start_time = time.perf_counter()

        legal_moves = list(board.legal_moves)
        if not legal_moves:
            elapsed = time.perf_counter() - self.start_time
            eval_score = evaluate_board(board, 0, weights)
            return {
                "best_move": None,
                "best_move_san": None,
                "score": eval_score,
                "nodes_explored": 1,
                "pruned_branches": 0,
                "execution_time": elapsed,
                "depth": depth,
                "candidate_moves": [],
                "principal_variation": [],
                "pv_san": []
            }

        if self.use_move_ordering:
            legal_moves = order_moves(board, legal_moves)

        is_maximizing = (board.turn == chess.WHITE)
        best_move = legal_moves[0]
        best_score = -float('inf') if is_maximizing else float('inf')
        candidate_moves = []

        # Root level search
        for move in legal_moves:
            board.push(move)
            self.nodes_explored += 1

            if depth <= 1:
                # Leaf evaluation
                score = evaluate_board(board, 1, weights)
                child_pv = []
            else:
                score, child_pv = self._minimax(
                    board, depth - 1, 1, not is_maximizing, weights
                )

            board.pop()

            san = get_move_san(board, move)
            candidate_moves.append({
                "move": move,
                "uci": move.uci(),
                "san": san,
                "score": score
            })

            if is_maximizing:
                if score > best_score:
                    best_score = score
                    best_move = move
                    best_pv = [move] + child_pv
            else:
                if score < best_score:
                    best_score = score
                    best_move = move
                    best_pv = [move] + child_pv

        # Sort candidate moves
        candidate_moves.sort(
            key=lambda x: x["score"],
            reverse=is_maximizing
        )

        elapsed = time.perf_counter() - self.start_time

        # Convert best PV to SAN
        temp_board = board.copy()
        pv_san = []
        for m in best_pv:
            if m in temp_board.legal_moves:
                pv_san.append(temp_board.san(m))
                temp_board.push(m)
            else:
                pv_san.append(m.uci())

        return {
            "best_move": best_move,
            "best_move_san": get_move_san(board, best_move),
            "score": best_score,
            "nodes_explored": self.nodes_explored,
            "pruned_branches": 0,
            "execution_time": elapsed,
            "depth": depth,
            "candidate_moves": candidate_moves[:3],
            "all_candidates": candidate_moves,
            "principal_variation": best_pv,
            "pv_san": pv_san,
            "nodes_per_second": self.nodes_explored / max(elapsed, 1e-6)
        }

    def _minimax(
        self,
        board: chess.Board,
        depth: int,
        ply: int,
        is_maximizing: bool,
        weights: Optional[Dict[str, float]]
    ) -> Tuple[int, List[chess.Move]]:
        """Recursive minimax implementation."""
        # Terminal checks
        if board.is_checkmate():
            return (-CHECKMATE_SCORE + ply if board.turn == chess.WHITE else CHECKMATE_SCORE - ply), []
        if board.is_stalemate() or board.is_insufficient_material() or board.can_claim_fifty_moves() or board.can_claim_threefold_repetition():
            return STALEMATE_SCORE, []

        if depth <= 0:
            return evaluate_board(board, ply, weights), []

        legal_moves = list(board.legal_moves)
        if not legal_moves:
            return evaluate_board(board, ply, weights), []

        if self.use_move_ordering:
            legal_moves = order_moves(board, legal_moves)

        best_pv: List[chess.Move] = []

        if is_maximizing:
            max_eval = -float('inf')
            for move in legal_moves:
                board.push(move)
                self.nodes_explored += 1
                eval_score, child_pv = self._minimax(
                    board, depth - 1, ply + 1, False, weights
                )
                board.pop()

                if eval_score > max_eval:
                    max_eval = eval_score
                    best_pv = [move] + child_pv
            return int(max_eval), best_pv
        else:
            min_eval = float('inf')
            for move in legal_moves:
                board.push(move)
                self.nodes_explored += 1
                eval_score, child_pv = self._minimax(
                    board, depth - 1, ply + 1, True, weights
                )
                board.pop()

                if eval_score < min_eval:
                    min_eval = eval_score
                    best_pv = [move] + child_pv
            return int(min_eval), best_pv


def minimax_search(
    board: chess.Board,
    depth: int = 3,
    use_move_ordering: bool = True,
    weights: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    """Convenience functional interface for Minimax search."""
    searcher = MinimaxSearcher(use_move_ordering=use_move_ordering)
    return searcher.search(board, depth, weights)
