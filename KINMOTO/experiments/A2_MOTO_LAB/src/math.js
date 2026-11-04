export const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
export const lerp=(a,b,t)=>a+(b-a)*t;
export const smooth=(a,b,t)=>lerp(a,b,clamp(t,0,1));
export const hypot=(a,b)=>Math.hypot(a,b);
export const dist=(a,b)=>Math.hypot(a.x-b.x,a.z-b.z);
export const wrapAngle=a=>Math.atan2(Math.sin(a),Math.cos(a));
export function rand(seed){let x=seed|0;return()=>{x^=x<<13;x^=x>>>17;x^=x<<5;return (x>>>0)/4294967296;};}
export const heading=yaw=>({x:Math.sin(yaw),z:-Math.cos(yaw)});
export const angleOf=(dx,dz)=>Math.atan2(dx,-dz);
export function nearestRoad(p,roads=[-120,0,120]){let nearest={distance:Infinity,axis:'x',value:0}; for(const v of roads){let dx=Math.abs(p.x-v),dz=Math.abs(p.z-v);if(dx<nearest.distance)nearest={distance:dx,axis:'x',value:v};if(dz<nearest.distance)nearest={distance:dz,axis:'z',value:v};}return nearest;}
export function routeDistance(a,b){return Math.abs(a.x-b.x)+Math.abs(a.z-b.z);}
