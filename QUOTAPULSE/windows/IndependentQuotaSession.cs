using System;
using System.Drawing;
using System.IO;
using System.Threading.Tasks;
using System.Windows.Forms;
using System.Web.Script.Serialization;
using Microsoft.Web.WebView2.Core;
using Microsoft.Web.WebView2.WinForms;

namespace QuotaPulse {
 public sealed class IndependentQuotaSession : IDisposable {
   private const string UsageUrl="https://mcp.desktopcommander.app/usage";
   private readonly Form owner;
   private Form login;
   private WebView2 browser;
   private Timer poll;
   private Label subtitle;
   private TaskCompletionSource<Quota> pending;
   private bool inspecting=false,navigated=false,complete=false;
   private DateTime began;
   public IndependentQuotaSession(Form parent){owner=parent;}
   public Task<Quota> ReadAsync(){
     pending=new TaskCompletionSource<Quota>();
     Initialize();return pending.Task;
   }
   private async void Initialize(){
     try{
       login=new Form{Text="QuotaPulse · Connexion",StartPosition=FormStartPosition.CenterParent,ClientSize=new Size(475,625),BackColor=Color.FromArgb(12,18,34),Opacity=0,ShowInTaskbar=false};
       login.FormClosing+=(sender,e)=>{if(!complete)pending.TrySetResult(null);};
       Panel heading=new Panel{Dock=DockStyle.Top,Height=55,BackColor=Color.FromArgb(20,29,51)};
       subtitle=new Label{Dock=DockStyle.Fill,TextAlign=ContentAlignment.MiddleLeft,Font=new Font("Segoe UI",10f,FontStyle.Bold),
        Text="Connexion Desktop Commander · une fois",ForeColor=Color.White,Padding=new Padding(15,0,4,0)};
       heading.Controls.Add(subtitle);
       browser=new WebView2{Dock=DockStyle.Fill};
       login.Controls.Add(browser);login.Controls.Add(heading);
       login.Show(owner);
       string dir=Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),"QuotaPulse","WebProfile");
       Directory.CreateDirectory(dir);
       CoreWebView2Environment env=await CoreWebView2Environment.CreateAsync(null,dir);
       await browser.EnsureCoreWebView2Async(env);
       browser.CoreWebView2.Settings.AreDevToolsEnabled=false;
       browser.CoreWebView2.NavigationCompleted+=async (s,e)=>{if(!e.IsSuccess&&login!=null){ShowLogin("Réseau lent · recharge la page si nécessaire");}await InspectAsync();};
       began=DateTime.Now;
       poll=new Timer{Interval=1700};
       poll.Tick+=async (s,e)=>{await InspectAsync();};
       poll.Start();
       browser.CoreWebView2.Navigate(UsageUrl);
     }catch(Exception ex){
       if(login!=null)ShowLogin("WebView2 indisponible · "+ex.GetType().Name);
       else pending.TrySetResult(null);
     }
   }
   private void ShowLogin(string status){
     if(login!=null&&!login.IsDisposed){
       login.Opacity=1;
       if(subtitle!=null)subtitle.Text=status;
     }
   }
   private static bool LoginPage(string url,string body){
     string u=(url??"").ToLowerInvariant(),b=(body??"").ToLowerInvariant();
     return u.StartsWith("https://auth.desktopcommander.app") ||
      u.Contains("/auth/")||u.Contains("/signin")||u.Contains("/login")||
      b.Contains("continue with email")||b.Contains("verification code")||
      b.Contains("check your inbox")||b.Contains("verify your email")||b.Contains("enter code");
   }
   private async Task InspectAsync(){
     if(inspecting||complete||browser==null||browser.CoreWebView2==null)return;
     inspecting=true;
     try{
       string url=browser.CoreWebView2.Source??"";
       string encoded=await browser.CoreWebView2.ExecuteScriptAsync("document.body ? document.body.innerText : ''");
       string body=new JavaScriptSerializer().Deserialize<string>(encoded)??"";
       if(LoginPage(url,body)){
         ShowLogin("Saisis ton e-mail et ton code · sans fermeture automatique");
         return;
       }
       if(url.StartsWith("https://mcp.desktopcommander.app",StringComparison.OrdinalIgnoreCase)){
         try{
           Quota value=Reader.ParseWeb(body);
           complete=true;
           pending.TrySetResult(value);
           Dispose();
           return;
         }catch(InvalidOperationException){}
         if(!navigated && !url.Contains("/usage") && body.IndexOf("Tool calls",StringComparison.OrdinalIgnoreCase)>=0 && body.IndexOf("Devices",StringComparison.OrdinalIgnoreCase)>=0){
           navigated=true;
           browser.CoreWebView2.Navigate(UsageUrl);
           return;
         }
       }
       if((DateTime.Now-began).TotalSeconds>35)ShowLogin("Page lente · termine la connexion ou recharge-la");
     }catch(Exception ex){
       if((DateTime.Now-began).TotalSeconds>25)ShowLogin("Lecture en attente · "+ex.GetType().Name);
     }finally{inspecting=false;}
   }
   public void Dispose(){
     if(poll!=null){poll.Stop();poll.Dispose();poll=null;}
     if(login!=null&&!login.IsDisposed){
       var f=login;login=null;f.Close();f.Dispose();
     }
     browser=null;
   }
 }
}