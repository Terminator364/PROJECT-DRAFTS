import {dist} from './math.js';
export const STREETS=[-120,0,120];
const points=STREETS.flatMap((z,r)=>STREETS.map((x,c)=>({x,z,id:r*3+c})));
function entrance(p){const options=[];for(let i=0;i<points.length;i++){const v=points[i],sameX=Math.min(...STREETS.map(x=>Math.abs(p.x-x)))<=14,sameZ=Math.min(...STREETS.map(z=>Math.abs(p.z-z)))<=14;
 if((sameX&&Math.abs(p.x-v.x)<=14)||(sameZ&&Math.abs(p.z-v.z)<=14))options.push({idx:i,cost:dist(p,v)});}
 return options.length?options.sort((a,b)=>a.cost-b.cost).slice(0,3):points.map((v,i)=>({idx:i,cost:dist(p,v)})).sort((a,b)=>a.cost-b.cost).slice(0,2);}
function neighbors(id){const r=Math.floor(id/3),c=id%3;return [[r-1,c],[r+1,c],[r,c-1],[r,c+1]].filter(([a,b])=>a>=0&&a<3&&b>=0&&b<3).map(([a,b])=>a*3+b);}
export function findRoute(from,to){let best=null;
 for(const a of entrance(from))for(const b of entrance(to)){
  const cost=Array(9).fill(Infinity),prev=Array(9).fill(-1),used=new Set();cost[a.idx]=0;
  for(let k=0;k<9;k++){let node=-1;for(let j=0;j<9;j++)if(!used.has(j)&&(node<0||cost[j]<cost[node]))node=j;if(node<0||!Number.isFinite(cost[node]))break;if(node===b.idx)break;used.add(node);for(const n of neighbors(node)){let v=cost[node]+dist(points[node],points[n]);if(v<cost[n]){cost[n]=v;prev[n]=node;}}}
  if(!Number.isFinite(cost[b.idx]))continue;let path=[b.idx],cur=b.idx,guard=0;while(cur!==a.idx&&guard++<11){cur=prev[cur];if(cur<0)break;path.unshift(cur)}
  if(path[0]!==a.idx)continue;const total=a.cost+cost[b.idx]+b.cost;
  if(!best||total<best.length){best={nodes:path.map(id=>points[id]),length:total};}
 }
 if(!best)return {nodes:[from,to],length:dist(from,to)};
 return {nodes:[from,...best.nodes,to],length:best.length};}
