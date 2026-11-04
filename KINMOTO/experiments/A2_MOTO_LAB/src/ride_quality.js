// Deterministic passenger/cargo comfort: mechanical events affect reward and reputation.
// Works without online services, sensors or allocations in the physics loop.
const clampComfort=(v,a,b)=>Math.min(b,Math.max(a,v));
export function addRideDiscomfort(m,amount,reason='driving') {
  if(!m || m.stage==='pickup' || !Number.isFinite(amount) || amount<=0)return 0;
  const before=clampComfort(m.comfort??100,0,100);
  m.comfort=clampComfort(before-amount,0,100);
  if(reason==='impact')m.impacts=(m.impacts||0)+1;
  return before-m.comfort;
}
export function observeRide(m,bike,speed,dt) {
  if(!m||m.stage==='pickup'||!bike||!(dt>0&&dt<=.10))return 0;
  // Harsh braking, excessive cornering and vertical shock are experienced
  // differently. The coefficients are gameplay parameters, not clinical units.
  const accel=Math.abs(bike.acceleration||0),lateral=Math.abs((bike.yawRate||0)*(speed||0));
  const bump=Math.abs(bike.suspensionVelocity||0);
  const harshBrake=Math.max(0,accel-6.3)*.75;
  const sharpCorner=Math.max(0,lateral-4.8)*.50;
  const suspensionShock=Math.max(0,bump-.45)*5.0;
  return addRideDiscomfort(m,(harshBrake+sharpCorner+suspensionShock)*dt);
}
export function rideComfortPaymentMultiplier(m) {
  const comfort=clampComfort(m?.comfort??100,0,100);
  return 1 - .22*Math.pow(1-comfort/100,1.3);
}
export function rideComfortGrade(m) {
  const c=clampComfort(m?.comfort??100,0,100);
  if(c>=85)return 'EXCELLENT';if(c>=65)return 'CORRECT';if(c>=40)return 'SECOUSSES';return 'INCONFORTABLE';
}
