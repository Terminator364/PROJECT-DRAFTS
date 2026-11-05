// KIN MOTO navigation: insert temporary anchors into actual road segments.
// On the same road, a short trip must not detour to an intersection and back.
import {dist} from './math.js';
export const STREETS=[-120,0,120];
const junctions=STREETS.flatMap((z,r)=>STREETS.map((x,c)=>({x,z,id:r*3+c})));
const SNAP_TOLERANCE=16; // Mission markers can be on sidewalks ~13 m from center.

function possibleAnchors(p){
 if(!p||!Number.isFinite(p.x)||!Number.isFinite(p.z))throw Error('Invalid navigation endpoint');
 const all=[];
 for(const v of STREETS){
  all.push({x:v,z:p.z,axis:'z',street:v,offset:Math.abs(p.x-v)});
  all.push({x:p.x,z:v,axis:'x',street:v,offset:Math.abs(p.z-v)});
 }
 all.sort((a,b)=>a.offset-b.offset);
 const near=all.filter(q=>q.offset<=SNAP_TOLERANCE);
 return near.length?near:all.slice(0,1);
}

function graphRoute(from,to,a,b){
 const nodes=[...junctions,a,b],edges=Array.from({length:nodes.length},()=>[]);
 const connect=(i,j)=>{const d=dist(nodes[i],nodes[j]);edges[i].push([j,d]);edges[j].push([i,d]);};
 for(const street of STREETS){
  const vertical=junctions.map((p,i)=>p.x===street?i:-1).filter(i=>i>=0);
  const horizontal=junctions.map((p,i)=>p.z===street?i:-1).filter(i=>i>=0);
  if(a.axis==='z'&&a.street===street)vertical.push(9);
  if(b.axis==='z'&&b.street===street)vertical.push(10);
  if(a.axis==='x'&&a.street===street)horizontal.push(9);
  if(b.axis==='x'&&b.street===street)horizontal.push(10);
  vertical.sort((i,j)=>nodes[i].z-nodes[j].z);
  horizontal.sort((i,j)=>nodes[i].x-nodes[j].x);
  for(let i=1;i<vertical.length;i++)connect(vertical[i-1],vertical[i]);
  for(let i=1;i<horizontal.length;i++)connect(horizontal[i-1],horizontal[i]);
 }
 const cost=Array(nodes.length).fill(Infinity),prev=Array(nodes.length).fill(-1),seen=new Set();cost[9]=0;
 for(let k=0;k<nodes.length;k++){
  let u=-1;
  for(let i=0;i<nodes.length;i++)if(!seen.has(i)&&(u<0||cost[i]<cost[u]))u=i;
  if(u<0||!Number.isFinite(cost[u])||u===10)break;
  seen.add(u);
  for(const [v,w] of edges[u])if(cost[u]+w<cost[v]){cost[v]=cost[u]+w;prev[v]=u;}
 }
 if(!Number.isFinite(cost[10]))return null;
 const path=[];let i=10;
 while(i>=0){path.unshift(nodes[i]);if(i===9)break;i=prev[i];}
 if(i!==9)return null;
 const dedup=[];
 for(const p of [from,...path,to])if(!dedup.length||dist(p,dedup[dedup.length-1])>1e-7)dedup.push({x:p.x,z:p.z});
 // guideTo expects at least two points even when the endpoints coincide.
 if(dedup.length===1)dedup.push({...dedup[0]});
 const length=dedup.slice(1).reduce((sum,p,i)=>sum+dist(p,dedup[i]),0);
 return {nodes:dedup,length};
}

export function findRoute(from,to){
 let best=null;
 for(const a of possibleAnchors(from))for(const b of possibleAnchors(to)){
  const route=graphRoute(from,to,a,b);
  if(route&&(!best||route.length<best.length-1e-8))best=route;
 }
 if(!best)throw Error('Navigation graph disconnected');
 return best;
}
