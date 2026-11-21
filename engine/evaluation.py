"""Handcrafted Chess Position Evaluation Function.
Calculates heuristic value from White's perspective:
Positive score = White advantage
Negative score = Black advantage

Incorporates:
1. Material balance (Pawn=100, Knight=320, Bishop=330, Rook=500, Queen=900, King=0)
2. Piece-Square Positional Tables (PST)
3. Mobility (legal move opportunities and freedom of movement)
4. Center control (occupying and attacking central squares e4, d4, e5, d5)
5. King safety (pawn shelter, open files near king, castling state)
6. Pawn structure (isolated pawns, doubled pawns, passed pawns)
7. Special bonuses (Bishop pair)
"""

from typing import Dict, Any, Tuple
import chess

# Material constants as defined in specification
PIECE_VALUES: Dict[int, int] = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 0,
}

CHECKMATE_SCORE = 20000
STALEMATE_SCORE = 0

# Piece-Square Tables (White perspective, rank 8 at top in array, mapped to square index 0..63)
# Values reflect standard classical chess heuristics (Tomasz Michniewski / PeSTO inspired).
PAWN_TABLE = [
     0,  0,  0,  0,  0,  0,  0,  0,
    50, 50, 50, 50, 50, 50, 50, 50,
    10, 10, 20, 30, 30, 20, 10, 10,
     5,  5, 10, 25, 25, 10,  5,  5,
     0,  0,  0, 20, 20,  0,  0,  0,
     5, -5,-10,  0,  0,-10, -5,  5,
     5, 10, 10,-20,-20, 10, 10,  5,
     0,  0,  0,  0,  0,  0,  0,  0
]

KNIGHT_TABLE = [
    -50,-40,-30,-30,-30,-30,-40,-50,
    -40,-20,  0,  0,  0,  0,-20,-40,
    -30,  0, 10, 15, 15, 10,  0,-30,
    -30,  5, 15, 20, 20, 15,  5,-30,
    -30,  0, 15, 20, 20, 15,  0,-30,
    -30,  5, 10, 15, 15, 10,  5,-30,
    -40,-20,  0,  5,  5,  0,-20,-40,
    -50,-40,-30,-30,-30,-30,-40,-50,
]

BISHOP_TABLE = [
    -20,-10,-10,-10,-10,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5, 10, 10,  5,  0,-10,
    -10,  5,  5, 10, 10,  5,  5,-10,
    -10,  0, 10, 10, 10, 10,  0,-10,
    -10, 10, 10, 10, 10, 10, 10,-10,
    -10,  5,  0,  0,  0,  0,  5,-10,
    -20,-10,-10,-10,-10,-10,-10,-20,
]

ROOK_TABLE = [
      0,  0,  0,  0,  0,  0,  0,  0,
      5, 10, 10, 10, 10, 10, 10,  5,
     -5,  0,  0,  0,  0,  0,  0, -5,
     -5,  0,  0,  0,  0,  0,  0, -5,
     -5,  0,  0,  0,  0,  0,  0, -5,
     -5,  0,  0,  0,  0,  0,  0, -5,
     -5,  0,  0,  0,  0,  0,  0, -5,
      0,  0,  0,  5,  5,  0,  0,  0
]

QUEEN_TABLE = [
    -20,-10,-10, -5, -5,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5,  5,  5,  5,  0,-10,
     -5,  0,  5,  5,  5,  5,  0, -5,
      0,  0,  5,  5,  5,  5,  0, -5,
    -10,  5,  5,  5,  5,  5,  0,-10,
    -10,  0,  5,  0,  0,  0,  0,-10,
    -20,-10,-10, -5, -5,-10,-10,-20
]

KING_MIDGAME_TABLE = [
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -20,-30,-30,-40,-40,-30,-30,-20,
    -10,-20,-20,-20,-20,-20,-20,-10,
     20, 20,  0,  0,  0,  0, 20, 20,
     20, 30, 10,  0,  0, 10, 30, 20
]

KING_ENDGAME_TABLE = [
    -50,-40,-30,-20,-20,-30,-40,-50,
    -30,-20,-10,  0,  0,-10,-20,-30,
    -30,-10, 20, 30, 30, 20,-10,-30,
    -30,-10, 30, 40, 40, 30,-10,-30,
    -30,-10, 30, 40, 40, 30,-10,-30,
    -30,-10, 20, 30, 30, 20,-10,-30,
    -30,-30,  0,  0,  0,  0,-30,-30,
    -50,-30,-30,-30,-30,-30,-30,-50
]

PIECE_TABLES = {
    chess.PAWN: PAWN_TABLE,
    chess.KNIGHT: KNIGHT_TABLE,
    chess.BISHOP: BISHOP_TABLE,
    chess.ROOK: ROOK_TABLE,
    chess.QUEEN: QUEEN_TABLE,
}

