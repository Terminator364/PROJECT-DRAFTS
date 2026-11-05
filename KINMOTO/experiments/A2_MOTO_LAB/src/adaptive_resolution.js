// Dynamic render resolution in low-power browsers: keep genuine 3D and game logic.
// Unlike switching to 2D, only GPU pixel workload changes. Deterministic testable policy.
const clampAdaptive=(x,a,b)=>Math.max(a,Math.min(b,x));
export class AdaptiveResolution {
 constructor({targetFps=30,minScale=.68,maxScale=1,initialScale=1}={}){
  this.targetFps=targetFps;this.minScale=minScale;this.maxScale=maxScale;
  this.scale=clampAdaptive(initialScale,minScale,maxScale);this.emaFrame=1/targetFps;
  this.samples=0;this.elapsed=0;this.cooldown=0;this.updates=0;this.slowVisibleFrames=0;
 }
 observe(dt,{visible=true}={}){
  if(!visible||!Number.isFinite(dt)||dt<.005||dt>.60){this.slowVisibleFrames=0;return false;}
  // Ignore 1–2 isolated 250–600ms stalls; adapt to sustained severe foreground drops.
  if(dt>.25){this.slowVisibleFrames++;if(this.slowVisibleFrames<3)return false;}
  else this.slowVisibleFrames=0;
  // We wait for actual in-foreground frames and do not react to tab throttling.
  this.emaFrame=this.samples?this.emaFrame*.94+dt*.06:dt;
  this.samples++;this.elapsed+=dt;this.cooldown=Math.max(0,this.cooldown-dt);
  if(this.samples<(dt>.25?6:45)||this.elapsed<1.6||this.cooldown>0)return false;
  this.elapsed=0;
  const slow=this.emaFrame>1/this.targetFps*1.24;
  const fast=this.emaFrame<1/this.targetFps*.83;
  const next=clampAdaptive(this.scale+(slow?-.08:fast?.035:0),this.minScale,this.maxScale);
  if(Math.abs(next-this.scale)<.009)return false;
  this.scale=Math.round(next*1000)/1000;this.cooldown=1.0;this.updates++;return true;
 }
 reset(initial=1){this.scale=clampAdaptive(initial,this.minScale,this.maxScale);this.emaFrame=1/this.targetFps;this.samples=0;this.elapsed=0;this.cooldown=0;this.slowVisibleFrames=0;}
}

// Explicit render scheduling outside gameplay. No GPU work is measured here.
// The policy only reduces calls; the renderer owns the real graphics backend.
export class IdleFrameGate {
 constructor(idleIntervalMs=120){
  if(!Number.isFinite(idleIntervalMs)||idleIntervalMs<=0)throw Error('Invalid idle rendering interval');
  this.idleIntervalMs=idleIntervalMs;this.lastIdle=-Infinity;
 }
 shouldRender(now,{active=true,visible=true}={}){
  if(!visible||!Number.isFinite(now))return false;
  if(active)return true;
  if(now<this.lastIdle)this.lastIdle=-Infinity;
  if(now-this.lastIdle<this.idleIntervalMs)return false;
  this.lastIdle=now;return true;
 }
 reset(){this.lastIdle=-Infinity;}
}
