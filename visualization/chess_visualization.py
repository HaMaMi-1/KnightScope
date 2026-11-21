"""Chess board visualization and search-tree generation for KnightScope.
Generates board representations with move arrows and illustrative search tree slices
demonstrating alpha-beta cutoffs.
"""

from typing import Optional, List, Dict, Any, Tuple
import chess
import chess.svg
import plotly.graph_objects as go
from engine.board_utils import get_move_san
from engine.evaluation import evaluate_board


def get_board_svg_with_arrows(
    board: chess.Board,
    last_move: Optional[chess.Move] = None,
    recommended_move: Optional[chess.Move] = None,
    candidate_moves: Optional[List[chess.Move]] = None,
    size: int = 460,
    flipped: bool = False
) -> str:
    """Render board SVG with highlighted arrows for recommended and candidate moves."""
    arrows = []

    # Secondary candidate moves in translucent cyan/blue
    if candidate_moves:
        for i, move in enumerate(candidate_moves):
            if move and move != recommended_move:
                arrows.append(
                    chess.svg.Arrow(
                        move.from_square,
                        move.to_square,
                        color="#38bdf888"  # light blue
                    )
                )

    # Primary recommended move in bold green
    if recommended_move:
        arrows.append(
            chess.svg.Arrow(
                recommended_move.from_square,
                recommended_move.to_square,
                color="#22c55e"  # emerald green
            )
        )

    check_sq = board.king(board.turn) if board.is_check() else None

    return chess.svg.board(
        board=board,
        lastmove=last_move,
        check=check_sq,
        arrows=arrows,
        size=size,
        orientation=chess.BLACK if flipped else chess.WHITE,
        coordinates=True
    )


def generate_search_tree_figure(
    board: chess.Board,
    depth: int = 2,
    max_branching: int = 4
) -> go.Figure:
    """Generate an illustrative Plotly search-tree diagram showing MAX and MIN levels,

    evaluated scores, and alpha-beta pruning concepts on top candidates.
    Avoids enormous trees by sampling the top candidate moves.
    """
    nodes = []
    edges = []

    is_white = (board.turn == chess.WHITE)
    root_id = "Root"
    nodes.append({
        "id": root_id,
        "label": f"Root ({'MAX' if is_white else 'MIN'})",
        "level": 0,
        "x": 0.5,
        "y": 1.0,
        "score": None,
        "type": "root",
        "hover": "Root position"
    })

    legal_moves = list(board.legal_moves)[:max_branching]
    num_moves = max(1, len(legal_moves))

    for i, m1 in enumerate(legal_moves):
        x1 = (i + 0.5) / num_moves
        y1 = 0.5
        m1_san = get_move_san(board, m1)
        node_1_id = f"m1_{i}"

        board.push(m1)
        score_1 = evaluate_board(board, 1)

        nodes.append({
            "id": node_1_id,
            "label": f"{m1_san}\n({score_1:+d})",
            "level": 1,
            "x": x1,
            "y": y1,
            "score": score_1,
            "type": "depth1",
            "hover": f"Move: {m1_san}<br>Eval: {score_1:+d} cp"
        })
        edges.append((root_id, node_1_id, m1_san, False))

        if depth >= 2:
            sub_moves = list(board.legal_moves)[:2]
            sub_count = max(1, len(sub_moves))
            for j, m2 in enumerate(sub_moves):
                x2 = x1 + (j - (sub_count - 1) / 2.0) * (0.8 / (num_moves * 2))
                y2 = 0.0
                m2_san = get_move_san(board, m2)
                node_2_id = f"m2_{i}_{j}"

                board.push(m2)
                score_2 = evaluate_board(board, 2)
                board.pop()

                is_pruned = (j > 0 and i > 0 and j >= 1)  # Illustrate hypothetical cutoff

                nodes.append({
                    "id": node_2_id,
                    "label": f"{m2_san}\n({score_2:+d})" if not is_pruned else f"{m2_san}\n[CUT]",
                    "level": 2,
                    "x": x2,
                    "y": y2,
                    "score": score_2,
                    "type": "pruned" if is_pruned else "leaf",
                    "hover": f"Reply: {m2_san}<br>Score: {score_2:+d}" if not is_pruned else f"Cutoff: {m2_san} (Pruned)"
                })
                edges.append((node_1_id, node_2_id, m2_san, is_pruned))

        board.pop()

    # Create Plotly figure
    edge_x = []
    edge_y = []
    pruned_edge_x = []
    pruned_edge_y = []

    for parent_id, child_id, _, is_pruned in edges:
        p = next(n for n in nodes if n["id"] == parent_id)
        c = next(n for n in nodes if n["id"] == child_id)
        if is_pruned:
            pruned_edge_x.extend([p["x"], c["x"], None])
            pruned_edge_y.extend([p["y"], c["y"], None])
        else:
            edge_x.extend([p["x"], c["x"], None])
            edge_y.extend([p["y"], c["y"], None])

    fig = go.Figure()

    # Normal edges
    fig.add_trace(go.Scatter(
        x=edge_x, y=edge_y,
        mode="lines",
        line=dict(color="#94a3b8", width=2),
        hoverinfo="none",
        showlegend=False
    ))

    # Pruned edges (red dashed)
    if pruned_edge_x:
        fig.add_trace(go.Scatter(
            x=pruned_edge_x, y=pruned_edge_y,
            mode="lines",
            line=dict(color="#ef4444", width=2, dash="dot"),
            hoverinfo="none",
            name="Alpha-Beta Cutoff"
        ))

    # Nodes
    node_x = [n["x"] for n in nodes]
    node_y = [n["y"] for n in nodes]
    node_text = [n["label"] for n in nodes]
    node_hover = [n["hover"] for n in nodes]
    node_colors = [
        "#f59e0b" if n["type"] == "root" else
        "#3b82f6" if n["type"] == "depth1" else
        "#ef4444" if n["type"] == "pruned" else "#10b981"
        for n in nodes
    ]

    fig.add_trace(go.Scatter(
        x=node_x, y=node_y,
        mode="markers+text",
        marker=dict(
            size=36,
            color=node_colors,
            line=dict(color="#1e293b", width=2)
        ),
        text=node_text,
        textposition="bottom center",
        textfont=dict(size=10, color="#f8fafc"),
        hoverinfo="text",
        hovertext=node_hover,
        showlegend=False
    ))

    fig.update_layout(
        title="Illustrative Minimax Search Tree with Alpha-Beta Pruning Cutoffs",
        showlegend=True,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor="#0f172a",
        paper_bgcolor="#0f172a",
        font=dict(color="#f8fafc"),
        height=380,
        margin=dict(l=20, r=20, t=40, b=30)
    )
    return fig
