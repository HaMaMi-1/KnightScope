"""Tests for benchmark test positions across tactical, strategic, and endgame scenarios."""

import json
import os
import pytest
import chess
from engine.board_utils import validate_fen, create_board
from engine.alphabeta import alphabeta_search


def test_benchmark_positions_load():
    json_path = os.path.join(os.path.dirname(__file__), "..", "data", "test_positions.json")
    assert os.path.exists(json_path), f"test_positions.json not found at {json_path}"

    with open(json_path, "r", encoding="utf-8") as f:
        positions = json.load(f)

    assert len(positions) >= 8, f"Expected at least 8 benchmark positions, found {len(positions)}"

    for pos in positions:
        assert "id" in pos
        assert "name" in pos
        assert "fen" in pos
        assert "category" in pos
        is_valid, err = validate_fen(pos["fen"])
        assert is_valid, f"Position {pos['id']} ({pos['name']}) has invalid FEN: {err}"


def test_positions_can_be_searched():
    json_path = os.path.join(os.path.dirname(__file__), "..", "data", "test_positions.json")
    with open(json_path, "r", encoding="utf-8") as f:
        positions = json.load(f)

    # Test that each position can be searched to depth 1 without crashing
    for pos in positions[:3]:
        board = create_board(pos["fen"])
        res = alphabeta_search(board, depth=1)
        assert res["best_move"] in board.legal_moves
