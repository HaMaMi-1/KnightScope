# KNIGHTSCOPE: Intelligent Chess Position Analysis Using Classical AI
**Team DEEP KNIGHTS • Artificial Intelligence with Python Course Project**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit App](https://img.shields.io/badge/Streamlit-1.30+-FF4B4B.svg)](https://streamlit.io/)
[![pytest](https://img.shields.io/badge/pytest-Passing-brightgreen.svg)](https://pytest.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 1. Project Overview

**KnightScope** is an autonomous, explainable chess position analysis and move recommendation application built purely using classical Artificial Intelligence search algorithms and handcrafted heuristic evaluation. 

Developed by **Team DEEP KNIGHTS** (4 students) for an academic AI with Python course, the application demonstrates:
- **No external chess engines** (e.g. Stockfish) or neural networks are used for move evaluation.
- All four search algorithms and the multi-component heuristic evaluation function are implemented from scratch.
- The `python-chess` library is utilized strictly for chess rule validation, legal move generation, and FEN parsing.
- The application functions as an **interactive position analyzer**, not a human-vs-machine playing game.

---

## 2. Implemented AI Algorithms

1. **Adversarial Minimax Search:**
   - Exhaustive depth-limited game-tree search alternating MAX (White) and MIN (Black) plies.
   - Evaluates leaf positions with the handcrafted heuristic evaluation function.
   - Accurately handles checkmate, stalemate, and draw conditions.
2. **Alpha-Beta Pruning:**
   - Optimal branch-and-bound pruning maintaining $[\alpha, \beta]$ search bounds.
   - Incorporates **Most Valuable Victim – Least Valuable Attacker (MVV-LVA)** move ordering.
   - Mathematically verified to yield the exact identical minimax score and optimal move while eliminating 88% to 98.9% of searched nodes at depth 3.
3. **Greedy Best-First Search:**
   - Single-ply heuristic candidate evaluation baseline.
   - Evaluates immediate successor positions without adversarial lookahead.
   - Empirically exposes the *tactical horizon effect* and vulnerability to traps (e.g., poisoned pawns).
4. **Iterative Deepening Search (IDS):**
   - Progressive deepening strategy ($d = 1, 2, 3, \dots$) utilizing Alpha-Beta search.
   - Guarantees any-time move recommendations under strict time budgets ($t \le t_{\text{limit}}$).

---

## 3. Handcrafted Evaluation Function

Evaluates board states strictly from White's perspective in centipawns (positive = White advantage; negative = Black advantage):
$$\text{Score}(s) = 1.0 \cdot \Delta_{\text{mat}} + 1.0 \cdot \Delta_{\text{pst}} + 0.1 \cdot \Delta_{\text{mob}} + 0.3 \cdot \Delta_{\text{cnt}} + 0.5 \cdot \Delta_{\text{ks}} + 0.25 \cdot \Delta_{\text{pwn}} + 0.5 \cdot \Delta_{\text{bp}}$$

- **Material Values:** Pawn = 100, Knight = 320, Bishop = 330, Rook = 500, Queen = 900, King = 0.
- **Piece-Square Tables (PST):** Positional piece values based on square control and king shelter.
- **Mobility:** Total attacked legal squares.
- **Center Control:** Control and occupation of central squares $\{e4, d4, e5, d5\}$.
- **King Safety:** Castling status and pawn shelter shield bonuses.
- **Pawn Structure:** Penalties for doubled pawns and isolated pawns; bonus for bishop pair.

---

## 4. Project Directory Structure

```text
KnightScope/
│
├── app.py                         # Complete Streamlit interactive web dashboard
│
├── engine/                        # Core AI search algorithms and evaluation
│   ├── __init__.py
│   ├── minimax.py                 # Adversarial Minimax implementation
│   ├── alphabeta.py               # Alpha-Beta Pruning implementation
│   ├── greedy.py                  # Greedy Best-First 1-ply baseline
│   ├── iterative_deepening.py     # Time-budgeted Iterative Deepening
│   ├── evaluation.py              # Handcrafted multi-factor evaluation
│   ├── move_ordering.py           # MVV-LVA move ordering
│   └── board_utils.py             # Board parsing, FEN validation, SVG rendering
│
├── analysis/                      # Empirical benchmarking and experiments
│   ├── __init__.py
│   ├── benchmark.py               # Benchmark harness across test positions
│   ├── experiments.py             # Experiments 1, 2, 3, and 4 runner
│   └── statistics.py              # Statistical metrics (speedup, pruning %)
│
├── visualization/                 # Interactive visual components
│   ├── __init__.py
│   ├── chess_visualization.py     # SVG board generation & search tree slice
│   └── performance_charts.py      # Plotly interactive comparison charts
│
├── tests/                         # Automated pytest test suite
│   ├── __init__.py
│   ├── test_moves.py              # Move legality and FEN tests
│   ├── test_algorithms.py         # Minimax, AlphaBeta, Greedy, IDS tests
│   ├── test_evaluation.py         # Evaluation symmetry & terminal tests
│   └── test_positions.py         # Benchmark positions validation tests
│
├── data/                          # Benchmark dataset and experimental CSVs
│   ├── test_positions.json        # 10 diverse benchmark test positions
│   ├── benchmark_results.csv      # Consolidated benchmark data
│   ├── exp1_minimax_vs_alphabeta.csv
│   ├── exp2_search_depth.csv
│   ├── exp3_greedy_vs_minimax.csv
│   └── exp4_iterative_deepening.csv
│
├── documentation/                 # Formal academic reports & figures
│   ├── PROJECT_REPORT.md          # Complete academic markdown report
│   ├── EXPERIMENTAL_RESULTS.md    # Detailed empirical analysis
│   ├── REFERENCES.md              # Academic bibliography
│   ├── figures/                   # SVG diagrams and chart PNGs
│   └── generate_report.py         # DOCX & PDF generation script
│
├── presentation/                  # PowerPoint presentation
│   ├── KnightScope_Presentation.pptx # Polished 16-slide academic presentation
│   └── generate_presentation.py  # Presentation builder script
│
├── scripts/                       # Helper and figure generation scripts
│   ├── generate_figures.py
│   └── consolidate_benchmarks.py
│
├── KnightScope_Report.docx        # Editable Word academic report (~25 pages)
├── KnightScope_Report.pdf         # Print-ready academic PDF report
├── requirements.txt               # Python package dependencies
├── README.md                      # Project documentation and guide
└── .gitignore                     # Git ignore rules
```

---

## 5. Installation & Setup

### Prerequisites
- Python 3.10 or higher
- pip package manager

### Step 1: Clone or Navigate to the Workspace
```bash
cd "Knight Scope"
```

### Step 2: Install Required Dependencies
```bash
pip install -r requirements.txt
```

---

## 6. Running the Application

Launch the interactive Streamlit dashboard:
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

### Key Interface Features:
1. **Position Input:** Start from standard position, enter any custom FEN, or choose from 10 preset positions.
2. **AI Analysis:** Select algorithm, configure depth or time limit, and click **"Run AI Analysis"**.
3. **Move Annotations:** View the recommended best move (green arrow) and top alternatives (cyan arrows).
4. **Side-by-Side Comparison:** Compare Minimax, Alpha-Beta, Greedy, and IDS on the same board position.
5. **Search Tree Visualization:** Inspect an illustrative game-tree slice showing MAX/MIN levels and cutoff lines.
6. **Position Explanation:** View an interactive radar chart and heuristic breakdown.

---

## 7. Running Automated Tests

Run the full pytest test suite:
```bash
pytest tests/ -v
```
All 19 test cases verify:
- Standard board parsing and legal move validation
- Illegal move rejection and promotion handling
- Checkmate, stalemate, and draw evaluations
- Handcrafted evaluation symmetry
- Minimax and Alpha-Beta move legality
- Exact Minimax vs. Alpha-Beta score and move equivalence
- Iterative Deepening progression and timeout safety

---

## 8. Executing Experiments & Generating Reports

### Re-running Benchmarks:
```bash
python analysis/experiments.py
```

### Re-generating Reports (DOCX and PDF):
```bash
python documentation/generate_report.py
```

### Re-generating Presentation (.pptx):
```bash
python presentation/generate_presentation.py
```

---

## 9. Team DEEP KNIGHTS Contributions

| Team Member | Assigned Roles | Core Deliverables Owned |
| :--- | :--- | :--- |
| **Member 1** | Chess representation, FEN handling, legal moves and backend. | `engine/board_utils.py`, FEN parsing, move validation |
| **Member 2** | Minimax and Alpha-Beta Pruning implementation. | `engine/minimax.py`, `engine/alphabeta.py`, move ordering |
| **Member 3** | Greedy Search, Iterative Deepening, evaluation function. | `engine/greedy.py`, `engine/iterative_deepening.py`, `engine/evaluation.py` |
| **Member 4** | User interface, visualization, benchmarking, and reports. | `app.py`, `visualization/`, `analysis/`, presentation, reports |

*All four members actively participated in system integration, automated testing, and academic reporting.*
