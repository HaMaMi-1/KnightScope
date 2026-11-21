"""Tests for chess move generation, FEN import, and board utilities."""

import pytest
import chess
from engine.board_utils import (
    create_board,
    validate_fen,
    get_game_status,
    parse_move,
    get_move_san
)


def test_standard_position_setup():
    board = create_board()
    assert board.turn == chess.WHITE
    assert board.legal_moves.count() == 20
    assert not board.is_check()
    assert not board.is_game_over()


def test_fen_import_and_validation():
    valid_fen = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"
    is_valid, err = validate_fen(valid_fen)
    assert is_valid
    assert err is None

    board = create_board(valid_fen)
    assert board.turn == chess.BLACK

    invalid_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1 99"
    is_valid, err = validate_fen(invalid_fen)
    assert not is_valid
    assert err is not None


def test_illegal_move_rejection():
    board = create_board()
    # e2e5 is illegal for white from starting position
    illegal_move = parse_move(board, "e2e5")
    assert illegal_move is None

    legal_move = parse_move(board, "e2e4")
    assert legal_move is not None
    assert legal_move in board.legal_moves


def test_checkmate_status():
    # Scholar's mate position
    # 1. e4 e5 2. Qh5 Nc6 3. Bc4 Nf6 4. Qxf7#
    board = chess.Board("r1bqkb1r/pppp1Qpp/2n2n2/4p3/2B1P3/8/PPPP1PPP/RNB1K1NR b KQkq - 0 4")
    status = get_game_status(board)
    assert status["is_checkmate"]
    assert status["is_game_over"]
    assert status["winner"] == "White"


def test_stalemate_status():
    # Stalemate position: White king on c8, queen on c7, Black king on a8
    board = chess.Board("k7/2Q5/1K6/8/8/8/8/8 b - - 0 1")
    status = get_game_status(board)
    assert status["is_stalemate"]
    assert status["is_draw"]
    assert status["is_game_over"]
    assert not status["is_check"]


def test_pawn_promotion_handling():
    # White pawn on a7 ready to promote
    board = chess.Board("8/P7/8/8/8/8/8/4K2k w - - 0 1")
    move_q = parse_move(board, "a7a8q")
    assert move_q is not None
    assert move_q in board.legal_moves

    board.push(move_q)
    assert board.piece_at(chess.A8).piece_type == chess.QUEEN
