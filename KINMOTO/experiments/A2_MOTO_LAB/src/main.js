import {clamp,dist,heading} from './math.js';
import {Renderer} from './render.js';
import {IdleFrameGate,FixedStepScheduler,DevicePerformanceRecorder} from './adaptive_resolution.js';
import {findRoute} from './navigation.js';
import {guideTo} from './route_guidance.js';
import {rideComfortGrade} from './ride_quality.js';
import {CHALLENGE_GATES,startChallenge,challengeTarget,restoreChallengeCareer} from './challenge.js';
import {VERSION,PLACES,SLICE_STORY,byId,missionTarget,makeGame,step,interactionState,interact,buy,validate,readSave,writeSave,snapshot,SAVE_KEY} from './sim.js';
const $=id=>document.getElementById(id),FC=n=>Math.round(n).toLocaleString('fr-FR')+' FC';
const STORAGE_SNAPSHOT='kinmoto_a2_lab_snapshot'; // Preserve previous V0.5.7 career saves in V1.
function isStorageAvailable(){try{const key='kinmoto_v1_storage_probe';localStorage.setItem(key,'1');localStorage.removeItem(key);return true;}catch{return false;}}
const persistentStorage=isStorageAvailable();
const QA_MODE=new URLSearchParams(location.search);const QA_AUTODRIVE=QA_MODE.get('autodrive');let qaDriveClock=0;
let saved=null;try{saved=JSON.parse(localStorage.getItem(STORAGE_SNAPSHOT)||'null')}catch{}
// A cached snapshot is untrusted: validate before allowing it to reach the HUD or controls.
let game=makeGame({save:readSave()});
if(QA_AUTODRIVE)game=makeGame();
else if(saved&&saved.schema===1){
 try{const restored=makeGame(saved);if(validate(restored).length===0)game=restored;}catch{}
}
let qaPeakSusp=0,qaPeakGrade=0,renderer=null,prev=performance.now(),physicsClock=new FixedStepScheduler(),uiClock=0,autoSaveClock=0,garageOrigin='menu',muted=false,audioCtx=null,engineOsc=null,engineGain=null,lastNotified=0,idleFrameGate=new IdleFrameGate(120),deviceRecorder=new DevicePerformanceRecorder();
let quality='eco';try{quality=localStorage.getItem('kinmoto_a2_lab_quality')||'eco'}catch{}$('quality').value=['eco','balanced','high'].includes(quality)?quality:'eco';
const show=id=>$(id).classList.remove('hidden'),hide=id=>$(id).classList.add('hidden');
function toast(text,type='info'){const e=document.createElement('div');e.textContent=text;e.className=type;$('toast').prepend(e);setTimeout(()=>e.remove(),3000);if($('toast').children.length>3)$('toast').lastElementChild.remove();}
function safeSave(){try{writeSave(game.save);localStorage.setItem(STORAGE_SNAPSHOT,JSON.stringify(snapshot(game)));return true}catch{return false}}
function initAudio(){if(muted||audioCtx)return;try{audioCtx=new(window.AudioContext||window.webkitAudioContext)();engineOsc=audioCtx.createOscillator();engineGain=audioCtx.createGain();engineOsc.type='sawtooth';engineOsc.frequency.value=52;engineGain.gain.value=0;engineOsc.connect(engineGain);engineGain.connect(audioCtx.destination);engineOsc.start()}catch{audioCtx=null;}}
function ping(freq=660,duration=.17){if(muted)return;try{initAudio();const o=audioCtx.createOscillator(),g=audioCtx.createGain(),t=audioCtx.currentTime;o.type='triangle';o.frequency.setValueAtTime(freq,t);o.frequency.exponentialRampToValueAtTime(freq*.75,t+duration);g.gain.setValueAtTime(.068,t);g.gain.exponentialRampToValueAtTime(.001,t+duration);o.connect(g);g.connect(audioCtx.destination);o.start(t);o.stop(t+duration)}catch{}}
function updateSound(){if(!audioCtx||!engineOsc)return;let vol=!muted&&game.playing&&!game.paused?.009+game.player.speed*.0015:0;let t=audioCtx.currentTime;engineGain.gain.setTargetAtTime(clamp(vol,0,.045),t,.06);engineOsc.frequency.setTargetAtTime(52+game.player.speed*5.3,t,.11)}
function start(options={}){if(!renderer){show('errorScreen');return;}initAudio();hide('menu');hide('helpScreen');hide('pauseScreen');hide('garageScreen');show('hud');game.playing=true;game.paused=false;game.controls={left:false,right:false,gas:false,brake:false};prev=performance.now();physicsClock.reset();if(options?.silent!==true)toast(game.save.rides<2?'Bienvenue à Bandal ! Deux courses de quartier t’attendent.':'Bienvenue à Kinshasa ! Suis le repère jaune.','success');updateUI();}
function pause(){if(!game.playing||game.paused)return;game.paused=true;releaseInputs();hide('hud');show('pauseScreen');$('challengeRestart').hidden=!game.challenge;safeSave();}
function resume(){if(!game.playing||(game.challenge&&game.challenge.status!=='running'))return;hide('pauseScreen');hide('garageScreen');show('hud');game.paused=false;prev=performance.now();physicsClock.reset();}
function menu(){if(game.challenge)restoreCareerFromChallenge();game.playing=false;game.paused=false;releaseInputs();safeSave();hide('hud');hide('pauseScreen');hide('garageScreen');hide('challengeResult');show('menu');}
function openGarage(origin){garageOrigin=origin;if(origin==='road'){game.paused=true;hide('hud');}else if(origin==='pause'){hide('pauseScreen');}else{hide('menu');}releaseInputs();refreshGarage();show('garageScreen');safeSave();}
function closeGarage(){hide('garageScreen');if(garageOrigin==='road'){game.paused=false;show('hud');prev=performance.now();}else if(garageOrigin==='pause'){show('pauseScreen');}else{show('menu');}}
function action(){if(game.challenge?.active){toast('Passe sous les portes jaunes avant la fin du chrono !','warning');return;}const result=interact(game);if(result.ok){if(result.type==='garage'){openGarage('road');return;}ping(result.type==='completed'?880:660,result.type==='completed'?.35:.18);safeSave();}updateUI();}
function purchase(item){const r=buy(game,item);toast(r.ok?'Achat effectué !':r.reason,r.ok?'success':'warning');if(r.ok){ping(690);safeSave();}refreshGarage();updateUI();}
function restoreCareerFromChallenge(){return restoreChallengeCareer(game);}
function launchChallenge(){
 if(!renderer){show('errorScreen');return;}
 hide('challengeResult');if(game.paused){game.paused=false;hide('pauseScreen');}
 start({silent:true});startChallenge(game);lastNotified=game.eventSeq||0;
 toast('DÉFI WEWA · 7 portes · 90 secondes !','success');updateUI();
}
function showChallengeResult(){
 const c=game.challenge;if(!c||c.shown||c.status==='running')return;
 c.shown=true;game.paused=true;releaseInputs();hide('hud');hide('pauseScreen');show('challengeResult');
 $('challengeResultTitle').textContent=c.status==='won'?'🏁 BRAVO, CHAMPION !':'⏱ TEMPS ÉCOULÉ';
 $('challengeResultPoints').textContent=c.score+' POINTS · '+(c.stars?'★'.repeat(c.stars):'À RETENTER');
 $('challengeResultDetails').textContent=c.status==='won'?`Les 7 portes sont franchies en ${c.elapsed.toFixed(1)} s. ${c.paid?'Nouveau record : +'+FC(c.paid)+' !':'Record personnel : '+game.save.highScore+' points.'}`:'La circulation continue : recommence et vise les 7 portes.';
 safeSave();
}
function refreshGarage(){const s=game.save;let repair=Math.max(0,Math.ceil((100-s.health)*12/50)*50);$('garageCash').textContent=FC(s.cash);$('repairInfo').textContent=`État ${Math.round(s.health)} % · ${FC(repair)}`;$('engineInfo').textContent=`Niveau ${s.engine}/4 · ${FC(s.engine*2400)}`;$('brakeInfo').textContent=`Niveau ${s.brakes}/4 · ${FC(s.brakes*1800)}`;
 for(const [id,cost,disabled] of [['buyRepair',repair,repair===0],['buyEngine',s.engine*2400,s.engine>=4],['buyBrakes',s.brakes*1800,s.brakes>=4]]){$(id).disabled=disabled||cost>s.cash;$(id).textContent=disabled?'TERMINÉ':cost>s.cash?'MANQUE FC':'ACHETER';}}
