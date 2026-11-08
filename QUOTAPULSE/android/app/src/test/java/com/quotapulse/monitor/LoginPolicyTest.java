package com.quotapulse.monitor;
import org.junit.Test;
import static org.junit.Assert.*;
public final class LoginPolicyTest {
 @Test public void otpFlowNeverRedirects(){
   assertTrue(LoginPolicy.isAuthenticationUrl("https://auth.desktopcommander.app/sign-in"));
   assertTrue(LoginPolicy.isAuthenticationUrl("https://mcp.desktopcommander.app/auth/callback?code=1"));
   assertFalse(LoginPolicy.canNavigateToUsage("https://mcp.desktopcommander.app/auth/callback?code=1","Devices Settings Usage Tool calls"));
   assertTrue(LoginPolicy.isLoginPage("Enter verification code sent to your email"));
   assertFalse(LoginPolicy.canNavigateToUsage("https://mcp.desktopcommander.app/devices","Continue with email"));
 }
 @Test public void onlyLoggedInDashboardMayNavigateOnce(){
   assertTrue(LoginPolicy.canNavigateToUsage("https://mcp.desktopcommander.app/devices","Devices Settings Usage Tool calls"));
   assertFalse(LoginPolicy.canNavigateToUsage("https://mcp.desktopcommander.app/usage","Devices Settings Usage Tool calls"));
   assertFalse(LoginPolicy.canNavigateToUsage("https://mcp.desktopcommander.app/devices","Loading..."));
 }
}