// KIN MOTO A2 — lightweight oriented motorcycle/vehicle footprint collision.
// Each vehicle is a box in its own yaw basis; the bike is a small disc.
// No physics engine dependency, heap allocation optional (pass reusable out object).
const BIKE_CONTACT_RADIUS = 0.58;
export const bikeCollisionRadius = BIKE_CONTACT_RADIUS;
export function inspectBikeCar(bike, car, out={}) {
  const x=bike.x-car.x,z=bike.z-car.z;
  const forwardX=Math.sin(car.yaw),forwardZ=-Math.cos(car.yaw);
  const sideX=Math.cos(car.yaw),sideZ=Math.sin(car.yaw);
  const along=x*forwardX+z*forwardZ, lateral=x*sideX+z*sideZ;
  const bus=car.kind%5===4;
  // Visual makeCar() dimensions: W 1.94/2.18m, L 4.2/6.3m.
  const halfWidth=bus?1.09:.97, halfLength=bus?3.15:2.10;
  const nearSide=Math.max(-halfWidth,Math.min(halfWidth,lateral));
  const nearForward=Math.max(-halfLength,Math.min(halfLength,along));
  const sideGap=lateral-nearSide,forwardGap=along-nearForward;
  const d=Math.hypot(sideGap,forwardGap);
  let normalS,normalF,clearance,inside=false;
  if (d>1e-7) {
    normalS=sideGap/d;normalF=forwardGap/d;clearance=d;
  } else {
    // The rider's center entered the body; choose the nearest exit face,
    // avoiding the old radial push that could embed the bike in façades.
    inside=true;
    const exitSide=halfWidth-Math.abs(lateral),exitForward=halfLength-Math.abs(along);
    if (exitSide<=exitForward) {normalS=lateral>=0?1:-1;normalF=0;clearance=-exitSide;}
    else {normalS=0;normalF=along>=0?1:-1;clearance=-exitForward;}
  }
  out.normalX=sideX*normalS+forwardX*normalF;
  out.normalZ=sideZ*normalS+forwardZ*normalF;
  out.clearance=clearance;
  out.overlap=Math.max(0,BIKE_CONTACT_RADIUS-clearance);
  out.hit=out.overlap>0;
  out.inside=inside;
  out.nearMiss=!out.hit && clearance<BIKE_CONTACT_RADIUS+1.10;
  out.frontGap=along;
  out.lateralGap=lateral;
  return out;
}
// Positive only when two vehicles converge along the contact normal.
export function closingSpeed(bike, car, contact) {
  const vx=bike.bike?.vx??Math.sin(bike.yaw)*bike.speed;
  const vz=bike.bike?.vz??-Math.cos(bike.yaw)*bike.speed;
  const cvx=Math.sin(car.yaw)*car.speed,cvz=-Math.cos(car.yaw)*car.speed;
  const relativeX=vx-cvx,relativeZ=vz-cvz;
  // For a deeply intersecting center the chosen normal is arbitrary: use
  // relative speed magnitude so existing contact still triggers real damage.
  if (contact.inside) return Math.hypot(relativeX,relativeZ);
  return Math.max(0,-(relativeX*contact.normalX+relativeZ*contact.normalZ));
}
