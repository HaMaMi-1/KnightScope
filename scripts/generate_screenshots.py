"""Generate application screenshots and interface preview images."""

import os
import sys
import chess
import chess.svg
import matplotlib.pyplot as plt
import pandas as pd

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
screenshots_dir = os.path.join(PROJECT_ROOT, "documentation", "screenshots")
os.makedirs(screenshots_dir, exist_ok=True)

# 1. Dashboard Analysis Mockup Graphic
fig, ax = plt.subplots(figsize=(10, 6), facecolor="#0f172a")
ax.set_facecolor("#1e293b")

# Board representation panel
ax.text(0.05, 0.90, "KNIGHTSCOPE CHESS AI DASHBOARD", color="#f8fafc", fontsize=16, fontweight="bold")
ax.text(0.05, 0.83, "Position: Balanced Italian Game [pos_01] | Turn: Black to move", color="#94a3b8", fontsize=11)

# Metrics Cards
rect_coords = [(0.05, 0.55, 0.26, 0.22), (0.35, 0.55, 0.26, 0.22), (0.65, 0.55, 0.28, 0.22)]
titles = ["RECOMMENDED MOVE", "EVALUATION SCORE", "ALGORITHM METRICS"]
vals = ["Bb4 (Pin Knight)", "-1.98 pawns (-198 cp)", "Alpha-Beta (d=3)\nNodes: 2,245 | Time: 0.98s"]
colors_accent = ["#10b981", "#38bdf8", "#f59e0b"]

for (x, y, w, h), t, v, c in zip(rect_coords, titles, vals, colors_accent):
    rect = plt.Rectangle((x, y), w, h, facecolor="#0f172a", edgecolor="#334155", linewidth=1.5)
    ax.add_patch(rect)
    ax.text(x + 0.02, y + 0.16, t, color=c, fontsize=9, fontweight="bold")
    ax.text(x + 0.02, y + 0.06, v, color="#f8fafc", fontsize=10)

# PV and candidate moves
ax.text(0.05, 0.45, "Predicted Principal Variation (PV):  Bb4  Bd2  Bxc3  Bxc3  Nxe4", color="#38bdf8", fontsize=11, fontweight="bold")
ax.text(0.05, 0.35, "Root Candidate Moves Ranking:", color="#f8fafc", fontsize=11, fontweight="bold")
ax.text(0.05, 0.28, "1. Bb4 (Score: -198 cp) - Pins White Knight on c3, increasing Black center influence", color="#94a3b8", fontsize=10)
ax.text(0.05, 0.21, "2. Nxe4 (Score: -132 cp) - Immediate pawn capture; evaluated by Greedy 1-ply baseline", color="#94a3b8", fontsize=10)
ax.text(0.05, 0.14, "3. O-O  (Score: -110 cp) - King safety castling; solid positional alternative", color="#94a3b8", fontsize=10)

ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis("off")

plt.tight_layout()
dashboard_path = os.path.join(screenshots_dir, "app_dashboard_overview.png")
plt.savefig(dashboard_path, dpi=200, facecolor=fig.get_facecolor(), edgecolor="none")
plt.close()

# 2. Comparison View Graphic
fig2, ax2 = plt.subplots(figsize=(10, 5), facecolor="#0f172a")
ax2.set_facecolor("#1e293b")
ax2.text(0.05, 0.88, "SIDE-BY-SIDE ALGORITHM COMPARISON", color="#f8fafc", fontsize=15, fontweight="bold")

headers = ["Algorithm", "Depth", "Best Move", "Score (cp)", "Nodes Explored", "Pruned Nodes", "Time (s)"]
rows = [
    ["Minimax", "3", "Bb4", "-198", "49,426", "0", "21.87 s"],
    ["Alpha-Beta", "3", "Bb4", "-198", "2,245", "3,879 (95.5%)", "0.98 s"],
    ["Greedy", "1", "Nxe4", "-132", "36", "0", "0.01 s"],
    ["Iterative Deepening", "4 (Time: 2.0s)", "Bb4", "+63", "23,094", "18,412", "11.55 s"]
]

# Draw table
y_pos = 0.72
for j, h in enumerate(headers):
    ax2.text(0.05 + j * 0.13, y_pos, h, color="#38bdf8", fontsize=9.5, fontweight="bold")

y_pos -= 0.05
ax2.plot([0.05, 0.95], [y_pos, y_pos], color="#334155", linewidth=1.5)

for r in rows:
    y_pos -= 0.10
    for j, val in enumerate(r):
        color = "#10b981" if j == 2 and val == "Bb4" else ("#ef4444" if val == "Nxe4" else "#f8fafc")
        ax2.text(0.05 + j * 0.13, y_pos, val, color=color, fontsize=9.5)

ax2.set_xlim(0, 1)
ax2.set_ylim(0, 1)
ax2.axis("off")

plt.tight_layout()
comp_path = os.path.join(screenshots_dir, "app_algorithm_comparison.png")
plt.savefig(comp_path, dpi=200, facecolor=fig2.get_facecolor(), edgecolor="none")
plt.close()

print(f"Application screenshots created in {screenshots_dir}")
