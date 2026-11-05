// Dynamic render resolution in low-power browsers: keep genuine 3D and game logic.
// Unlike switching to 2D, only GPU pixel workload changes. Deterministic testable policy.
const clampAdaptive=(x,a,b)=>Math.max(a,Math.min(b,x));
export class AdaptiveResolution {
 constructor({targetFps=30,minScale=.68,maxScale=1,initialScale=1}={}){
  this.targetFps=targetFps;this.minScale=minScale;this.maxScale=maxScale;
  this.scale=clampAdaptive(initialScale,minScale,maxScale);this.emaFrame=1/targetFps;
  this.samples=0;this.elapsed=0;this.cooldown=0;this.updates=0;this.slowVisibleFrames=0;this.sustainedSlowFrames=0;
 }
 observe(dt,{visible=true}={}){
  // A visible sequence of 1–10 FPS frames can be genuine overload, not a tab wake.
  // Ignore one-off stalls, background time and extreme scheduler suspensions.
  if(!visible){
    // A background tab may resume at a completely different rendering cadence.
    // Forget stale timing statistics, but preserve the last chosen quality scale.
    this.emaFrame=1/this.targetFps;this.samples=0;this.elapsed=0;this.cooldown=0;
    this.slowVisibleFrames=0;this.sustainedSlowFrames=0;return false;
  }
  if(!Number.isFinite(dt)||dt<.005||dt>2){this.slowVisibleFrames=0;this.sustainedSlowFrames=0;return false;}
  if(dt>.25){this.slowVisibleFrames++;if(this.slowVisibleFrames<3)return false;}
  else this.slowVisibleFrames=0;
  this.sustainedSlowFrames=dt>=1/12?this.sustainedSlowFrames+1:0;
  // We wait for actual in-foreground frames and do not react to tab throttling.
  this.emaFrame=this.samples?this.emaFrame*.94+dt*.06:dt;
  this.samples++;this.elapsed+=dt;this.cooldown=Math.max(0,this.cooldown-dt);
  // At 5–10 FPS 45 samples could take 5–9 seconds before the FIRST reduction.
  // After six consecutive visible slow frames, use an accelerated evaluation gate.
  if(this.samples<(this.sustainedSlowFrames>=6?6:45)||this.elapsed<1.6||this.cooldown>0)return false;
  this.elapsed=0;
  const slow=this.emaFrame>1/this.targetFps*1.24;
  const fast=this.emaFrame<1/this.targetFps*.83;
  const next=clampAdaptive(this.scale+(slow?-.08:fast?.035:0),this.minScale,this.maxScale);
  if(Math.abs(next-this.scale)<.009)return false;
  this.scale=Math.round(next*1000)/1000;this.cooldown=1.0;this.updates++;return true;
 }
 reset(initial=1){this.scale=clampAdaptive(initial,this.minScale,this.maxScale);this.emaFrame=1/this.targetFps;this.samples=0;this.elapsed=0;this.cooldown=0;this.slowVisibleFrames=0;this.sustainedSlowFrames=0;}
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

// Bounded fixed-step simulation pacing for low-frame-rate devices.
// The 3D renderer may run at 2-5 FPS while the physical motorcycle still
// advances at 60Hz in small deterministic steps. Avoid unbounded catch-up
// after a suspended tab or a multi-second GPU stall.
export class FixedStepScheduler {
 constructor({fixed=1/60,maxFrame=.5,maxSteps=30}={}){
  if(!Number.isFinite(fixed)||fixed<=0||!Number.isFinite(maxFrame)||maxFrame<fixed
      ||!Number.isInteger(maxSteps)||maxSteps<1||maxSteps*fixed<maxFrame-1e-9)
    throw Error('Invalid fixed-step scheduler budget');
  this.fixed=fixed;this.maxFrame=maxFrame;this.maxSteps=maxSteps;
  this.accumulator=0;this.droppedSeconds=0;this.ticks=0;
 }
 advance(elapsed,callback,{active=true}={}){
  if(!active){this.reset();return 0;}
  if(!Number.isFinite(elapsed)||elapsed<0)return 0;
  const accepted=Math.min(this.maxFrame,elapsed);
  this.droppedSeconds+=Math.max(0,elapsed-accepted);
  this.accumulator=Math.min(this.maxFrame,this.accumulator+accepted);
  let ticks=0;
  while(this.accumulator+1e-10>=this.fixed&&ticks<this.maxSteps){
   callback(this.fixed);this.accumulator=Math.max(0,this.accumulator-this.fixed);ticks++;
  }
  this.ticks+=ticks;
  if(ticks===this.maxSteps&&this.accumulator>=this.fixed){
   this.droppedSeconds+=this.accumulator;this.accumulator=0;
  }
  return ticks;
 }
 reset(){this.accumulator=0;}
}

// Offline-only QA sample ring: no network, device identifiers, or career details.
// Sampling is low frequency so measurement does not itself burden a weak device.
export class DevicePerformanceRecorder {
 constructor({intervalMs=1000,maxSamples=900}={}){
  if(!Number.isFinite(intervalMs)||intervalMs<250||!Number.isInteger(maxSamples)||maxSamples<1)
   throw Error('Invalid performance recorder budget');
  this.intervalMs=intervalMs;this.maxSamples=maxSamples;
  this.samples=[];this.startedMs=null;this.lastSampleMs=null;
 }
 shouldSample(now,active=true){
  return !!active&&Number.isFinite(now)&&
   (this.lastSampleMs===null||now<this.lastSampleMs||now-this.lastSampleMs>=this.intervalMs);
 }
 record(now,values,active=true){
  if(!this.shouldSample(now,active))return false;
  if(this.startedMs===null||now<this.lastSampleMs)this.startedMs=now;
  this.lastSampleMs=now;
  const safe=(value,upper=1e15)=>typeof value==='number'&&Number.isFinite(value)&&value>=0&&value<=upper?
   Math.round(value*1000)/1000:null;
  this.samples.push({elapsed_ms:Math.max(0,Math.round(now-this.startedMs)),
   fps:safe(values?.fps,500),renderScale:safe(values?.renderScale,2),
   renderPixels:safe(values?.renderPixels,10e7),
   simSeconds:safe(values?.simSeconds),droppedSeconds:safe(values?.droppedSeconds),
   jsHeapBytes:safe(values?.jsHeapBytes)});
  if(this.samples.length>this.maxSamples)this.samples.shift();
  return true;
 }
 report(meta={}){
  const fps=this.samples.map(s=>s.fps).filter(v=>v!==null&&v>0).sort((a,b)=>a-b);
  const avg=fps.length?Math.round(fps.reduce((a,b)=>a+b,0)*10/fps.length)/10:null;
  const last=this.samples[this.samples.length-1],first=this.samples[0];
  const minScale=this.samples.map(s=>s.renderScale).filter(x=>x!==null).reduce((a,b)=>Math.min(a,b),Infinity);
  return {schema:1,type:'KINMOTO_LOCAL_DEVICE_DIAGNOSTIC',
   privacy:'Local only; no GPS, account ID, wallet, passenger, location, or network transfer.',
   meta,summary:{samples:this.samples.length,validFpsSamples:fps.length,
    avgFps:avg,minFps:fps[0]??null,p10Fps:fps.length?fps[Math.floor((fps.length-1)*.1)]:null,
    maxFps:fps.length?fps[fps.length-1]:null,minRenderScale:Number.isFinite(minScale)?minScale:null,
    sampleWindowSeconds:last&&first?Math.round((last.elapsed_ms-first.elapsed_ms)/1000*10)/10:0,
    droppedSimSeconds:last?.droppedSeconds??null},samples:this.samples.map(s=>({...s}))};
 }
}
