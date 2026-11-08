package com.quotapulse.monitor;
import org.junit.Test;
import static org.junit.Assert.*;

public class QuotaParserTest {
  @Test public void realSamsungScreenshotText() {
    String text="Desktop Commander Remote MCP Tool calls this month\n7 811 / 10 000\n78% used · Resets on 1 déc., in 23 days\nDaily average\n976\nCalls so far this month";
    QuotaParser.Data d=QuotaParser.parse(text);
    assertNotNull(d);assertEquals(7811,d.used);assertEquals(10000,d.limit);assertEquals(2189,d.remaining);assertEquals(976,d.dailyAverage);assertEquals("1 déc.",d.reset);
  }
  @Test public void doesNotSwallowPercentageAfterLimit() {
    QuotaParser.Data d=QuotaParser.parse("Tool calls this month 7 811 / 10 000 78% used");
    assertNotNull(d);assertEquals(10000,d.limit);assertEquals(7811,d.used);assertEquals(2189,d.remaining);
  }
  @Test public void parsesSidebarWithNarrowSpaces() {
    QuotaParser.Data d=QuotaParser.parse("Tool calls 7\u202f811 of 10\u202f000 this month, 2\u202f189 tool calls left this month");
    assertNotNull(d);assertEquals(2189,d.remaining);
  }
  @Test public void takesMainUsageWhenSidebarPrecedesIt() {
    String text="Tool calls 78% 7 811 of 10 000 this month. 2 189 tool calls left this month. Tool calls this month 7 811 / 10 000 Daily average 976";
    QuotaParser.Data d=QuotaParser.parse(text);assertNotNull(d);assertEquals(7811,d.used);assertEquals(10000,d.limit);
  }
  @Test public void rejectsContradictoryRemaining() {
    assertNull(QuotaParser.parse("Tool calls this month 7 811 / 10 000 2 188 tool calls left this month"));
  }
  @Test public void doesNotCreateDataOnLoginPage() {
    assertNull(QuotaParser.parse("Welcome to Desktop Commander. Continue with email to sign in"));
  }
  @Test public void handlesZeroUsage() {
    QuotaParser.Data d=QuotaParser.parse("Tool calls this month 0 / 10 000");
    assertNotNull(d);assertEquals(10000,d.remaining);
  }
  @Test public void handlesExhaustion() {
    QuotaParser.Data d=QuotaParser.parse("Tool calls this month 10 000 / 10 000");
    assertNotNull(d);assertEquals(0,d.remaining);
  }
  @Test public void resetIsNotContaminatedByUpgradeBanner() {
    QuotaParser.Data d=QuotaParser.parse("Tool calls this month 7 812 / 10 000 78% used · Resets on 1 déc. Upgrade to Pro BL Daily average 977");
    assertNotNull(d);assertEquals("1 déc.",d.reset);assertEquals(2188,d.remaining);
  }
  @Test public void oldCachedResetValueIsCleanedBeforeRendering() {
    assertEquals("1 déc.",QuotaParser.cleanReset("1 déc. Upgrade to Pro BL"));
    assertEquals("À confirmer",QuotaParser.cleanReset("Upgrade to Pro"));
    assertEquals("1 déc.",QuotaParser.cleanReset("1 déc., in 23 days"));
  }
  @Test public void rejectsInvalidOverage() {
    assertNull(QuotaParser.parse("Tool calls this month 10 001 / 10 000"));
  }
}
