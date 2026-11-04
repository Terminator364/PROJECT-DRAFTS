// Dynamic render resolution in low-power browsers: keep genuine 3D and game logic.
// Unlike switching to 2D, only GPU pixel workload changes. Deterministic testable policy.
const clampAdaptive=(x,a,b)=>Math.max(a,Math.min(b,x));
export class AdaptiveResolution {
 constructor({targetFps=30,minScale=.68,maxScale=1,initialScale=1}={}){
  this.targetFps=targetFps;this.minScale=minScale;this.maxScale=maxScale;
  this.scale=clampAdaptive(initialScale,minScale,maxScale);this.emaFrame=1/targetFps;
  this.samples=0;this.elapsed=0;this.cooldown=0;this.updates=0;
 }
 observe(dt,{visible=true}={}){
  // Sustained 4–8 FPS in a visible tab is real GPU overload: do not ignore it.
  // Frames longer than 250 ms remain excluded as possible tab wake/scheduler pauses.
  if(!visible||!Number.isFinite(dt)||dt<.005||dt>.25)return false;
  // We wait for actual in-foreground frames and do not react to tab throttling.
  this.emaFrame=this.samples?this.emaFrame*.94+dt*.06:dt;
  this.samples++;this.elapsed+=dt;this.cooldown=Math.max(0,this.cooldown-dt);
  if(this.samples<45||this.elapsed<1.6||this.cooldown>0)return false;
  this.elapsed=0;
  const slow=this.emaFrame>1/this.targetFps*1.24;
  const fast=this.emaFrame<1/this.targetFps*.83;
  const next=clampAdaptive(this.scale+(slow?-.08:fast?.035:0),this.minScale,this.maxScale);
  if(Math.abs(next-this.scale)<.009)return false;
  this.scale=Math.round(next*1000)/1000;this.cooldown=1.0;this.updates++;return true;
 }
 reset(initial=1){this.scale=clampAdaptive(initial,this.minScale,this.maxScale);this.emaFrame=1/this.targetFps;this.samples=0;this.elapsed=0;this.cooldown=0;}
}
