import {clamp,lerp,wrapAngle,hypot,dist,heading,angleOf,nearestRoad,keepOverStreet,STREET_SAFE_HALF_WIDTH,rand} from './math.js';
import {advanceBike,createBikeTelemetry,BIKE_WHEEL_RADIUS} from './bike_physics.js';
import {inspectBikeCar,closingSpeed} from './collision.js';
import {observeRide,addRideDiscomfort,rideComfortPaymentMultiplier} from './ride_quality.js';
import {advanceChallenge} from './challenge.js';
export const VERSION='KIN-MOTO-NEXT-V1-1.0.0-REVIEW';
export const PLACES=[
 {id:'victoire',name:'PLACE VICTOIRE',x:13,z:12,kind:'place'},
 {id:'matonge',name:'MATONGE',x:13,z:-73,kind:'place'},
 {id:'ecole',name:'ÉCOLE DES ARTS',x:-13,z:64,kind:'school'},
 {id:'marche',name:'MARCHÉ CENTRAL',x:109,z:13,kind:'market'},
 {id:'clinique',name:'CLINIQUE DU QUARTIER',x:-108,z:-13,kind:'medical'},
 {id:'restaurant',name:'MAISON DE LA RUMBA',x:13,z:157,kind:'music'},
 {id:'station',name:'STATION MOTO',x:109,z:-13,kind:'station'},
 {id:'residence',name:'RÉSIDENCE BANDAL',x:-13,z:-78,kind:'home'},
 {id:'arret',name:'ARRÊT WEWA DE BANDAL',x:-7,z:85,kind:'slice'},
 {id:'garage',name:'GARAGE KIN MOTO',x:14,z:78,kind:'garage'}
];
const NAMES=['Maman Chantal','Papa Serge','Junior','Mado','Coach Patrick','Maman Carine','Sarah','Nadine','Christelle','Blaise','Madame Esther'];
const KINDS=[{id:'taxi',name:'COURSE WEWA',mult:1,description:'Un passager attend sa course.'},{id:'express',name:'RENDEZ-VOUS',mult:1.22,description:'Un client souhaite arriver sans retard.'},{id:'colis',name:'LIVRAISON',mult:1.10,description:'Transport d’un colis, conduite souple.'},{id:'tour',name:'DÉCOUVERTE',mult:1.30,description:'Un trajet découverte avec un arrêt supplémentaire.'}];
// A3 vertical-slice missions: a hand-authored, navigable first neighborhood,
// no external assets, no new economy schema, and a deterministic continuation.
export const SLICE_STORY=Object.freeze([
 Object.freeze({from:'arret',to:'ecole',kind:'taxi',title:'01 · COURSE DU QUARTIER',client:'Maman Chantal',reward:850,description:'Départ de Bandal, direction École des Arts.'}),
 Object.freeze({from:'ecole',to:'victoire',kind:'colis',title:'02 · COLIS POUR VICTOIRE',client:'Junior',reward:1150,description:'Récupérer le colis à l’école et livrer près de la Place Victoire.'})
]);
// A special customer has a real comfort and time premium distinct from taxi and delivery.
export const VIP_STORY=Object.freeze({ride:2,from:'victoire',to:'matonge',kind:'vip',title:'03 · CLIENT SPÉCIAL',client:'Docteur Alain',reward:1450,description:'Conduite douce et ponctuelle : trajet VIP à Matonge.'});
const DEFAULT_SAVE={schema:1,cash:3500,rides:0,engine:1,brakes:1,health:100,stars:4.5,finished:0,highScore:0};
export const SAVE_KEY='kinmoto_a2_lab_career';
export function readSave(storage){
 try{
  storage=storage||globalThis.localStorage;
  const o=JSON.parse(storage.getItem(SAVE_KEY)||'null');
  if(o&&o.schema===1&&Number.isFinite(o.cash)&&o.cash>=0){
   const safe=(v,defaultValue,min,max,integer=false)=>
     typeof v==='number'&&Number.isFinite(v)?clamp(integer?Math.floor(v):v,min,max):defaultValue;
   // Never let a corrupt localStorage value break the HUD's numeric operations.
   return {schema:1,
    cash:safe(o.cash,DEFAULT_SAVE.cash,0,1e12,true),
    rides:safe(o.rides,DEFAULT_SAVE.rides,0,1e7,true),
    engine:safe(o.engine,DEFAULT_SAVE.engine,1,4,true),
    brakes:safe(o.brakes,DEFAULT_SAVE.brakes,1,4,true),
    health:safe(o.health,DEFAULT_SAVE.health,0,100),
    stars:safe(o.stars,DEFAULT_SAVE.stars,1,5),
    finished:safe(o.finished,DEFAULT_SAVE.finished,0,1e7,true),
    highScore:safe(o.highScore,DEFAULT_SAVE.highScore,0,1e12,true)};
  }
 }catch{}
 return {...DEFAULT_SAVE};
}
export function writeSave(data,storage){try{storage=storage||globalThis.localStorage;storage.setItem(SAVE_KEY,JSON.stringify(data));return true}catch{return false}}
export function makeRoute(left,top,right,bottom){const l=left+4.6,r=right-4.6,t=top+4.6,b=bottom-4.6;
 // Corner trajectories must stay inside the asphalt CROSS, not cut across
 // building blocks at diagonals (old 3m/7m corner reached 9.6m from roads).
 // Intermediate points keep the route <= 6.2m from an intersection road axis.
 const pts=[{x:l,z:b-15},
 {x:l,z:t+15},{x:l,z:t+6},{x:l+1.5,z:t+1.5},{x:l+6,z:t},{x:l+15,z:t},
 {x:r-15,z:t},{x:r-6,z:t},{x:r-1.5,z:t+1.5},{x:r,z:t+6},{x:r,z:t+15},
 {x:r,z:b-15},{x:r,z:b-6},{x:r-1.5,z:b-1.5},{x:r-6,z:b},{x:r-15,z:b},
 {x:l+15,z:b},{x:l+6,z:b},{x:l+1.5,z:b-1.5},{x:l,z:b-6}];let segments=[],length=0;for(let i=0;i<pts.length;i++){const a=pts[i],b=pts[(i+1)%pts.length],d=dist(a,b);segments.push({a,b,start:length,len:d});length+=d;}return {segments,length};}
