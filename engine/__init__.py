"""KnightScope Chess Engine Package.
Classical AI search algorithms and evaluation functions for chess position analysis.
"""

from .evaluation import evaluate_board, evaluate_detailed, PIECE_VALUES
from .board_utils import (
    create_board,
    validate_fen,
    get_game_status,
    render_board_svg,
    get_move_san,
    parse_move
)
from .minimax import minimax_search
from .alphabeta import alphabeta_search
from .greedy import greedy_search
from .iterative_deepening import iterative_deepening_search

__all__ = [
    "evaluate_board",
    "evaluate_detailed",
    "PIECE_VALUES",
    "create_board",
    "validate_fen",
    "get_game_status",
    "render_board_svg",
    "get_move_san",
    "parse_move",
    "minimax_search",
    "alphabeta_search",
    "greedy_search",
    "iterative_deepening_search",
]
