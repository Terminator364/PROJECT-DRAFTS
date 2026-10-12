import com.blessing.rescuebridge.MissionPolicy;
public class MissionPolicyProbe {
 public static void main(String[] args) {
  long now=1700000000L;
  System.out.println(MissionPolicy.actionAllowed("status"));
  System.out.println(MissionPolicy.actionAllowed("shell"));
  System.out.println(MissionPolicy.validExpiry(now,now+1));
  System.out.println(MissionPolicy.validExpiry(now,now-1));
  System.out.println(MissionPolicy.validExpiry(now,now+86401));
  System.out.println(MissionPolicy.safeRelativePath("rapport/test.txt"));
  System.out.println(MissionPolicy.safeRelativePath("../secret"));
  System.out.println(MissionPolicy.safeRelativePath("foo/../../bar"));
  System.out.println(MissionPolicy.safeRelativePath("a\\b"));
  System.out.println(MissionPolicy.validWriteContent("é"));
  System.out.println(MissionPolicy.validWriteContent("é".repeat(32769)));
 }
}