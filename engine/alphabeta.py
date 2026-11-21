"""Alpha-Beta Pruning Adversarial Search Algorithm.
Optimized Minimax search maintaining alpha and beta bounds.
Prunes provably inferior branches without affecting the final minimax score.

White: Maximizer (raises alpha)
Black: Minimizer (lowers beta)
Cutoff condition: beta <= alpha
"""

import time
from typing import Dict, Any, Optional, List, Tuple
import chess
from .evaluation import evaluate_board, CHECKMATE_SCORE, STALEMATE_SCORE
from .move_ordering import order_moves
from .board_utils import get_move_san


class AlphaBetaSearcher:
    """Alpha-Beta Pruning searcher maintaining pruning metrics."""

    def __init__(self, use_move_ordering: bool = True):
        self.nodes_explored = 0
        self.pruned_branches = 0
        self.use_move_ordering = use_move_ordering
        self.start_time = 0.0

    def search(
        self,
        board: chess.Board,
        depth: int,
        weights: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """Execute Alpha-Beta search on the given chess position."""
        self.nodes_explored = 0
        self.pruned_branches = 0
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
                "pv_san": [],
                "nodes_per_second": 1.0 / max(elapsed, 1e-6)
            }

        if self.use_move_ordering:
            legal_moves = order_moves(board, legal_moves)

        is_maximizing = (board.turn == chess.WHITE)
        alpha = -float('inf')
        beta = float('inf')

        best_move = legal_moves[0]
        best_score = -float('inf') if is_maximizing else float('inf')
        best_pv: List[chess.Move] = [best_move]
        candidate_moves = []

        # Root level search
        for move in legal_moves:
            board.push(move)
            self.nodes_explored += 1

            if depth <= 1:
                score = evaluate_board(board, 1, weights)
                child_pv = []
            else:
                score, child_pv = self._alphabeta(
                    board, depth - 1, 1, alpha, beta, not is_maximizing, weights
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
                alpha = max(alpha, best_score)
            else:
                if score < best_score:
                    best_score = score
                    best_move = move
                    best_pv = [move] + child_pv
                beta = min(beta, best_score)

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
            "pruned_branches": self.pruned_branches,
            "execution_time": elapsed,
            "depth": depth,
            "candidate_moves": candidate_moves[:3],
            "all_candidates": candidate_moves,
            "principal_variation": best_pv,
            "pv_san": pv_san,
            "nodes_per_second": self.nodes_explored / max(elapsed, 1e-6)
        }

    def _alphabeta(
        self,
        board: chess.Board,
        depth: int,
        ply: int,
        alpha: float,
        beta: float,
        is_maximizing: bool,
        weights: Optional[Dict[str, float]]
    ) -> Tuple[int, List[chess.Move]]:
        """Recursive alpha-beta search."""
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
            for i, move in enumerate(legal_moves):
                board.push(move)
                self.nodes_explored += 1
                eval_score, child_pv = self._alphabeta(
                    board, depth - 1, ply + 1, alpha, beta, False, weights
                )
                board.pop()

                if eval_score > max_eval:
                    max_eval = eval_score
                    best_pv = [move] + child_pv

                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    # Branch pruned
                    self.pruned_branches += (len(legal_moves) - 1 - i)
                    break
            return int(max_eval), best_pv
        else:
            min_eval = float('inf')
            for i, move in enumerate(legal_moves):
                board.push(move)
                self.nodes_explored += 1
                eval_score, child_pv = self._alphabeta(
                    board, depth - 1, ply + 1, alpha, beta, True, weights
                )
                board.pop()

                if eval_score < min_eval:
                    min_eval = eval_score
                    best_pv = [move] + child_pv

                beta = min(beta, eval_score)
                if beta <= alpha:
                    # Branch pruned
                    self.pruned_branches += (len(legal_moves) - 1 - i)
                    break
            return int(min_eval), best_pv


def alphabeta_search(
    board: chess.Board,
    depth: int = 3,
    use_move_ordering: bool = True,
    weights: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    """Convenience functional interface for Alpha-Beta search."""
    searcher = AlphaBetaSearcher(use_move_ordering=use_move_ordering)
    return searcher.search(board, depth, weights)
