/**
 * TLIB HYBRID V2 — PC LEASE BRIDGE (LAB DESIGN)
 * Add to the existing Apps Script project only after review.
 * This file intentionally contains NO secret.
 *
 * Contract:
 * - Apps Script remains canonical owner of L1_QUEUE.
 * - PC claims bounded work through atomic leases.
 * - Expired leases can be reclaimed.
 * - Commit is idempotent by entity_id + enrichment_version.
 */

const TLIB_PC = Object.freeze({
  WORKER_PROTOCOL: '2.0-lab',
  LEASE_SECONDS: 600,
  CLAIM_MAX: 100,
  ENRICHMENT_VERSION: 'l1-github-v1'
});

function TLIB_PC_claim(workerId, requested) {
  workerId = String(workerId || '').trim();
  if (!/^[A-Za-z0-9._-]{3,80}$/.test(workerId)) throw new Error('INVALID_WORKER_ID');
  requested = Math.max(1, Math.min(Number(requested || 25), TLIB_PC.CLAIM_MAX));

  var lock = LockService.getScriptLock();
  if (!lock.tryLock(5000)) return {ok:false, state:'BUSY_RETRY'};
  try {
    var sh = get_(TLIB.S.L1);
    ensureLeaseColumns_(sh);
    releaseExpiredLeases_(sh);

    var n = sh.getLastRow();
    if (n < 2) return {ok:true, lease_id:'', items:[]};
    var v = sh.getRange(2,1,n-1,10).getValues();
    var now = new Date(), expires = new Date(now.getTime()+TLIB_PC.LEASE_SECONDS*1000);
    var leaseId = 'LEASE-'+Utilities.getUuid();
    var picked = [];

    for (var i=0; i<v.length && picked.length<requested; i++) {
      var status = String(v[i][1] || '');
      if (status !== 'PENDING' && status !== 'RETRY') continue;
      picked.push({row:i+2, entity_id:String(v[i][0]), priority:Number(v[i][2]||0)});
    }

    picked.forEach(function(x){
      sh.getRange(x.row,2,1,9).setValues([[
        'LEASED', x.priority, Number(sh.getRange(x.row,4).getValue()||0),
        '', '', workerId, leaseId, now.toISOString(), expires.toISOString()
      ]]);
    });

    log_('PC-'+leaseId,'PC_LEASE_CLAIM',workerId,'OK','items='+picked.length);
    return {ok:true, lease_id:leaseId, expires_at:expires.toISOString(),
            items:picked.map(function(x){return {entity_id:x.entity_id,priority:x.priority};})};
  } finally { lock.releaseLock(); }
}

function TLIB_PC_commit(workerId, leaseId, results) {
  workerId = String(workerId || '').trim();
  leaseId = String(leaseId || '').trim();
  if (!workerId || !leaseId || !Array.isArray(results)) throw new Error('INVALID_COMMIT');

  var lock = LockService.getScriptLock();
  if (!lock.tryLock(5000)) return {ok:false, state:'BUSY_RETRY'};
  try {
    var q = get_(TLIB.S.L1), e = get_(TLIB.S.ENT);
    ensureLeaseColumns_(q);
    var qn=q.getLastRow(), qv=qn>=2?q.getRange(2,1,qn-1,10).getValues():[];
    var byId={};
    qv.forEach(function(r,i){byId[String(r[0])]={row:i+2,status:String(r[1]),worker:String(r[6]||''),lease:String(r[7]||'')};});

    var accepted=0, rejected=0;
    results.forEach(function(r){
      var id=String(r && r.entity_id || ''), qrow=byId[id];
      if(!qrow || qrow.status!=='LEASED' || qrow.worker!==workerId || qrow.lease!==leaseId){rejected++;return;}
      // Full L1 entity-column mapping must reuse the canonical runL1_/writeL1_ schema.
      // Until that mapping is frozen, LAB commits mark queue completion only.
      q.getRange(qrow.row,2).setValue('DONE_PC_LAB');
      q.getRange(qrow.row,5).setValue('');
      accepted++;
    });
    log_('PC-'+leaseId,'PC_LEASE_COMMIT',workerId,'OK','accepted='+accepted+'; rejected='+rejected);
    return {ok:true,accepted:accepted,rejected:rejected,enrichment_version:TLIB_PC.ENRICHMENT_VERSION};
  } finally { lock.releaseLock(); }
}

function ensureLeaseColumns_(sh){
  var headers=['entity_id','status','priority','attempts','last_error','last_attempt_at','worker_id','lease_id','leased_at','lease_expires_at'];
  if(sh.getMaxColumns()<headers.length) sh.insertColumnsAfter(sh.getMaxColumns(),headers.length-sh.getMaxColumns());
  sh.getRange(1,1,1,headers.length).setValues([headers]);
}

function releaseExpiredLeases_(sh){
  var n=sh.getLastRow(); if(n<2)return 0;
  var v=sh.getRange(2,1,n-1,10).getValues(), now=Date.now(), released=0;
  v.forEach(function(r,i){
    if(String(r[1])!=='LEASED')return;
    var exp=Date.parse(String(r[9]||''));
    if(!exp || exp>now)return;
    sh.getRange(i+2,2,1,9).setValues([['RETRY',r[2],Number(r[3]||0)+1,'LEASE_EXPIRED',new Date().toISOString(),'','','','']]);
    released++;
  });
  return released;
}
