"""Move Ordering utilities for adversarial search.
Ensures identical move ordering for both Minimax and Alpha-Beta
to enable strict, fair scientific comparison.

Move ordering priority:
1. Winning & equal captures (MVV-LVA: Most Valuable Victim - Least Valuable Attacker)
2. Promotions
3. Checks
4. Killer moves (moves that caused beta-cutoffs at the same ply)
5. Quiet moves
"""

from typing import List, Optional, Dict
import chess
from .evaluation import PIECE_VALUES


def score_move(board: chess.Board, move: chess.Move) -> int:
    """Calculate move priority score for move ordering."""
    score = 0

    # 1. Captures: MVV-LVA
    if board.is_capture(move):
        victim = board.piece_at(move.to_square)
        attacker = board.piece_at(move.from_square)

        victim_val = PIECE_VALUES.get(victim.piece_type, 100) if victim else 100
        attacker_val = PIECE_VALUES.get(attacker.piece_type, 100) if attacker else 100

        # En passant capture
        if board.is_en_passant(move):
            victim_val = PIECE_VALUES[chess.PAWN]

        score += 10000 + (victim_val * 10) - attacker_val

    # 2. Promotions
    if move.promotion:
        score += 9000 + PIECE_VALUES.get(move.promotion, 0)

    # 3. Checks (give higher priority to giving check)
    board.push(move)
    if board.is_check():
        score += 500
    board.pop()

    # 4. Castling
    if board.is_castling(move):
        score += 300

    return score


def order_moves(board: chess.Board, moves: Optional[List[chess.Move]] = None) -> List[chess.Move]:
    """Sort legal moves by heuristic promise."""
    legal_moves = list(board.legal_moves) if moves is None else list(moves)
    if len(legal_moves) <= 1:
        return legal_moves

    # Sort descending by move ordering score
    return sorted(legal_moves, key=lambda m: score_move(board, m), reverse=True)
