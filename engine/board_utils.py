"""Board utilities for chess representation, FEN parsing, and SVG rendering.
Leverages python-chess strictly for rule enforcement, move generation, and FEN parsing.
"""

from typing import Tuple, Optional, Dict, Any, List
import chess
import chess.svg


def create_board(fen: Optional[str] = None) -> chess.Board:
    """Create a chess.Board instance from FEN or standard starting position."""
    if fen and fen.strip():
        return chess.Board(fen.strip())
    return chess.Board()


def validate_fen(fen: str) -> Tuple[bool, Optional[str]]:
    """Validate a FEN string. Returns (is_valid, error_message)."""
    if not fen or not fen.strip():
        return False, "FEN string cannot be empty."
    try:
        board = chess.Board(fen.strip())
        if not board.is_valid():
            # Check reasons
            status = board.status()
            reasons = []
            if status & chess.STATUS_NO_WHITE_KING:
                reasons.append("Missing white king")
            if status & chess.STATUS_NO_BLACK_KING:
                reasons.append("Missing black king")
            if status & chess.STATUS_TOO_MANY_KINGS:
                reasons.append("Too many kings")
            if status & chess.STATUS_TOO_MANY_WHITE_PAWNS:
                reasons.append("Too many white pawns")
            if status & chess.STATUS_TOO_MANY_BLACK_PAWNS:
                reasons.append("Too many black pawns")
            if status & chess.STATUS_PAWNS_ON_FIRST_OR_LAST_RANK:
                reasons.append("Pawns present on first or eighth rank")
            if status & chess.STATUS_OPPOSITE_CHECK:
                reasons.append("Opponent king is in check (illegal state)")
            msg = f"Invalid board state: {', '.join(reasons) if reasons else 'Illegal position'}"
            return False, msg
        return True, None
    except ValueError as e:
        return False, f"Syntax error in FEN string: {str(e)}"
    except Exception as e:
        return False, f"Unexpected error parsing FEN: {str(e)}"


def get_game_status(board: chess.Board) -> Dict[str, Any]:
    """Inspect game status: check, checkmate, stalemate, draws, active player."""
    is_checkmate = board.is_checkmate()
    is_stalemate = board.is_stalemate()
    is_insufficient_material = board.is_insufficient_material()
    can_claim_50 = board.can_claim_fifty_moves()
    can_claim_rep = board.can_claim_threefold_repetition()
    is_check = board.is_check()

    is_game_over = board.is_game_over()
    result_desc = "Active game"
    winner = None

    if is_checkmate:
        winner = "Black" if board.turn == chess.WHITE else "White"
        result_desc = f"Checkmate! {winner} wins."
    elif is_stalemate:
        result_desc = "Draw by stalemate."
    elif is_insufficient_material:
        result_desc = "Draw by insufficient material."
    elif can_claim_50:
        result_desc = "Draw claimable by 50-move rule."
    elif can_claim_rep:
        result_desc = "Draw claimable by threefold repetition."
    elif is_check:
        result_desc = f"Check! {'White' if board.turn == chess.WHITE else 'Black'} is under attack."

    return {
        "is_game_over": is_game_over,
        "is_checkmate": is_checkmate,
        "is_stalemate": is_stalemate,
        "is_draw": is_stalemate or is_insufficient_material or can_claim_50 or can_claim_rep,
        "is_check": is_check,
        "turn": "White" if board.turn == chess.WHITE else "Black",
        "turn_color": board.turn,
        "winner": winner,
        "description": result_desc,
        "legal_moves_count": board.legal_moves.count()
    }


def render_board_svg(
    board: chess.Board,
    last_move: Optional[chess.Move] = None,
    check_square: Optional[chess.Square] = None,
    size: int = 440,
    flipped: bool = False
) -> str:
    """Render board to clean SVG format with optional move highlighting."""
    check = None
    if check_square is not None:
        check = check_square
    elif board.is_check():
        check = board.king(board.turn)

    svg_data = chess.svg.board(
        board=board,
        lastmove=last_move,
        check=check,
        size=size,
        orientation=chess.BLACK if flipped else chess.WHITE,
        coordinates=True
    )
    return svg_data


def get_move_san(board: chess.Board, move: chess.Move) -> str:
    """Safely convert move to Standard Algebraic Notation (SAN)."""
    try:
        return board.san(move)
    except Exception:
        return move.uci()


def parse_move(board: chess.Board, move_str: str) -> Optional[chess.Move]:
    """Parse move from UCI or SAN string."""
    move_str = move_str.strip()
    try:
        # Try UCI first
        move = chess.Move.from_uci(move_str)
        if move in board.legal_moves:
            return move
    except Exception:
        pass

    try:
        # Try SAN
        move = board.parse_san(move_str)
        if move in board.legal_moves:
            return move
    except Exception:
        pass

    return None
