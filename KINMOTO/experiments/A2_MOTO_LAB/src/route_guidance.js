import {dist,angleOf,wrapAngle,clamp} from './math.js';
import {findRoute} from './navigation.js';
// Navigation instructions and remaining road distance must follow the street
// graph rather than a straight line through buildings. UI-only, not physics.
export function guideTo(from,target,yaw, routeOverride=null) {
  if(!target) return {kind:'missing',label:'PAS DE DESTINATION',distance:Infinity,turnDistance:Infinity,route:[]};
  const route=routeOverride||findRoute(from,target);
  if(!route||!Array.isArray(route.nodes)||route.nodes.length<2) throw Error('Invalid navigation route');
  let distance=0;for(let i=1;i<route.nodes.length;i++)distance+=dist(route.nodes[i-1],route.nodes[i]);
  if(!Number.isFinite(distance))throw Error('Invalid navigation distance');
  if(dist(from,target)<13) return {kind:'arrive',label:'ARRÊT À PROXIMITÉ',distance,turnDistance:0,route:route.nodes};
  let next=route.nodes.find((point,i)=>i>0&&dist(from,point)>5) || route.nodes[route.nodes.length-1];
  const aimYaw=angleOf(next.x-from.x,next.z-from.z),diff=wrapAngle(aimYaw-yaw);
  const turnDistance=dist(from,next);
  const kind=diff > .45?'right':diff < -.45?'left':'straight';
  const labels={left:'TOURNER À GAUCHE',right:'TOURNER À DROITE',straight:'CONTINUER TOUT DROIT'};
  return {kind,label:labels[kind],distance:Math.round(distance),turnDistance:Math.round(turnDistance),angle:diff,route:route.nodes};
}
