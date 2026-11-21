import time
import chess, chess.svg, streamlit as st
st.set_page_config("KnightScope","♞",layout="wide")
V={chess.PAWN:100,chess.KNIGHT:320,chess.BISHOP:330,chess.ROOK:500,chess.QUEEN:900,chess.KING:0}
def ev(b):
 if b.is_checkmate(): return -20000 if b.turn else 20000
 if b.is_game_over(claim_draw=True): return 0
 s=sum(v*len(b.pieces(p,chess.WHITE))-v*len(b.pieces(p,chess.BLACK)) for p,v in V.items())
 t=b.turn;b.turn=chess.WHITE;w=b.legal_moves.count();b.turn=chess.BLACK;k=b.legal_moves.count();b.turn=t
 return s+2*(w-k)
def moves(b): return sorted(list(b.legal_moves),key=lambda m:(b.is_capture(m),b.gives_check(m)),reverse=True)
def ab(b,d,a,z,n):
 n[0]+=1
 if not d or b.is_game_over(claim_draw=True): return ev(b),[]
 best=-1e9 if b.turn else 1e9;line=[]
 for m in moves(b):
  b.push(m);x,p=ab(b,d-1,a,z,n);b.pop()
  if (b.turn and x>best) or (not b.turn and x<best): best,line=x,[m]+p
  if b.turn:a=max(a,best)
  else:z=min(z,best)
  if a>=z:break
 return best,line
st.title("♞ KnightScope")
st.caption("Classical AI chess-position analysis using Alpha-Beta pruning")
st.info("Educational analyser. Results depend on the selected depth and handcrafted evaluation.")
depth=st.sidebar.slider("Search depth",1,3,2)
fen=st.text_input("FEN position",chess.STARTING_FEN)
try:b=chess.Board(fen)
except ValueError: st.error("Enter a valid FEN.");st.stop()
l,r=st.columns([1.1,1])
with l:st.image(chess.svg.board(b,size=560),use_container_width=True)
with r:
 st.write("Side to move:", "White" if b.turn else "Black")
 st.write("Legal moves:",b.legal_moves.count())
 if st.button("Run AI analysis",type="primary"):
  n=[0];t=time.perf_counter();score,line=ab(b.copy(),depth,-1e9,1e9,n);secs=time.perf_counter()-t
  st.success("Recommended move: "+(b.san(line[0]) if line else "No legal move"))
  x,y,z=st.columns(3);x.metric("Evaluation",f"{score:+d} cp");y.metric("Nodes",f"{n[0]:,}");z.metric("Time",f"{secs:.3f}s")
  q=b.copy();pv=[]
  for m in line:pv.append(q.san(m));q.push(m)
  st.code(" ".join(pv))
