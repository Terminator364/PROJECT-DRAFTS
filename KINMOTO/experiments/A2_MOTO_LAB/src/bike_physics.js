import {sampleRoadSurface, ROAD_TOP_Y} from './road_surface.js';
// KIN MOTO A2 — deterministic semi-physical motorcycle controller.
// No external library, no runtime download, no network, no model assets.
// Deliberately independent of camera and rendering.
const BIKE_WHEELBASE = 2.18;
const BIKE_WHEEL_RADIUS = 0.49;
const BIKE_GRAVITY = 9.81;
export function createBikeTelemetry() {
  return { steer:0, steerAngle:0, yawRate:0, lean:0, lateralSlip:0,
    vx:0, vz:0, wheelSpin:0, suspension:0, pitch:0, acceleration:0,
    frontGrounded:true, rearGrounded:true, lastSpeed:0, traction:1,
    frontHeight:ROAD_TOP_Y, rearHeight:ROAD_TOP_Y, suspensionVelocity:0,
    frontWheelY:.56, rearWheelY:.56, roadGrade:0 };
}
export function advanceBike(p, control, dt, config={}) {
  const clamp=(x,a,b)=>Math.max(a,Math.min(b,x));
  if (!Number.isFinite(dt) || dt <= 0 || dt > .10) throw Error('invalid fixed bike timestep');
  const t = p.bike || (p.bike=createBikeTelemetry());
  const maxSpeed=config.maxSpeed ?? 22.6;
  const engine=config.engine ?? 1;
  const brakes=config.brakes ?? 1;
  const condition=config.condition ?? 1;
  const roadGrip=config.roadGrip ?? 1;
  const steerInput=clamp(control.steer ?? 0,-1,1);
  const gas=clamp(control.gas ?? 0,0,1),brake=clamp(control.brake ?? 0,0,1);
  const steeringResponse=5.7;
  const ease=1-Math.exp(-steeringResponse*dt);
  t.steer+=(steerInput-t.steer)*ease;
  const speedBefore=p.speed;
  const throttleForce=gas*(6.0+(engine-1)*1.25);
  const brakingForce=brake*(11.6+(brakes-1)*1.95);
  const drag=(.22 + p.speed*.033)+(roadGrip<.90 ? 0.08:0);
  const accel=throttleForce-brakingForce-drag;
  p.speed=clamp(p.speed+accel*dt,0,maxSpeed*condition + (engine-1)*1.6);
  const speedForTurn=(p.speed+speedBefore)*.5;
  // The steering angle becomes smaller at high speed; no bicycle can pivot 90 degrees instantly.
  const maxAngle=.38/(1+speedForTurn*.115);
  t.steerAngle=t.steer*maxAngle;
  t.yawRate=speedForTurn < .12 ? 0 : speedForTurn*Math.tan(t.steerAngle)/BIKE_WHEELBASE;
  // A hard cap prevents pathological turns after frame hitches or very high speeds.
  t.yawRate=clamp(t.yawRate,-1.05,1.05);
  const oldYaw=p.yaw;
  p.yaw+=t.yawRate*dt;
  // Forward basis: yaw=0 is toward screen-up in the game's world (-Z).
  const fX=Math.sin(p.yaw),fZ=-Math.cos(p.yaw),rX=Math.cos(p.yaw),rZ=Math.sin(p.yaw);
  const oldForward=Math.sin(oldYaw)*t.vx-Math.cos(oldYaw)*t.vz;
  const unexpectedSpeed=Math.abs(p.speed-(t.lastSpeed??p.speed))>3;
  // Older savegames and QA fixtures can directly set p.speed/heading; re-align velocities once.
  if(t.lastSpeed===0 && Math.hypot(t.vx,t.vz)<.001 && p.speed>.2 || unexpectedSpeed){t.vx=fX*p.speed;t.vz=fZ*p.speed;}
  let lateral=t.vx*rX+t.vz*rZ;
  // Sideways tyre velocity decays under friction; wet/worn road keeps slightly more slip.
  const lateralDamping=clamp(11.5*roadGrip*condition,4,15);
  lateral*=Math.exp(-lateralDamping*dt);
  // To avoid bicycle-on-ice feel, base velocity follows forward body speed, leaving only
  // bounded lateral-slip inertia. No teleporting lateral offsets or static fake sways.
  t.vx=fX*p.speed+rX*lateral;
  t.vz=fZ*p.speed+rZ*lateral;
  const dx=t.vx*dt,dz=t.vz*dt;
  p.x+=dx;p.z+=dz;
  t.lateralSlip=lateral;
  t.acceleration=(p.speed-speedBefore)/dt;
  // Physical estimate for a motorcycle lean in a steady turn: tan(theta)=v*yawRate/g.
  const leanTarget=clamp(Math.atan2(speedForTurn*t.yawRate,BIKE_GRAVITY),-.51,.51);
  t.lean+=(leanTarget-t.lean)*(1-Math.exp(-4.5*dt));
  p.lean=t.lean;
  // Wheel rotation is tied to distance travelled, not to a HUD counter.
  t.wheelSpin+=Math.hypot(dx,dz)/BIKE_WHEEL_RADIUS;
  // Two contact samples under the two independently placed tires. Both physics
  // and road geometry use the same deterministic speed-bump height function.
  // A spring-damper moves the chassis while the tire centers stay on the road.
  const frontX=p.x+Math.sin(p.yaw)*1.08,frontZ=p.z-Math.cos(p.yaw)*1.08;
  const rearX=p.x-Math.sin(p.yaw)*1.10,rearZ=p.z+Math.cos(p.yaw)*1.10;
  t.frontHeight=sampleRoadSurface(frontX,frontZ);
  t.rearHeight=sampleRoadSurface(rearX,rearZ);
  const heightTarget=(t.frontHeight+t.rearHeight)*.5-ROAD_TOP_Y;
  const springAcc=(heightTarget-t.suspension)*84-17*t.suspensionVelocity;
  t.suspensionVelocity=clamp(t.suspensionVelocity+springAcc*dt,-2,2);
  t.suspension+=t.suspensionVelocity*dt;
  t.suspension=clamp(t.suspension,-.16,.22);
  t.roadGrade=Math.atan2(t.frontHeight-t.rearHeight,BIKE_WHEELBASE);
  const pitchTarget=clamp(t.roadGrade-t.acceleration*.006,-.14,.14);
  t.pitch+=(pitchTarget-t.pitch)*(1-Math.exp(-6.5*dt));
  const cp=Math.max(.95,Math.cos(t.pitch)),sp=Math.sin(t.pitch);
  // Roll, pitch and suspension all transform tire centers. Compensate for
  // those rotations so each visible wheel remains on its sampled surface.
  const rollScale=Math.max(.86,Math.cos(t.lean));
  t.frontWheelY=((.56+t.frontHeight-ROAD_TOP_Y-t.suspension)/rollScale+1.08*sp)/cp;
  t.rearWheelY=((.56+t.rearHeight-ROAD_TOP_Y-t.suspension)/rollScale-1.10*sp)/cp;
  t.frontGrounded=true;t.rearGrounded=true; // Known height field, both tire centers placed on it.
  t.traction=roadGrip*condition;
  t.lastSpeed=p.speed;
  return {dx,dz,travel:Math.hypot(dx,dz),accel:t.acceleration,yawRate:t.yawRate,lateralSlip:lateral};
}
