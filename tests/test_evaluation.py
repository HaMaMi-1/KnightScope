"""Tests for position evaluation function."""

import pytest
import chess
from engine.evaluation import (
    evaluate_board,
    evaluate_detailed,
    PIECE_VALUES,
    CHECKMATE_SCORE,
    STALEMATE_SCORE
)


def test_starting_position_symmetry():
    board = chess.Board()
    eval_res = evaluate_detailed(board)
    # Starting position should be roughly balanced (close to 0, slight white tempo/pst variation)
    assert -50 <= eval_res["total_score"] <= 50
    assert eval_res["material"] == 0


def test_material_advantage_scoring():
    # White is up a Queen
    board = chess.Board("rnb1kbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    score = evaluate_board(board)
    # Up a Queen (900 cp) -> score should be heavily positive
    assert score > 700


def test_checkmate_evaluation():
    # Black is checkmated
    mate_board = chess.Board("r1bqkb1r/pppp1Qpp/2n2n2/4p3/2B1P3/8/PPPP1PPP/RNB1K1NR b KQkq - 0 4")
    # Black to move and mated -> White wins -> +CHECKMATE_SCORE - ply
    score_black_turn = evaluate_board(mate_board, ply_from_root=0)
    assert score_black_turn >= (CHECKMATE_SCORE - 10)

    # White is checkmated (Fool's Mate: 1. f3 e5 2. g4 Qh4#)
    fools_mate = chess.Board("rnb1kbnr/pppp1ppp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq - 1 3")
    score_white_turn = evaluate_board(fools_mate, ply_from_root=0)
    assert score_white_turn <= (-CHECKMATE_SCORE + 10)


def test_stalemate_evaluation():
    board = chess.Board("k7/2Q5/1K6/8/8/8/8/8 b - - 0 1")
    score = evaluate_board(board)
    assert score == STALEMATE_SCORE


def test_evaluation_consistency():
    board = chess.Board()
    score1 = evaluate_board(board)
    score2 = evaluate_board(board)
    assert score1 == score2
