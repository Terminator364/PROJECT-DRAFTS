// KIN MOTO A2 — deterministic road-surface model shared by geometry and physics.
// A low, visible speed bump is preferable to applying random visual shaking.
export const ROAD_TOP_Y = 0.025;
export const SPEED_BUMPS = Object.freeze([
  {axis:'z',road:0,along:39,halfLength:2.0,height:0.105},
  {axis:'z',road:120,along:-51,halfLength:1.75,height:0.082},
  {axis:'x',road:0,along:-42,halfLength:1.85,height:0.090},
]);
export function smoothBump(distance, halfLength){
  const normalized=Math.abs(distance)/halfLength;
  return normalized>=1?0:(1+Math.cos(Math.PI*normalized))*.5;
}
export function sampleRoadSurface(x,z){
  let h=ROAD_TOP_Y;
  for(const b of SPEED_BUMPS){
    const lateral=(b.axis==='z'?x:z)-b.road;
    if(Math.abs(lateral)>8.75)continue;
    const longitudinal=(b.axis==='z'?z:x)-b.along;
    const e=smoothBump(longitudinal,b.halfLength);
    if(e)h=Math.max(h,ROAD_TOP_Y+b.height*e);
  }
  return h;
}