const LOOPS=[makeRoute(-120,-120,0,0),makeRoute(0,-120,120,0),makeRoute(-120,0,0,120),makeRoute(0,0,120,120)];
export function sampleRoute(route,m){m=((m%route.length)+route.length)%route.length;for(const s of route.segments){if(m<=s.start+s.len){let t=(m-s.start)/Math.max(.00001,s.len);return {x:lerp(s.a.x,s.b.x,t),z:lerp(s.a.z,s.b.z,t),yaw:angleOf(s.b.x-s.a.x,s.b.z-s.a.z)};}}const s=route.segments[0];return {...s.a,yaw:angleOf(s.b.x-s.a.x,s.b.z-s.a.z)};}
// Traffic is strictly forward-moving: cache the current route segment instead
// of scanning all 20 segments for every car on all 60 simulation ticks.
// If a test or recovery changes u backwards, the cached pointer also rewinds.
function sampleTrafficRoute(route,u,car){
 const segments=route.segments;
 let i=car.routeSegmentIndex||0;
 if(u<segments[i].start)i=0;
 while(i+1<segments.length&&u>segments[i].start+segments[i].len)i++;
 const seg=segments[i],t=clamp((u-seg.start)/Math.max(.00001,seg.len),0,1);
 car.routeSegmentIndex=i;
 const out=car.routeSample||(car.routeSample={x:0,z:0,yaw:0});
 out.x=lerp(seg.a.x,seg.b.x,t);out.z=lerp(seg.a.z,seg.b.z,t);
 out.yaw=angleOf(seg.b.x-seg.a.x,seg.b.z-seg.a.z);
 return out;
}
function newMission(ride=0){
 if(ride<SLICE_STORY.length||ride===VIP_STORY.ride){const a=ride===VIP_STORY.ride?VIP_STORY:SLICE_STORY[ride];return {ride,kind:a.kind,title:a.title,from:a.from,to:a.to,via:null,stage:'pickup',client:a.client,reward:a.reward,penalty:0,comfort:100,impacts:0,startedAt:0,timer:0};}
 const r=rand(7946+ride*773),options=PLACES.filter(p=>p.kind!=='garage'&&p.kind!=='slice');const from=options[(ride*3+1)%options.length];let to=options[(ride*5+4)%options.length];if(from.id===to.id)to=options[(options.indexOf(to)+3)%options.length];const kind=KINDS[ride%KINDS.length],length=Math.abs(from.x-to.x)+Math.abs(from.z-to.z),reward=Math.round((750+length*10)*kind.mult/50)*50;
 let via=kind.id==='tour'?options[(ride*2+5)%options.length]:null;if(via&&(via.id===from.id||via.id===to.id))via=options[(ride*2+6)%options.length];return {ride,kind:kind.id,title:kind.name,from:from.id,to:to.id,via:via?.id||null,stage:'pickup',client:NAMES[ride%NAMES.length],reward,penalty:0,comfort:100,impacts:0,startedAt:0,timer:0};}
