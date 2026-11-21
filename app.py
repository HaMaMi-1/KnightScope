import time
import chess
import streamlit as st

st.set_page_config("KnightScope", "♞", layout="wide")
V={chess.PAWN:100,chess.KNIGHT:320,chess.BISHOP:330,chess.ROOK:500,chess.QUEEN:900,chess.KING:0}
GLYPHS={(chess.WHITE,chess.KING):"♔",(chess.WHITE,chess.QUEEN):"♕",(chess.WHITE,chess.ROOK):"♖",(chess.WHITE,chess.BISHOP):"♗",(chess.WHITE,chess.KNIGHT):"♘",(chess.WHITE,chess.PAWN):"♙",(chess.BLACK,chess.KING):"♚",(chess.BLACK,chess.QUEEN):"♛",(chess.BLACK,chess.ROOK):"♜",(chess.BLACK,chess.BISHOP):"♝",(chess.BLACK,chess.KNIGHT):"♞",(chess.BLACK,chess.PAWN):"♟"}
if "board" not in st.session_state: st.session_state.board=chess.Board()
if "selected" not in st.session_state: st.session_state.selected=None

def score(b):
 if b.is_checkmate(): return -20000 if b.turn else 20000
 if b.is_game_over(claim_draw=True): return 0
 return sum(v*(len(b.pieces(p,1))-len(b.pieces(p,0))) for p,v in V.items())
def order(b): return sorted(list(b.legal_moves),key=lambda m:(b.is_capture(m),b.gives_check(m)),reverse=True)
def ab(b,d,a,z,n):
 n[0]+=1
 if not d or b.is_game_over(claim_draw=True): return score(b),[]
 best=-1e9 if b.turn else 1e9;pv=[]
 for m in order(b):
  b.push(m);x,line=ab(b,d-1,a,z,n);b.pop()
  if (b.turn and x>best) or (not b.turn and x<best): best,pv=x,[m]+line
  if b.turn:a=max(a,best)
  else:z=min(z,best)
  if a>=z:break
 return best,pv
def sync_rights(b,wk,wq,bk,bq):
 rights=0
 if wk:rights|=chess.BB_H1
 if wq:rights|=chess.BB_A1
 if bk:rights|=chess.BB_H8
 if bq:rights|=chess.BB_A8
 b.castling_rights=rights

st.title("♞ KnightScope")
st.caption("Classical AI chess-position analysis")
st.info("Use the board editor to arrange any position. In Move mode, click a piece and then its destination. Add and Remove modes let you construct a custom position.")

side,editor,analysis=st.columns([1,2,1.2])
with side:
 st.subheader("Position controls")
 mode=st.radio("Editor mode",["Move piece","Add piece","Remove piece"])
 color=st.radio("Active colour",["White","Black"],horizontal=True)
 choices=list(GLYPHS.items())
 label={v:k for k,v in GLYPHS.items()}
 selected_glyph=st.selectbox("Piece to add",list(label),index=0)
 if st.button("Reset starting position",use_container_width=True):
  st.session_state.board=chess.Board();st.session_state.selected=None;st.rerun()
 if st.button("Clear board",use_container_width=True):
  st.session_state.board=chess.Board(None);st.session_state.selected=None;st.rerun()
 b=st.session_state.board
 b.turn=color=="White"
 st.subheader("Castling availability")
 wk=st.checkbox("White kingside",bool(b.castling_rights & chess.BB_H1))
 wq=st.checkbox("White queenside",bool(b.castling_rights & chess.BB_A1))
 bk=st.checkbox("Black kingside",bool(b.castling_rights & chess.BB_H8))
 bq=st.checkbox("Black queenside",bool(b.castling_rights & chess.BB_A8))
 sync_rights(b,wk,wq,bk,bq)

with editor:
 st.subheader("Interactive board")
 for rank in range(7,-1,-1):
  cols=st.columns(8,gap="small")
  for file in range(8):
   sq=chess.square(file,rank);piece=b.piece_at(sq)
   mark=" ●" if st.session_state.selected==sq else ""
   text=(GLYPHS[(piece.color,piece.piece_type)] if piece else "·")+mark
   if cols[file].button(text,key=f"sq{sq}",use_container_width=True):
    if mode=="Remove piece": b.remove_piece_at(sq)
    elif mode=="Add piece":
     c,p=label[selected_glyph];b.set_piece_at(sq,chess.Piece(p,c))
    elif st.session_state.selected is None:
     if piece: st.session_state.selected=sq
    else:
     source=st.session_state.selected
     moving=b.piece_at(source)
     if moving:
      b.remove_piece_at(source);b.set_piece_at(sq,moving)
     st.session_state.selected=None
    st.rerun()
 st.caption("Files a-h run left to right. Ranks 8-1 run top to bottom. A dot marks an empty square.")

with analysis:
 st.subheader("AI analysis")
 depth=st.slider("Search depth",1,3,2)
 st.write("Side to move:", "White" if b.turn else "Black")
 st.write("FEN")
 st.code(b.fen(),language=None)
 if not b.is_valid(): st.warning("This board is not a valid chess position. Arrange both kings before analysing.")
 if st.button("Run Alpha-Beta analysis",type="primary",disabled=not b.is_valid()):
  n=[0];started=time.perf_counter();value,line=ab(b.copy(),depth,-1e9,1e9,n);elapsed=time.perf_counter()-started
  st.success("Recommended move: "+(b.san(line[0]) if line else "No legal move"))
  x,y,z=st.columns(3);x.metric("Evaluation",f"{value:+d} cp");y.metric("Nodes",f"{n[0]:,}");z.metric("Time",f"{elapsed:.3f}s")
  q=b.copy();names=[]
  for m in line:names.append(q.san(m));q.push(m)
  st.code(" ".join(names),language=None)
