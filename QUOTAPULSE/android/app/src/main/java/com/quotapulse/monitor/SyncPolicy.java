package com.quotapulse.monitor;

/** Pure Java policy: refresh only while the app is visible, with a 20-minute cooldown. */
public final class SyncPolicy {
  private SyncPolicy() {}
  public static final long INTERVAL_MS = 20L * 60L * 1000L;

  public static boolean shouldAutoRefresh(boolean sessionKnown,
      boolean busy, long lastGoodAt, long lastAttemptAt, long now) {
    if(!sessionKnown || busy || lastGoodAt<=0 || now<=0) return false;
    if(lastGoodAt>now || lastAttemptAt>now) return false;
    if(now-lastGoodAt<INTERVAL_MS) return false;
    return lastAttemptAt==0 || now-lastAttemptAt>=INTERVAL_MS;
  }
}
