import {SPEED_BUMPS, smoothBump, ROAD_TOP_Y} from './road_surface.js';
import {rand} from './math.js';
export function C(s){let x=parseInt(s.replace('#',''),16);return [(x>>>16&255)/255,(x>>>8&255)/255,(x&255)/255];}
export const P={asphalt:C('#353e4b'),road2:C('#303944'),line:C('#f5eed9'),yellow:C('#efb93e'),shoulder:C('#909f8a'),pavement:C('#b3aa93'),tree:C('#368475'),dark:C('#233444'),sand:C('#c5ba9b'),glass:C('#6a92a0'),metal:C('#c5d6d9'),tire:C('#242b35'),bike:C('#f6c634'),red:C('#d45444'),skin:C('#9d633d')};
export class Geo{
 constructor(){this.a=[];this.count=0;}
 v(p,n,c){this.a.push(p[0],p[1],p[2],n[0],n[1],n[2],c[0],c[1],c[2]);this.count++}
 tri(a,b,c,col,n){if(!n){const u=[b[0]-a[0],b[1]-a[1],b[2]-a[2]],v=[c[0]-a[0],c[1]-a[1],c[2]-a[2]];n=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]];const d=Math.hypot(...n)||1;n=n.map(x=>x/d);}this.v(a,n,col);this.v(b,n,col);this.v(c,n,col);}
 quad(a,b,c,d,col,n){this.tri(a,b,c,col,n);this.tri(a,c,d,col,n)}
 box(x,y,z,w,h,d,col){let a=x-w/2,b=x+w/2,lo=y-h/2,hi=y+h/2,f=z-d/2,g=z+d/2;
 this.quad([a,lo,g],[b,lo,g],[b,hi,g],[a,hi,g],col,[0,0,1]);this.quad([b,lo,f],[a,lo,f],[a,hi,f],[b,hi,f],col,[0,0,-1]);this.quad([b,lo,g],[b,lo,f],[b,hi,f],[b,hi,g],col,[1,0,0]);this.quad([a,lo,f],[a,lo,g],[a,hi,g],[a,hi,f],col,[-1,0,0]);this.quad([a,hi,g],[b,hi,g],[b,hi,f],[a,hi,f],col,[0,1,0]);this.quad([a,lo,f],[b,lo,f],[b,lo,g],[a,lo,g],col,[0,-1,0]);}
 cy(x,y,z,r,h,n,color,r1=r){for(let i=0;i<n;i++){let a=i*Math.PI*2/n,b=(i+1)*Math.PI*2/n;this.quad([x+r*Math.cos(a),y,z+r*Math.sin(a)],[x+r*Math.cos(b),y,z+r*Math.sin(b)],[x+r1*Math.cos(b),y+h,z+r1*Math.sin(b)],[x+r1*Math.cos(a),y+h,z+r1*Math.sin(a)],color);}}

 tube(a,b,r,color,n=8){
   let d=[b[0]-a[0],b[1]-a[1],b[2]-a[2]],len=Math.hypot(...d)||1;
   d=d.map(v=>v/len);let pivot=Math.abs(d[1])<.85?[0,1,0]:[1,0,0];
   let u=[pivot[1]*d[2]-pivot[2]*d[1],pivot[2]*d[0]-pivot[0]*d[2],pivot[0]*d[1]-pivot[1]*d[0]];
   const un=Math.hypot(...u)||1;u=u.map(v=>v/un);
   let v=[d[1]*u[2]-d[2]*u[1],d[2]*u[0]-d[0]*u[2],d[0]*u[1]-d[1]*u[0]];
   for(let i=0;i<n;i++){
     let a0=i*2*Math.PI/n,a1=(i+1)*2*Math.PI/n;
     const mk=(point,angle)=>point.map((c,k)=>c+r*(u[k]*Math.cos(angle)+v[k]*Math.sin(angle)));
     this.quad(mk(a,a0),mk(a,a1),mk(b,a1),mk(b,a0),color);
   }
 }
 ellipsoid(x,y,z,rx,ry,rz,color,segments=12,rings=7){
   for(let q=0;q<rings;q++){
     let v0=-Math.PI/2+q*Math.PI/rings,v1=-Math.PI/2+(q+1)*Math.PI/rings;
     for(let k=0;k<segments;k++){
       let a=k*2*Math.PI/segments,b=(k+1)*2*Math.PI/segments;
       let at=(v,t)=>[x+rx*Math.cos(v)*Math.cos(t),y+ry*Math.sin(v),z+rz*Math.cos(v)*Math.sin(t)];
       this.quad(at(v0,a),at(v0,b),at(v1,b),at(v1,a),color);
     }
   }
 }
 wheel(x,y,z,r,w,color){for(let i=0;i<12;i++){let a=i*Math.PI/6,b=(i+1)*Math.PI/6;this.quad([x-w/2,y+r*Math.cos(a),z+r*Math.sin(a)],[x-w/2,y+r*Math.cos(b),z+r*Math.sin(b)],[x+w/2,y+r*Math.cos(b),z+r*Math.sin(b)],[x+w/2,y+r*Math.cos(a),z+r*Math.sin(a)],color);}}
}
const BUILD=['#e6c5aa','#e2d9c9','#bfd0d1','#d7b99b','#e5d1a4','#b7d0c8','#e2b79c','#d9c6b3','#c1c1a9','#f0d1b2'].map(C);
const ROOF=['#a76356','#8d8680','#d5d2c3','#97654c','#b7b9b1'].map(C);
function shadow(g,x,z,w,d){g.box(x,.018,z,w,.016,d,C('#7c796b'));}
function building(g,x,z,w,d,h,seed){const rnd=rand(seed),co=BUILD[Math.floor(rnd()*BUILD.length)];shadow(g,x+.55,z+.7,w+1.5,d+1.4);g.box(x,h/2,z,w,h,d,co);g.box(x,h+.12,z,w+.55,.24,d+.5,ROOF[Math.floor(rnd()*ROOF.length)]);
 const levels=Math.max(1,Math.floor(h/3));for(let side of [-1,1])for(let k=0;k<levels;k++)for(let j=-1;j<=1;j++){
   let zf=z+j*d*.27,xf=x+side*(w/2+.018);g.box(xf,1.65+k*2.83,zf,.045,1.32,.92,C('#537b89'));g.box(xf+side*.03,1.59+k*2.83,zf,.052,.07,1.03,C('#dde7de'));
 }
 // Windows on the second façade; avoids untextured block walls from road view
 for(let side of [-1,1])for(let k=0;k<levels;k++)for(let j=-1;j<=1;j++){
   let xx=x+j*w*.26,zz=z+side*(d/2+.018);
   const y=1.7+k*2.83;g.quad([xx-.475,y-.62,zz],[xx+.475,y-.62,zz],[xx+.475,y+.62,zz],[xx-.475,y+.62,zz],C('#6e95a4'),[0,0,side]);
   const sill=y-.55,zs=zz+side*.025;g.quad([xx-.51,sill-.035,zs],[xx+.51,sill-.035,zs],[xx+.51,sill+.035,zs],[xx-.51,sill+.035,zs],C('#dfe7e3'),[0,0,side]);
 }
 if(seed%3===1){g.box(x,.94,z+d/2+.055,1.65,1.88,.11,C('#465d66'));g.box(x,2.62,z+d/2+.20,2.95,.30,.46,C('#e5b14c'));}
 // Storefront facing road with colored canopy; every other lot
 if(seed%3!==0){g.box(x-w/2-.15,2.6,z,1.45,.2,Math.min(d*.72,4.2),seed%2?P.yellow:C('#4ca9a4'));g.box(x-w/2-.17,1.1,z,1.4,1.65,Math.min(d*.58,3.25),C('#455a66'));}
 if(seed%5===0){g.box(x-w/2-.2,3.4,z,1.1,.9,Math.min(d*.68,4),C('#f1c857'));}
}
function palm(g,x,z,size=1){g.cy(x,0,z,.22*size,6.2*size,6,C('#6b6851'),.13*size);for(let k=0;k<8;k++){let a=k*Math.PI/4,dx=Math.cos(a),dz=Math.sin(a);let p=[x,6.2*size,z],q=[x+dx*2.2*size,6.8*size,z+dz*2.2*size],r=[x+dx*4.3*size,4.7*size,z+dz*4.3*size],sw=[-dz*.75*size,0,dx*.75*size];g.tri(p,[q[0]+sw[0],q[1],q[2]+sw[2]],r,k%2?C('#377f69'):C('#439976'));g.tri(p,r,[q[0]-sw[0],q[1],q[2]-sw[2]],C('#32816d'));}}
function stall(g,x,z,seed){const cols=['#f5c449','#e66d5b','#54a4a5','#68a37b'];let c=C(cols[seed%cols.length]);g.box(x,1,z,5,2.0,3,C('#987f5d'));g.box(x,2.35,z,6,.18,4,c);for(const s of [-1,1])g.box(x+s*2.3,1.2,z+s*.1,.1,2.3,.1,P.metal);g.box(x,1.2,z+1.55,4,.45,.28,C('#efbb72'));}
function lamp(g,x,z){g.cy(x,0,z,.115,7.1,6,C('#68757c'),.08);g.box(x-.94,7.05,z,2.0,.12,.12,P.metal);g.box(x-1.8,7.05,z,.5,.18,.45,C('#ffe2a0'));}
function bench(g,x,z){g.box(x,.7,z,2.15,.16,.55,C('#a56e43'));for(const s of [-.82,.82])g.box(x+s,.35,z,.1,.65,.5,P.dark);}
function person(g,x,z,shirt=P.yellow){g.box(x,.46,z,.34,.82,.23,C('#314257'));g.box(x,1.3,z,.50,.83,.35,shirt);g.cy(x,1.73,z,.23,.38,8,P.skin);g.box(x-.2,.24,z,.16,.45,.18,P.dark);g.box(x+.2,.24,z,.16,.45,.18,P.dark);}
export function makeWorld(){const g=new Geo();g.box(0,-.24,0,390,.34,390,C('#879977'));
 const streets=[-120,0,120];
 for(const v of streets){g.box(v,-.025,0,18,.10,365,P.asphalt);g.box(0,-.017,v,365,.11,18,P.asphalt);
  for(const o of [-9.4,9.4]){g.box(v+o,.055,0,.20,.028,365,P.line);g.box(0,.064,v+o,365,.028,.20,P.line);}
  for(let t=-177;t<178;t+=13){let cross=streets.some(v2=>Math.abs(t-v2)<15);if(cross)continue;g.box(v,.060,t,.19,.022,5,P.yellow);g.box(t,.067,v,5,.022,.19,P.yellow);}
 }
 // Shallow raised road features are meshed from the same profile sampled by the tires.
 for(const b of SPEED_BUMPS){
   const steps=16,side=8.70;
   for(let k=0;k<steps;k++){
     const u0=-b.halfLength+2*b.halfLength*k/steps,u1=-b.halfLength+2*b.halfLength*(k+1)/steps;
     const h0=ROAD_TOP_Y+b.height*smoothBump(u0,b.halfLength),h1=ROAD_TOP_Y+b.height*smoothBump(u1,b.halfLength);
     const color=C(k%2?'#bdb4a1':'#c6bc9f');
     if(b.axis==='z')g.quad([b.road-side,h0,b.along+u0],[b.road+side,h0,b.along+u0],[b.road+side,h1,b.along+u1],[b.road-side,h1,b.along+u1],color,[0,1,0]);
     else g.quad([b.along+u0,h0,b.road-side],[b.along+u1,h1,b.road-side],[b.along+u1,h1,b.road+side],[b.along+u0,h0,b.road+side],color,[0,1,0]);
   }
 }
 // paved blocks between/at edges
 const bounds=[-184,-130,-110,-10,10,110,130,184];
 const slots=[[-184,-130],[-110,-10],[10,110],[130,184]];
 let seed=1;
 for(const [xl,xr] of slots)for(const [zl,zr] of slots){
 const xc=(xl+xr)/2,zc=(zl+zr)/2,w=xr-xl,d=zr-zl;g.box(xc,-.004,zc,w,.11,d,P.pavement);
 const rows=(w>80?3:2),cols=(d>80?3:2),dx=w/rows,dz=d/cols;
 for(let i=0;i<rows;i++)for(let j=0;j<cols;j++){
   let cx=xl+(i+.5)*dx,cz=zl+(j+.5)*dz,rr=rand(seed*991+31);let s=seed++;if(cx>10&&cx<58&&cz>52&&cz<110)continue;
   if((s*13)%11===0){stall(g,cx,cz,s);palm(g,cx+dx*.28,cz+dz*.26,.75);}else if((s*7)%19===0){palm(g,cx,cz,1.05);bench(g,cx+2,cz-2);}else{building(g,cx,cz,dx*.70,dz*.69,3.6+rr()*8.6,s);}
 }
 }
 // The hand-authored starter neighborhood: a WEWA stop with a recognizable
 // shelter, yellow roof and motorcycle waiting bays, all merged into the world
 // geometry's existing single draw call (zero added runtime mesh objects).
 g.box(-11.2,1.85,85,3.2,.18,5.3,P.yellow);
 for(const z of [82.6,87.4])for(const x of [-12.6,-9.8])g.box(x,1.0,z,.13,2.0,.13,P.metal);
 g.box(-11.3,.44,85,2.7,.20,1.0,C('#a87f50'));
 g.box(-8.8,1.55,82.2,.16,3.1,.16,P.dark);
 g.box(-8.8,2.92,82.25,.20,.52,.6,P.yellow);
 for(const x of [-7.5,-3.0])g.box(x,.070,87.3,1.6,.024,.19,P.line);
 // corner vegetation, street infrastructure and market activity
 let n=0;
 for(const x of streets)for(const z of streets){for(const sx of [-1,1])for(const sz of [-1,1]){
  let px=x+sx*15,pz=z+sz*15;if(Math.abs(px)>175||Math.abs(pz)>175)continue;
  if(n++%3===0)palm(g,px,pz,.67);else lamp(g,px,pz);
 }
 for(const sx of [-1,1])for(const sz of [-1,1]){
 // dashed crosswalks before intersections
 for(let j=0;j<5;j++){g.box(x+(j-2)*2.8,.064,z+sz*13,1.5,.028,.75,P.line);g.box(x+sx*13,.064,z+(j-2)*2.8,.75,.028,1.5,P.line);}
 }}
 for(let i=0;i<29;i++){const rr=rand(i*1241+9),axis=i%2,road=streets[Math.floor(rr()*3)],side=(i%2?1:-1),along=-160+rr()*320;let x=axis?along:road+side*12.8,z=axis?road+side*12.8:along; person(g,x,z,[P.yellow,C('#54b0bc'),C('#c3535c'),C('#e7f0cc')][i%4]);}
 for(let i=0;i<9;i++){let s=streets[i%3],v=-150+(i*44)%300;stall(g,(i%2)?v:s+16,(i%2)?s+16:v,i);}
 return g;
}
export function makeBikeWheel(){
 const g=new Geo(),r=.49,w=.24,side=w*.5,n=20;
 const tire=C('#151a20'),tread=C('#20242a'),rim=C('#c9d5dc'),inner=C('#6e828e'),bolt=C('#a5b4ba');
 for(let i=0;i<n;i++){
   const a=i*Math.PI*2/n,b=(i+1)*Math.PI*2/n;
   const r0=r*.79;
   for(const x of [-side,side]){
     const outerA=[x,r*Math.cos(a),r*Math.sin(a)],outerB=[x,r*Math.cos(b),r*Math.sin(b)];
     const inA=[x,r0*Math.cos(a),r0*Math.sin(a)],inB=[x,r0*Math.cos(b),r0*Math.sin(b)];
     g.quad(outerA,outerB,inB,inA,tire);
   }
   g.quad([-side,r*Math.cos(a),r*Math.sin(a)],[-side,r*Math.cos(b),r*Math.sin(b)],
       [side,r*Math.cos(b),r*Math.sin(b)],[side,r*Math.cos(a),r*Math.sin(a)],tread);
   for(let x of [-side-.018,side+.018]){
     let k=.70;
     g.quad([x,k*r*Math.cos(a),k*r*Math.sin(a)],[x,k*r*Math.cos(b),k*r*Math.sin(b)],
       [x,k*.55*r*Math.cos(b),k*.55*r*Math.sin(b)], [x,k*.55*r*Math.cos(a),k*.55*r*Math.sin(a)],rim);
   }
 }
 // Radial spokes, hub and brake discs produce a recognizable metal motorcycle wheel.
 for(let x of [-side-.025,side+.025])for(let i=0;i<10;i++){
   let a=i*Math.PI*2/10;
   g.tube([x,0,0],[x,.33*Math.cos(a),.33*Math.sin(a)],.015,bolt,5);
 }
 g.tube([-.18,0,0],[.18,0,0],.13,inner,10);
 return g;
}
export function makeBike(passenger=false){
 let g=new Geo();
 const frame=C('#394852'),chrome=C('#c9d6db'),rubber=C('#1d232a'),seat=C('#252c34'),engine=C('#687780');
 const yellow=C('#f5c439'),deepYellow=C('#d29b19'),tail=C('#a93534'),glass=C('#f9e1a7');
 const body={top:[0,1.60,.32],head:[0,1.75,.89],rear:[0,1.28,-.91],motor:[0,1.04,-.10]};
 // Backbone, triangulated structural frame and swingarm.
 for(const side of [-1,1]){
   const xx=side*.21;
   g.tube([xx,1.45,.43],[xx,1.26,-.78],.067,frame);
   g.tube([xx,1.41,.36],[xx,.92,-.20],.060,frame);
   g.tube([xx,.92,-.20],[xx,1.22,-.77],.062,frame);
   g.tube([xx,1.26,-.77],[xx,.55,-1.1],.072,chrome);
   g.tube([xx*.8,1.73,.88],[xx*.8,.60,1.10],.068,chrome);
 }
 g.tube([0,1.58,-.85],[0,1.68,.72],.060,frame);
 // Engine, cooling fins and exhaust attached to the frame.
 g.ellipsoid(0,1.03,.05,.37,.28,.49,engine,14,7);
 for(let k=0;k<5;k++)g.box(0,.88+k*.083,.04,.86,.030,.72,k%2?C('#59646d'):chrome);
 g.tube([-.40,.97,.1],[-.47,.82,-.83],.07,chrome);
 g.tube([-.47,.82,-.83],[-.43,.78,-1.43],.125,chrome);
 // Fuel tank is a rounded shape; color trim and side panels identify the taxi motorbike.
 g.ellipsoid(0,1.56,.13,.43,.28,.62,yellow,16,10);
 for(let side of [-1,1])g.ellipsoid(side*.37,1.43,.02,.11,.20,.41,deepYellow,10,5);
 g.ellipsoid(0,1.48,-.78,.46,.12,.74,seat,14,6);
 g.ellipsoid(0,1.33,-1.35,.28,.11,.34,seat,10,5);
 // A sculpted front mudguard and tail cowl.
 g.ellipsoid(0,1.04,1.08,.35,.12,.57,deepYellow,12,5);
 g.ellipsoid(0,1.37,-1.27,.38,.16,.38,yellow,10,6);
 g.box(0,1.30,-1.57,.33,.13,.07,tail);
 g.ellipsoid(0,1.47,1.44,.27,.25,.22,chrome,12,8);
 g.ellipsoid(0,1.47,1.66,.19,.18,.075,glass,12,8);
 // Handlebar, grips, mirror stalks, footrests.
 g.tube([-.65,1.94,.83],[.65,1.94,.83],.050,frame);
 for(const side of [-1,1]){
   g.tube([side*.55,1.94,.83],[side*.72,1.94,.83],.071,rubber);
   g.tube([side*.60,1.96,.84],[side*.77,2.21,.93],.024,chrome);
   g.ellipsoid(side*.79,2.24,.93,.16,.13,.09,rubber,9,6);
   g.tube([side*.26,1.02,-.32],[side*.48,1.02,-.28],.052,chrome);
 }
 // Driver's legs and jacket: articulated looking limbs, helmet and face shield.
 let skin=C('#986642'),trousers=C('#324457'),jacket=C('#e5b93b');
 g.ellipsoid(0,2.18,-.34,.44,.56,.34,jacket,12,8);
 for(const side of [-1,1]){
   g.tube([side*.32,2.31,-.15],[side*.50,1.88,.38],.132,jacket,8);
   g.tube([side*.50,1.88,.38],[side*.58,1.93,.80],.094,skin,8);
   g.tube([side*.25,1.65,-.50],[side*.34,1.24,-.16],.19,trousers,10);
   g.tube([side*.34,1.24,-.16],[side*.48,.96,-.35],.135,trousers,8);
   g.ellipsoid(side*.49,.94,-.25,.17,.11,.25,rubber,8,5);
 }
 g.tube([0,2.44,-.39],[0,2.69,-.31],.17,skin);
 g.ellipsoid(0,2.82,-.30,.34,.38,.33,C('#b73334'),14,9);
 g.ellipsoid(0,2.82,-.01,.28,.15,.065,C('#2b3d51'),12,6);
 if(passenger){
   let green=C('#52a6a1');
   g.ellipsoid(0,2.09,-1.18,.41,.52,.33,green,12,8);
   for(const side of [-1,1]){
     g.tube([side*.26,1.73,-1.13],[side*.39,1.18,-1.18],.17,C('#344452'),9);
     g.tube([side*.36,2.31,-1.0],[side*.42,1.84,-.52],.096,green,8);
   }
   g.tube([0,2.43,-1.2],[0,2.68,-1.2],.15,skin);
   g.ellipsoid(0,2.88,-1.18,.31,.34,.29,C('#354a4c'),12,9);
 }
 return g;
}
export function makeCar(kind=0){let g=new Geo();let colors=['#f2db98','#74b7c0','#d56858','#d2d7d7','#b9c18e','#edbf45'].map(C);let col=colors[kind%colors.length];let bus=kind%5===4,L=bus?6.3:4.2,H=bus?2.4:1.85,W=bus?2.18:1.94;
 for(const z of [-L*.34,L*.34])for(const x of [-W*.45,W*.45])g.wheel(x,.45,z,.47,.18,P.tire);
 g.box(0,.72,0,W,1.0,L,col);g.box(0,1.37,0,W*.84,bus?1.3:.77,L*.55,C('#6d9daa'));g.box(0,bus?2.12:1.73,0,W*.85,.17,L*.6,col);
 for(const side of [-1,1]){g.box(side*W*.43,1.37,0,.07,.55,L*.50,C('#527e90'));}
 for(const sx of [-.65,.65]){g.box(sx,.79,L/2+.01,.31,.18,.07,C('#f8efb4'));g.box(sx,.78,-L/2-.01,.31,.16,.07,C('#d45242'));}
 if(bus){g.box(0,.9,L*.2,W*.7,.3,.12,C('#f1d5a6'));}return g;
}
export function makeMarker(type='pickup'){const g=new Geo();let co=type==='garage'?C('#6ff0e4'):type==='drop'?C('#9bf2c3'):P.yellow;let small=type==='garage',radius=small?1.25:2.35,height=small?2.6:4.3;g.cy(0,.14,0,radius,.09,20,co);g.cy(0,.15,0,radius*.62,.09,20,P.line);g.cy(0,.25,0,.36,height,12,co,.36);g.cy(0,.25+height,0,.69,.65,12,co,.05);return g;}
export function makeGarage(){const g=new Geo();g.box(0,2.7,0,15,5.4,12,C('#6f867e'));g.box(0,5.5,0,17,.55,14,C('#bb8c60'));g.box(0,2.2,6.05,10,4.4,.12,C('#354f5b'));g.box(0,4.65,6.2,11,.72,.20,P.yellow);g.box(-4.2,1.0,6.24,1.5,2,.16,P.metal);g.box(4.2,1.0,6.24,1.5,2,.16,P.metal);return g;}
