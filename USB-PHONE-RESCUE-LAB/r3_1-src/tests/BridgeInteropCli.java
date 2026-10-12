import com.blessing.rescuebridge.BridgeProtocol;
import java.net.*;
import java.nio.charset.StandardCharsets;
import java.io.*;
import java.util.UUID;

public class BridgeInteropCli {
  public static void main(String[] args) throws Exception {
    if(args.length!=3) throw new IllegalArgumentException("host port key");
    String path="/v1/status", key=args[2];
    String ts=Long.toString(System.currentTimeMillis()/1000L), nonce=UUID.randomUUID().toString().replace("-","");
    byte[] body="{}".getBytes(StandardCharsets.UTF_8);
    HttpURLConnection connection=(HttpURLConnection)new URL("http://"+args[0]+":"+args[1]+path).openConnection();
    connection.setConnectTimeout(2000);connection.setReadTimeout(4000);
    connection.setRequestMethod("POST");connection.setDoOutput(true);
    connection.setRequestProperty("X-Bridge-Time",ts);
    connection.setRequestProperty("X-Bridge-Nonce",nonce);
    connection.setRequestProperty("X-Bridge-Signature",BridgeProtocol.signRequest(key,"POST",path,ts,nonce,body));
    try(OutputStream out=connection.getOutputStream()){out.write(body);}
    int status=connection.getResponseCode();
    String sig=connection.getHeaderField("X-Bridge-Signature");
    byte[] response;
    try(InputStream in=(status<400?connection.getInputStream():connection.getErrorStream());ByteArrayOutputStream stream=new ByteArrayOutputStream()) {
      in.transferTo(stream);response=stream.toByteArray();
    }
    boolean valid=BridgeProtocol.constantTimeHexEquals(sig,BridgeProtocol.signResponse(key,nonce,status,response));
    if(status!=200||!valid||!new String(response,StandardCharsets.UTF_8).contains("BCP_USB_RESCUE_R1"))
      throw new SecurityException("Windows/Java interop broken: HTTP "+status+" signed "+valid);
    System.out.println("INTEROP_OK: Java HMAC request -> Python HTTP server -> Java verified HMAC response");
  }
}