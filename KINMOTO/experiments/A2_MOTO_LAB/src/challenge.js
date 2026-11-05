// KIN MOTO V1 — first-party, deterministic skill challenge. All points lie on
// existing asphalt. No external model, service or telemetry is required.
export const CHALLENGE_GATES=Object.freeze([
 {x:4.4,z:78,name:'Départ Bandal'},
 {x:4.4,z:58,name:'Accélération'},
 {x:4.4,z:34,name:'Tenir sa ligne'},
 {x:4.4,z:9,name:'Approche Victoire'},
 {x:4.4,z:-4.4,name:'Virage du carrefour'},
 {x:27,z:-4.4,name:'Ligne droite'},
 {x:57,z:-4.4,name:'Arrivée Victoire'}
]);
export const CHALLENGE_LIMIT_SECONDS=90;
const challengeDistance=(a,b)=>Math.hypot(a.x-b.x,a.z-b.z);
export function challengeTarget(g){const c=g?.challenge;return c?.active?CHALLENGE_GATES[c.index]||null:null;}
export function startChallenge(g){
 if(!g||!g.player||!g.save)throw Error('Partie non initialisée');
 // Skills mode is sandboxed from passenger, mission, fines and career progress.
 const returnPlayer=g.challenge?.returnPlayer||{x:g.player.x,z:g.player.z,yaw:g.player.yaw};
 g.player.x=4.4;g.player.z=95;g.player.yaw=0;g.player.speed=0;g.player.lean=0;
 g.player.damageCooldown=0;
 if(g.player.bike){g.player.bike.vx=0;g.player.bike.vz=0;g.player.bike.groundSpeed=0;g.player.bike.lastSpeed=0;}
 g.controls={left:false,right:false,gas:false,brake:false};
 g.challenge={returnPlayer,active:true,status:'running',index:0,elapsed:0,limit:CHALLENGE_LIMIT_SECONDS,
  score:0,combos:0,stars:0,paid:0,startCollisions:g.collisions||0,finishedAt:null};
 return g.challenge;
}
export function advanceChallenge(g,dt){
 const c=g?.challenge;
 if(!c?.active||c.status!=='running'||!(dt>0))return null;
 c.elapsed+=dt;
 const target=CHALLENGE_GATES[c.index];
 if(target&&challengeDistance(g.player,target)<=6.0){
  c.index++;c.combos++;
  c.score+=100+Math.min(80,c.combos*10);
  if(c.index===CHALLENGE_GATES.length){
   c.active=false;c.status='won';c.finishedAt=c.elapsed;
   const hits=(g.collisions||0)-c.startCollisions;
   c.score+=Math.max(0,Math.round((c.limit-c.elapsed)*7));
   c.stars=Math.max(1,(c.elapsed<=40?3:c.elapsed<=65?2:1)-Math.min(1,Math.max(0,hits)));
   if(c.score>g.save.highScore){
    c.paid=450;g.save.cash+=c.paid;g.save.highScore=c.score;
   }
   return {type:'complete',score:c.score,stars:c.stars,reward:c.paid};
  }
  return {type:'gate',gate:c.index,total:CHALLENGE_GATES.length};
 }
 if(c.elapsed>=c.limit){c.active=false;c.status='timeout';c.finishedAt=c.elapsed;return {type:'timeout'};}
 return null;
}
