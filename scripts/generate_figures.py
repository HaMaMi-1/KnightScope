"""Generate visualization figures and diagrams for KnightScope documentation and presentation:
1. Board diagrams with recommended moves and candidate arrows
2. Performance charts saved as PNG images
"""

import os
import sys
import chess
import chess.svg
import pandas as pd
import matplotlib.pyplot as plt

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from engine.board_utils import create_board
from visualization.chess_visualization import get_board_svg_with_arrows


def generate_all_figures():
    fig_dir = os.path.join(PROJECT_ROOT, "documentation", "figures")
    os.makedirs(fig_dir, exist_ok=True)

    # 1. Generate SVG Board Diagrams for Key Positions
    # Position 1: Italian Game
    b1 = create_board("r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/2NP1N2/PPP2PPP/R1BQK2R b KQkq - 0 5")
    svg1 = get_board_svg_with_arrows(
        b1,
        recommended_move=chess.Move.from_uci("c5b4"),
        candidate_moves=[chess.Move.from_uci("f6e4"), chess.Move.from_uci("e8g8")]
    )
    with open(os.path.join(fig_dir, "board_italian_game.svg"), "w", encoding="utf-8") as f:
        f.write(svg1)

    # Position 6: Scholar's mate threat
    b6 = create_board("r1bqkb1r/pppp1ppp/2n2n2/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR w KQkq - 4 4")
    svg6 = get_board_svg_with_arrows(
        b6,
        recommended_move=chess.Move.from_uci("h5f7"),
        candidate_moves=[chess.Move.from_uci("c4f7")]
    )
    with open(os.path.join(fig_dir, "board_scholars_mate.svg"), "w", encoding="utf-8") as f:
        f.write(svg6)

    # Position 8: Poisoned pawn trap
    b8 = create_board("r1bqk2r/pp2bppp/2n1pn2/2pp4/3P4/2PBPN2/PP1N1PPP/R1BQK2R w KQkq - 1 7")
    svg8 = get_board_svg_with_arrows(
        b8,
        recommended_move=chess.Move.from_uci("d3b5"),
        candidate_moves=[chess.Move.from_uci("d3h7")]
    )
    with open(os.path.join(fig_dir, "board_poisoned_pawn.svg"), "w", encoding="utf-8") as f:
        f.write(svg8)

    # 2. Performance Comparison Plot (Matplotlib)
    exp1_path = os.path.join(PROJECT_ROOT, "data", "exp1_minimax_vs_alphabeta.csv")
    if os.path.exists(exp1_path):
        df = pd.read_csv(exp1_path)
        df_d3 = df[df["depth"] == 3].copy()

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        plt.style.use("seaborn-v0_8-darkgrid" if "seaborn-v0_8-darkgrid" in plt.style.available else "default")

        # Plot 1: Nodes Explored (Log Scale)
        positions = [f"P{i+1}" for i in range(len(df_d3))]
        x = range(len(df_d3))
        ax1.bar([p - 0.2 for p in x], df_d3["minimax_nodes"], width=0.4, label="Minimax (Depth 3)", color="#ef4444")
        ax1.bar([p + 0.2 for p in x], df_d3["alphabeta_nodes"], width=0.4, label="Alpha-Beta (Depth 3)", color="#10b981")
        ax1.set_yscale("log")
        ax1.set_title("Nodes Explored at Depth 3 (Log Scale)", fontsize=12, fontweight="bold")
        ax1.set_ylabel("Nodes Explored (Log)")
        ax1.set_xticks(list(x))
        ax1.set_xticklabels(positions)
        ax1.legend()

        # Plot 2: Speedup Ratio
        ax2.bar(positions, df_d3["speedup"], color="#38bdf8")
        ax2.axhline(y=1.0, color="gray", linestyle="--", alpha=0.7)
        ax2.set_title("Alpha-Beta Speedup Ratio over Minimax (Depth 3)", fontsize=12, fontweight="bold")
        ax2.set_ylabel("Speedup Factor (x Times Faster)")
        ax2.set_xlabel("Test Positions (P1 to P10)")

        plt.tight_layout()
        chart_path = os.path.join(fig_dir, "minimax_vs_alphabeta_chart.png")
        plt.savefig(chart_path, dpi=180)
        plt.close()

    print(f"Figures and diagrams generated successfully in {fig_dir}")


if __name__ == "__main__":
    generate_all_figures()