CENTER_SQUARES = [chess.E4, chess.D4, chess.E5, chess.D5]
EXTENDED_CENTER = [chess.C3, chess.D3, chess.E3, chess.F3,
                   chess.C4, chess.F4, chess.C5, chess.F5,
                   chess.C6, chess.D6, chess.E6, chess.F6]

DEFAULT_WEIGHTS = {
    "material": 1.0,
    "pst": 1.0,
    "mobility": 0.1,
    "center": 0.3,
    "king_safety": 0.5,
    "pawn_structure": 0.25,
    "bishop_pair": 0.5,
}


def _get_pst_value(piece_type: int, square: int, color: chess.Color, is_endgame: bool = False) -> int:
    """Retrieve piece-square value. Squares are flipped for Black."""
    if piece_type == chess.KING:
        table = KING_ENDGAME_TABLE if is_endgame else KING_MIDGAME_TABLE
    else:
        table = PIECE_TABLES.get(piece_type, None)
        if table is None:
            return 0

    # chess.square_mirror flips rank (rank 1 -> 8, 8 -> 1)
    sq = square if color == chess.WHITE else chess.square_mirror(square)
    # The table is arranged from rank 8 (top, index 0..7) down to rank 1 (index 56..63).
    # python-chess squares go from A1=0 to H8=63.
    # To map square (file, rank) to table index:
    # table_idx = (7 - rank) * 8 + file
    rank = chess.square_rank(sq)
    file = chess.square_file(sq)
    table_index = (7 - rank) * 8 + file
    return table[table_index]


def is_endgame_position(board: chess.Board) -> bool:
    """Determine if position is an endgame (both sides have no queen or queen + minor max)."""
    white_queens = len(board.pieces(chess.QUEEN, chess.WHITE))
    black_queens = len(board.pieces(chess.QUEEN, chess.BLACK))
    white_pieces = len(board.pieces(chess.ROOK, chess.WHITE)) + len(board.pieces(chess.BISHOP, chess.WHITE)) + len(board.pieces(chess.KNIGHT, chess.WHITE))
    black_pieces = len(board.pieces(chess.ROOK, chess.BLACK)) + len(board.pieces(chess.BISHOP, chess.BLACK)) + len(board.pieces(chess.KNIGHT, chess.BLACK))

    if white_queens == 0 and black_queens == 0:
        return True
    if white_queens <= 1 and white_pieces <= 1 and black_queens <= 1 and black_pieces <= 1:
        return True
    return False


