import com.blessing.rescuebridge.RescueAdvisor;

public final class RescueAdvisorProbe {
    public static void main(String[] args) {
        assertContains(RescueAdvisor.problem("CONFIGURATION_MISSING"), "Réglages");
        assertContains(RescueAdvisor.problem("PAIRING_REQUIRED"), "clé");
        assertContains(RescueAdvisor.problem("USB_UNAVAILABLE"), "Transfert de fichiers");
        assertContains(RescueAdvisor.problem("LINK_VERIFIED"), "signée");
        assertContains(RescueAdvisor.problem("PC_ASLEEP"), "veille");
        if (!"TIMEOUT".equals(RescueAdvisor.codeForException("SocketTimeoutException"))) throw new AssertionError("timeout");
        if (!"AUTH_FAILED".equals(RescueAdvisor.codeForException("SecurityException"))) throw new AssertionError("auth");
        if (!"AGENT_UNAVAILABLE".equals(RescueAdvisor.codeForException("ConnectException"))) throw new AssertionError("connect");
        if (RescueAdvisor.problem("<script>alert(1)</script>").contains("<")) throw new AssertionError("diagnostic injection");
        System.out.println("9 ADVISOR CHECKS PASS");
    }
    private static void assertContains(String s,String fragment) { if(!s.contains(fragment)) throw new AssertionError(s); }
}