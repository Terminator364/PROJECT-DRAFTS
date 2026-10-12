import com.blessing.rescuebridge.BridgeProtocol;
import java.nio.charset.StandardCharsets;
public final class ProtocolProbe {
    public static void main(String[] args) throws Exception {
        String key=args[0],path=args[1],ts=args[2],nonce=args[3],json=args[4];
        byte[] bytes=json.getBytes(StandardCharsets.UTF_8);
        System.out.println(BridgeProtocol.signRequest(key,"POST",path,ts,nonce,bytes));
        System.out.println(BridgeProtocol.signResponse(key,nonce,200,bytes));
        System.out.println(BridgeProtocol.sha256(bytes));
        System.out.println(BridgeProtocol.constantTimeHexEquals("aaa","aaa"));
        System.out.println(BridgeProtocol.constantTimeHexEquals("aaa","bbb"));
        System.out.println(BridgeProtocol.escapeJson("hello\n\"x\""));
    }
}