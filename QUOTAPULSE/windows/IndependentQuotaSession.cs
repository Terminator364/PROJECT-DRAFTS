using System;
using System.IO;
using System.Drawing;
using System.Threading.Tasks;
using System.Windows.Forms;
using System.Web.Script.Serialization;
using Microsoft.Web.WebView2.Core;
using Microsoft.Web.WebView2.WinForms;

namespace QuotaPulse {
 public sealed class IndependentQuotaSession : IDisposable {
   const string UsageUrl="https://mcp.desktopcommander.app/usage";
   readonly Form owner;
   Form login;
   WebView2 browser;
   Timer pulse;
   Label subtitle;
   Button retry;
   TaskCompletionSource<Quota> pending;
   DateTime began;
   bool initializing=true, inspecting=false, navigated=false, complete=false, enteredAuth=false, disposed=false;
   string profilePath;
   string diagnosticPath;

   public IndependentQuotaSession(Form ownerForm){owner=ownerForm;}
   void Log(string message) {
     try {
       string dir=Path.Combine(Path.GetDirectoryName(typeof(IndependentQuotaSession).Assembly.Location),"diagnostics");
       Directory.CreateDirectory(dir);
       diagnosticPath=Path.Combine(dir,"webview2-status.log");
       File.AppendAllText(diagnosticPath,DateTime.UtcNow.ToString("o")+" "+message+Environment.NewLine);
       FileInfo fi=new FileInfo(diagnosticPath);
       if(fi.Length>65536)File.WriteAllText(diagnosticPath,DateTime.UtcNow.ToString("o")+" LOG_ROTATED"+Environment.NewLine);
     }catch{}
   }
   public Task<Quota> ReadAsync(){
     pending=new TaskCompletionSource<Quota>();
     began=DateTime.UtcNow;
     Log("START");
     Initialize();
     return pending.Task;
   }
   private async void Initialize() {
     try {
       login=new Form{
         Text="QuotaPulse - Connexion au compte",
         StartPosition=FormStartPosition.CenterParent,
         ClientSize=new Size(470,590),
         BackColor=Color.FromArgb(12,18,34),
         Opacity=0.04,
         ShowInTaskbar=false,
         MinimizeBox=false
       };
       login.FormClosing+=(s,e)=>{
         if(!complete && !disposed) {
           Log("USER_CLOSED_LOGIN_WINDOW");
           pending.TrySetResult(null);
         }
       };
       Panel header=new Panel{Dock=DockStyle.Top,Height=54,BackColor=Color.FromArgb(22,32,57)};
       subtitle=new Label{Dock=DockStyle.Fill,TextAlign=ContentAlignment.MiddleLeft,Font=new Font("Segoe UI",10f,FontStyle.Bold),
         ForeColor=Color.White,Padding=new Padding(12,0,0,0),Text="Connexion en cours..."};
       retry=new Button{Text="Recharger",Dock=DockStyle.Right,Width=90,Visible=false};
       retry.Click+=(s,e)=>{
         if(browser==null||browser.CoreWebView2==null)return;
         Log("USER_RELOAD");browser.CoreWebView2.Navigate(UsageUrl);
       };
       header.Controls.Add(subtitle);header.Controls.Add(retry);
       browser=new WebView2{Dock=DockStyle.Fill};
       login.Controls.Add(browser);login.Controls.Add(header);
       login.Show(owner);

       pulse=new Timer{Interval=500};
       pulse.Tick+=(s,e)=>{
         if(disposed||complete)return;
         double elapsed=(DateTime.UtcNow-began).TotalSeconds;
         if(initializing && elapsed>15){
           initializing=false;
           Log("INIT_TIMEOUT elapsed_sec="+((int)elapsed));
           ShowLogin("Chargement WebView2 trop long. Ferme pour annuler.");
           retry.Visible=true;
           // Stop the parent task: no endless spinner while the embedded runtime stalls.
           pending.TrySetResult(null);
           return;
         }
         if(!initializing && !enteredAuth && elapsed>22){
           Log("READ_TIMEOUT elapsed_sec="+((int)elapsed));
           pending.TrySetResult(null);
           return;
         }
         if(!initializing && !inspecting && !enteredAuth) {
           var task=InspectAsync();
         }
       };
       pulse.Start();

       // Explicit stable app-owned profile. Not Edge's profile or current browser session.
       profilePath=Path.Combine(Path.GetDirectoryName(typeof(IndependentQuotaSession).Assembly.Location),"WebProfile");
       Directory.CreateDirectory(profilePath);
       Log("ENV_CREATE_BEGIN");
       CoreWebView2Environment env=await CoreWebView2Environment.CreateAsync(null,profilePath);
       if(disposed||pending.Task.IsCompleted) {Log("ENV_LATE_AFTER_TIMEOUT");return;}
       Log("ENV_CREATE_OK");
       await browser.EnsureCoreWebView2Async(env);
       if(disposed||pending.Task.IsCompleted) {Log("INIT_LATE_AFTER_TIMEOUT");return;}
       initializing=false;
       Log("WEBVIEW_INIT_OK");
       browser.CoreWebView2.Settings.AreDevToolsEnabled=false;
       browser.CoreWebView2.NavigationStarting+=(s,e)=>Log("NAV_BEGIN");
       browser.CoreWebView2.NavigationCompleted+=async (s,e)=>{
         if(disposed||complete)return;
         Log(e.IsSuccess?"NAV_COMPLETE_OK":"NAV_FAILED_"+e.WebErrorStatus);
         if(!e.IsSuccess)ShowLogin("Problème de chargement, tu peux recharger.");
         await InspectAsync();
       };
       browser.CoreWebView2.Navigate(UsageUrl);
       Log("NAV_USAGE_REQUESTED");
     }catch(Exception ex) {
       Log("INIT_ERROR_"+ex.GetType().Name+"_"+ex.HResult.ToString("X8"));
       if(!disposed) {
         ShowLogin("Impossible d'initialiser WebView2. Ferme pour annuler.");
         retry.Visible=browser!=null&&browser.CoreWebView2!=null;
       }
       pending.TrySetResult(null);
     }
   }
   void ShowLogin(string status) {
     if(login==null||login.IsDisposed)return;
     login.Opacity=1;
     subtitle.Text=status;
     if(retry!=null)retry.Visible=true;
   }
   static bool LoginPage(string url,string body) {
     string u=(url??"").ToLowerInvariant(),b=(body??"").ToLowerInvariant();
     return u.Contains("/auth/")||u.Contains("/login")||u.Contains("/signin")||u.Contains("/verify")||
       b.Contains("continue with email")||b.Contains("verification code")||
       b.Contains("check your inbox")||b.Contains("verify your email")||b.Contains("enter code");
   }
   async Task InspectAsync() {
     if(disposed||complete||inspecting||browser==null||browser.CoreWebView2==null)return;
     inspecting=true;
     try {
       string url=browser.CoreWebView2.Source??"";
       string encoded=await browser.CoreWebView2.ExecuteScriptAsync("document.body ? document.body.innerText : ''");
       if(disposed||complete||pending.Task.IsCompleted)return;
       string body=new JavaScriptSerializer().Deserialize<string>(encoded)??"";
       bool isLogin=LoginPage(url,body);
       if(isLogin){
         if(!enteredAuth)Log("AUTH_REQUIRED");
         enteredAuth=true;
         ShowLogin("Termine l'identification. Aucun délai imposé.");
         return;
       }
       if(url.StartsWith("https://mcp.desktopcommander.app",StringComparison.OrdinalIgnoreCase)) {
         try {
           Quota value=Reader.ParseWeb(body);
           Log("COUNTER_READ_OK");
           complete=true;
           pending.TrySetResult(value);
           Dispose();return;
         }catch(InvalidOperationException){}
         if(!navigated&&!url.Contains("/usage")&&body.IndexOf("Tool calls",StringComparison.OrdinalIgnoreCase)>=0&&
            body.IndexOf("Devices",StringComparison.OrdinalIgnoreCase)>=0) {
           navigated=true;
           Log("AUTHENTICATED_DASHBOARD_REDIRECT_USAGE");
           browser.CoreWebView2.Navigate(UsageUrl);
           return;
         }
       }
       // A real auth flow can take as long as the person needs; never close it automatically.
       if(enteredAuth) ShowLogin("Connexion en cours. Termine le code ou recharge la page.");
     }catch(Exception ex) {
       Log("READ_ERROR_"+ex.GetType().Name);
     }finally{inspecting=false;}
   }
   public void Dispose() {
     if(disposed)return;disposed=true;
     if(pulse!=null){pulse.Stop();pulse.Dispose();pulse=null;}
     if(login!=null&&!login.IsDisposed){Form form=login;login=null;form.Close();form.Dispose();}
     browser=null;Log("DISPOSE");
   }
 }
}
