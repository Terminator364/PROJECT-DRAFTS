package com.quotapulse.monitor;

import org.junit.Test;
import static org.junit.Assert.*;

public final class SyncPolicyTest {
  static final long NOW=1762634000000L;
  static final long INTERVAL=SyncPolicy.INTERVAL_MS;

  @Test public void firstGoodSessionMayRefreshAfterTwentyMinutes() {
    assertTrue(SyncPolicy.shouldAutoRefresh(true,false,NOW-INTERVAL,0,NOW));
  }
  @Test public void freshCacheIsImmediateAndDoesNotTriggerNetwork() {
    assertFalse(SyncPolicy.shouldAutoRefresh(true,false,NOW-INTERVAL+1,0,NOW));
  }
  @Test public void expiredSessionNeverAutomaticallyLaunchesLogin() {
    assertFalse(SyncPolicy.shouldAutoRefresh(false,false,NOW-INTERVAL*3,0,NOW));
  }
  @Test public void failedNetworkRetryIsThrottledForTwentyMinutes() {
    assertFalse(SyncPolicy.shouldAutoRefresh(true,false,NOW-INTERVAL*3,NOW-INTERVAL+1,NOW));
    assertTrue(SyncPolicy.shouldAutoRefresh(true,false,NOW-INTERVAL*3,NOW-INTERVAL,NOW));
  }
  @Test public void busySessionNeverDuplicatesTheWebView() {
    assertFalse(SyncPolicy.shouldAutoRefresh(true,true,NOW-INTERVAL*2,0,NOW));
  }
  @Test public void futureAndMissingTimestampsAreNotTrusted() {
    assertFalse(SyncPolicy.shouldAutoRefresh(true,false,0,0,NOW));
    assertFalse(SyncPolicy.shouldAutoRefresh(true,false,NOW+1,0,NOW));
    assertFalse(SyncPolicy.shouldAutoRefresh(true,false,NOW-INTERVAL*2,NOW+1,NOW));
  }
}
