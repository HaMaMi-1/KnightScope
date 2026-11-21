"""Tests for search algorithms: Minimax, Alpha-Beta, Greedy, and Iterative Deepening."""

import pytest
import chess
from engine.minimax import minimax_search
from engine.alphabeta import alphabeta_search
from engine.greedy import greedy_search
from engine.iterative_deepening import iterative_deepening_search


def test_minimax_and_alphabeta_score_equivalence():
    """Verify that Alpha-Beta returns the EXACT same minimax score and optimal move

    under identical depth and move ordering settings.
    """
    board = chess.Board("r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/2NP1N2/PPP2PPP/R1BQK2R b KQkq - 0 5")
    depth = 2

    res_mm = minimax_search(board, depth=depth, use_move_ordering=True)
    res_ab = alphabeta_search(board, depth=depth, use_move_ordering=True)

    assert res_mm["score"] == res_ab["score"], (
        f"Scores diverge! Minimax: {res_mm['score']}, AlphaBeta: {res_ab['score']}"
    )
    assert res_mm["best_move"] == res_ab["best_move"], (
        f"Moves diverge! Minimax: {res_mm['best_move']}, AlphaBeta: {res_ab['best_move']}"
    )
    # Alpha-Beta should explore equal or fewer nodes
    assert res_ab["nodes_explored"] <= res_mm["nodes_explored"], (
        f"Alpha-Beta explored {res_ab['nodes_explored']} vs Minimax {res_mm['nodes_explored']}"
    )


def test_minimax_move_legality():
    board = chess.Board()
    res = minimax_search(board, depth=2)
    assert res["best_move"] in board.legal_moves
    assert res["nodes_explored"] > 0
    assert res["execution_time"] >= 0


def test_alphabeta_move_legality():
    board = chess.Board()
    res = alphabeta_search(board, depth=2)
    assert res["best_move"] in board.legal_moves
    assert res["nodes_explored"] > 0
    assert res["pruned_branches"] >= 0


def test_greedy_move_legality():
    board = chess.Board()
    res = greedy_search(board)
    assert res["best_move"] in board.legal_moves
    assert res["nodes_explored"] == board.legal_moves.count()


def test_iterative_deepening_progression():
    board = chess.Board("r1bqkb1r/pppp1ppp/2n5/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 2 4")
    res = iterative_deepening_search(board, max_depth=3, time_limit=5.0)
    assert res["completed_depth"] >= 1
    assert len(res["iterations"]) >= 1
    assert res["best_move"] in board.legal_moves

    # Check progression monotonicity in depth
    depths = [it["depth"] for it in res["iterations"]]
    assert depths == list(range(1, len(depths) + 1))


def test_tactical_mate_in_one():
    # Scholar's mate threat: Qxf7#
    board = chess.Board("r1bqkb1r/pppp1ppp/2n2n2/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR w KQkq - 4 4")
    res_ab = alphabeta_search(board, depth=2)
    expected_mate_move = chess.Move.from_uci("h5f7")
    assert res_ab["best_move"] == expected_mate_move
