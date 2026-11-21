"""Plotly interactive charts for KnightScope AI performance analysis.
Visualizes:
1. Execution time across algorithms
2. Nodes explored (log scale)
3. Alpha-Beta pruning efficiency
4. Iterative Deepening progression
5. Evaluation score comparison
6. Heuristic component breakdown
"""

from typing import List, Dict, Any, Optional
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px


def create_execution_time_chart(df: pd.DataFrame) -> go.Figure:
    """Compare execution time across algorithms."""
    fig = px.bar(
        df,
        x="algorithm",
        y="execution_time_sec",
        color="algorithm",
        barmode="group",
        title="Algorithm Execution Time Comparison (Seconds)",
        labels={"execution_time_sec": "Time (seconds)", "algorithm": "Algorithm"},
        color_discrete_map={
            "Minimax": "#ef4444",
            "AlphaBeta": "#10b981",
            "Greedy": "#3b82f6",
            "IterativeDeepening": "#8b5cf6"
        }
    )
    fig.update_layout(
        plot_bgcolor="#0f172a",
        paper_bgcolor="#0f172a",
        font=dict(color="#f8fafc"),
        showlegend=False
    )
    return fig


def create_nodes_explored_chart(df: pd.DataFrame) -> go.Figure:
    """Compare nodes explored across algorithms using log scale."""
    fig = px.bar(
        df,
        x="algorithm",
        y="nodes_explored",
        color="algorithm",
        log_y=True,
        title="Nodes Explored Comparison (Logarithmic Scale)",
        labels={"nodes_explored": "Nodes Explored (log scale)", "algorithm": "Algorithm"},
        color_discrete_map={
            "Minimax": "#ef4444",
            "AlphaBeta": "#10b981",
            "Greedy": "#3b82f6",
            "IterativeDeepening": "#8b5cf6"
        }
    )
    fig.update_layout(
        plot_bgcolor="#0f172a",
        paper_bgcolor="#0f172a",
        font=dict(color="#f8fafc"),
        showlegend=False
    )
    return fig


def create_pruning_efficiency_chart(df_exp1: pd.DataFrame) -> go.Figure:
    """Plot pruning efficiency (% node reduction) by depth."""
    df_grouped = df_exp1.groupby("depth").agg({
        "minimax_nodes": "mean",
        "alphabeta_nodes": "mean",
        "node_reduction_pct": "mean",
        "speedup": "mean"
    }).reset_index()

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=[f"Depth {d}" for d in df_grouped["depth"]],
        y=df_grouped["node_reduction_pct"],
        name="Node Reduction (%)",
        marker_color="#10b981",
        text=[f"{v:.1f}%" for v in df_grouped["node_reduction_pct"]],
        textposition="outside"
    ))

    fig.update_layout(
        title="Alpha-Beta Pruning Efficiency by Search Depth",
        xaxis_title="Search Depth",
        yaxis_title="Reduction in Nodes Explored (%)",
        yaxis=dict(range=[0, 100]),
        plot_bgcolor="#0f172a",
        paper_bgcolor="#0f172a",
        font=dict(color="#f8fafc")
    )
    return fig


def create_iterative_deepening_progression_chart(iterations: List[Dict[str, Any]]) -> go.Figure:
    """Plot iterative deepening progression across completed depths."""
    if not iterations:
        fig = go.Figure()
        fig.update_layout(title="No iterations available")
        return fig

    depths = [f"Depth {it['depth']}" for it in iterations]
    times = [it["iteration_time"] for it in iterations]
    nodes = [it["nodes_explored"] for it in iterations]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=depths,
        y=times,
        name="Iteration Time (s)",
        marker_color="#8b5cf6",
        yaxis="y"
    ))
    fig.add_trace(go.Scatter(
        x=depths,
        y=nodes,
        name="Nodes Explored",
        mode="lines+markers",
        marker=dict(color="#f59e0b", size=8),
        line=dict(color="#f59e0b", width=3),
        yaxis="y2"
    ))

    fig.update_layout(
        title="Iterative Deepening Progression Across Search Depths",
        xaxis_title="Depth",
        yaxis=dict(title="Time (s)", titlefont=dict(color="#8b5cf6")),
        yaxis2=dict(
            title="Nodes Explored",
            titlefont=dict(color="#f59e0b"),
            overlaying="y",
            side="right"
        ),
        legend=dict(x=0.05, y=0.95),
        plot_bgcolor="#0f172a",
        paper_bgcolor="#0f172a",
        font=dict(color="#f8fafc")
    )
    return fig


def create_evaluation_radar_chart(eval_details: Dict[str, Any]) -> go.Figure:
    """Create a radar chart showing breakdown of positional evaluation components."""
    categories = [
        "Material", "PST Position", "Mobility",
        "Center Control", "King Safety", "Pawn Structure"
    ]
    values = [
        eval_details.get("material", 0),
        eval_details.get("pst", 0),
        eval_details.get("mobility", 0),
        eval_details.get("center", 0),
        eval_details.get("king_safety", 0),
        eval_details.get("pawn_structure", 0)
    ]
    # Close the radar loop
    categories.append(categories[0])
    values.append(values[0])

    fig = go.Figure(data=go.Scatterpolar(
        r=values,
        theta=categories,
        fill="toself",
        fillcolor="rgba(56, 189, 248, 0.3)",
        line=dict(color="#38bdf8", width=2),
        name="Score Component (cp)"
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, showline=True, gridcolor="#334155"),
            angularaxis=dict(gridcolor="#334155")
        ),
        title="Evaluation Heuristic Components Breakdown (White Perspective)",
        showlegend=False,
        plot_bgcolor="#0f172a",
        paper_bgcolor="#0f172a",
        font=dict(color="#f8fafc"),
        height=360,
        margin=dict(l=30, r=30, t=40, b=30)
    )
    return fig