export const byId=id=>PLACES.find(p=>p.id===id);
export const missionTarget=m=>byId(m.stage==='pickup'?m.from:m.stage==='via'?m.via:m.to);
export function makeGame(snapshot=null){let previous=snapshot||{};let save={...DEFAULT_SAVE,...(previous.save||{})};let player={x:4.4,z:95,speed:0,yaw:0,lean:0,damageCooldown:0,meters:0,bike:createBikeTelemetry(),...(previous.player||{})};
 let m=(previous.mission&&byId(previous.mission.from)&&byId(previous.mission.to))?{...previous.mission}:newMission(save.rides);
 let cars=[];let count=0;for(let loop=0;loop<LOOPS.length;loop++)for(let j=0;j<4;j++){
  const path=LOOPS[loop],u=(j/4)*path.length+(loop*19)%20,p=sampleRoute(path,u);
  cars.push({id:count++,loop,u,speed:4+(j%3)*2,preferred:6.5+(count%4)*1.5,kind:count%6, stun:0, x:p.x,z:p.z,yaw:p.yaw});
 }
 const game={save,player,mission:m,cars,clock:0,events:[],playing:false,paused:false,controls:{left:false,right:false,gas:false,brake:false},travel:0,collisions:0,nearMisses:0,stats:{steps:0,lastSave:0}};
 return game;
}
export function snapshot(g){return {schema:1,version:VERSION,save:{...g.save},player:{x:g.player.x,z:g.player.z,yaw:g.player.yaw,speed:0,lean:0,damageCooldown:0,meters:g.player.meters},mission:{...g.mission}}}
export const emit=(g,type,message)=>{g.eventSeq=(g.eventSeq||0)+1;g.events.push({type,message,at:g.clock,seq:g.eventSeq});if(g.events.length>35)g.events.shift();};
const signedDistance=(a,b)=>dist(a,b);
/** Target speed under car-following and intersection yielding, no allocations. */
export function trafficTargetSpeed(car,cars){
 let v=car.stun>0?Math.min(1.7,car.preferred*.2):car.preferred;
 const path=LOOPS[car.loop];
 let ahead=Infinity;
 const fx=Math.sin(car.yaw),fz=-Math.cos(car.yaw),rx0=Math.cos(car.yaw),rz0=Math.sin(car.yaw);
 for(const other of cars){if(other===car)continue;
  if(other.loop===car.loop){const gap=(other.u-car.u+path.length)%path.length;if(gap>0&&gap<ahead)ahead=gap;}
  const rx=other.x-car.x,rz=other.z-car.z;
  const along=rx*fx+rz*fz,side=Math.abs(rx*rx0+rz*rz0);
  if(along>0&&along<15&&side<3.3)v=Math.min(v,Math.max(0,(along-3.6)*1.03));
  else if(other.loop!==car.loop&&other.id<car.id&&along>0&&along<12&&side<7.5&&Math.abs(Math.sin(other.yaw-car.yaw))>.65)
    v=Math.min(v,Math.max(0,(along-6)*1.20));
 }
 if(ahead<16)v=Math.min(v,clamp((ahead-5)*.9,0,car.preferred));
 return Math.max(0,v);
}
export function step(g,dt){const p=g.player,c=g.controls;if(!g.playing||g.paused)return;dt=clamp(dt,0,.04);g.clock+=dt;g.stats.steps++;p.damageCooldown=Math.max(0,p.damageCooldown-dt);
 const grip=clamp(g.save.health/100,.40,1);let onRoad=nearestRoad(p).distance<9.7;
 const ox=p.x,oz=p.z,wheelSpinBefore=p.bike?.wheelSpin??0;
 const drive=advanceBike(p,{
   steer:(c.right?1:0)-(c.left?1:0),gas:c.gas?1:0,brake:c.brake?1:0
 },dt,{condition:grip,roadGrip:onRoad?1:.77,
   engine:g.save.engine,brakes:g.save.brakes,maxSpeed:onRoad?22.6:8});
 p.x=clamp(p.x,-175,175);p.z=clamp(p.z,-175,175);
 const road=nearestRoad(p);
 // The motorcycle is not allowed to penetrate the buildings. Previous builds
 // permitted 14.5 m lateral offset on an 18 m road (asphalt half-width = 9 m),
 // which made the rider visibly enter building façades. Clamp the actual body
 // to a safe road envelope, keeping the forward slide tangential to the curb.
 if(keepOverStreet(p)){
   const impactSpeed=p.speed;
   p.speed=Math.min(p.speed,Math.max(2.2,p.speed*.55));
   p.bike.vx=Math.sin(p.yaw)*p.speed;
   p.bike.vz=-Math.cos(p.yaw)*p.speed;
   p.bike.lastSpeed=p.speed;
   if(p.damageCooldown<=0&&impactSpeed>5){
     p.damageCooldown=1.2;
     if(!g.challenge?.active)g.save.health=clamp(g.save.health-Math.min(4,impactSpeed*.16),0,100);
     emit(g,'warning','Bordure : ralentis et reste sur la chaussée.');
     g.curbContacts=(g.curbContacts||0)+1;
   }
 } else if(road.distance>STREET_SAFE_HALF_WIDTH-1.2){
   // Near the edge tyres lose some grip; do not force a teleport or fake skid.
   p.speed=Math.min(p.speed,12.5);
 }
 // The tire cannot spin for motion canceled by the road envelope or world bounds.
 // Keep the controller reusable; override its free-body travel with ground-resolved travel.
 const roadTravel=hypot(p.x-ox,p.z-oz);
 p.bike.groundSpeed=dt>0?roadTravel/dt:0;
 p.bike.wheelSpin=wheelSpinBefore+roadTravel/BIKE_WHEEL_RADIUS;
 p.meters+=roadTravel;g.travel+=roadTravel;
 if(!g.challenge?.active)observeRide(g.mission,p.bike,p.speed,dt);
 // Four real-road loops, spatial sensing, deterministic intersection priority.
 for(const car of g.cars){
  const oldCarX=car.x,oldCarZ=car.z;
  car.stun=Math.max(0,(car.stun||0)-dt);
  let v=trafficTargetSpeed(car,g.cars);
  const path=LOOPS[car.loop];
 // The traffic must yield to a slow bike without freezing indefinitely:
 // when a lane is blocked ahead, change lateral lane bias gradually toward
 // the *opposite* side of the rider, only if the target stays on asphalt.
 const relX=p.x-car.x,relZ=p.z-car.z,fx=Math.sin(car.yaw),fz=-Math.cos(car.yaw);
 const along=relX*fx+relZ*fz,side=relX*Math.cos(car.yaw)+relZ*Math.sin(car.yaw);
 const blocking=along>0&&along<13&&Math.abs(side)<2.75&&p.speed<car.preferred+2;
 if(blocking){
   if(!(car.avoidUntil>g.clock)){
     const desired=side>=0?-2.9:2.9;
     const here=sampleTrafficRoute(path,car.u,car);
     const sx=Math.cos(here.yaw),sz=Math.sin(here.yaw);
     const candidate={x:here.x+sx*desired,z:here.z+sz*desired};
     // Never initiate an overtake into a neighboring kinematic vehicle.
     const laneClear=g.cars.every(other=>other===car||Math.hypot(other.x-candidate.x,other.z-candidate.z)>5.0);
     if(nearestRoad(candidate).distance<=7.1&&laneClear){car.avoidTarget=desired;car.avoidUntil=g.clock+3.5;}
   }
   // Brake until the remaining nose gap is safe, then proceed past the rider.
   if(Math.abs(side)<2.4)v=Math.min(v,Math.max(0,(along-3.8)*1.0));
 }
 if(!(car.avoidUntil>g.clock))car.avoidTarget=0;
 car.braking=v<car.speed-.15;
 car.speed=lerp(car.speed,v,dt*(v<car.speed?3.5:1.2));car.u=(car.u+car.speed*dt)%path.length;
 const pos=sampleTrafficRoute(path,car.u,car);
 const bias=car.avoidTarget||0;
 // The normal case is a car following its original lane. Do not run the
 // sidestep vector math or road query for all 16 cars on every 60Hz tick.
 if(bias||car.avoidDX||car.avoidDZ){
   const sideX=Math.cos(pos.yaw),sideZ=Math.sin(pos.yaw);
   // Smooth *world-space* displacement so a sudden corner heading does not
   // teleport a biased car sideways by metres in one frame.
   let dx=sideX*bias-(car.avoidDX||0),dz=sideZ*bias-(car.avoidDZ||0);
   const shift=Math.hypot(dx,dz),maxShift=3.1*dt;
   if(shift>maxShift){dx*=maxShift/shift;dz*=maxShift/shift;}
   const avoidDX=(car.avoidDX||0)+dx,avoidDZ=(car.avoidDZ||0)+dz;
   const candidate={x:pos.x+avoidDX,z:pos.z+avoidDZ};
   if(nearestRoad(candidate).distance<=7.2){car.avoidDX=avoidDX;car.avoidDZ=avoidDZ;}
   car.x=pos.x+(car.avoidDX||0);car.z=pos.z+(car.avoidDZ||0);
 }else{car.x=pos.x;car.z=pos.z;}
 car.yaw=pos.yaw;
 // The visual chassis should steer into a lane change instead of sliding
 // sideways while the collider continues to follow its road-aligned route.
 // Avoid a global atan2 every frame for the 15 unaffected vehicles.
 if((bias||car.avoidDX||car.avoidDZ)&&car.speed>1&&dt>0){
   const vx=car.x-oldCarX,vz=car.z-oldCarZ;
   if(Math.hypot(vx,vz)>.025){
     const yawDelta=wrapAngle(angleOf(vx,vz)-car.yaw);
     car.visualYaw=car.yaw+clamp(yawDelta,-.30,.30);
   }else car.visualYaw=car.yaw;
 }else car.visualYaw=car.yaw;
 }
 // Oriented box/car vs disc/bike contact: a parallel overtake must not
 // trigger a collision simply because the two vehicle centers are <3.1m.
 const contact=g._contactScratch||(g._contactScratch={});
 for(const car of g.cars){
   inspectBikeCar(p,car,contact);
   if(contact.hit){
     const approach=closingSpeed(p,car,contact);
     // Avoid a one-frame multi-metre teleport if an imported or spawned state
     // starts with the bike already inside a car. Resolve overlap across a
     // bounded number of fixed physics ticks instead of moving the whole depth.
     // The penetration correction is NOT propulsion and is excluded from wheel
     // rotation, odometer and ride-distance telemetry.
     const correction=Math.min(contact.overlap,.32);
     p.x=clamp(p.x+contact.normalX*correction,-175,175);
     p.z=clamp(p.z+contact.normalZ*correction,-175,175);
     g.peakContactCorrection=Math.max(g.peakContactCorrection||0,correction);
     g.contactCorrections=(g.contactCorrections||0)+1;
     if(p.damageCooldown<=0&&approach>1.2){
       car.stun=Math.max(car.stun||0,1.55);
       const severity=Math.min(18,3.5+approach*.88);
       if(!g.challenge?.active)g.save.health=clamp(g.save.health-severity,0,100);
       p.speed*=.23;p.bike.vx*=.23;p.bike.vz*=.23;p.bike.lastSpeed=p.speed;
       p.damageCooldown=1.3;g.collisions++;
       if(!g.challenge?.active){g.mission.penalty=(g.mission.penalty||0)+Math.round(severity*16);
       addRideDiscomfort(g.mission,Math.min(20,8+approach*1.35),'impact');}
       emit(g,'impact',`Accrochage ! -${Math.round(severity)} % d'état.`);
     }
   }else if(contact.nearMiss&&p.speed>5&&g.clock-(g.lastNearMiss||0)>4){
     g.nearMisses++;g.lastNearMiss=g.clock;
   }
 }
 // An impact can push the motorcycle outside the curb. Never leave it
 // inside a building at the end of the simulation step.
 if(keepOverStreet(p)){
   p.speed=Math.min(p.speed,5.0);
   p.bike.vx=Math.sin(p.yaw)*p.speed;
   p.bike.vz=-Math.cos(p.yaw)*p.speed;
   p.bike.lastSpeed=p.speed;
 }
 if((g.mission.kind==='express'||g.mission.kind==='vip')&&g.mission.stage!=='pickup'&&!g.challenge?.active){g.mission.timer+=dt;}
 const challengeEvent=advanceChallenge(g,dt);
 if(challengeEvent?.type==='gate')emit(g,'success',`PORTE ${challengeEvent.gate}/${challengeEvent.total} · + POINTS`);
 if(challengeEvent?.type==='complete')emit(g,'success',`DÉFI GAGNÉ · ${challengeEvent.score} PTS · ${challengeEvent.stars} ★`);
 if(challengeEvent?.type==='timeout')emit(g,'warning','Temps écoulé ! Réessaie pour battre ton record.');
 g.stats.lastSave+=dt;
}
export function interactionState(g){const p=g.player,t=missionTarget(g.mission),nearMission=t&&dist(p,t)<16,garage=byId('garage'),nearGarage=dist(p,garage)<15;
 const stopped=p.speed<3.1;return {nearMission:!!nearMission,nearGarage,stopped,missionDistance:t?Math.round(dist(p,t)):Infinity,target:t,garageDistance:Math.round(dist(p,garage))};}
