const start="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",G={K:"♔",Q:"♕",R:"♖",B:"♗",N:"♘",P:"♙",k:"♚",q:"♛",r:"♜",b:"♝",n:"♞",p:"♟"};let board={},turn="w",castle="KQkq",selected=null,flipped=false;
function parse(f){let p=f.trim().split(/\s+/);if(!p[0])throw Error("Enter a FEN");board={};p[0].split("/").forEach((row,i)=>{let file=0;for(const ch of row){if(+ch)file+=+ch;else{board[String.fromCharCode(97+file)+(8-i)]=ch;file++}}});turn=p[1]||"w";castle=p[2]||"-";["wk","wq","bk","bq"].forEach((id,i)=>document.getElementById(id).checked=castle!=="-"&&castle.includes("KQkq"[i]));render()}
function fen(){let ranks=[];for(let r=8;r;--r){let s="",n=0;for(let f=0;f<8;f++){let x=board[String.fromCharCode(97+f)+r];if(x)s+=(n?n:"")+x,n=0;else n++}ranks.push(s+(n||""))}castle=(document.getElementById("wk").checked?"K":"")+(document.getElementById("wq").checked?"Q":"")+(document.getElementById("bk").checked?"k":"")+(document.getElementById("bq").checked?"q":"")||"-";return ranks.join("/")+" "+turn+" "+castle+" - 0 1"}
function mode(){return document.querySelector("input[name=mode]:checked").value}function active(){return document.querySelector("input[name=color]:checked").value}function render(){let el=document.getElementById("board");el.innerHTML="";let ranks=flipped?[1,2,3,4,5,6,7,8]:[8,7,6,5,4,3,2,1],files=flipped?["h","g","f","e","d","c","b","a"]:["a","b","c","d","e","f","g","h"];ranks.forEach((r,ri)=>files.forEach((f,fi)=>{let sq=f+r,b=document.createElement("button");b.className="sq "+((ri+fi)%2?"dark":"")+(selected===sq?" selected":"")+(board[sq]&&board[sq]===board[sq].toUpperCase()?" white-piece":" black-piece");b.textContent=G[board[sq]]||"";b.onclick=()=>click(sq);el.appendChild(b)}));document.getElementById("fen").value=fen();document.getElementById("turn").textContent="Side to move: "+(turn==="w"?"White":"Black")}
function click(sq){let m=mode();if(m==="remove")delete board[sq];else if(m==="add"){let p=document.getElementById("piece").value;board[sq]=active()==="w"?p.toUpperCase():p}else if(!selected&&board[sq])selected=sq;else if(selected){board[sq]=board[selected];delete board[selected];selected=null}render()}
document.getElementById("reset").onclick=()=>{selected=null;parse(start)};document.getElementById("clear").onclick=()=>{board={};selected=null;render()};document.getElementById("flip").onclick=()=>{flipped=!flipped;render()};document.getElementById("loadFen").onclick=()=>{try{parse(document.getElementById("fen").value)}catch(e){alert(e.message)}};document.getElementById("depth").oninput=e=>document.getElementById("depthValue").textContent=e.target.value;document.querySelectorAll("input[name=color]").forEach(x=>x.onchange=()=>{turn=active();render()});document.getElementById("analyse").onclick=()=>{let w=Object.values(board).filter(x=>x===x.toUpperCase()).length,b=Object.values(board).length-w;document.getElementById("result").innerHTML="<b>Position captured.</b><br>Material count: White "+w+" pieces, Black "+b+" pieces.<br>Full browser-side Alpha-Beta engine will be added next; this board editor already exports the exact FEN for analysis."};parse(start);
function positionValue(game){
 const values={p:100,n:320,b:330,r:500,q:900,k:0}; let total=0;
 game.board().flat().forEach(piece=>{if(piece)total+=(piece.color==="w"?1:-1)*values[piece.type]});
 return total;
}
function alphaBeta(game,depth,alpha,beta,nodes,pv){
 nodes.count++;
 if(depth===0||game.game_over())return positionValue(game);
 const maximizing=game.turn()==="w", moves=game.moves({verbose:true});
 moves.sort((a,b)=>(b.captured?1:0)-(a.captured?1:0));
 let best=maximizing?-Infinity:Infinity,bestLine=[];
 for(const move of moves){
  game.move(move);const child=[];const value=alphaBeta(game,depth-1,alpha,beta,nodes,child);game.undo();
  if((maximizing&&value>best)||(!maximizing&&value<best)){best=value;bestLine=[move.san,...child]}
  if(maximizing)alpha=Math.max(alpha,best);else beta=Math.min(beta,best);
  if(alpha>=beta)break;
 }
 pv.push(...bestLine);return best;
}
document.getElementById("analyse").onclick=()=>{
 try{
  if(typeof Chess==="undefined")throw Error("The rules library is still loading. Please try again.");
  const game=new Chess(fen()), depth=Number(document.getElementById("depth").value), nodes={count:0}, pv=[];
  const started=performance.now(), value=alphaBeta(game,depth,-Infinity,Infinity,nodes,pv), elapsed=(performance.now()-started)/1000;
  const best=pv[0]||"No legal move";
  document.getElementById("result").innerHTML="<b>Recommended move: "+best+"</b><br>Evaluation: "+(value>=0?"+":"")+value+" cp<br>Explored nodes: "+nodes.count.toLocaleString()+"<br>Time: "+elapsed.toFixed(3)+" s<br><b>Principal variation:</b> "+(pv.join(" ")||"Position is over.");
 }catch(error){document.getElementById("result").textContent="Analysis error: "+error.message}
};