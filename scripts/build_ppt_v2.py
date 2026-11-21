"""
KnightScope — Intelligent Chess Position Analysis Using Classical AI
PowerPoint Presentation Builder (python-pptx)
Team: DEEP KNIGHTS | AI with Python Course | 2026
"""

import os
import copy
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt
from pptx.oxml.ns import qn
from pptx.oxml import parse_xml
from pptx.enum.dml import MSO_THEME_COLOR
import copy
from lxml import etree

# ── Colour palette ──────────────────────────────────────────────────────────────
BG       = RGBColor(0x0f, 0x17, 0x2a)   # dark navy
ACCENT   = RGBColor(0x22, 0xd3, 0xee)   # cyan
GOLD     = RGBColor(0xf5, 0x9e, 0x0b)   # gold
WHITE    = RGBColor(0xff, 0xff, 0xff)
LIGHT    = RGBColor(0x94, 0xa3, 0xb8)   # slate-400 — subdued text
DARKCARD = RGBColor(0x1e, 0x29, 0x3b)   # card background
BORDER   = RGBColor(0x33, 0x4a, 0x5e)   # subtle border colour
GREEN    = RGBColor(0x22, 0xc5, 0x5e)
RED      = RGBColor(0xef, 0x44, 0x44)

# ── Slide dimensions ────────────────────────────────────────────────────────────
W  = Inches(13.33)
H  = Inches(7.5)

# ── Create presentation ─────────────────────────────────────────────────────────
prs = Presentation()
prs.slide_width  = W
prs.slide_height = H

BLANK_LAYOUT = prs.slide_layouts[6]   # completely blank

# ═══════════════════════════════════════════════════════════════════════════════
# Utility helpers
# ═══════════════════════════════════════════════════════════════════════════════

def add_bg(slide, color=BG):
    """Fill the entire slide with a solid colour rectangle."""
    left = top = Inches(0)
    shape = slide.shapes.add_shape(1, left, top, W, H)   # 1 = MSO_SHAPE_TYPE.RECTANGLE
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()
    return shape


def add_rect(slide, l, t, w, h, fill=DARKCARD, border=BORDER, border_width=Pt(1), radius=False):
    """Add a coloured rectangle card."""
    shape = slide.shapes.add_shape(1, l, t, w, h)
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    shape.line.color.rgb = border
    shape.line.width = border_width
    return shape


def add_label(slide, text, l, t, w, h,
              font_size=Pt(13), bold=False, color=WHITE,
              align=PP_ALIGN.LEFT, wrap=True):
    """Add a plain text box."""
    txb = slide.shapes.add_textbox(l, t, w, h)
    tf  = txb.text_frame
    tf.word_wrap = wrap
    p   = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size  = font_size
    run.font.bold  = bold
    run.font.color.rgb = color
    return txb


def add_para(tf, text, font_size=Pt(13), bold=False, color=WHITE,
             align=PP_ALIGN.LEFT, space_before=Pt(4)):
    """Append a paragraph to an existing text frame."""
    p = tf.add_paragraph()
    p.alignment = align
    p.space_before = space_before
    run = p.add_run()
    run.text = text
    run.font.size  = font_size
    run.font.bold  = bold
    run.font.color.rgb = color
    return p


def slide_header(slide, title_text, subtitle_text=None):
    """Add the standard slide header bar."""
    # Accent stripe at top
    stripe = slide.shapes.add_shape(1, Inches(0), Inches(0), W, Inches(0.07))
    stripe.fill.solid()
    stripe.fill.fore_color.rgb = ACCENT
    stripe.line.fill.background()

    # Title
    txb = slide.shapes.add_textbox(Inches(0.5), Inches(0.12), Inches(12), Inches(0.65))
    tf  = txb.text_frame
    tf.word_wrap = False
    p = tf.paragraphs[0]
    run = p.add_run()
    run.text = title_text
    run.font.size  = Pt(28)
    run.font.bold  = True
    run.font.color.rgb = WHITE

    if subtitle_text:
        p2 = tf.add_paragraph()
        r2 = p2.add_run()
        r2.text = subtitle_text
        r2.font.size  = Pt(14)
        r2.font.color.rgb = ACCENT

    # Bottom accent line
    bot = slide.shapes.add_shape(1, Inches(0), Inches(0.78), W, Inches(0.025))
    bot.fill.solid()
    bot.fill.fore_color.rgb = BORDER
    bot.line.fill.background()


def bullet_box(slide, bullets, l, t, w, h,
               font_size=Pt(13.5), title=None, title_color=ACCENT):
    """Draw a card with an optional title and bullet list."""
    add_rect(slide, l, t, w, h)
    txb = slide.shapes.add_textbox(l + Inches(0.18), t + Inches(0.12),
                                   w - Inches(0.36), h - Inches(0.24))
    tf  = txb.text_frame
    tf.word_wrap = True

    if title:
        p = tf.paragraphs[0]
        p.space_before = Pt(0)
        r = p.add_run()
        r.text = title
        r.font.size  = font_size + Pt(1)
        r.font.bold  = True
        r.font.color.rgb = title_color
    else:
        # Remove blank first paragraph
        pass

    for i, bullet in enumerate(bullets):
        if title or i > 0:
            p = tf.add_paragraph()
        else:
            p = tf.paragraphs[0]
        p.space_before = Pt(5)
        r = p.add_run()
        r.text = bullet
        r.font.size  = font_size
        r.font.color.rgb = WHITE
    return txb


def add_table_slide(slide, headers, rows, l, t, w, h,
                    hdr_fill=ACCENT, hdr_text=BG,
                    row_fills=None, font_size=Pt(11.5)):
    """Add a styled table."""
    n_cols = len(headers)
    n_rows = len(rows) + 1  # +1 for header

    tbl = slide.shapes.add_table(n_rows, n_cols, l, t, w, h).table

    # Column widths — equal
    col_w = w // n_cols
    for col in tbl.columns:
        col.width = col_w

    def _set_cell(cell, text, bold=False, fg=WHITE, bg=None, align=PP_ALIGN.CENTER, fs=font_size):
        cell.text = ""
        tf = cell.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.alignment = align
        run = p.add_run()
        run.text = text
        run.font.size  = fs
        run.font.bold  = bold
        run.font.color.rgb = fg
        if bg:
            cell.fill.solid()
            cell.fill.fore_color.rgb = bg

    # Header row
    for ci, h_text in enumerate(headers):
        _set_cell(tbl.cell(0, ci), h_text, bold=True, fg=hdr_text, bg=hdr_fill)

    # Data rows
    for ri, row in enumerate(rows):
        bg = row_fills[ri] if row_fills and ri < len(row_fills) else DARKCARD
        for ci, cell_text in enumerate(row):
            fg = WHITE
            # Highlight special values
            if '×' in str(cell_text) or '%' in str(cell_text):
                fg = GOLD
            _set_cell(tbl.cell(ri + 1, ci), str(cell_text), fg=fg, bg=bg)

    return tbl


# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 1 — Title Slide
# ═══════════════════════════════════════════════════════════════════════════════
def slide_01():
    s = prs.slides.add_slide(BLANK_LAYOUT)
    add_bg(s)

    # Gradient stripe top
    top_stripe = s.shapes.add_shape(1, Inches(0), Inches(0), W, Inches(0.12))
    top_stripe.fill.solid(); top_stripe.fill.fore_color.rgb = ACCENT
    top_stripe.line.fill.background()

    # Chess knight watermark (large, faint)
    txb = s.shapes.add_textbox(Inches(9.5), Inches(1.2), Inches(3.5), Inches(4))
    tf  = txb.text_frame
    p   = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run(); r.text = "♞"
    r.font.size = Pt(220); r.font.color.rgb = RGBColor(0x22, 0xd3, 0xee)
    # Faint via alpha not directly supported; we just use a lighter shade
    r.font.color.rgb = RGBColor(0x1a, 0x4a, 0x5a)

    # Main title
    txb2 = s.shapes.add_textbox(Inches(0.7), Inches(1.3), Inches(9), Inches(1.6))
    tf2  = txb2.text_frame; tf2.word_wrap = False
    p2   = tf2.paragraphs[0]
    r2   = p2.add_run(); r2.text = "KNIGHT"
    r2.font.size = Pt(72); r2.font.bold = True; r2.font.color.rgb = WHITE
    r2b  = p2.add_run(); r2b.text = "SCOPE"
    r2b.font.size = Pt(72); r2b.font.bold = True; r2b.font.color.rgb = ACCENT

    # Subtitle
    add_label(s, "Intelligent Chess Position Analysis Using Classical AI",
              Inches(0.7), Inches(2.9), Inches(9), Inches(0.65),
              font_size=Pt(22), color=LIGHT)

    # Divider
    div = s.shapes.add_shape(1, Inches(0.7), Inches(3.62), Inches(5), Inches(0.04))
    div.fill.solid(); div.fill.fore_color.rgb = ACCENT; div.line.fill.background()

    # Team info
    add_label(s, "DEEP KNIGHTS  |  AI with Python Course  |  2026",
              Inches(0.7), Inches(3.75), Inches(9), Inches(0.5),
              font_size=Pt(16), bold=True, color=GOLD)

    # Badges
    for i, (icon, txt, col) in enumerate([
        ("🔗", "github.com/HaMaMi-1/KnightScope", ACCENT),
        ("🌐", "knightscope-classic.onrender.com", GREEN),
    ]):
        add_label(s, f"{icon}  {txt}",
                  Inches(0.7), Inches(4.45 + i * 0.55), Inches(9), Inches(0.45),
                  font_size=Pt(14), color=col)

    # Bottom stripe
    bot = s.shapes.add_shape(1, Inches(0), Inches(7.38), W, Inches(0.12))
    bot.fill.solid(); bot.fill.fore_color.rgb = GOLD; bot.line.fill.background()


# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 2 — Problem Statement
# ═══════════════════════════════════════════════════════════════════════════════
def slide_02():
    s = prs.slides.add_slide(BLANK_LAYOUT)
    add_bg(s)
    slide_header(s, "Problem Statement")

    bullets = [
        "♟  Chess is a canonical AI problem: ~10⁴⁴ possible states, ~35 avg branching factor",
        "🔍  Challenge: Select the best move from exponentially growing search spaces",
        "🤖  Application: Intelligent chess position analyzer with classical AI",
        "⚠   Not a game-playing agent — a position analysis and recommendation tool",
    ]
    bullet_box(s, bullets,
               Inches(0.5), Inches(1.05), Inches(12.33), Inches(5.9),
               font_size=Pt(17))

    # Stat callouts
    for i, (val, lbl, col) in enumerate([
        ("10⁴⁴", "possible states", ACCENT),
        ("~35", "avg branching factor", GOLD),
        ("4", "AI algorithms implemented", GREEN),
    ]):
        cx = Inches(0.9 + i * 4.1)
        add_rect(s, cx, Inches(5.5), Inches(3.6), Inches(1.4),
                 fill=RGBColor(0x0a, 0x20, 0x36), border=col, border_width=Pt(2))
        add_label(s, val, cx, Inches(5.5), Inches(3.6), Inches(0.75),
                  font_size=Pt(28), bold=True, color=col, align=PP_ALIGN.CENTER)
        add_label(s, lbl, cx, Inches(6.25), Inches(3.6), Inches(0.5),
                  font_size=Pt(13), color=LIGHT, align=PP_ALIGN.CENTER)


# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 3 — Problem Formulation
# ═══════════════════════════════════════════════════════════════════════════════
def slide_03():
    s = prs.slides.add_slide(BLANK_LAYOUT)
    add_bg(s)
    slide_header(s, "Problem Formulation")

    left_items = [
        ("Initial State",     "Any legal chess position (FEN string)"),
        ("Goal State",        "Position with highest heuristic evaluation h(s)"),
        ("State Space",       "All reachable positions via legal moves"),
        ("Actions",           "Set of all legal moves from current position"),
    ]
    right_items = [
        ("Transition Model",  "chess.js move generation + application"),
        ("Constraints",       "Only legal moves per FIDE chess rules"),
        ("Heuristic h(s)",    "material + PST + mobility + king_safety"),
    ]

    card_w = Inches(6.0)
    card_h = Inches(5.6)

    for col_i, items in enumerate([left_items, right_items]):
        cx = Inches(0.4 + col_i * 6.5)
        add_rect(s, cx, Inches(1.0), card_w, card_h)
        y = Inches(1.1)
        for term, desc in items:
            add_label(s, term, cx + Inches(0.15), y, card_w - Inches(0.3), Inches(0.38),
                      font_size=Pt(14), bold=True, color=ACCENT)
            y += Inches(0.37)
            add_label(s, desc, cx + Inches(0.15), y, card_w - Inches(0.3), Inches(0.42),
                      font_size=Pt(13), color=LIGHT)
            y += Inches(0.47)
            # divider
            div = s.shapes.add_shape(1, cx + Inches(0.1), y - Inches(0.06),
                                     card_w - Inches(0.2), Inches(0.02))
            div.fill.solid(); div.fill.fore_color.rgb = BORDER
            div.line.fill.background()

    # Heuristic formula box
    add_rect(s, Inches(0.4), Inches(6.7), Inches(12.4), Inches(0.65),
             fill=RGBColor(0x0a, 0x20, 0x36), border=GOLD, border_width=Pt(2))
    add_label(s,
              "h(s)  =  w₁·material  +  w₂·PST  +  w₃·mobility  +  w₄·king_safety",
              Inches(0.6), Inches(6.72), Inches(12), Inches(0.55),
              font_size=Pt(16), bold=True, color=GOLD, align=PP_ALIGN.CENTER)


# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 4 — System Architecture
# ═══════════════════════════════════════════════════════════════════════════════
def slide_04():
    s = prs.slides.add_slide(BLANK_LAYOUT)
    add_bg(s)
    slide_header(s, "System Architecture")

    components = [
        ("👤 User", "Browser interaction\nClick-to-move UI", ACCENT),
        ("🖥 HTML/CSS/JS\nInterface", "Board rendering\nMove highlighting\nResult display", GOLD),
        ("🧠 AI Engine", "4 algorithms\nMinimax · Alpha-Beta\nGreedy · IDS", GREEN),
        ("♟ chess.js", "Legal move generation\nFEN parsing\nGame state mgmt", ACCENT),
        ("📊 Evaluation\nFunction", "Material · PST\nMobility · King safety\nCenter · Pawns", GOLD),
    ]

    n = len(components)
    box_w = Inches(2.2)
    box_h = Inches(2.6)
    gap   = Inches(0.35)
    total_w = n * box_w + (n - 1) * gap
    start_x = (W - total_w) / 2

    for i, (title, desc, col) in enumerate(components):
        bx = start_x + i * (box_w + gap)
        by = Inches(1.95)
        add_rect(s, bx, by, box_w, box_h,
                 fill=RGBColor(0x0d, 0x1f, 0x38), border=col, border_width=Pt(2))
        add_label(s, title, bx + Inches(0.1), by + Inches(0.15),
                  box_w - Inches(0.2), Inches(0.75),
                  font_size=Pt(13.5), bold=True, color=col, align=PP_ALIGN.CENTER)
        add_label(s, desc, bx + Inches(0.1), by + Inches(0.9),
                  box_w - Inches(0.2), Inches(1.5),
                  font_size=Pt(11.5), color=LIGHT, align=PP_ALIGN.CENTER)

        # Arrow between boxes
        if i < n - 1:
            ax = bx + box_w + Inches(0.05)
            ay = by + box_h / 2 - Inches(0.12)
            add_label(s, "→", ax, ay, gap, Inches(0.3),
                      font_size=Pt(20), bold=True, color=BORDER, align=PP_ALIGN.CENTER)

    # Bottom description
    add_rect(s, Inches(0.5), Inches(5.0), Inches(12.33), Inches(2.1),
             fill=RGBColor(0x0a, 0x1a, 0x2f))
    desc_lines = [
        "• Static HTML deployment on Render — no backend required",
        "• chess.js (CDN) handles all legal move generation and FEN parsing",
        "• All 4 AI algorithms implemented in pure JavaScript (~500 lines)",
        "• Evaluation function: material + piece-square tables + mobility + king safety + center control + pawn structure",
    ]
    y = Inches(5.08)
    for line in desc_lines:
        add_label(s, line, Inches(0.75), y, Inches(11.8), Inches(0.42),
                  font_size=Pt(13.5), color=LIGHT)
        y += Inches(0.46)


# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 5 — AI Algorithms Overview
# ═══════════════════════════════════════════════════════════════════════════════
def slide_05():
    s = prs.slides.add_slide(BLANK_LAYOUT)
    add_bg(s)
    slide_header(s, "AI Algorithms Implemented")

    algos = [
        ("01", "Minimax",           "Full adversarial game tree\nComplete & optimal\nTime: O(bᵈ)  Space: O(bd)",               ACCENT),
        ("02", "Alpha-Beta\nPruning","Pruned minimax search\nIdentical result, fewer nodes\nBest: O(b^(d/2))  Worst: O(bᵈ)", GOLD),
        ("03", "Greedy\nBest-First", "1-ply heuristic evaluation\nFastest: O(b)\nMyopic — horizon effect",                   GREEN),
        ("04", "Iterative\nDeepening","Progressive depth α-β\nAnytime algorithm\nTime-limited: O(bᵈ)",                     RGBColor(0xc0, 0x84, 0xfc)),
    ]

    box_w = Inches(5.9)
    box_h = Inches(2.5)

    positions = [
        (Inches(0.4), Inches(1.05)),
        (Inches(6.9), Inches(1.05)),
        (Inches(0.4), Inches(4.0)),
        (Inches(6.9), Inches(4.0)),
    ]

    for (bx, by), (num, title, desc, col) in zip(positions, algos):
        add_rect(s, bx, by, box_w, box_h,
                 fill=RGBColor(0x0d, 0x1f, 0x38), border=col, border_width=Pt(2.5))
        # Number badge
        badge = s.shapes.add_shape(1, bx + Inches(0.18), by + Inches(0.18),
                                   Inches(0.52), Inches(0.52))
        badge.fill.solid(); badge.fill.fore_color.rgb = col; badge.line.fill.background()
        add_label(s, num, bx + Inches(0.18), by + Inches(0.14),
                  Inches(0.52), Inches(0.42),
                  font_size=Pt(13), bold=True, color=BG, align=PP_ALIGN.CENTER)
        # Title
        add_label(s, title, bx + Inches(0.85), by + Inches(0.14),
                  box_w - Inches(1.1), Inches(0.72),
                  font_size=Pt(19), bold=True, color=col)
        # Desc
        add_label(s, desc, bx + Inches(0.18), by + Inches(0.95),
                  box_w - Inches(0.4), Inches(1.4),
                  font_size=Pt(13.5), color=LIGHT)


# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 6 — Minimax Algorithm
# ═══════════════════════════════════════════════════════════════════════════════
def slide_06():
    s = prs.slides.add_slide(BLANK_LAYOUT)
    add_bg(s)
    slide_header(s, "Minimax Search")

    # Pseudocode card
    code = (
        "function minimax(node, depth, isMaximizing):\n"
        "    if depth == 0 or is_terminal(node):\n"
        "        return evaluate(node)\n"
        "    if isMaximizing:\n"
        "        best = -∞\n"
        "        for child in generate_moves(node):\n"
        "            best = max(best, minimax(child, depth-1, False))\n"
        "        return best\n"
        "    else:  # minimizing\n"
        "        best = +∞\n"
        "        for child in generate_moves(node):\n"
        "            best = min(best, minimax(child, depth-1, True))\n"
        "        return best"
    )
    add_rect(s, Inches(0.4), Inches(1.05), Inches(6.6), Inches(4.5),
             fill=RGBColor(0x07, 0x11, 0x1f))
    add_label(s, code, Inches(0.6), Inches(1.1), Inches(6.3), Inches(4.4),
              font_size=Pt(11.5), color=RGBColor(0x7d, 0xd3, 0xfc))

    # Properties card
    props = [
        ("Complete",   "Yes — always finds a solution if one exists"),
        ("Optimal",    "Yes — with perfect evaluation function"),
        ("Time",       "O(bᵈ)  where b=branching factor, d=depth"),
        ("Space",      "O(bd)  — linear in depth"),
        ("Limitation", "b=35, d=4 → 35⁴ ≈ 1.5M nodes"),
    ]
    add_rect(s, Inches(7.2), Inches(1.05), Inches(5.7), Inches(2.9))
    y = Inches(1.12)
    for term, val in props:
        add_label(s, term + ":", Inches(7.4), y, Inches(1.6), Inches(0.42),
                  font_size=Pt(12.5), bold=True, color=ACCENT)
        add_label(s, val, Inches(9.1), y, Inches(3.6), Inches(0.42),
                  font_size=Pt(12.5), color=LIGHT)
        y += Inches(0.5)

    # Tree diagram
    add_rect(s, Inches(7.2), Inches(4.1), Inches(5.7), Inches(2.5),
             fill=RGBColor(0x07, 0x11, 0x1f))
    tree_lines = [
        ("             MAX level (White to move)", ACCENT),
        ("        ┌──────────┼──────────┐", LIGHT),
        ("       MIN        MIN        MIN   (Black to move)", GOLD),
        ("      / \\        / \\        / \\", LIGHT),
        ("    MAX MAX    MAX MAX    MAX MAX  (White)", ACCENT),
        ("    ↓   ↓      ↓   ↓      ↓   ↓", LIGHT),
        ("  leaf leaf  leaf leaf  leaf leaf  h(s) evaluated", RGBColor(0x86, 0xef, 0xac)),
    ]
    y = Inches(4.18)
    for line, col in tree_lines:
        add_label(s, line, Inches(7.3), y, Inches(5.5), Inches(0.32),
                  font_size=Pt(10.5), color=col)
        y += Inches(0.32)

    # Properties bottom bar
    add_rect(s, Inches(0.4), Inches(5.65), Inches(6.6), Inches(1.65),
             fill=RGBColor(0x0a, 0x1a, 0x2f))
    add_label(s, "Key Properties",
              Inches(0.6), Inches(5.7), Inches(6.2), Inches(0.4),
              font_size=Pt(13), bold=True, color=GOLD)
    add_label(s, "• Complete & optimal with correct evaluation function\n"
                 "• Explores ALL nodes at depth d — becomes impractical for d>4\n"
                 "• Baseline against which Alpha-Beta is validated",
              Inches(0.6), Inches(6.1), Inches(6.2), Inches(1.1),
              font_size=Pt(12.5), color=LIGHT)


# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 7 — Alpha-Beta Pruning
# ═══════════════════════════════════════════════════════════════════════════════
def slide_07():
    s = prs.slides.add_slide(BLANK_LAYOUT)
    add_bg(s)
    slide_header(s, "Alpha-Beta Pruning")

    # Key insight callout
    add_rect(s, Inches(0.4), Inches(1.05), Inches(12.33), Inches(0.75),
             fill=RGBColor(0x0a, 0x20, 0x1a), border=GREEN, border_width=Pt(2))
    add_label(s,
              "✦  Key Insight: Prune branches where α ≥ β — produces IDENTICAL result to Minimax",
              Inches(0.65), Inches(1.1), Inches(11.9), Inches(0.6),
              font_size=Pt(16), bold=True, color=GREEN, align=PP_ALIGN.CENTER)

    # Pseudocode
    code = (
        "function alphabeta(node, depth, α, β, isMax):\n"
        "    if depth == 0 or is_terminal(node): return evaluate(node)\n"
        "    if isMax:\n"
        "        v = -∞\n"
        "        for child in moves(node):\n"
        "            v = max(v, alphabeta(child, depth-1, α, β, False))\n"
        "            α = max(α, v)\n"
        "            if α >= β: break  # ✂ PRUNE\n"
        "        return v\n"
        "    else:\n"
        "        v = +∞\n"
        "        for child in moves(node):\n"
        "            v = min(v, alphabeta(child, depth-1, α, β, True))\n"
        "            β = min(β, v)\n"
        "            if α >= β: break  # ✂ PRUNE\n"
        "        return v"
    )
    add_rect(s, Inches(0.4), Inches(1.9), Inches(6.5), Inches(5.2),
             fill=RGBColor(0x07, 0x11, 0x1f))
    add_label(s, code, Inches(0.6), Inches(1.95), Inches(6.2), Inches(5.1),
              font_size=Pt(11.5), color=RGBColor(0x7d, 0xd3, 0xfc))

    # Complexity & stats cards
    stats = [
        ("Best Case",    "O(b^(d/2))",   "With perfect move ordering", GREEN),
        ("Worst Case",   "O(bᵈ)",        "With reverse move ordering",  RED),
        ("Practical",    "O(b^(3d/4))",  "Random move ordering",       GOLD),
        ("Node Reduction", "95%+",       "At depth 3 in our experiments", ACCENT),
    ]
    bw = Inches(2.8)
    bh = Inches(1.15)
    for i, (title, val, sub, col) in enumerate(stats):
        bx = Inches(7.15) + (i % 2) * (bw + Inches(0.15))
        by = Inches(1.9)  + (i // 2) * (bh + Inches(0.15))
        add_rect(s, bx, by, bw, bh,
                 fill=RGBColor(0x0d, 0x1f, 0x38), border=col, border_width=Pt(2))
        add_label(s, title, bx + Inches(0.12), by + Inches(0.08),
                  bw - Inches(0.2), Inches(0.35),
                  font_size=Pt(12), bold=True, color=col)
        add_label(s, val, bx + Inches(0.12), by + Inches(0.4),
                  bw - Inches(0.2), Inches(0.4),
                  font_size=Pt(18), bold=True, color=WHITE)
        add_label(s, sub, bx + Inches(0.12), by + Inches(0.78),
                  bw - Inches(0.2), Inches(0.3),
                  font_size=Pt(10.5), color=LIGHT)

    # Formula
    add_rect(s, Inches(7.15), Inches(4.5), Inches(5.75), Inches(0.75),
             fill=RGBColor(0x0a, 0x20, 0x36), border=GOLD, border_width=Pt(2))
    add_label(s, "NR  =  1  −  (nodes_AB / nodes_MM)",
              Inches(7.3), Inches(4.57), Inches(5.4), Inches(0.55),
              font_size=Pt(16), bold=True, color=GOLD, align=PP_ALIGN.CENTER)

    add_rect(s, Inches(7.15), Inches(5.4), Inches(5.75), Inches(1.7),
             fill=RGBColor(0x07, 0x11, 0x1f))
    add_label(s,
              "• Guarantees same minimax score\n"
              "• α = best already found for MAX\n"
              "• β = best already found for MIN\n"
              "• Prune when α ≥ β (no better move can exist)",
              Inches(7.3), Inches(5.47), Inches(5.4), Inches(1.55),
              font_size=Pt(13), color=LIGHT)


# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 8 — Greedy & Iterative Deepening
# ═══════════════════════════════════════════════════════════════════════════════
def slide_08():
    s = prs.slides.add_slide(BLANK_LAYOUT)
    add_bg(s)
    slide_header(s, "Greedy Best-First & Iterative Deepening")

    half_w = Inches(6.0)

    # --- GREEDY (left) ---
    add_rect(s, Inches(0.4), Inches(1.05), half_w, Inches(6.0),
             fill=RGBColor(0x0d, 0x1f, 0x38), border=RED, border_width=Pt(2))
    add_label(s, "🔴  Greedy Best-First Search",
              Inches(0.65), Inches(1.12), half_w - Inches(0.4), Inches(0.5),
              font_size=Pt(18), bold=True, color=RED)

    greedy_items = [
        ("Algorithm",    "1-ply evaluation only — no look-ahead"),
        ("Complexity",   "O(b)  — single ply, all moves evaluated"),
        ("Speed",        "Extremely fast: ~0.01s per position"),
        ("Weakness",     "Horizon effect — cannot see 2+ moves ahead"),
        ("Result",       "Diverges from adversarial in 8/10 positions"),
    ]
    y = Inches(1.72)
    for term, val in greedy_items:
        add_label(s, term + ":", Inches(0.65), y, Inches(1.65), Inches(0.4),
                  font_size=Pt(12.5), bold=True, color=RED)
        add_label(s, val, Inches(2.4), y, Inches(3.75), Inches(0.4),
                  font_size=Pt(12.5), color=LIGHT)
        y += Inches(0.5)

    code_g = (
        "function greedy(position):\n"
        "    best_move = None\n"
        "    best_score = -∞\n"
        "    for move in legal_moves(position):\n"
        "        score = evaluate(apply(position, move))\n"
        "        if score > best_score:\n"
        "            best_score = score\n"
        "            best_move = move\n"
        "    return best_move"
    )
    add_rect(s, Inches(0.6), Inches(4.4), half_w - Inches(0.4), Inches(2.4),
             fill=RGBColor(0x07, 0x11, 0x1f))
    add_label(s, code_g, Inches(0.75), Inches(4.45), half_w - Inches(0.6), Inches(2.3),
              font_size=Pt(11), color=RGBColor(0x7d, 0xd3, 0xfc))

    # --- IDS (right) ---
    add_rect(s, Inches(6.9), Inches(1.05), half_w + Inches(0.43), Inches(6.0),
             fill=RGBColor(0x0d, 0x1f, 0x38), border=GREEN, border_width=Pt(2))
    add_label(s, "🟢  Iterative Deepening Search",
              Inches(7.15), Inches(1.12), half_w, Inches(0.5),
              font_size=Pt(18), bold=True, color=GREEN)

    ids_items = [
        ("Algorithm",   "depth 1 → 2 → 3 → … → d (time-limited)"),
        ("Complexity",  "O(bᵈ)  — same asymptotic as Minimax"),
        ("Benefit",     "Anytime: always has a valid result"),
        ("Move order",  "Earlier depths guide move ordering"),
        ("Time limit",  "Configurable: 0.2s / 0.5s / 1.0s / 2.0s"),
    ]
    y = Inches(1.72)
    for term, val in ids_items:
        add_label(s, term + ":", Inches(7.15), y, Inches(1.75), Inches(0.4),
                  font_size=Pt(12.5), bold=True, color=GREEN)
        add_label(s, val, Inches(9.0), y, Inches(4.1), Inches(0.4),
                  font_size=Pt(12.5), color=LIGHT)
        y += Inches(0.5)

    code_i = (
        "function IDS(position, time_limit):\n"
        "    best = None\n"
        "    for depth in 1, 2, 3, ...:\n"
        "        if elapsed() > time_limit: break\n"
        "        result = alphabeta(position, depth, -∞, +∞)\n"
        "        best = result  # save anytime result\n"
        "    return best  # best depth reached in time"
    )
    add_rect(s, Inches(7.1), Inches(4.4), half_w + Inches(0.23), Inches(2.4),
             fill=RGBColor(0x07, 0x11, 0x1f))
    add_label(s, code_i, Inches(7.25), Inches(4.45), half_w + Inches(0.05), Inches(2.3),
              font_size=Pt(11), color=RGBColor(0x7d, 0xd3, 0xfc))


# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 9 — Evaluation Function
# ═══════════════════════════════════════════════════════════════════════════════
def slide_09():
    s = prs.slides.add_slide(BLANK_LAYOUT)
    add_bg(s)
    slide_header(s, "Handcrafted Evaluation Function")

    # Formula
    add_rect(s, Inches(0.4), Inches(1.05), Inches(12.33), Inches(0.65),
             fill=RGBColor(0x0a, 0x20, 0x36), border=GOLD, border_width=Pt(2))
    add_label(s,
              "h(s)  =  w₁·material  +  w₂·PST  +  w₃·mobility  +  w₄·king_safety  +  w₅·center  +  w₆·pawn_struct",
              Inches(0.6), Inches(1.1), Inches(11.9), Inches(0.55),
              font_size=Pt(14.5), bold=True, color=GOLD, align=PP_ALIGN.CENTER)

    headers = ["Component", "Description", "Values / Details", "Weight"]
    rows = [
        ["Material",      "Piece count × value",         "P=100  N=320  B=330  R=500  Q=900 (centipawns)", "High"],
        ["PST",           "Piece-square positional bonus", "8×8 table per piece type — rewards centre, mobility",  "Medium"],
        ["Mobility",      "Legal move count differential", "Score ∝ (White moves − Black moves)",               "Low"],
        ["King Safety",   "Pawn shield protection",       "Bonus for pawns in front of castled king",           "Medium"],
        ["Center Control","d4,e4,d5,e5 occupancy",        "Bonus for controlling the 4 central squares",        "Low"],
        ["Pawn Structure","Structural penalties",         "Doubled pawns: −20cp  |  Isolated pawns: −15cp",    "Low"],
    ]

    weight_colors = {
        "High":   GREEN,
        "Medium": GOLD,
        "Low":    ACCENT,
    }

    tbl = slide.shapes if False else None  # placeholder

    # Manual table drawing (more control over colours)
    col_ws = [Inches(2.0), Inches(2.4), Inches(5.73), Inches(1.6)]
    headers_list = headers
    row_h = Inches(0.72)
    tbl_t = Inches(1.82)
    tbl_l = Inches(0.4)

    # Header
    x = tbl_l
    add_rect(s, tbl_l, tbl_t, Inches(11.73), row_h, fill=ACCENT, border=ACCENT)
    for ci, (hdr, cw) in enumerate(zip(headers_list, col_ws)):
        add_label(s, hdr, x + Inches(0.08), tbl_t + Inches(0.17),
                  cw - Inches(0.1), row_h - Inches(0.1),
                  font_size=Pt(13.5), bold=True, color=BG, align=PP_ALIGN.CENTER)
        x += cw

    # Data rows
    for ri, row in enumerate(rows):
        ry = tbl_t + (ri + 1) * row_h
        rbg = RGBColor(0x12, 0x26, 0x3d) if ri % 2 == 0 else DARKCARD
        add_rect(s, tbl_l, ry, Inches(11.73), row_h, fill=rbg, border=BORDER)
        x = tbl_l
        for ci, (cell, cw) in enumerate(zip(row, col_ws)):
            col = WHITE
            if ci == 3:  # weight col
                col = weight_colors.get(cell, WHITE)
            add_label(s, cell, x + Inches(0.08), ry + Inches(0.17),
                      cw - Inches(0.1), row_h - Inches(0.1),
                      font_size=Pt(11.5), color=col,
                      align=PP_ALIGN.CENTER if ci in (0, 3) else PP_ALIGN.LEFT)
            x += cw

    # Bottom note
    add_label(s, "✦  Positive score = White advantage  |  Negative = Black advantage  |  ±20,000cp = Checkmate",
              Inches(0.4), Inches(7.05), Inches(12.33), Inches(0.38),
              font_size=Pt(13), color=LIGHT, align=PP_ALIGN.CENTER)


# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 10 — Experiment 1: Minimax vs Alpha-Beta
# ═══════════════════════════════════════════════════════════════════════════════
def slide_10():
    s = prs.slides.add_slide(BLANK_LAYOUT)
    add_bg(s)
    slide_header(s, "Experiment 1: Minimax vs Alpha-Beta (Depth 3)")

    headers = ["Position", "MM Time (s)", "AB Time (s)", "Speedup", "Node Reduction"]
    rows = [
        ["Italian Game",    "21.87", "0.98", "22.3×", "95.5%"],
        ["Material+Rook",   " 8.35", "0.53", "15.8×", "93.6%"],
        ["Knight Fork",     "26.25", "0.27", "96.5×", "98.9%"],
        ["Mate-in-2",       "19.13", "0.58", "33.0×", "97.0%"],
    ]

    tbl_l = Inches(0.4); tbl_t = Inches(1.1)
    col_ws = [Inches(3.0), Inches(2.1), Inches(2.1), Inches(2.1), Inches(2.4)]
    row_h  = Inches(0.75)

    add_rect(s, tbl_l, tbl_t, sum(col_ws), row_h, fill=ACCENT, border=ACCENT)
    x = tbl_l
    for hdr, cw in zip(headers, col_ws):
        add_label(s, hdr, x + Inches(0.08), tbl_t + Inches(0.18),
                  cw - Inches(0.1), row_h - Inches(0.15),
                  font_size=Pt(13.5), bold=True, color=BG, align=PP_ALIGN.CENTER)
        x += cw

    for ri, row in enumerate(rows):
        ry = tbl_t + (ri + 1) * row_h
        rbg = RGBColor(0x12, 0x26, 0x3d) if ri % 2 == 0 else DARKCARD
        add_rect(s, tbl_l, ry, sum(col_ws), row_h, fill=rbg, border=BORDER)
        x = tbl_l
        for ci, (cell, cw) in enumerate(zip(row, col_ws)):
            col = WHITE
            if ci == 3: col = GOLD   # speedup
            if ci == 4: col = GREEN  # reduction
            add_label(s, cell, x + Inches(0.08), ry + Inches(0.2),
                      cw - Inches(0.1), row_h - Inches(0.15),
                      font_size=Pt(13), color=col, align=PP_ALIGN.CENTER)
            x += cw

    # Key finding
    add_rect(s, Inches(0.4), Inches(4.2), Inches(11.73), Inches(0.8),
             fill=RGBColor(0x05, 0x25, 0x1a), border=GREEN, border_width=Pt(2.5))
    add_label(s,
              "✅  Alpha-Beta ALWAYS produces the IDENTICAL minimax score",
              Inches(0.65), Inches(4.28), Inches(11.2), Inches(0.6),
              font_size=Pt(18), bold=True, color=GREEN, align=PP_ALIGN.CENTER)

    # Visual bars (approximate)
    bar_data = [
        ("Italian Game",  21.87, 0.98),
        ("Material+Rook",  8.35, 0.53),
        ("Knight Fork",   26.25, 0.27),
        ("Mate-in-2",     19.13, 0.58),
    ]
    max_mm = 26.25
    bar_area_l = Inches(0.4)
    bar_area_t = Inches(5.15)
    bar_area_w = Inches(11.73)
    bar_area_h = Inches(2.1)
    add_rect(s, bar_area_l, bar_area_t, bar_area_w, bar_area_h,
             fill=RGBColor(0x07, 0x11, 0x1f))
    add_label(s, "Time Comparison (seconds at depth 3)  ■ Minimax  ■ Alpha-Beta",
              bar_area_l + Inches(0.1), bar_area_t + Inches(0.05),
              bar_area_w - Inches(0.2), Inches(0.35),
              font_size=Pt(12), color=LIGHT, align=PP_ALIGN.CENTER)

    for i, (name, mm, ab) in enumerate(bar_data):
        bx = bar_area_l + Inches(0.3) + i * Inches(2.85)
        # MM bar
        mm_h = Inches(1.1) * (mm / max_mm)
        mmy  = bar_area_t + Inches(1.9) - mm_h
        bar = s.shapes.add_shape(1, bx, mmy, Inches(0.9), mm_h)
        bar.fill.solid(); bar.fill.fore_color.rgb = RGBColor(0xef, 0x44, 0x44)
        bar.line.fill.background()
        # AB bar
        ab_h = max(Inches(0.08), Inches(1.1) * (ab / max_mm))
        aby  = bar_area_t + Inches(1.9) - ab_h
        bar2 = s.shapes.add_shape(1, bx + Inches(1.0), aby, Inches(0.9), ab_h)
        bar2.fill.solid(); bar2.fill.fore_color.rgb = GREEN
        bar2.line.fill.background()
        # Label
        add_label(s, name, bx - Inches(0.15), bar_area_t + Inches(1.95),
                  Inches(2.5), Inches(0.3), font_size=Pt(10), color=LIGHT)


# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 11 — Experiment 2: Depth Scaling
# ═══════════════════════════════════════════════════════════════════════════════
def slide_11():
    s = prs.slides.add_slide(BLANK_LAYOUT)
    add_bg(s)
    slide_header(s, "Experiment 2: Search Depth Scaling (Alpha-Beta)")

    headers = ["Depth", "Avg Time (s)", "Avg Nodes", "Complexity", "Growth Factor"]
    rows = [
        ["1", "0.011",  "36",    "O(b)",  "—"],
        ["2", "0.077",  "174",   "O(b²)", "4.8×"],
        ["3", "0.868",  "1,696", "O(b³)", "9.7×"],
        ["4", "5.980",  "11,242","O(b⁴)", "6.6×"],
    ]

    tbl_l = Inches(0.4); tbl_t = Inches(1.05)
    col_ws = [Inches(1.5), Inches(2.2), Inches(2.4), Inches(2.4), Inches(2.4)]
    row_h  = Inches(0.78)

    add_rect(s, tbl_l, tbl_t, sum(col_ws), row_h, fill=ACCENT, border=ACCENT)
    x = tbl_l
    for hdr, cw in zip(headers, col_ws):
        add_label(s, hdr, x + Inches(0.08), tbl_t + Inches(0.2),
                  cw - Inches(0.1), row_h - Inches(0.15),
                  font_size=Pt(13.5), bold=True, color=BG, align=PP_ALIGN.CENTER)
        x += cw

    depth_colors = [GREEN, GOLD, ACCENT, RED]
    for ri, row in enumerate(rows):
        ry = tbl_t + (ri + 1) * row_h
        rbg = RGBColor(0x12, 0x26, 0x3d) if ri % 2 == 0 else DARKCARD
        add_rect(s, tbl_l, ry, sum(col_ws), row_h, fill=rbg, border=BORDER)
        x = tbl_l
        for ci, (cell, cw) in enumerate(zip(row, col_ws)):
            col = depth_colors[ri] if ci == 0 else WHITE
            if ci == 3: col = depth_colors[ri]
            if ci == 4 and cell != "—": col = GOLD
            add_label(s, cell, x + Inches(0.08), ry + Inches(0.22),
                      cw - Inches(0.1), row_h - Inches(0.15),
                      font_size=Pt(13.5), color=col, align=PP_ALIGN.CENTER)
            x += cw

    # Insight box
    add_rect(s, Inches(0.4), Inches(4.3), Inches(11.0), Inches(0.75),
             fill=RGBColor(0x0a, 0x20, 0x36), border=GOLD, border_width=Pt(2))
    add_label(s,
              "🔑  Depth 3→4 adds ~6-7× nodes  |  Effective branching factor ≈ 6.6 after pruning",
              Inches(0.6), Inches(4.38), Inches(10.6), Inches(0.55),
              font_size=Pt(15), bold=True, color=GOLD, align=PP_ALIGN.CENTER)

    # Visual growth chart
    add_rect(s, Inches(0.4), Inches(5.2), Inches(11.0), Inches(2.1),
             fill=RGBColor(0x07, 0x11, 0x1f))
    add_label(s, "Node Count Growth",
              Inches(0.6), Inches(5.25), Inches(10.6), Inches(0.35),
              font_size=Pt(12), color=LIGHT, align=PP_ALIGN.CENTER)

    node_counts = [36, 174, 1696, 11242]
    max_n = 11242
    bw2 = Inches(1.6)
    for i, (nc, col) in enumerate(zip(node_counts, depth_colors)):
        bh2 = max(Inches(0.08), Inches(1.4) * (nc / max_n))
        bx2 = Inches(1.5) + i * Inches(2.5)
        by2 = Inches(7.1) - bh2
        bar = s.shapes.add_shape(1, bx2, by2, bw2, bh2)
        bar.fill.solid(); bar.fill.fore_color.rgb = col; bar.line.fill.background()
        add_label(s, f"d={i+1}\n{nc:,}", bx2, by2 - Inches(0.45), bw2, Inches(0.4),
                  font_size=Pt(11), color=col, align=PP_ALIGN.CENTER)


# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 12 — Experiment 3: Greedy Failure
# ═══════════════════════════════════════════════════════════════════════════════
def slide_12():
    s = prs.slides.add_slide(BLANK_LAYOUT)
    add_bg(s)
    slide_header(s, "Experiment 3: Greedy vs Adversarial Search")

    # Main finding banner
    add_rect(s, Inches(0.4), Inches(1.05), Inches(12.33), Inches(0.65),
             fill=RGBColor(0x2d, 0x05, 0x05), border=RED, border_width=Pt(2))
    add_label(s,
              "⚠  Greedy diverged in 8/10 positions — demonstrates the horizon effect",
              Inches(0.65), Inches(1.12), Inches(11.9), Inches(0.52),
              font_size=Pt(16), bold=True, color=RED, align=PP_ALIGN.CENTER)

    # Case 1
    add_rect(s, Inches(0.4), Inches(1.85), Inches(5.9), Inches(3.2),
             fill=RGBColor(0x0d, 0x1f, 0x38), border=RED, border_width=Pt(1.5))
    add_label(s, "Case 1: Poisoned Pawn (pos_08)",
              Inches(0.65), Inches(1.92), Inches(5.5), Inches(0.45),
              font_size=Pt(14), bold=True, color=RED)
    for label, move, score, col in [
        ("Greedy:",      "Bxh7",  "+77 cp",   RED),
        ("Adversarial:", "Bb5",   "+168 cp",  GREEN),
        ("Difference:",  "91 cp", "91 cp gap", GOLD),
    ]:
        y_off = {"Greedy:": 2.47, "Adversarial:": 2.95, "Difference:": 3.43}[label]
        add_label(s, label, Inches(0.65), Inches(y_off), Inches(1.6), Inches(0.4),
                  font_size=Pt(13), bold=True, color=col)
        add_label(s, move, Inches(2.4), Inches(y_off), Inches(1.4), Inches(0.4),
                  font_size=Pt(13), bold=True, color=WHITE)
        add_label(s, score, Inches(3.9), Inches(y_off), Inches(1.9), Inches(0.4),
                  font_size=Pt(13), color=col)
    add_label(s, "Greedy takes a pawn immediately, missing the deeper positional strategy.",
              Inches(0.65), Inches(4.75), Inches(5.5), Inches(0.4),
              font_size=Pt(11.5), color=LIGHT)

    # Case 2
    add_rect(s, Inches(6.6), Inches(1.85), Inches(6.1), Inches(3.2),
             fill=RGBColor(0x0d, 0x1f, 0x38), border=GOLD, border_width=Pt(1.5))
    add_label(s, "Case 2: Italian Game (pos_01)",
              Inches(6.85), Inches(1.92), Inches(5.7), Inches(0.45),
              font_size=Pt(14), bold=True, color=GOLD)
    for label, move, score, col in [
        ("Greedy:",      "Nxe4",  "−132 cp",  RED),
        ("Adversarial:", "Bb4",   "−198 cp",  GREEN),
        ("Difference:",  "66 cp", "66 cp gap", GOLD),
    ]:
        y_off = {"Greedy:": 2.47, "Adversarial:": 2.95, "Difference:": 3.43}[label]
        add_label(s, label, Inches(6.85), Inches(y_off), Inches(1.6), Inches(0.4),
                  font_size=Pt(13), bold=True, color=col)
        add_label(s, move, Inches(8.6), Inches(y_off), Inches(1.4), Inches(0.4),
                  font_size=Pt(13), bold=True, color=WHITE)
        add_label(s, score, Inches(10.1), Inches(y_off), Inches(2.3), Inches(0.4),
                  font_size=Pt(13), color=col)
    add_label(s, "Greedy blunders a knight, unable to see the opponent's reply.",
              Inches(6.85), Inches(4.75), Inches(5.5), Inches(0.4),
              font_size=Pt(11.5), color=LIGHT)

    # Horizon effect explanation
    add_rect(s, Inches(0.4), Inches(5.3), Inches(12.33), Inches(1.9),
             fill=RGBColor(0x07, 0x11, 0x1f))
    add_label(s, "The Horizon Effect",
              Inches(0.65), Inches(5.37), Inches(12), Inches(0.42),
              font_size=Pt(15), bold=True, color=GOLD)
    add_label(s,
              "Greedy only sees 1 move ahead — it cannot anticipate the opponent's response.\n"
              "A \"good\" move for the current position may set up a devastating reply.\n"
              "Greedy agrees with adversarial only on immediate mate positions (pos_06, pos_07) — where there is only one legal best reply.",
              Inches(0.65), Inches(5.82), Inches(12), Inches(1.3),
              font_size=Pt(13), color=LIGHT)


# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 13 — Experiment 4: IDS
# ═══════════════════════════════════════════════════════════════════════════════
def slide_13():
    s = prs.slides.add_slide(BLANK_LAYOUT)
    add_bg(s)
    slide_header(s, "Experiment 4: Iterative Deepening Results")

    headers = ["Position", "0.2s limit", "0.5s limit", "1.0s limit", "2.0s limit"]
    rows = [
        ["Italian Game (pos_01)", "d=3", "d=3", "d=3", "d=4"],
        ["Endgame (pos_09)",      "d=5", "d=6", "d=6", "d=6"],
        ["Mate-in-2 (pos_06)",    "d=1", "d=1", "d=1", "d=1"],
    ]

    tbl_l = Inches(0.4); tbl_t = Inches(1.05)
    col_ws = [Inches(3.5), Inches(2.0), Inches(2.0), Inches(2.0), Inches(2.0)]
    row_h  = Inches(0.85)

    add_rect(s, tbl_l, tbl_t, sum(col_ws), row_h, fill=ACCENT, border=ACCENT)
    x = tbl_l
    for hdr, cw in zip(headers, col_ws):
        add_label(s, hdr, x + Inches(0.08), tbl_t + Inches(0.22),
                  cw - Inches(0.1), row_h - Inches(0.15),
                  font_size=Pt(14), bold=True, color=BG, align=PP_ALIGN.CENTER)
        x += cw

    for ri, row in enumerate(rows):
        ry = tbl_t + (ri + 1) * row_h
        rbg = RGBColor(0x12, 0x26, 0x3d) if ri % 2 == 0 else DARKCARD
        add_rect(s, tbl_l, ry, sum(col_ws), row_h, fill=rbg, border=BORDER)
        x = tbl_l
        for ci, (cell, cw) in enumerate(zip(row, col_ws)):
            col = WHITE if ci == 0 else GOLD
            align = PP_ALIGN.LEFT if ci == 0 else PP_ALIGN.CENTER
            add_label(s, cell, x + Inches(0.1), ry + Inches(0.25),
                      cw - Inches(0.1), row_h - Inches(0.15),
                      font_size=Pt(13.5), color=col, align=align)
            x += cw

    # Key insight
    add_rect(s, Inches(0.4), Inches(4.0), Inches(11.5), Inches(0.75),
             fill=RGBColor(0x0a, 0x20, 0x36), border=GOLD, border_width=Pt(2))
    add_label(s,
              "🔑  IDS provides anytime behavior — always has a valid result even if interrupted",
              Inches(0.6), Inches(4.08), Inches(11.1), Inches(0.55),
              font_size=Pt(15.5), bold=True, color=GOLD, align=PP_ALIGN.CENTER)

    # Observations
    obs = [
        ("Italian Game", "Complexity prevents reaching d=4 within 1s — depth limited by branching"),
        ("Endgame",      "Sparse position (few pieces) allows deeper search — d=6 within 0.5s"),
        ("Mate-in-2",    "Mate found at d=1 (Qxf7#) — no deeper search needed"),
    ]
    add_rect(s, Inches(0.4), Inches(4.9), Inches(12.33), Inches(2.4),
             fill=RGBColor(0x07, 0x11, 0x1f))
    add_label(s, "Position-by-Position Analysis",
              Inches(0.65), Inches(4.97), Inches(12), Inches(0.42),
              font_size=Pt(14), bold=True, color=ACCENT)
    y = Inches(5.45)
    for pos, note in obs:
        add_label(s, f"• {pos}:", Inches(0.65), y, Inches(2.4), Inches(0.42),
                  font_size=Pt(13), bold=True, color=ACCENT)
        add_label(s, note, Inches(3.1), y, Inches(9.4), Inches(0.42),
                  font_size=Pt(13), color=LIGHT)
        y += Inches(0.52)


# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 14 — Live Demo Screenshot 1: Interactive Board & Position Setup
# ═══════════════════════════════════════════════════════════════════════════════
def slide_14():
    s = prs.slides.add_slide(BLANK_LAYOUT)
    add_bg(s)
    slide_header(s, "Live Demo — Interactive Board & Position Setup")

    img_path = r"c:\Users\chait\Documents\Knight Scope\KnightScope_Final_Report\images\initial-position.png"
    if os.path.exists(img_path):
        # Frame
        add_rect(s, Inches(1.6), Inches(1.0), Inches(10.13), Inches(5.5),
                 fill=RGBColor(0x07, 0x11, 0x1f), border=ACCENT, border_width=Pt(2))
        s.shapes.add_picture(img_path, Inches(1.75), Inches(1.1), Inches(9.83), Inches(5.2))
    else:
        add_rect(s, Inches(0.6), Inches(1.05), Inches(12.1), Inches(5.65),
                 fill=RGBColor(0x07, 0x11, 0x1f), border=ACCENT, border_width=Pt(3))
        add_label(s, "📸", Inches(5.5), Inches(2.0), Inches(2), Inches(1.2),
                  font_size=Pt(60), color=ACCENT, align=PP_ALIGN.CENTER)
        add_label(s, "[SCREENSHOT: Starting position setup and interactive editor]",
                  Inches(1), Inches(3.3), Inches(11.1), Inches(0.55),
                  font_size=Pt(16), bold=True, color=LIGHT, align=PP_ALIGN.CENTER)

    add_label(s, "🌐 Live Application: knightscope-classic.onrender.com  ·  Source: github.com/HaMaMi-1/KnightScope",
              Inches(0.6), Inches(6.8), Inches(12.1), Inches(0.42),
              font_size=Pt(13), bold=True, color=ACCENT, align=PP_ALIGN.CENTER)


# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 15 — Live Demo Screenshot 2: Tactical Analysis (Depth 3)
# ═══════════════════════════════════════════════════════════════════════════════
def slide_15():
    s = prs.slides.add_slide(BLANK_LAYOUT)
    add_bg(s)
    slide_header(s, "Live Demo — Tactical Move Analysis (Depth 3)")

    img_path = r"c:\Users\chait\Documents\Knight Scope\KnightScope_Final_Report\images\tactical-depth3.png"
    if os.path.exists(img_path):
        add_rect(s, Inches(1.6), Inches(1.0), Inches(10.13), Inches(5.5),
                 fill=RGBColor(0x07, 0x11, 0x1f), border=GOLD, border_width=Pt(2))
        s.shapes.add_picture(img_path, Inches(1.75), Inches(1.1), Inches(9.83), Inches(5.2))
    else:
        add_rect(s, Inches(0.6), Inches(1.05), Inches(12.1), Inches(5.65),
                 fill=RGBColor(0x07, 0x11, 0x1f), border=GOLD, border_width=Pt(3))
        add_label(s, "📊", Inches(5.5), Inches(2.0), Inches(2), Inches(1.2),
                  font_size=Pt(60), color=GOLD, align=PP_ALIGN.CENTER)

    add_label(s, "Recommendation: Nxe5  ·  Nodes: 1,423  ·  Time: 0.161s  ·  Principal Variation computed via Alpha-Beta",
              Inches(0.6), Inches(6.8), Inches(12.1), Inches(0.42),
              font_size=Pt(13), bold=True, color=GOLD, align=PP_ALIGN.CENTER)


# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 15B — Live Demo Screenshot 3: Forced Checkmate Opportunity
# ═══════════════════════════════════════════════════════════════════════════════
def slide_15b():
    s = prs.slides.add_slide(BLANK_LAYOUT)
    add_bg(s)
    slide_header(s, "Live Demo — Forced Checkmate Detection (Mate-in-2)")

    img_path = r"c:\Users\chait\Documents\Knight Scope\KnightScope_Final_Report\images\forced-mate.png"
    if os.path.exists(img_path):
        add_rect(s, Inches(1.6), Inches(1.0), Inches(10.13), Inches(5.5),
                 fill=RGBColor(0x07, 0x11, 0x1f), border=GREEN, border_width=Pt(2))
        s.shapes.add_picture(img_path, Inches(1.75), Inches(1.1), Inches(9.83), Inches(5.2))
    else:
        add_rect(s, Inches(0.6), Inches(1.05), Inches(12.1), Inches(5.65),
                 fill=RGBColor(0x07, 0x11, 0x1f), border=GREEN, border_width=Pt(3))

    add_label(s, "Winning Move Found: Qxf7# (Checkmate)  ·  Evaluation: +20,000 cp  ·  Verified by all 4 algorithms",
              Inches(0.6), Inches(6.8), Inches(12.1), Inches(0.42),
              font_size=Pt(13), bold=True, color=GREEN, align=PP_ALIGN.CENTER)



# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 16 — Implementation Highlights
# ═══════════════════════════════════════════════════════════════════════════════
def slide_16():
    s = prs.slides.add_slide(BLANK_LAYOUT)
    add_bg(s)
    slide_header(s, "Implementation Highlights")

    items = [
        ("💻", "Language",       "JavaScript — browser-native, no server required"),
        ("♟", "Chess Rules",    "chess.js library (legal move generation, FEN parsing)"),
        ("🎨", "UI",             "Pure HTML5 + CSS3, no frameworks"),
        ("🚀", "Deployment",    "Static HTML on Render (from GitHub) — 100% serverless"),
        ("🧠", "AI Engine",     "4 algorithms — ~500 lines of JS AI engine code"),
        ("🖱", "Interactive",   "Click-to-move board with legal move highlighting"),
        ("⚡", "Real-time",     "Full analysis runs in browser — no server round-trips"),
    ]

    col_w = Inches(5.9)
    for i, (icon, title, desc) in enumerate(items):
        col = i % 2
        row = i // 2
        bx  = Inches(0.4) + col * Inches(6.5)
        by  = Inches(1.08) + row * Inches(1.33)
        add_rect(s, bx, by, col_w, Inches(1.2),
                 fill=RGBColor(0x0d, 0x1f, 0x38), border=ACCENT, border_width=Pt(1.5))
        add_label(s, icon, bx + Inches(0.1), by + Inches(0.25),
                  Inches(0.55), Inches(0.6),
                  font_size=Pt(22), color=ACCENT, align=PP_ALIGN.CENTER)
        add_label(s, title, bx + Inches(0.75), by + Inches(0.1),
                  col_w - Inches(1.0), Inches(0.42),
                  font_size=Pt(13.5), bold=True, color=ACCENT)
        add_label(s, desc, bx + Inches(0.75), by + Inches(0.52),
                  col_w - Inches(1.0), Inches(0.55),
                  font_size=Pt(13), color=LIGHT)

    # GitHub link at bottom
    add_label(s, "🔗  github.com/HaMaMi-1/KnightScope",
              Inches(0.4), Inches(7.05), Inches(12.33), Inches(0.38),
              font_size=Pt(14), color=ACCENT, align=PP_ALIGN.CENTER)


# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 17 — Limitations & Future Work
# ═══════════════════════════════════════════════════════════════════════════════
def slide_17():
    s = prs.slides.add_slide(BLANK_LAYOUT)
    add_bg(s)
    slide_header(s, "Limitations & Future Work")

    # Limitations
    lims = [
        "Handcrafted evaluation function does not reach grandmaster-level strength",
        "Exponential branching limits practical search depth to 4-5 plies",
        "No transposition table — identical positions may be re-evaluated multiple times",
        "No endgame tablebases — weak in K+P vs K and similar simple endings",
    ]
    bullet_box(s, lims, Inches(0.4), Inches(1.05), Inches(5.9), Inches(5.9),
               font_size=Pt(14), title="⚠  Current Limitations", title_color=RED)

    # Future work
    future = [
        "Monte Carlo Tree Search (MCTS) — probabilistic sampling",
        "Neural network evaluation (learned heuristic from GM games)",
        "Transposition tables & Zobrist hashing — avoid re-computation",
        "Opening book integration — book moves for first 10-15 moves",
        "Multi-threaded Web Workers for parallel α-β search",
    ]
    bullet_box(s, future, Inches(6.9), Inches(1.05), Inches(5.83), Inches(5.9),
               font_size=Pt(14), title="🚀  Future Work", title_color=GREEN)


# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 18 — Conclusion
# ═══════════════════════════════════════════════════════════════════════════════
def slide_18():
    s = prs.slides.add_slide(BLANK_LAYOUT)
    add_bg(s)

    # Top stripe
    top = s.shapes.add_shape(1, Inches(0), Inches(0), W, Inches(0.1))
    top.fill.solid(); top.fill.fore_color.rgb = ACCENT; top.line.fill.background()

    # Title
    add_label(s, "Conclusion", Inches(0.5), Inches(0.15), Inches(10), Inches(0.7),
              font_size=Pt(32), bold=True, color=WHITE)

    # Key findings
    findings = [
        ("✅", "Implemented 4 classical AI algorithms in JavaScript", GREEN),
        ("✅", "Alpha-Beta produces IDENTICAL minimax scores with 95%+ node reduction at depth 3", GREEN),
        ("🔍", "Greedy demonstrates the horizon effect in 8/10 test positions", GOLD),
        ("⏱", "IDS provides anytime search behavior — always has a valid result", ACCENT),
        ("🌐", "Full interactive web application deployed at knightscope-classic.onrender.com", ACCENT),
    ]

    y = Inches(1.05)
    for icon, text, col in findings:
        add_rect(s, Inches(0.4), y, Inches(12.33), Inches(0.82),
                 fill=RGBColor(0x0d, 0x1f, 0x38), border=col, border_width=Pt(2))
        add_label(s, icon, Inches(0.55), y + Inches(0.18),
                  Inches(0.55), Inches(0.5),
                  font_size=Pt(20), color=col, align=PP_ALIGN.CENTER)
        add_label(s, text, Inches(1.2), y + Inches(0.2),
                  Inches(11.3), Inches(0.52),
                  font_size=Pt(15), bold=True, color=WHITE)
        y += Inches(0.98)

    # Bottom footer
    add_rect(s, Inches(0), Inches(6.75), W, Inches(0.75),
             fill=RGBColor(0x07, 0x11, 0x1f), border=RGBColor(0x07, 0x11, 0x1f))

    # Three columns: GitHub | Demo | Team
    for i, (icon, txt, link_col) in enumerate([
        ("🔗", "github.com/HaMaMi-1/KnightScope",    ACCENT),
        ("🌐", "knightscope-classic.onrender.com",    GREEN),
        ("👥", "Team DEEP KNIGHTS  ·  2026",          GOLD),
    ]):
        cx = Inches(0.5 + i * 4.3)
        add_label(s, f"{icon}  {txt}", cx, Inches(6.82), Inches(4.0), Inches(0.55),
                  font_size=Pt(13), bold=True, color=link_col)

    # Gold bottom bar
    bot = s.shapes.add_shape(1, Inches(0), Inches(7.38), W, Inches(0.12))
    bot.fill.solid(); bot.fill.fore_color.rgb = GOLD; bot.line.fill.background()


# ═══════════════════════════════════════════════════════════════════════════════
# BUILD ALL SLIDES
# ═══════════════════════════════════════════════════════════════════════════════
print("Building KnightScope presentation...")
slide_01(); print("  Slide 1  — Title")
slide_02(); print("  Slide 2  — Problem Statement")
slide_03(); print("  Slide 3  — Problem Formulation")
slide_04(); print("  Slide 4  — System Architecture")
slide_05(); print("  Slide 5  — AI Algorithms Overview")
slide_06(); print("  Slide 6  — Minimax")
slide_07(); print("  Slide 7  — Alpha-Beta Pruning")
slide_08(); print("  Slide 8  — Greedy & IDS")
slide_09(); print("  Slide 9  — Evaluation Function")
slide_10(); print("  Slide 10 — Experiment 1")
slide_11(); print("  Slide 11 — Experiment 2")
slide_12(); print("  Slide 12 — Experiment 3")
slide_13(); print("  Slide 13 — Experiment 4")
slide_14(); print("  Slide 14 — Demo: Interactive Board Setup")
slide_15(); print("  Slide 15 — Demo: Tactical Analysis")
slide_15b(); print("  Slide 16 — Demo: Forced Checkmate")
slide_16(); print("  Slide 17 — Implementation")
slide_17(); print("  Slide 18 — Limitations & Future Work")
slide_18(); print("  Slide 19 — Conclusion")

OUT1 = r"c:\Users\chait\Documents\Knight Scope\KnightScope_Final_Presentation.pptx"
OUT2 = r"c:\Users\chait\Documents\Knight Scope\KnightScope_Presentation.pptx"
prs.save(OUT1)
prs.save(OUT2)
print(f"\n✅  Saved: {OUT1}")
print(f"✅  Saved: {OUT2}")