export function interact(g){if(!g.playing||g.paused)return {ok:false,reason:'partie inactive'};const i=interactionState(g);
 if(i.nearMission){if(!i.stopped){emit(g,'warning','Ralentis sous 11 km/h pour t’arrêter.');return {ok:false,reason:'Ralentis'}}
  const m=g.mission;if(m.stage==='pickup'){m.stage=m.via?'via':'drop';m.startedAt=g.clock;m.timer=0;emit(g,'pickup',m.kind==='colis'?'Colis chargé, destination indiquée.':`${m.client} est à bord. Bonne route !`);return {ok:true,type:'pickup'};}
  if(m.stage==='via'){m.stage='drop';emit(g,'info','Arrêt effectué. Direction la destination finale !');return {ok:true,type:'via'};}
  if(m.stage==='drop'){let base=m.reward,late=m.kind==='express'?Math.max(0,m.timer-85)*8:m.kind==='vip'?Math.max(0,m.timer-115)*10:0,damages=m.penalty||0;
   const comfort=Math.max(0,Math.min(100,m.comfort??100));const multiplier=rideComfortPaymentMultiplier(m);
   const vipPremium=m.kind==='vip'?(m.comfort>=88&&m.impacts===0&&m.timer<=115?650:0):0;
   const payout=Math.max(250,Math.round((base*multiplier+vipPremium-late-damages)/50)*50);g.save.cash+=payout;g.save.rides++;g.save.finished++;g.save.stars=clamp(g.save.stars+(damages>0?-.08:comfort<60?-.05:comfort<85?0:.03),1,5);g.mission=newMission(g.save.rides);emit(g,'success',`Course terminée : +${payout.toLocaleString('fr-FR')} FC`);return {ok:true,type:'completed',payout};}
 }
 if(i.nearGarage){if(!i.stopped){emit(g,'warning','Freine pour entrer au garage.');return {ok:false,reason:'Ralentis'}}return {ok:true,type:'garage'};}
 emit(g,'info','Approche-toi du repère jaune pour interagir.');return {ok:false,reason:'Trop loin'};
}
export function buy(g,item){let costs={repair:Math.max(0,Math.ceil((100-g.save.health)*12/50)*50),engine:g.save.engine*2400,brakes:g.save.brakes*1800};let price=costs[item];if(price==null)return {ok:false,reason:'invalide'};
 if(item==='repair'&&price===0)return {ok:false,reason:'Moto en parfait état'};if(item!=='repair'&&g.save[item]>=4)return {ok:false,reason:'Niveau maximal'};
 if(g.save.cash<price)return {ok:false,reason:'Solde insuffisant'};g.save.cash-=price;if(item==='repair')g.save.health=100;else g.save[item]++;emit(g,'success',item==='repair'?'Moto réparée':`Amélioration ${item} installée`);return {ok:true,cost:price};}
