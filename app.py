"""KnightScope: Intelligent Chess Position Analysis Using Classical AI.
Interactive Streamlit Dashboard.
Developed by Team Deep Knights.
"""

import os
import sys
import time
import json
import streamlit as st
import chess
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from engine.board_utils import (
    create_board,
    validate_fen,
    get_game_status,
    render_board_svg,
    get_move_san,
    parse_move
)
from engine.evaluation import evaluate_detailed, evaluate_board, PIECE_VALUES
from engine.minimax import minimax_search
from engine.alphabeta import alphabeta_search
from engine.greedy import greedy_search
from engine.iterative_deepening import iterative_deepening_search
from visualization.chess_visualization import get_board_svg_with_arrows, generate_search_tree_figure
from visualization.performance_charts import (
    create_execution_time_chart,
    create_nodes_explored_chart,
    create_evaluation_radar_chart,
    create_iterative_deepening_progression_chart
)

st.set_page_config(
    page_title="KnightScope - Intelligent Chess Position Analysis",
    page_icon="♞",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling for modern dark chess aesthetic
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #f8fafc;
        margin-bottom: 0px;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #94a3b8;
        margin-bottom: 15px;
    }
    .metric-card {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 14px;
        margin-bottom: 10px;
    }
    .disclaimer-box {
        background-color: #1e1b4b;
        border-left: 4px solid #6366f1;
        padding: 10px 15px;
        border-radius: 4px;
        font-size: 0.88rem;
        color: #c7d2fe;
        margin-bottom: 15px;
    }
    .explanation-box {
        background-color: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 8px;
        padding: 15px;
        font-size: 0.95rem;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_sample_positions():
    json_path = os.path.join(PROJECT_ROOT, "data", "test_positions.json")
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


# Initialize Session State
if "fen" not in st.session_state:
    st.session_state.fen = chess.STARTING_FEN
if "last_move" not in st.session_state:
    st.session_state.last_move = None
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "comparison_results" not in st.session_state:
    st.session_state.comparison_results = None
if "flip_board" not in st.session_state:
    st.session_state.flip_board = False


sample_positions = load_sample_positions()

# ----------------- SIDEBAR -----------------
with st.sidebar:
    st.markdown("## ♞ KnightScope AI")
    st.caption("Team Deep Knights • Classical AI Project")
    st.markdown("---")

    st.subheader("1. Position Input")
    pos_options = ["Standard Starting Position", "Custom FEN Input"] + [
        f"[{p['id']}] {p['name']}" for p in sample_positions
    ]
    selected_pos_opt = st.selectbox("Select Preset Position:", pos_options)

    if selected_pos_opt == "Standard Starting Position":
        if st.session_state.fen != chess.STARTING_FEN:
            st.session_state.fen = chess.STARTING_FEN
            st.session_state.analysis_result = None
    elif selected_pos_opt == "Custom FEN Input":
        custom_fen = st.text_area(
            "Enter FEN string:",
            value=st.session_state.fen,
            height=70
        )
        if st.button("Apply FEN"):
            is_valid, err = validate_fen(custom_fen)
            if is_valid:
                st.session_state.fen = custom_fen.strip()
                st.session_state.analysis_result = None
                st.success("FEN applied successfully!")
            else:
                st.error(f"Invalid FEN: {err}")
    else:
        # Match sample position
        pos_id = selected_pos_opt.split("]")[0].replace("[", "")
        matched = next((p for p in sample_positions if p["id"] == pos_id), None)
        if matched and st.session_state.fen != matched["fen"]:
            st.session_state.fen = matched["fen"]
            st.session_state.analysis_result = None

    # Current FEN status
    is_valid_fen, fen_err = validate_fen(st.session_state.fen)
    board = create_board(st.session_state.fen) if is_valid_fen else chess.Board()

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("↺ Reset Board"):
            st.session_state.fen = chess.STARTING_FEN
            st.session_state.analysis_result = None
            st.session_state.comparison_results = None
            st.rerun()
    with col_btn2:
        st.session_state.flip_board = st.checkbox("Flip Board", value=(board.turn == chess.BLACK))

    st.markdown("---")
    st.subheader("2. AI Algorithm & Parameters")
    algo_choice = st.selectbox(
        "Search Algorithm:",
        ["Alpha-Beta Pruning", "Minimax", "Greedy Best-First Search", "Iterative Deepening"]
    )

    if algo_choice in ["Minimax", "Alpha-Beta Pruning"]:
        depth = st.slider("Search Depth (plies):", min_value=1, max_value=4, value=3)
        time_limit = 2.0
    elif algo_choice == "Iterative Deepening":
        depth = st.slider("Max Depth Target:", min_value=1, max_value=6, value=4)
        time_limit = st.slider("Time Limit (seconds):", min_value=0.5, max_value=10.0, value=2.0, step=0.5)
    else:
        st.info("Greedy evaluates immediate 1-ply candidates only.")
        depth = 1
        time_limit = 0.5

    move_ordering = st.checkbox("Enable Move Ordering (MVV-LVA)", value=True)

    st.markdown("---")
    analyze_btn = st.button("⚡ Run AI Analysis", type="primary", use_container_width=True)
    compare_btn = st.button("⚖ Compare All Algorithms", use_container_width=True)


# ----------------- MAIN CONTENT -----------------
st.markdown('<div class="main-title">KNIGHTSCOPE</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">Intelligent Chess Position Analysis Using Classical AI Search & Handcrafted Heuristics</div>',
    unsafe_allow_html=True
)

st.markdown("""
<div class="disclaimer-box">
    <strong>Academic Notice:</strong> Move recommendations are determined by classical adversarial search and handcrafted heuristic evaluation at the configured depth, not by external engines or neural networks. Heuristic values reflect algorithmic search conclusions under the specified depth and evaluation parameters.
</div>
""", unsafe_allow_html=True)

# Game Status Banner
status = get_game_status(board)
status_col1, status_col2, status_col3 = st.columns([2, 1, 1])
with status_col1:
    st.write(f"**Turn:** {status['turn']} to move | **Legal Moves:** {status['legal_moves_count']} | **State:** {status['description']}")
with status_col2:
    eval_quick = evaluate_board(board)
    st.write(f"**Static Heuristic:** `{eval_quick:+d}` cp ({eval_quick/100:+.2f} pawns)")
with status_col3:
    st.write(f"**FEN Valid:** {'✅ Yes' if is_valid_fen else '❌ Invalid'}")

if not is_valid_fen:
    st.error(f"Cannot proceed with invalid FEN: {fen_err}")
    st.stop()


# Execute Single AI Analysis if requested
if analyze_btn:
    with st.spinner(f"Running {algo_choice}..."):
        if algo_choice == "Minimax":
            res = minimax_search(board, depth=depth, use_move_ordering=move_ordering)
        elif algo_choice == "Alpha-Beta Pruning":
            res = alphabeta_search(board, depth=depth, use_move_ordering=move_ordering)
        elif algo_choice == "Greedy Best-First Search":
            res = greedy_search(board)
        else:
            res = iterative_deepening_search(board, max_depth=depth, time_limit=time_limit, use_move_ordering=move_ordering)

        st.session_state.analysis_result = {
            "algorithm": algo_choice,
            "data": res
        }

# Execute Multi-Algorithm Comparison if requested
if compare_btn:
    with st.spinner("Executing side-by-side multi-algorithm evaluation..."):
        comp_data = []
        # Minimax
        res_mm = minimax_search(board, depth=min(depth, 3), use_move_ordering=move_ordering)
        comp_data.append({"algorithm": "Minimax", "depth": min(depth, 3), **res_mm})

        # Alpha-Beta
        res_ab = alphabeta_search(board, depth=min(depth, 3), use_move_ordering=move_ordering)
        comp_data.append({"algorithm": "Alpha-Beta", "depth": min(depth, 3), **res_ab})

        # Greedy
        res_gr = greedy_search(board)
        comp_data.append({"algorithm": "Greedy (1-ply)", "depth": 1, **res_gr})

        # IDS
        res_ids = iterative_deepening_search(board, max_depth=depth, time_limit=time_limit, use_move_ordering=move_ordering)
        comp_data.append({"algorithm": "Iterative Deepening", "depth": res_ids["completed_depth"], **res_ids})

        st.session_state.comparison_results = comp_data


# ----------------- TABS LAYOUT -----------------
tab_analysis, tab_compare, tab_tree, tab_explanation, tab_about = st.tabs([
    "🎯 Position & Analysis",
    "⚖ Algorithm Comparison",
    "🌲 Search Tree Visualization",
    "🔍 Position Explanation",
    "📖 About & Documentation"
])

# ------------- TAB 1: POSITION & ANALYSIS -------------
with tab_analysis:
    col_board, col_metrics = st.columns([1.1, 1.2])

    rec_move = None
    cand_moves = []
    if st.session_state.analysis_result:
        res_data = st.session_state.analysis_result["data"]
        rec_move = res_data.get("best_move")
        cand_moves = [c["move"] for c in res_data.get("candidate_moves", []) if "move" in c]

    with col_board:
        st.subheader("Chess Board View")
        svg = get_board_svg_with_arrows(
            board=board,
            last_move=st.session_state.last_move,
            recommended_move=rec_move,
            candidate_moves=cand_moves,
            size=440,
            flipped=st.session_state.flip_board
        )
        st.image(svg, width=440)
        st.caption("🟢 Green arrow: Recommended move | 🔵 Cyan arrow: Alternative candidate moves")

        # Move execution simulation
        if rec_move:
            if st.button(f"▶ Apply Recommended Move ({res_data.get('best_move_san', '')})"):
                board.push(rec_move)
                st.session_state.fen = board.fen()
                st.session_state.last_move = rec_move
                st.session_state.analysis_result = None
                st.rerun()

    with col_metrics:
        st.subheader("AI Analysis Results")
        if st.session_state.analysis_result is None:
            st.info("👈 Select an algorithm and click **'Run AI Analysis'** in the sidebar to inspect this position.")
            # Show static evaluation details
            eval_det = evaluate_detailed(board)
            st.markdown(f"""
            **Static Board Assessment (White perspective):**
            - **Material Balance:** `{eval_det['material']:+d}` cp
            - **Positional Advantage (PST):** `{eval_det['pst']:+d}` cp
            - **Mobility Differential:** `{eval_det['mobility']:+d}` cp
            - **Center Control:** `{eval_det['center']:+d}` cp
            - **King Safety:** `{eval_det['king_safety']:+d}` cp
            - **Pawn Structure:** `{eval_det['pawn_structure']:+d}` cp
            """)
        else:
            cur_algo = st.session_state.analysis_result["algorithm"]
            res = st.session_state.analysis_result["data"]

            # Key metric cards
            m1, m2, m3 = st.columns(3)
            with m1:
                st.metric("Recommended Move", f"{res.get('best_move_san', 'None')}")
            with m2:
                eval_cp = res.get("score", 0)
                st.metric("Evaluation Score", f"{eval_cp:+d} cp", delta=f"{eval_cp/100:+.2f} pawns")
            with m3:
                st.metric("Explored Nodes", f"{res.get('nodes_explored', 0):,}")

            m4, m5, m6 = st.columns(3)
            with m4:
                st.metric("Execution Time", f"{res.get('execution_time', 0.0):.4f} s")
            with m5:
                nps = res.get("nodes_per_second", 0)
                st.metric("Search Speed", f"{nps:,.0f} nps")
            with m6:
                if cur_algo == "Alpha-Beta Pruning":
                    st.metric("Pruned Branches", f"{res.get('pruned_branches', 0):,}")
                elif cur_algo == "Iterative Deepening":
                    st.metric("Completed Depth", f"{res.get('completed_depth', 0)} / {res.get('max_depth_target', 0)}")
                else:
                    st.metric("Depth", f"{res.get('depth', 1)} plies")

            # Principal Variation
            pv_list = res.get("pv_san", [])
            pv_str = " ".join(pv_list) if pv_list else res.get("best_move_san", "None")
            st.markdown(f"**Predicted Principal Variation (PV):** `{pv_str}`")

            # Top Candidate Moves
            cands = res.get("candidate_moves", [])
            if cands:
                st.markdown("**Top Candidate Moves Evaluated at Root:**")
                cand_table = []
                for i, c in enumerate(cands, 1):
                    cand_table.append({
                        "Rank": f"#{i}",
                        "Move (SAN)": c.get("san"),
                        "Move (UCI)": c.get("uci"),
                        "Heuristic Score (cp)": f"{c.get('score', 0):+d}",
                        "Pawn Equivalent": f"{c.get('score', 0)/100:+.2f}"
                    })
                st.dataframe(pd.DataFrame(cand_table), use_container_width=True, hide_index=True)

            # If Iterative Deepening, display iteration progression
            if cur_algo == "Iterative Deepening" and res.get("iterations"):
                st.markdown("**Iterative Deepening Progression Table:**")
                it_df = pd.DataFrame([
                    {
                        "Depth": it["depth"],
                        "Best Move": it["best_move_san"],
                        "Score (cp)": it["score"],
                        "Depth Nodes": it["nodes_explored"],
                        "Time (s)": round(it["iteration_time"], 4),
                        "PV": " ".join(it["pv_san"][:4])
                    }
                    for it in res["iterations"]
                ])
                st.dataframe(it_df, use_container_width=True, hide_index=True)


# ------------- TAB 2: ALGORITHM COMPARISON -------------
with tab_compare:
    st.subheader("Side-by-Side Algorithm Comparison")
    st.write("Examines how different classical AI search techniques evaluate the identical chess position.")

    if st.session_state.comparison_results is None:
        st.info("Click **'Compare All Algorithms'** in the sidebar to benchmark Minimax, Alpha-Beta, Greedy, and Iterative Deepening.")
    else:
        comp_df = pd.DataFrame([
            {
                "Algorithm": r["algorithm"],
                "Search Depth": r["depth"],
                "Best Move": r["best_move_san"],
                "Score (cp)": r["score"],
                "Nodes Explored": r["nodes_explored"],
                "Pruned Branches": r.get("pruned_branches", 0),
                "Execution Time (s)": round(r["execution_time"], 4),
                "Nodes/Sec": round(r.get("nodes_per_second", 0), 1)
            }
            for r in st.session_state.comparison_results
        ])

        st.dataframe(comp_df, use_container_width=True, hide_index=True)

        st.markdown("""
        > **Methodological Note on Metric Comparability:**
        > - **Minimax vs Alpha-Beta:** Directly comparable at identical depth and evaluation function. Alpha-Beta is mathematically guaranteed to find the identical minimax score while exploring fewer or equal nodes.
        > - **Greedy Best-First Search:** Evaluates only immediate 1-ply candidates without adversarial lookahead. Its low node count represents limited search scope rather than computational efficiency.
        > - **Iterative Deepening:** Aggregates nodes across iterative depth passes (1..d).
        """)

        # Charts
        c_col1, c_col2 = st.columns(2)
        plot_df = pd.DataFrame([
            {
                "algorithm": r["algorithm"],
                "execution_time_sec": r["execution_time"],
                "nodes_explored": r["nodes_explored"]
            }
            for r in st.session_state.comparison_results
        ])
        with c_col1:
            st.plotly_chart(create_execution_time_chart(plot_df), use_container_width=True)
        with c_col2:
            st.plotly_chart(create_nodes_explored_chart(plot_df), use_container_width=True)


# ------------- TAB 3: SEARCH TREE VISUALIZATION -------------
with tab_tree:
    st.subheader("Classical Search Tree & Pruning Visualization")
    st.write(
        "Illustrative visualization of adversarial game-tree lookahead with MAX and MIN levels. "
        "Demonstrates where Alpha-Beta cutoff thresholds prune provably unpromising candidate branches."
    )
    tree_depth = st.slider("Tree Visualization Depth:", min_value=1, max_value=2, value=2)
    tree_fig = generate_search_tree_figure(board, depth=tree_depth, max_branching=4)
    st.plotly_chart(tree_fig, use_container_width=True)

    st.markdown("""
    **Understanding the Tree:**
    - **Root Node (Gold):** Current board position (MAX player if White, MIN player if Black).
    - **Level 1 Nodes (Blue):** First-ply candidate moves evaluated.
    - **Level 2 Nodes (Green / Red):** Opponent replies. Red dashed lines with `[CUT]` indicate subtrees pruned when `beta <= alpha`.
    """)


# ------------- TAB 4: POSITION EXPLANATION -------------
with tab_explanation:
    st.subheader("Heuristic Position Explanation")
    st.write(
        "Breakdown of handcrafted evaluation features contributing to the overall numerical score. "
        "Positive scores denote an advantage for White; negative scores denote an advantage for Black."
    )

    eval_det = evaluate_detailed(board)

    exp_col1, exp_col2 = st.columns([1, 1.2])

    with exp_col1:
        st.markdown(f"### Total Score: `{eval_det['total_score']:+d}` cp")
        pawn_equiv = eval_det['total_score'] / 100.0

        if abs(eval_det['total_score']) < 50:
            summary_text = "The position is dynamically balanced. Neither player possesses a decisive advantage."
        elif eval_det['total_score'] > 0:
            summary_text = f"White holds an advantage of approximately {pawn_equiv:+.2f} pawns."
        else:
            summary_text = f"Black holds an advantage of approximately {abs(pawn_equiv):.2f} pawns."

        st.markdown(f"""
        <div class="explanation-box">
            <strong>Strategic Summary:</strong><br>
            {summary_text}
            <br><br>
            <strong>Factor Analysis:</strong>
            <ul>
                <li><strong>Material Difference:</strong> {eval_det['material']:+d} cp (White: {eval_det['white_material']} vs Black: {eval_det['black_material']})</li>
                <li><strong>Piece-Square Positional Bonus:</strong> {eval_det['pst']:+d} cp</li>
                <li><strong>Mobility Difference:</strong> {eval_det['mobility']:+d} cp</li>
                <li><strong>Center Control Bonus:</strong> {eval_det['center']:+d} cp</li>
                <li><strong>King Safety Factor:</strong> {eval_det['king_safety']:+d} cp</li>
                <li><strong>Pawn Structure (Doubled/Isolated):</strong> {eval_det['pawn_structure']:+d} cp</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with exp_col2:
        radar_fig = create_evaluation_radar_chart(eval_det)
        st.plotly_chart(radar_fig, use_container_width=True)


# ------------- TAB 5: ABOUT & DOCUMENTATION -------------
with tab_about:
    st.subheader("About KnightScope")
    st.markdown("""
    **KnightScope: Intelligent Chess Position Analysis Using Classical AI**
    - **Academic Category:** Classical Artificial Intelligence Course Project
    - **Team Identity:** DEEP KNIGHTS (Team of 4 Students)
    - **Core AI Algorithms:**
      1. **Adversarial Minimax Search:** Complete game tree exploration across alternating MAX and MIN plies.
      2. **Alpha-Beta Pruning:** Optimal branch-and-bound pruning maintaining $[\\alpha, \\beta]$ interval bounds.
      3. **Greedy Best-First Search:** Single-ply heuristic evaluation baseline highlighting the horizon effect and local myopia.
      4. **Iterative Deepening Search:** Progressive deepening strategy executing depth-limited Alpha-Beta search under hard time constraints.
    - **Evaluation Model:** Handcrafted multi-factor evaluation combining material weights, piece-square tables (PST), mobility, center control, and king safety.
    """)

    st.markdown("---")
    st.subheader("Team Roles & Responsibilities")
    st.markdown("""
    | Team Member | Assigned Core Responsibilities |
    | :--- | :--- |
    | **Member 1** | Chess representation, FEN handling, legal moves and application backend. |
    | **Member 2** | Minimax and Alpha-Beta Pruning algorithm implementation. |
    | **Member 3** | Greedy Best-First Search, Iterative Deepening and evaluation function. |
    | **Member 4** | User interface, visualization, benchmarking and performance dashboard. |
    *All members collaboratively participated in system integration, automated testing, and report generation.*
    """)
