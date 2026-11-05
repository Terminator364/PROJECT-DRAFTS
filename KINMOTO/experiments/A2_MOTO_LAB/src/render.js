import {AdaptiveResolution} from './adaptive_resolution.js';
import {clamp,lerp,keepOverStreet} from './math.js';
import {makeWorld,makeBike,makeBikeWheel,makeCar,makeMarker,makeGarage} from './geom.js';
import {missionTarget,byId} from './sim.js';
const ID=()=>new Float32Array([1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1]);
function perspective(fovy,aspect,near,far){const f=1/Math.tan(fovy/2),m=new Float32Array(16);m[0]=f/aspect;m[5]=f;m[10]=(far+near)/(near-far);m[11]=-1;m[14]=2*far*near/(near-far);return m;}
function lookAt(e,t){const norm=a=>{const n=Math.hypot(...a)||1;return a.map(v=>v/n)};const cross=(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];const z=norm([e[0]-t[0],e[1]-t[1],e[2]-t[2]]),x=norm(cross([0,1,0],z)),y=cross(z,x);return new Float32Array([x[0],y[0],z[0],0,x[1],y[1],z[1],0,x[2],y[2],z[2],0,-(x[0]*e[0]+x[1]*e[1]+x[2]*e[2]),-(y[0]*e[0]+y[1]*e[1]+y[2]*e[2]),-(z[0]*e[0]+z[1]*e[1]+z[2]*e[2]),1]);}
function mul(a,b){const m=new Float32Array(16);for(let c=0;c<4;c++)for(let r=0;r<4;r++){m[c*4+r]=a[r]*b[c*4]+a[r+4]*b[c*4+1]+a[r+8]*b[c*4+2]+a[r+12]*b[c*4+3];}return m;}
function model(x=0,y=0,z=0,rot=0,roll=0){let m=ID(),co=Math.cos(rot),si=Math.sin(rot),cr=Math.cos(roll),sr=Math.sin(roll);m[0]=co*cr;m[1]=sr;m[2]=-si*cr;m[4]=-co*sr;m[5]=cr;m[6]=si*sr;m[8]=si;m[10]=co;m[12]=x;m[13]=y;m[14]=z;return m;}
function bikeBodyModel(p){
 const base=model(p.x,-.045+(p.bike?.suspension||0),p.z,Math.PI-p.yaw,p.lean);
 const pitch=p.bike?.pitch||0,cp=Math.cos(pitch),sp=Math.sin(pitch);
 const rot=ID();rot[5]=cp;rot[6]=sp;rot[9]=-sp;rot[10]=cp;
 return mul(base,rot);
}
function localWheel(x,y,z,spin=0,steer=0){
 const m=ID(),ca=Math.cos(spin),sa=Math.sin(spin),cb=Math.cos(steer),sb=Math.sin(steer);
 // Local steering rotation about Y, then wheel spin around the axle (X).
 m[0]=cb;m[2]=-sb;m[4]=sb*sa;m[5]=ca;m[6]=cb*sa;
 m[8]=sb*ca;m[9]=-sa;m[10]=cb*ca;
 m[12]=x;m[13]=y;m[14]=z;
 return m;
}
export class Renderer{
 constructor(canvas,opts={}){this.canvas=canvas;this.gl=canvas.getContext('webgl2',{antialias:false,alpha:true,depth:true,powerPreference:'low-power',preserveDrawingBuffer:false})||canvas.getContext('webgl',{antialias:false,alpha:true,depth:true,powerPreference:'low-power',preserveDrawingBuffer:false});if(!this.gl)throw new Error('WebGL indisponible sur ce navigateur / appareil.');
  this.quality=opts.quality||'eco';this.dynamic=new AdaptiveResolution({targetFps:opts.targetFps||30,minScale:opts.quality==='high'?.85:.68});this.camera={x:0,y:7.5,z:108},this.target={x:0,y:2,z:75},this.mode=0,this.vp=ID(),this.lastRender=0,this.fps=0,this.frames=0,this.seconds=0;
  const gl=this.gl;
  const vs=`attribute vec3 aPos;attribute vec3 aNormal;attribute vec3 aColor;uniform mat4 uVP;uniform mat4 uModel;uniform vec3 uSun;uniform vec3 uCamera;uniform float uTint;varying vec3 vColor;varying float vFog;void main(){vec4 w=uModel*vec4(aPos,1.);gl_Position=uVP*w;vec3 n=normalize(mat3(uModel)*aNormal);float lit=max(dot(n,normalize(uSun)),0.);vColor=aColor*(0.54+lit*.51)*uTint;vFog=clamp((distance(w.xyz,uCamera)-92.)/260.,0.,1.);}`;
  const fs=`precision mediump float;varying vec3 vColor;varying float vFog;uniform vec3 uFog;void main(){vec3 rgb=mix(vColor,uFog,vFog*.57);gl_FragColor=vec4(pow(max(rgb,vec3(0.)),vec3(.92)),1.);}`;
  const shader=(type,src)=>{const s=gl.createShader(type);gl.shaderSource(s,src);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))throw new Error('Erreur WebGL shader: '+gl.getShaderInfoLog(s));return s;};
  this.program=gl.createProgram();gl.attachShader(this.program,shader(gl.VERTEX_SHADER,vs));gl.attachShader(this.program,shader(gl.FRAGMENT_SHADER,fs));gl.linkProgram(this.program);if(!gl.getProgramParameter(this.program,gl.LINK_STATUS))throw new Error('Erreur WebGL: '+gl.getProgramInfoLog(this.program));gl.useProgram(this.program);
  this.attr={pos:gl.getAttribLocation(this.program,'aPos'),normal:gl.getAttribLocation(this.program,'aNormal'),color:gl.getAttribLocation(this.program,'aColor')};this.uniform={vp:gl.getUniformLocation(this.program,'uVP'),model:gl.getUniformLocation(this.program,'uModel'),sun:gl.getUniformLocation(this.program,'uSun'),tint:gl.getUniformLocation(this.program,'uTint'),camera:gl.getUniformLocation(this.program,'uCamera'),fog:gl.getUniformLocation(this.program,'uFog')};
  gl.uniform3f(this.uniform.sun,.53,1.0,.25);gl.uniform3f(this.uniform.fog,.59,.72,.78);gl.enable(gl.DEPTH_TEST);gl.depthFunc(gl.LEQUAL);gl.disable(gl.CULL_FACE);gl.clearColor(0,0,0,0);
  this.mesh={world:this.upload(makeWorld()),bike:this.upload(makeBike(false)),bikePassenger:this.upload(makeBike(true)),bikeWheel:this.upload(makeBikeWheel()),cars:Array.from({length:6},(_,i)=>this.upload(makeCar(i))),pickup:this.upload(makeMarker('pickup')),drop:this.upload(makeMarker('drop')),garageMarker:this.upload(makeMarker('garage')),garage:this.upload(makeGarage())};this.glVersion=typeof WebGL2RenderingContext!=='undefined'&&gl instanceof WebGL2RenderingContext?2:1;this.resize();
 }
 upload(g){const gl=this.gl,b=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,b);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(g.a),gl.STATIC_DRAW);return {buffer:b,n:g.count,bytes:g.count*36};}
 resize(){const vw=Math.max(1,innerWidth),vh=Math.max(1,innerHeight);const base=this.quality==='eco'?.78:this.quality==='high'?1.35:1.0;const dpr=Math.min(devicePixelRatio||1,base,Math.sqrt((this.quality==='eco'?780000:1350000)/(vw*vh)))*this.dynamic.scale;const w=Math.max(1,Math.floor(vw*dpr)),h=Math.max(1,Math.floor(vh*dpr));if(this.canvas.width!==w||this.canvas.height!==h){this.canvas.width=w;this.canvas.height=h;this.gl.viewport(0,0,w,h);}this.proj=perspective(innerWidth<700?1.04:.89,w/h,.13,390);}
 setQuality(level){this.quality=level;this.dynamic.minScale=level==='high'?.85:.68;this.dynamic.reset();this.resize();}
 draw(mesh,m,tint=1){const gl=this.gl,at=this.attr;gl.bindBuffer(gl.ARRAY_BUFFER,mesh.buffer);for(const idx of Object.values(at))gl.enableVertexAttribArray(idx);gl.vertexAttribPointer(at.pos,3,gl.FLOAT,false,36,0);gl.vertexAttribPointer(at.normal,3,gl.FLOAT,false,36,12);gl.vertexAttribPointer(at.color,3,gl.FLOAT,false,36,24);gl.uniformMatrix4fv(this.uniform.model,false,m);gl.uniform1f(this.uniform.tint,tint);gl.drawArrays(gl.TRIANGLES,0,mesh.n);}
 render(g,dt,active=true){if(!this.gl||this.lost)return;const foreground=typeof document==='undefined'||!document.hidden;this.dynamic.observe(dt,{visible:foreground&&active});this.resize();const gl=this.gl,p=g.player,h={x:Math.sin(p.yaw),z:-Math.cos(p.yaw)},distance=this.mode===0?12.8:this.mode===1?23.5:3.6,height=this.mode===0?7.9:this.mode===1?19.0:3.25;
  const desired={x:p.x-h.x*distance,y:height,z:p.z-h.z*distance},aim={x:p.x+h.x*(this.mode===1?9:13),y:this.mode===1?1.8:2.05,z:p.z+h.z*(this.mode===1?9:13)};
  // Camera collision: keep the chase camera on drivable streets, avoiding
  // the "building fills the screen" regression after hard steering near façades.
  keepOverStreet(desired,7.5);
  const k=clamp((dt||.016)*5,0,1);for(const a of ['x','y','z']){this.camera[a]=lerp(this.camera[a],desired[a],k);this.target[a]=lerp(this.target[a],aim[a],k);}
  keepOverStreet(this.camera,7.5);
  this.vp=mul(this.proj,lookAt([this.camera.x,this.camera.y,this.camera.z],[this.target.x,this.target.y,this.target.z]));gl.viewport(0,0,this.canvas.width,this.canvas.height);gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);gl.useProgram(this.program);gl.uniformMatrix4fv(this.uniform.vp,false,this.vp);gl.uniform3f(this.uniform.camera,this.camera.x,this.camera.y,this.camera.z);
  this.draw(this.mesh.world,ID());this.draw(this.mesh.garage,model(27,0,76,-Math.PI/2));
  // active markers are drawn at source/destination, physical position near road edge
  const q=missionTarget(g.mission);if(q)this.draw(g.mission.stage==='pickup'?this.mesh.pickup:this.mesh.drop,model(q.x,.2,q.z));this.draw(this.mesh.garageMarker,model(13,.05,80));
  for(const car of g.cars){
    const playerDistance=Math.hypot(car.x-p.x,car.z-p.z);
    const cameraDistance=Math.hypot(car.x-this.camera.x,car.z-this.camera.z);
    const behind=(car.x-p.x)*h.x+(car.z-p.z)*h.z < -1;
    // Standard third-person camera occlusion mitigation: hide a traffic mesh if
    // it would engulf the camera. The car remains active and collidable in sim.
    if(playerDistance<190 && !(behind && cameraDistance<11))
      this.draw(this.mesh.cars[car.kind%this.mesh.cars.length],model(car.x,0,car.z,Math.PI-car.yaw));
   }
  if(this.mode!==2){
   const base=bikeBodyModel(p);
   this.draw(g.mission.stage==='pickup'?this.mesh.bike:this.mesh.bikePassenger,base);
   const spin=p.bike?.wheelSpin||0,steer=p.bike?.steerAngle||0;
   this.draw(this.mesh.bikeWheel,mul(base,localWheel(0,p.bike?.rearWheelY??.56,-1.10,spin,0)));
   this.draw(this.mesh.bikeWheel,mul(base,localWheel(0,p.bike?.frontWheelY??.56,1.08,spin,steer)));
  }
  if(active){this.frames++;this.seconds+=dt||0;if(this.seconds>.65){this.fps=Math.round(this.frames/this.seconds);this.frames=0;this.seconds=0;}}
  else {this.frames=0;this.seconds=0;}
 }
 project(x,y,z){const a=this.vp,v=[x,y,z,1],t=[0,0,0,0];for(let row=0;row<4;row++)for(let col=0;col<4;col++)t[row]+=a[col*4+row]*v[col];if(t[3]<=0)return null;let nx=t[0]/t[3],ny=t[1]/t[3];if(Math.abs(nx)>1.4||Math.abs(ny)>1.4)return null;return {x:(nx*.5+.5)*innerWidth,y:(1-(ny*.5+.5))*innerHeight,visible:Math.abs(nx)<1&&Math.abs(ny)<1};}
 stats(){return {glVersion:this.glVersion,quality:this.quality,fps:this.fps,adaptiveScale:this.dynamic.scale,adaptiveSteps:this.dynamic.updates,pixels:this.canvas.width*this.canvas.height,meshBytes:Object.values(this.mesh).flat().filter(x=>x?.bytes).reduce((s,x)=>s+x.bytes,0),worldVertices:this.mesh.world.n};}
 dispose(){const gl=this.gl;for(const m of Object.values(this.mesh).flat())if(m?.buffer)gl.deleteBuffer(m.buffer);if(this.program)gl.deleteProgram(this.program);}
}