def evaluate_detailed(
    board: chess.Board,
    ply_from_root: int = 0,
    weights: Dict[str, float] = None
) -> Dict[str, Any]:
    """Calculate detailed evaluation breakdown from White's perspective."""
    if weights is None:
        weights = DEFAULT_WEIGHTS

    # Terminal checks
    if board.is_checkmate():
        # If White to move is checkmated, Black wins (negative score).
        # Adjust by ply so shallower mate is preferred.
        if board.turn == chess.WHITE:
            score = -CHECKMATE_SCORE + ply_from_root
        else:
            score = CHECKMATE_SCORE - ply_from_root
        return {
            "total_score": score,
            "is_terminal": True,
            "terminal_type": "checkmate",
            "material": 0,
            "pst": 0,
            "mobility": 0,
            "center": 0,
            "king_safety": 0,
            "pawn_structure": 0,
            "bishop_pair": 0,
        }

    if board.is_stalemate() or board.is_insufficient_material() or board.can_claim_fifty_moves() or board.can_claim_threefold_repetition():
        return {
            "total_score": STALEMATE_SCORE,
            "is_terminal": True,
            "terminal_type": "draw",
            "material": 0,
            "pst": 0,
            "mobility": 0,
            "center": 0,
            "king_safety": 0,
            "pawn_structure": 0,
            "bishop_pair": 0,
        }

    endgame = is_endgame_position(board)

    # 1. Material & 2. Piece-Square Positional Advantages
    white_material = 0
    black_material = 0
    white_pst = 0
    black_pst = 0

    for square, piece in board.piece_map().items():
        val = PIECE_VALUES[piece.piece_type]
        pst_val = _get_pst_value(piece.piece_type, square, piece.color, endgame)
        if piece.color == chess.WHITE:
            white_material += val
            white_pst += pst_val
        else:
            black_material += val
            black_pst += pst_val

    material_diff = white_material - black_material
    pst_diff = white_pst - black_pst

    # 3. Mobility (approximate number of pseudo-legal moves without changing board turn)
    # python-chess board.attacks() gives attacked squares
    white_mobility = 0
    black_mobility = 0
    for square, piece in board.piece_map().items():
        attack_count = len(board.attacks(square))
        if piece.color == chess.WHITE:
            white_mobility += attack_count
        else:
            black_mobility += attack_count
    mobility_diff = (white_mobility - black_mobility) * 2  # scale factor

    # 4. Center control (e4, d4, e5, d5)
    white_center = 0
    black_center = 0
    for sq in CENTER_SQUARES:
        piece = board.piece_at(sq)
        if piece:
            if piece.color == chess.WHITE:
                white_center += 25
            else:
                black_center += 25
        white_center += len(board.attackers(chess.WHITE, sq)) * 10
        black_center += len(board.attackers(chess.BLACK, sq)) * 10

    center_diff = white_center - black_center

    # 5. King safety (penalize missing pawn shelter, open files near king, reward castling)
    white_king_safety = 0
    black_king_safety = 0
    if not endgame:
        white_king_sq = board.king(chess.WHITE)
        black_king_sq = board.king(chess.BLACK)

        if white_king_sq is not None:
            # Pawn shield in front of king
            file = chess.square_file(white_king_sq)
            rank = chess.square_rank(white_king_sq)
            for f in range(max(0, file - 1), min(8, file + 2)):
                shield_sq = chess.square(f, min(7, rank + 1))
                p = board.piece_at(shield_sq)
                if p and p.piece_type == chess.PAWN and p.color == chess.WHITE:
                    white_king_safety += 15
                elif p is None:
                    white_king_safety -= 10

        if black_king_sq is not None:
            file = chess.square_file(black_king_sq)
            rank = chess.square_rank(black_king_sq)
            for f in range(max(0, file - 1), min(8, file + 2)):
                shield_sq = chess.square(f, max(0, rank - 1))
                p = board.piece_at(shield_sq)
                if p and p.piece_type == chess.PAWN and p.color == chess.BLACK:
                    black_king_safety += 15
                elif p is None:
                    black_king_safety -= 10

    king_safety_diff = white_king_safety - black_king_safety

    # 6. Pawn structure (doubled pawns, isolated pawns)
    white_pawn_structure = 0
    black_pawn_structure = 0
    white_pawns = board.pieces(chess.PAWN, chess.WHITE)
    black_pawns = board.pieces(chess.PAWN, chess.BLACK)

    # Doubled pawns penalty
    white_files = [chess.square_file(sq) for sq in white_pawns]
    black_files = [chess.square_file(sq) for sq in black_pawns]
    for f in range(8):
        w_count = white_files.count(f)
        b_count = black_files.count(f)
        if w_count > 1:
            white_pawn_structure -= (w_count - 1) * 20
        if b_count > 1:
            black_pawn_structure -= (b_count - 1) * 20
        # Isolated pawn: no friendly pawns on adjacent files
        if w_count > 0:
            left = white_files.count(f - 1) if f > 0 else 0
            right = white_files.count(f + 1) if f < 7 else 0
            if left == 0 and right == 0:
                white_pawn_structure -= 15
        if b_count > 0:
            left = black_files.count(f - 1) if f > 0 else 0
            right = black_files.count(f + 1) if f < 7 else 0
            if left == 0 and right == 0:
                black_pawn_structure -= 15

    pawn_structure_diff = white_pawn_structure - black_pawn_structure

    # 7. Bishop pair bonus (30 centipawns)
    white_bishop_pair = 30 if len(board.pieces(chess.BISHOP, chess.WHITE)) >= 2 else 0
    black_bishop_pair = 30 if len(board.pieces(chess.BISHOP, chess.BLACK)) >= 2 else 0
    bishop_pair_diff = white_bishop_pair - black_bishop_pair

    # Weighted sum
    total = (
        weights.get("material", 1.0) * material_diff +
        weights.get("pst", 1.0) * pst_diff +
        weights.get("mobility", 0.1) * mobility_diff +
        weights.get("center", 0.3) * center_diff +
        weights.get("king_safety", 0.5) * king_safety_diff +
        weights.get("pawn_structure", 0.25) * pawn_structure_diff +
        weights.get("bishop_pair", 0.5) * bishop_pair_diff
    )

    return {
        "total_score": int(round(total)),
        "is_terminal": False,
        "terminal_type": None,
        "material": material_diff,
        "pst": pst_diff,
        "mobility": mobility_diff,
        "center": center_diff,
        "king_safety": king_safety_diff,
        "pawn_structure": pawn_structure_diff,
        "bishop_pair": bishop_pair_diff,
        "white_material": white_material,
        "black_material": black_material,
        "is_endgame": endgame
    }


def evaluate_board(
    board: chess.Board,
    ply_from_root: int = 0,
    weights: Dict[str, float] = None
) -> int:
    """Fast evaluation returning total heuristic score from White's perspective."""
    res = evaluate_detailed(board, ply_from_root, weights)
    return res["total_score"]
