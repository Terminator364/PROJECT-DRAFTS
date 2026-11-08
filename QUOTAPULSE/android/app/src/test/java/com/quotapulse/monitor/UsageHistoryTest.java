package com.quotapulse.monitor;
import java.util.List;
import org.junit.Test;
import static org.junit.Assert.*;

public final class UsageHistoryTest {
  @Test public void exactFrenchPercentage() {
    assertEquals("21,88 %",UsageHistory.percentage(2188,10000));
    assertEquals("21,89 %",UsageHistory.percentage(2189,10000));
    assertEquals("0,00 %",UsageHistory.percentage(0,10000));
  }
  @Test public void plusTwoAfterRefreshing(){
    UsageHistory.Update first=UsageHistory.record("",0,-1,0,1000,7812,10000);
    UsageHistory.Update second=UsageHistory.record(first.serialized,1000,7812,10000,2000,7814,10000);
    assertTrue(second.comparable);assertEquals(2,second.increase);
    assertEquals("+2 appels depuis le dernier relevé",UsageHistory.changeText(second.comparable,second.changedCycle,second.increase));
    assertEquals(2,second.points.size());
  }
  @Test public void noNewCallIsZeroNotFakePlus(){
    UsageHistory.Update v=UsageHistory.record("",1000,7812,10000,2000,7812,10000);
    assertEquals(0,v.increase);assertEquals("0 nouvel appel depuis le dernier relevé",UsageHistory.changeText(v.comparable,v.changedCycle,v.increase));
  }
  @Test public void resetDoesNotProduceNegativeDelta(){
    UsageHistory.Update v=UsageHistory.record("",1000,7812,10000,2000,4,10000);
    assertTrue(v.changedCycle);assertFalse(v.comparable);assertEquals(1,v.points.size());
  }
  @Test public void initialUpdateMigratesPreviousCache(){
    UsageHistory.Update u=UsageHistory.record("",1731000000000L,7811,10000,1731000010000L,7812,10000);
    assertEquals(2,u.points.size());assertEquals(1,u.increase);
  }
  @Test public void malformedStoredHistoryIsIgnored(){
    List<UsageHistory.Point> pts=UsageHistory.parse("garbage;123,7811,10000;42,-1,10000;99,10,5;");
    assertEquals(1,pts.size());assertEquals(7811,pts.get(0).used);
  }
}
