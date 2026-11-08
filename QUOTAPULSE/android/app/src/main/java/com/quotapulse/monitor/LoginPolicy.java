package com.quotapulse.monitor;
import java.util.Locale;
/** No navigation to usage while password or OTP steps are active. */
public final class LoginPolicy {
  private LoginPolicy(){}
  public static boolean isAuthenticationUrl(String url){
    if(url==null)return false;
    String u=url.toLowerCase(Locale.ROOT);
    return u.startsWith("https://auth.desktopcommander.app")||
     (u.startsWith("https://mcp.desktopcommander.app")&&(u.contains("/login")||u.contains("/signin")||u.contains("/auth/")||u.contains("/callback")||u.contains("/verify")));
  }
  public static boolean isLoginPage(String page){
    if(page==null)return false;
    String p=page.toLowerCase(Locale.ROOT);
    return p.contains("continue with email")||p.contains("verification code")||p.contains("verify your email")||
      p.contains("check your inbox")||p.contains("sign in with email")||p.contains("magic link");
  }
  public static boolean canNavigateToUsage(String url,String page){
    if(url==null||page==null||isAuthenticationUrl(url)||isLoginPage(page))return false;
    String u=url.toLowerCase(Locale.ROOT),p=page.toLowerCase(Locale.ROOT);
    return u.startsWith("https://mcp.desktopcommander.app")&&!u.contains("/usage")&&
      p.contains("tool calls")&&p.contains("devices")&&(p.contains("usage")||p.contains("settings"));
  }
}