export function validate(g){
 const issues=[];
 if(!g||typeof g!=='object'||!g.player||!g.save||!g.mission||!Array.isArray(g.cars))return ['invalid-game'];
 const p=g.player,s=g.save,m=g.mission,t=p.bike;
 const numeric=[p.x,p.z,p.speed,p.yaw,p.meters,s.cash,s.health,s.stars,s.rides,s.finished,s.highScore,s.engine,s.brakes,m.reward];
 if(numeric.some(v=>typeof v!=='number'||!Number.isFinite(v)))issues.push('non-finite');
 if(!(s.cash>=0&&s.cash<=1e12))issues.push('invalid-cash');
 if(!(s.health>=0&&s.health<=100))issues.push('invalid-health');
 if(!(s.stars>=1&&s.stars<=5))issues.push('invalid-stars');
 if(!Number.isSafeInteger(s.rides)||s.rides<0||s.rides>1e7||!Number.isSafeInteger(s.finished)||s.finished<0)issues.push('invalid-counters');
 if(!Number.isInteger(s.engine)||s.engine<1||s.engine>4||!Number.isInteger(s.brakes)||s.brakes<1||s.brakes>4)issues.push('invalid-upgrades');
 if(!(p.speed>=0&&p.speed<=35)||!(p.meters>=0))issues.push('invalid-player-motion');
 if(!(p.x>=-175&&p.x<=175&&p.z>=-175&&p.z<=175))issues.push('player-out-of-world');
 if(!t||[t.steer,t.vx,t.vz,t.wheelSpin,t.suspension].some(v=>typeof v!=='number'||!Number.isFinite(v)))issues.push('invalid-bike-telemetry');
 if(!byId(m.from)||!byId(m.to)||!['pickup','via','drop'].includes(m.stage)||!['taxi','express','colis','tour','vip'].includes(m.kind)||
    (m.stage==='via'&&!byId(m.via)))issues.push('invalid-mission');
 if(!(typeof m.reward==='number'&&Number.isFinite(m.reward)&&m.reward>=0&&m.reward<=1e9))issues.push('invalid-reward');
 for(const field of ['penalty','timer','comfort','impacts'])if(m[field]!==undefined&&(!Number.isFinite(m[field])||m[field]<0))issues.push('invalid-mission-'+field);
 if(g.cars.some(car=>!car||!Number.isFinite(car.x)||!Number.isFinite(car.z)||!Number.isFinite(car.speed)))issues.push('invalid-traffic');
 return issues;
}