// Reuse a 220 x 220 static background for the minimap, redraw only rider and
// route. This works in Safari without OffscreenCanvas or worker privileges.
let minimapBase=null,mapBackgroundBuilds=0;
function minimapBackground(){
 if(minimapBase)return minimapBase;
 const cv=document.createElement('canvas');cv.width=220;cv.height=220;
 const ctx=cv.getContext('2d'),w=cv.width,h=cv.height;
 const tx=x=>(x+190)*w/380,ty=z=>(z+190)*h/380;
 ctx.fillStyle='#214c50';ctx.fillRect(0,0,w,h);
 ctx.fillStyle='#9c9c84';for(const v of [-120,0,120]){ctx.fillRect(tx(v-9),0,18*w/380,h);ctx.fillRect(0,ty(v-9),w,18*h/380);}
 ctx.strokeStyle='#f0e3bc';ctx.lineWidth=1;ctx.setLineDash([3,6]);
 for(const v of [-120,0,120]){ctx.beginPath();ctx.moveTo(tx(v),0);ctx.lineTo(tx(v),h);ctx.stroke();ctx.beginPath();ctx.moveTo(0,ty(v));ctx.lineTo(w,ty(v));ctx.stroke()}
 ctx.setLineDash([]);
 for(const p of PLACES){ctx.fillStyle=p.id==='garage'?'#67ddcb':'#e9da9e';ctx.beginPath();ctx.arc(tx(p.x),ty(p.z),p.id==='garage'?4:2.8,0,Math.PI*2);ctx.fill();}
 minimapBase=cv;mapBackgroundBuilds++;return cv;
}
function drawMap(){
 const cv=$('map'),ctx=cv.getContext('2d'),w=cv.width,h=cv.height;
 ctx.clearRect(0,0,w,h);ctx.drawImage(minimapBackground(),0,0,w,h);
 const tx=x=>(x+190)*w/380,ty=z=>(z+190)*h/380;
 const target=challengeTarget(game)||missionTarget(game.mission),px=tx(game.player.x),py=ty(game.player.z);
 ctx.strokeStyle='#ffd340';ctx.lineWidth=2.6;ctx.setLineDash([5,4]);ctx.beginPath();
 const route=findRoute(game.player,target).nodes;
 route.forEach((pt,i)=>{if(i===0)ctx.moveTo(tx(pt.x),ty(pt.z));else ctx.lineTo(tx(pt.x),ty(pt.z));});
 ctx.stroke();ctx.setLineDash([]);
 ctx.fillStyle='#ffd23c';ctx.beginPath();ctx.arc(tx(target.x),ty(target.z),7,0,Math.PI*2);ctx.fill();ctx.strokeStyle='#172637';ctx.lineWidth=2;ctx.stroke();
 ctx.save();ctx.translate(px,py);ctx.rotate(game.player.yaw);ctx.fillStyle='#fff';ctx.strokeStyle='#233445';ctx.lineWidth=2;
 ctx.beginPath();ctx.moveTo(0,-9);ctx.lineTo(6,7);ctx.lineTo(0,4);ctx.lineTo(-6,7);ctx.closePath();ctx.fill();ctx.stroke();ctx.restore();
}
function updateUI(){const p=game.player,s=game.save,m=game.mission,target=challengeTarget(game)||missionTarget(m),state=interactionState(game),challenge=game.challenge?.active?game.challenge:null;
 $('cash').textContent=FC(s.cash);$('speed').textContent=String(Math.round((p.bike?.groundSpeed??p.speed)*3.6)).padStart(2,'0');$('healthBar').style.width=clamp(s.health,0,100)+'%';$('healthNum').textContent=Math.round(s.health)+'%';$('rides').textContent=s.rides;$('stars').textContent=s.stars.toFixed(1);$('district').textContent=p.z>47?'BANDAL · ARRÊT WEWA':p.z>-35?'VICTOIRE · CENTRE':'MATONGE · QUARTIER';$('fpsMark').textContent=(renderer?.fps||'—')+' FPS · 3D';
 $('kindLabel').textContent=m.title;const pick=byId(m.from),drop=byId(m.to);$('missionFrom').textContent=pick.name;$('missionTo').textContent=drop.name;$('missionReward').textContent='+ '+FC(m.reward);
 $('comfortInfo').hidden=m.stage==='pickup';$('comfortValue').textContent=Math.round(m.comfort??100)+'% · '+rideComfortGrade(m);
 $('missionTitle').textContent=m.stage==='pickup'?(m.kind==='colis'?'Récupérer le colis':`Récupérer ${m.client}`):m.stage==='via'?'Arrêt touristique':m.kind==='colis'?'Livrer le colis':`Déposer ${m.client}`;
 $('missionDescription').textContent=m.stage==='pickup'&&m.ride<SLICE_STORY.length?SLICE_STORY[m.ride].description:m.stage==='pickup'?`Rejoins ${target.name} pour la prise en charge.`:m.stage==='via'?`Fais l'arrêt à ${target.name} puis poursuis.`:`Direction ${target.name} : conduis prudemment.`;
 if(!challenge&&m.kind==='vip')$('missionDescription').textContent=m.stage==='pickup'?'Client VIP · conduite douce, confortable et ponctuelle pour gagner un bonus.':`Service VIP : confort ${Math.round(m.comfort)} % · ${Math.max(0,Math.ceil(115-m.timer))} s avant pénalité.`;
 if(challenge){$('kindLabel').textContent='DÉFI MAÎTRISE';$('missionTitle').textContent=`PORTE ${challenge.index+1} / ${CHALLENGE_GATES.length}`;
 $('missionDescription').textContent=target.name+' · Suis les repères pour battre ton record.';
 $('missionFrom').textContent='WEWA BANDAL';$('missionTo').textContent='VICTOIRE';
 $('missionReward').textContent=Math.max(0,Math.ceil(challenge.limit-challenge.elapsed))+' S · '+challenge.score+' PTS';
 $('comfortInfo').hidden=true;}

 const nav=guideTo(p,target,p.yaw);$('missionDistance').textContent=nav.distance+' m';$('navText').textContent=nav.label;$('navMeters').textContent=nav.turnDistance+' m';$('navArrow').textContent=nav.kind==='right'?'↱':nav.kind==='left'?'↰':nav.kind==='arrive'?'◎':'↑';
 let label=challenge?'':state.nearMission?(m.stage==='pickup'?'✓ RÉCUPÉRER':m.stage==='via'?'✓ FAIRE L’ARRÊT':'✓ DÉPOSER'):state.nearGarage?'⚙ GARAGE':'';
 if(label){show('action');$('action').textContent=state.stopped?label:'FREINE POUR T’ARRÊTER';hide('tip');}else{hide('action');show('tip');$('tip').textContent=`Mission : ${target.name} · ${nav.distance} m · E pour interagir`;}
 drawMap();const projected=renderer?.project(target.x,5.5,target.z),tag=$('targetLabel');if(projected&&projected.visible){show('targetLabel');tag.style.left=projected.x+'px';tag.style.top=projected.y+'px';tag.textContent=target.name+' · '+nav.distance+' m';}else hide('targetLabel');
}
function releaseInputs(){for(const k of Object.keys(game.controls))game.controls[k]=false;document.querySelectorAll('.controls button.pressed').forEach(el=>el.classList.remove('pressed'));}
function onInteract(){action();}
function exportTechnicalReport(){
 const report=deviceRecorder.report({version:VERSION,quality,
  screen:{width:innerWidth,height:innerHeight,devicePixelRatio:devicePixelRatio||1},
  webglVersion:renderer?.glVersion??null,
  note:'Logiciels et mesures du navigateur seulement ; ne prouvent pas un GPU matériel.'});
 const blob=new Blob([JSON.stringify(report,null,2)],{type:'application/json'});
 const url=URL.createObjectURL(blob),a=document.createElement('a');
 a.href=url;a.download='KINMOTO_RAPPORT_APPAREIL_'+Date.now()+'.json';a.click();
 setTimeout(()=>URL.revokeObjectURL(url),5000);
 toast(report.summary.samples<60?'Rapport exporté (session courte : vise 15 min).':'Rapport de performance exporté !','success');
}
function exportSave(){safeSave();const blob=new Blob([JSON.stringify(snapshot(game),null,2)],{type:'application/json'}),a=document.createElement('a'),url=URL.createObjectURL(blob);a.href=url;a.download='KIN_MOTO_V1_SAUVEGARDE.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),5000);toast('Sauvegarde exportée','success');}
async function importSave(file){if(!file)return;try{if(file.size>250000)throw Error('Fichier trop volumineux');let obj=JSON.parse(await file.text());if(obj.schema!==1||!obj.save||!obj.player||!obj.mission||!byId(obj.mission.from)||!byId(obj.mission.to)||!Number.isFinite(obj.save.cash)||obj.save.cash<0)throw Error('Format de sauvegarde invalide');let restored=makeGame(obj);if(validate(restored).length)throw Error('Sauvegarde incohérente');game=restored;game.playing=true;game.paused=true;safeSave();refreshGarage();toast('Sauvegarde restaurée !','success');updateUI();}catch(e){toast('Import impossible : '+e.message,'impact');}finally{$('importSave').value='';}}
function installInputs(){const keys={ArrowUp:'gas',KeyW:'gas',ArrowDown:'brake',KeyS:'brake',Space:'brake',ArrowLeft:'left',KeyA:'left',ArrowRight:'right',KeyD:'right'};
 document.addEventListener('keydown',e=>{if(keys[e.code]){if(game.playing&&!game.paused)game.controls[keys[e.code]]=true;e.preventDefault();}if(!e.repeat&&e.code==='KeyE'){if(game.playing&&!game.paused)onInteract();e.preventDefault();}if(!e.repeat&&(['Escape','KeyP'].includes(e.code))){if(game.playing){game.paused?resume():pause();}e.preventDefault();}if(!e.repeat&&e.code==='KeyC'){if(renderer){renderer.mode=(renderer.mode+1)%3;toast(['Caméra arrière','Caméra haute','Vue guidon'][renderer.mode]);}}});
 document.addEventListener('keyup',e=>{if(keys[e.code]){game.controls[keys[e.code]]=false;e.preventDefault();}});
 for(const b of document.querySelectorAll('.controls [data-key]')){const k=b.dataset.key;b.addEventListener('pointerdown',e=>{e.preventDefault();if(!game.paused){game.controls[k]=true;b.classList.add('pressed');}try{b.setPointerCapture(e.pointerId)}catch{}});for(const event of ['pointerup','pointercancel','lostpointercapture'])b.addEventListener(event,e=>{game.controls[k]=false;b.classList.remove('pressed')});}
 window.addEventListener('blur',()=>{releaseInputs();if(game.playing&&!game.paused)pause()});document.addEventListener('visibilitychange',()=>{if(document.hidden){releaseInputs();safeSave();if(game.playing&&!game.paused)pause();prev=performance.now()}});window.addEventListener('pagehide',safeSave);window.addEventListener('beforeunload',safeSave);window.addEventListener('resize',()=>renderer?.resize());
 $('play').onclick=start;$('pause').onclick=pause;$('resume').onclick=resume;$('returnMenu').onclick=menu;$('action').onclick=action;
 $('openGarageMenu').onclick=()=>openGarage('menu');$('openGaragePause').onclick=()=>openGarage('pause');$('garageBack').onclick=closeGarage;
 $('buyRepair').onclick=()=>purchase('repair');$('buyEngine').onclick=()=>purchase('engine');$('buyBrakes').onclick=()=>purchase('brakes');
 $('challengePlay').onclick=launchChallenge;$('challengeRestart').onclick=launchChallenge;
 $('challengeAgain').onclick=launchChallenge;$('challengeBack').onclick=()=>{restoreCareerFromChallenge();menu();};
 $('helpButton').onclick=()=>{hide('menu');show('helpScreen')};$('helpBack').onclick=()=>{hide('helpScreen');show('menu')};$('saveButton').onclick=exportSave;$('exportTechReport').onclick=exportTechnicalReport;$('importSave').onchange=e=>importSave(e.target.files?.[0]);
 $('cameraToggle').onclick=()=>{if(renderer){renderer.mode=(renderer.mode+1)%3;toast(['Caméra arrière','Caméra haute','Vue guidon'][renderer.mode])}};
 $('quality').onchange=e=>{renderer?.setQuality(e.target.value);quality=e.target.value;try{localStorage.setItem('kinmoto_a2_lab_quality',quality)}catch{}};
 $('soundToggle').onclick=()=>{muted=!muted;$('soundToggle').textContent=muted?'♪ Son coupé':'♪ Son activé';updateSound()};
 $('retryEco').onclick=()=>{try{localStorage.setItem('kinmoto_a2_lab_quality','eco')}catch{}location.reload()};
 $('world').addEventListener('webglcontextlost',e=>{e.preventDefault();renderer.lost=true;releaseInputs();if(game.playing&&!game.paused)pause();toast('Contexte graphique interrompu : relance nécessaire.','impact')});
 $('world').addEventListener('webglcontextrestored',()=>location.reload());
}
function frame(now){const frameSeconds=Math.max(0,(now-prev)/1000);const delta=Math.min(.5,frameSeconds);prev=now;
 if(QA_AUTODRIVE && game.playing && !game.paused){
   qaDriveClock+=delta;
   game.controls.gas=qaDriveClock<6.5;
   game.controls.brake=qaDriveClock>=6.5&&qaDriveClock<8;
   game.controls.left=QA_AUTODRIVE==='left'&&qaDriveClock>=1.5&&qaDriveClock<2.5;
   game.controls.right=QA_AUTODRIVE==='right'&&qaDriveClock>=1.5&&qaDriveClock<2.5;
 }
 const isSimulating=game.playing&&!game.paused&&!document.hidden;
 physicsClock.advance(frameSeconds,fixed=>step(game,fixed),{active:isSimulating});
 if(game.challenge&&game.challenge.status!=='running')showChallengeResult();
 try{const active=game.playing&&!game.paused;
  const shouldRender=idleFrameGate.shouldRender(now,{active,visible:!document.hidden});
  if(shouldRender)renderer?.render(game,active?frameSeconds:1/60,active);
 }catch(e){console.error(e);show('errorScreen');$('errorDetail').textContent=e.message;game.paused=true;renderer=null;}
 if(deviceRecorder.shouldSample(now,game.playing&&!game.paused&&!document.hidden&&!!renderer)){
  deviceRecorder.record(now,{fps:renderer.fps,renderScale:renderer.dynamic.scale,
   renderPixels:renderer.canvas.width*renderer.canvas.height,simSeconds:game.clock,
   droppedSeconds:physicsClock.droppedSeconds,jsHeapBytes:performance.memory?.usedJSHeapSize??null});
 }
 uiClock+=delta;autoSaveClock+=delta;if(uiClock>.18){uiClock=0;if(game.playing&&!game.paused)updateUI();if(QA_AUTODRIVE){let t=game.player.bike||{};qaPeakSusp=Math.max(qaPeakSusp,Math.abs(t.suspension||0));qaPeakGrade=Math.max(qaPeakGrade,Math.abs(t.roadGrade||0));$('qaLive').hidden=false;$('qaLive').textContent=`QA:${QA_AUTODRIVE} t=${qaDriveClock.toFixed(1)} x=${game.player.x.toFixed(2)} z=${game.player.z.toFixed(2)} yaw=${game.player.yaw.toFixed(3)} kmh=${(game.player.speed*3.6).toFixed(1)} slip=${(t.lateralSlip||0).toFixed(2)} bump=${(t.frontHeight||0).toFixed(3)}/${(t.rearHeight||0).toFixed(3)} shockPeak=${qaPeakSusp.toFixed(3)} gradePeak=${qaPeakGrade.toFixed(3)}`;}let events=game.events.filter(event=>event.seq>lastNotified);for(const event of events){toast(event.message,event.type);if(event.type==='impact')ping(190,.26);else if(event.type==='success')ping(840,.2)}lastNotified=game.events.length?game.events[game.events.length-1].seq:lastNotified;}
 if(autoSaveClock>9){autoSaveClock=0;if(game.playing)safeSave();}updateSound();requestAnimationFrame(frame);}
function boot(){installInputs();if(!persistentStorage)setTimeout(()=>toast('Stockage local indisponible ici : exporte régulièrement ta sauvegarde depuis Pause.','impact'),850);try{renderer=new Renderer($('world'),{quality});}catch(e){console.warn(e);$('errorDetail').textContent=e.message;show('errorScreen');}
 window.KINMOTO_DIAGNOSTIC=()=>({version:VERSION,challenge:game.challenge?{...game.challenge}:null,persistentStorage,mode:renderer?'webgl'+renderer.glVersion:'unavailable',render:renderer?.stats()??null,player:{...game.player},mission:{...game.mission},cars:game.cars.map(c=>({x:c.x,z:c.z,yaw:c.yaw,speed:c.speed})),playing:game.playing,paused:game.paused,errors:validate(game),rides:game.save.rides,cash:game.save.cash,steps:game.stats.steps,collisionCount:game.collisions,physics:{ticks:physicsClock.ticks,droppedSeconds:physicsClock.droppedSeconds,maxCatchupSeconds:physicsClock.maxFrame}});
 if(location.search.includes('qa=1'))window.KINMOTO_QA={get:()=>game,step:(dt=.016)=>step(game,dt),interact:()=>interact(game),forcePosition:(x,z,yaw=0)=>{game.player.x=x;game.player.z=z;game.player.yaw=yaw;game.player.speed=0;},save:safeSave};
 requestAnimationFrame(frame);if(location.search.includes('qa=1')&&location.search.includes('autoplay=1'))setTimeout(start,350);if('serviceWorker' in navigator&&(location.protocol==='https:'||location.hostname==='localhost'||location.hostname==='127.0.0.1'))navigator.serviceWorker.register('./sw.js').catch(e=>console.warn('Cache hors ligne indisponible',e));}
boot();
