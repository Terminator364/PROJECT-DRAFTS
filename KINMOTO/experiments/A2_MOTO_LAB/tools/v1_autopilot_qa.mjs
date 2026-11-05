import {makeGame,step,validate} from '../src/sim.js';
import {startChallenge,CHALLENGE_GATES} from '../src/challenge.js';
const g=makeGame();g.playing=true;g.cars=[];startChallenge(g);
let min=Infinity,max=0;
for(let i=0;i<90*60&&g.challenge.status==='running';i++){
 const p=g.player,target=CHALLENGE_GATES[g.challenge.index];
 const dx=target.x-p.x,dz=target.z-p.z;
 const heading=Math.atan2(dx,-dz),error=Math.atan2(Math.sin(heading-p.yaw),Math.cos(heading-p.yaw));
 const distance=Math.hypot(dx,dz),kmh=p.speed*3.6;
 const needBrake=Math.abs(error)>.6&&kmh>20||distance<8&&Math.abs(error)>.3&&kmh>13;
 g.controls.right=error>.06;g.controls.left=error<-.06;
 g.controls.gas=!needBrake&&kmh<(Math.abs(error)>.5?28:47);
 g.controls.brake=needBrake;
 step(g,1/60);
 min=Math.min(min,Math.hypot(g.player.x-target.x,g.player.z-target.z));max=Math.max(max,kmh);
 if(i%300===0)console.log(JSON.stringify({t:i/60,stage:g.challenge.index,p:{x:p.x,z:p.z,yaw:p.yaw,kmh},target,err:error,dist:distance}));
}
console.log('RESULT',JSON.stringify({status:g.challenge.status,index:g.challenge.index,elapsed:g.challenge.elapsed,score:g.challenge.score,stars:g.challenge.stars,maxSpeedKmH:max,collisions:g.collisions,issues:validate(g),p:{x:g.player.x,z:g.player.z}}));
if(g.challenge.status!=='won'||validate(g).length)process.exitCode=1;
