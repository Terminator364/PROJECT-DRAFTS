using System;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using System.Diagnostics;
using System.Drawing;
using System.Drawing.Drawing2D;
using System.Globalization;
using System.Collections.Generic;
using System.Threading.Tasks;
using System.Windows.Forms;
using System.Windows.Automation;
using System.Runtime.InteropServices;

namespace QuotaPulse {
 public sealed class Quota {
  public long Used, Limit, Left;
  public int Avg;
  public string Reset;
  public DateTime Seen;
  public string Status;
 }
 public static class Reader {
  static readonly string Store=Path.Combine(Path.GetDirectoryName(typeof(Reader).Assembly.Location),"quota.txt");
  static int Index(List<string> a,string token) {
   for(int i=0;i<a.Count;i++)if(a[i].Trim().Equals(token,StringComparison.OrdinalIgnoreCase)) return i;
   return -1;
  }
  static long Num(string text) {
   if(String.IsNullOrEmpty(text)) return -1;
   Match m=Regex.Match(text,@"^\s*(?:of\s+)?([\d\u00A0\u202F\?\s]+)",RegexOptions.IgnoreCase);
   if(!m.Success)return -1;
   string digits=Regex.Replace(m.Groups[1].Value,@"\D","");
   long n;return digits.Length==0||digits.Length>12||!long.TryParse(digits,out n)?-1:n;
  }
  static long Next(List<string> a,int start,int max){
   for(int i=start;i<Math.Min(a.Count,start+max);i++){long n=Num(a[i]);if(n>=0)return n;}return -1;
  }
  public static Quota Parse(List<string> a) {
   int p=Index(a,"Tool calls this month");
   if(p<0)throw new Exception("Libellé du compteur introuvable.");
   long used=Next(a,p+1,4);
   if(used<0)throw new Exception("Valeur des appels consommés absente.");
   int usedIdx=-1;
   for(int i=p+1;i<Math.Min(p+5,a.Count);i++){if(Num(a[i])==used){usedIdx=i;break;}}
   long limit=Next(a,usedIdx+1,5);
   if(limit<=0||used>limit||limit>1000000000)throw new Exception("Valeurs du compteur incohérentes.");
   long left=limit-used;
   int li=-1;
   for(int i=0;i<a.Count;i++)if(a[i].IndexOf("tool calls left this month",StringComparison.OrdinalIgnoreCase)>=0){li=i;break;}
   if(li>=1){
    long observed=Num(a[li-1]);
    if(observed>=0&&observed!=left)throw new Exception("Appels restants contradictoires.");
   }
   int avgIndex=Index(a,"Daily average");
   long average=avgIndex>=0?Next(a,avgIndex+1,3):-1;
   string reset="À confirmer";
   for(int i=p;i<Math.Min(a.Count,p+16);i++){
    if(a[i].Trim().Equals("Resets on",StringComparison.OrdinalIgnoreCase)||a[i].Trim().StartsWith("% used",StringComparison.OrdinalIgnoreCase)){
     for(int k=i+1;k<Math.Min(a.Count,i+4);k++){
      if(Regex.IsMatch(a[k],@"\b\d{1,2}\s+[A-Za-zÀ-ÿ]{3,}")){
       reset=a[k].Trim();break;
      }
     }
     if(reset!="À confirmer")break;
    }
   }
   if(reset=="À confirmer"){
    for(int i=0;i<a.Count-1;i++)if(a[i].Trim().Equals("Resets on",StringComparison.OrdinalIgnoreCase)){reset=a[i+1].Trim();break;}
   }
   return new Quota{Used=used,Limit=limit,Left=left,Avg=(int)Math.Max(0,Math.Min(average,1000000)),Reset=reset,Seen=DateTime.Now,Status="Synchronisé"};
  }
  public static List<string> GetNames(){
   Process target=null;
   foreach(Process p in Process.GetProcessesByName("msedge")){
    try{if(p.MainWindowHandle!=IntPtr.Zero&&p.MainWindowTitle.IndexOf("Desktop Commander",StringComparison.OrdinalIgnoreCase)>=0){target=p;break;}}catch{}
   }
   if(target==null)throw new Exception("La page Desktop Commander n'est pas ouverte dans Edge.");
   AutomationElement root=AutomationElement.FromHandle(target.MainWindowHandle);
   AutomationElementCollection nodes=root.FindAll(TreeScope.Descendants,Condition.TrueCondition);
   List<string> list=new List<string>();
   for(int i=0;i<nodes.Count;i++){
    try{string s=nodes[i].Current.Name;if(!String.IsNullOrWhiteSpace(s))list.Add(s.Trim());}catch{}
   }
   return list;
  }
  public static Quota Read(){return Parse(GetNames());}
  public static string CleanReset(string raw) {
    if(String.IsNullOrWhiteSpace(raw))return "\u00c0 confirmer";
    string t=raw.Replace('\u00a0',' ').Replace('\u202f',' ');
    Match day=Regex.Match(t,@"(?i)\b(\d{1,2})\s+([\p{L}]{3,12}\.?)");
    if(day.Success)return day.Groups[1].Value+" "+day.Groups[2].Value;
    return "\u00c0 confirmer";
  }  public static Quota ParseWeb(string raw){
   if(String.IsNullOrWhiteSpace(raw))throw new InvalidOperationException("Compteur absent");
   string t=Regex.Replace(raw.Replace('\u00a0',' ').Replace('\u202f',' ').Replace('\u2009',' '),@"\s+"," ");
   int start=t.IndexOf("Tool calls this month",StringComparison.OrdinalIgnoreCase);
   if(start<0)throw new InvalidOperationException("Compteur absent");
   string scoped=t.Substring(start,Math.Min(250,t.Length-start));
   string n=@"(\d{1,3}(?: \d{3})+|\d+)";
   Match m=Regex.Match(scoped,@"(?<!\d)"+n+@"\s*(?:/|of|sur)\s*"+n+@"(?!\d)",RegexOptions.IgnoreCase);
   if(!m.Success)throw new InvalidOperationException("Chiffres non disponibles");
   long used=Num(m.Groups[1].Value),limit=Num(m.Groups[2].Value);
   if(used<0||limit<=0||used>limit||limit>1000000000)throw new InvalidOperationException("Chiffres incohérents");
   long left=limit-used;
   Match remain=Regex.Match(t,n+@"\s*(?:tool calls left|appels restants)",RegexOptions.IgnoreCase);
   if(remain.Success && Num(remain.Groups[1].Value)!=left)throw new InvalidOperationException("Appels restants incohérents");
   Match av=Regex.Match(t,@"Daily average\s*"+n,RegexOptions.IgnoreCase);
   int average=av.Success?(int)Math.Min(1000000,Num(av.Groups[1].Value)):0;
   Match re=Regex.Match(t,@"Resets on\s*(\d{1,2}\s+[\p{L}]{3,12}\.?)",RegexOptions.IgnoreCase);
   string reset=CleanReset(re.Success?re.Groups[1].Value:"");   return new Quota{Used=used,Limit=limit,Left=left,Avg=average,Reset=reset,Seen=DateTime.Now,Status="Synchronisé"};
  }
  public static void Save(Quota q) {
   Directory.CreateDirectory(Path.GetDirectoryName(Store));
   File.WriteAllLines(Store,new[]{q.Used.ToString(),q.Limit.ToString(),q.Avg.ToString(),q.Reset,q.Seen.ToString("o")},Encoding.UTF8);
  }
  public static Quota Load() {
   try{
    string[] v=File.ReadAllLines(Store,Encoding.UTF8);
    long used=long.Parse(v[0]),limit=long.Parse(v[1]);if(used<0||limit<=0||used>limit)return null;
    return new Quota{Used=used,Limit=limit,Left=limit-used,Avg=int.Parse(v[2]),Reset=CleanReset(v[3]),Seen=DateTime.Parse(v[4],null,DateTimeStyles.RoundtripKind),Status="Dernier relevé"};
   }catch{return null;}
  }
  public static string Json(Quota q){
   return "{\"used\":"+q.Used+",\"limit\":"+q.Limit+",\"remaining\":"+q.Left+",\"daily_average\":"+q.Avg+",\"reset\":\""+q.Reset.Replace("\"","")+"\",\"captured_at\":\""+q.Seen.ToString("o")+"\"}";
  }
  public static void Test(){
   List<string> a=new List<string>{"Tool calls","78","%","7\u202F811","of 10\u202F000 this month","Resets on","1 déc.","Usage","2\u202F189"," tool calls left this month, resets on ","1 déc.","Tool calls this month","7\u202F811","/ ","10\u202F000","78","% used · Resets on","1 déc.",",","in 23 days","Daily average","976"};
   Quota q=Parse(a);
   if(q.Used!=7811||q.Limit!=10000||q.Left!=2189||q.Avg!=976||q.Reset!="1 déc.")throw new Exception("TEST_FAILED");
   a[a.IndexOf("2\u202F189")]="2\u202F188";
   bool failed=false;try{Parse(a);}catch{failed=true;}
   if(!failed)throw new Exception("CONSISTENCY_TEST_FAILED");
   Quota q2=ParseWeb("Tool calls this month 7 811 / 10 000 78% used Resets on 1 déc., in 23 days Daily average 976 2 189 tool calls left this month");
   if(q2.Left!=2189||q2.Limit!=10000||q2.Avg!=976)throw new Exception("WEB_TEST_FAILED");
   Console.WriteLine("TEST_PASS=3;USED=7811;LIMIT=10000;LEFT=2189;AVG=976;RESET=1 déc.");
  }
 }
 public sealed class Window:Form {
  Quota data; bool busy=false; string notice="Dernier relevé"; Bitmap brandLogo; System.Windows.Forms.Timer autoRefresh; Rectangle closeBox=new Rectangle(370,10,27,28),minBox=new Rectangle(340,10,27,28),refreshBox=new Rectangle(22,329,366,44);
  Color bg=Color.FromArgb(10,16,33),card=Color.FromArgb(25,36,64),muted=Color.FromArgb(155,171,197),mint=Color.FromArgb(38,224,177),white=Color.White;
  [DllImport("user32.dll")] static extern bool ReleaseCapture();
  [DllImport("user32.dll")] static extern IntPtr SendMessage(IntPtr h,int m,int w,int l);
  public Window(bool previewOnly=false){
   this.FormBorderStyle=FormBorderStyle.None;this.StartPosition=FormStartPosition.CenterScreen;this.ClientSize=new Size(410,435);
   this.BackColor=bg;this.DoubleBuffered=true;this.Font=new Font("Segoe UI",10f);this.ShowInTaskbar=true;
   try{string logoPath=Path.Combine(Path.GetDirectoryName(typeof(Window).Assembly.Location),"logo.png");if(File.Exists(logoPath))brandLogo=new Bitmap(logoPath);}catch{}
   try{string icoPath=Path.Combine(Path.GetDirectoryName(typeof(Window).Assembly.Location),"logo.ico");if(File.Exists(icoPath))this.Icon=new Icon(icoPath);}catch{}
   this.Text="QuotaPulse";this.AutoScaleMode=AutoScaleMode.None;this.MinimumSize=this.MaximumSize=this.Size;
   data=Reader.Load();
   this.Shown+=(s,e)=>{if(previewOnly){notice="Apercu graphique";Invalidate();}else if(IsEdgeVisible()||File.Exists(Path.Combine(Path.GetDirectoryName(typeof(Window).Assembly.Location),"WebProfile","quotapulse-auth-ok.flag")))RefreshData();else{notice=data==null?"Actualiser pour se connecter":"Dernier relevé · Actualiser pour connecter";Invalidate();}};
   autoRefresh=new System.Windows.Forms.Timer{Interval=20*60*1000};
   autoRefresh.Tick+=(s,e)=>{if(this.Visible&&!busy&&(IsEdgeVisible()||File.Exists(Path.Combine(Path.GetDirectoryName(typeof(Window).Assembly.Location),"WebProfile","quotapulse-auth-ok.flag"))))RefreshData();};
   autoRefresh.Start();
  }
  static bool IsEdgeVisible(){
   try {return Process.GetProcessesByName("msedge").Any(p=>p.MainWindowHandle!=IntPtr.Zero&&p.MainWindowTitle.Contains("Desktop Commander"));}catch{return false;}
  }
  static GraphicsPath Round(RectangleF r,float radius){
   GraphicsPath p=new GraphicsPath();float d=radius*2;
   p.AddArc(r.Left,r.Top,d,d,180,90);p.AddArc(r.Right-d,r.Top,d,d,270,90);p.AddArc(r.Right-d,r.Bottom-d,d,d,0,90);p.AddArc(r.Left,r.Bottom-d,d,d,90,90);p.CloseFigure();return p;
  }
  void Panel(Graphics g,Rectangle r,int radius,Color c){using(GraphicsPath p=Round(r,radius))using(SolidBrush b=new SolidBrush(c)){g.FillPath(b,p);}}
  void Txt(Graphics g,string value,float size,Color color,float x,float y,FontStyle style=FontStyle.Regular){
   using(Font f=new Font("Segoe UI",size,style,GraphicsUnit.Point))using(Brush b=new SolidBrush(color)){g.DrawString(value,f,b,x,y,StringFormat.GenericTypographic);}
  }
  void Center(Graphics g,string value,float size,Color color,RectangleF area,FontStyle style=FontStyle.Regular){
   using(Font f=new Font("Segoe UI",size,style,GraphicsUnit.Point))using(Brush b=new SolidBrush(color))
   using(StringFormat sf=new StringFormat{Alignment=StringAlignment.Center,LineAlignment=StringAlignment.Center}){g.DrawString(value,f,b,area,sf);}
  }
  protected override void OnPaint(PaintEventArgs e){
   base.OnPaint(e);
   Graphics g=e.Graphics;g.SmoothingMode=SmoothingMode.AntiAlias;g.Clear(bg);
   if(brandLogo!=null)g.DrawImage(brandLogo,new Rectangle(22,16,43,43));
   Txt(g,"QuotaPulse",18,white,74,17,FontStyle.Bold);
   Txt(g,"Desktop Commander",9,muted,76,50);
   Txt(g,"\u2014",15,muted,344,10);Txt(g,"\u00D7",16,muted,374,7);
   Rectangle hero=new Rectangle(22,84,366,153);
   using(GraphicsPath path=Round(hero,19))
   using(LinearGradientBrush brush=new LinearGradientBrush(hero,Color.FromArgb(28,58,107),Color.FromArgb(21,29,69),LinearGradientMode.ForwardDiagonal)){
     g.FillPath(brush,path);
   }
   Txt(g,"APPELS RESTANTS",10,muted,41,102,FontStyle.Bold);
   if(data!=null){
     float r=(float)data.Left/data.Limit;
     Txt(g,(r*100).ToString("0.00",CultureInfo.GetCultureInfo("fr-FR"))+" %",11,mint,304,103,FontStyle.Bold);
   }
   Txt(g,data==null?"\u2014":data.Left.ToString("N0",CultureInfo.GetCultureInfo("fr-FR")),34,white,38,126,FontStyle.Bold);
   Txt(g,data==null?"Aucun releve":"sur "+data.Limit.ToString("N0",CultureInfo.GetCultureInfo("fr-FR"))+" appels",9,muted,41,192);
   Panel(g,new Rectangle(41,214,326,8),4,Color.FromArgb(64,82,110));
   float pct=data==null?0f:(float)data.Left/data.Limit;
   if(pct>0)Panel(g,new Rectangle(41,214,Math.Max(8,(int)(326*pct)),8),4,pct<.10f?Color.FromArgb(255,156,94):mint);
   Panel(g,new Rectangle(22,249,116,69),14,card);
   Panel(g,new Rectangle(147,249,116,69),14,card);
   Panel(g,new Rectangle(272,249,116,69),14,card);
   Txt(g,"UTILIS\u00C9S",9,muted,35,260,FontStyle.Bold);
   Txt(g,data==null?"\u2014":data.Used.ToString("N0",CultureInfo.GetCultureInfo("fr-FR")),17,white,34,279,FontStyle.Bold);
   Txt(g,"PLAFOND",9,muted,160,260,FontStyle.Bold);
   Txt(g,data==null?"\u2014":data.Limit.ToString("N0",CultureInfo.GetCultureInfo("fr-FR")),17,white,159,279,FontStyle.Bold);
   Txt(g,"RENOUVELLE",8,muted,282,260,FontStyle.Bold);
   Txt(g,data==null?"\u2014":Reader.CleanReset(data.Reset),16,white,282,280,FontStyle.Bold);
   Panel(g,refreshBox,13,busy?Color.FromArgb(50,92,104):mint);
   Center(g,busy?"LECTURE EN COURS...":"ACTUALISER",12,busy?muted:bg,refreshBox,FontStyle.Bold);
   string status=busy?"Lecture en cours":notice;
   if(!busy&&data!=null)status+=" / "+data.Seen.ToString("dd/MM HH:mm");
   if(status.Length>55)status=status.Substring(0,52)+"...";
   Txt(g,status,9,muted,25,387);
   Txt(g,"Session autonome / 0 service permanent",8,muted,25,409);
  }async void RefreshData(bool userInitiated=false){
   if(busy)return;
   busy=true;notice="Lecture du compte";Invalidate();
   var stopwatch=Stopwatch.StartNew();
   try{
     Quota q=null;
     bool independent=false;
     // Use the already-authenticated Edge tab as a fast optional shortcut.
     // It is NOT required: WebView2 is the independent path when Edge is closed.
     if(IsEdgeVisible()){
       try{q=await Task.Run(()=>Reader.Read());}
       catch(Exception){q=null;}
     }
     if(q==null){
       using(var session=new IndependentQuotaSession(this,userInitiated)){
         q=await session.ReadAsync();
         independent=q!=null;
       }
     }
     if(q!=null){
       long previous=data==null?-1:data.Used;
       Reader.Save(q);data=q;
       string delta=previous<0?"Premier relev\u00e9":q.Used>=previous?"+"+(q.Used-previous)+" appels":"Nouveau cycle";
       notice=delta+" / "+stopwatch.Elapsed.TotalSeconds.ToString("0.0",CultureInfo.GetCultureInfo("fr-FR"))+" s";
       if(independent){
         string profile=Path.Combine(Path.GetDirectoryName(typeof(Window).Assembly.Location),"WebProfile");
         Directory.CreateDirectory(profile);
         File.WriteAllText(Path.Combine(profile,"quotapulse-auth-ok.flag"),DateTime.UtcNow.ToString("o"));
       }
     }else notice="Relev\u00e9 conserv\u00e9; connexion n\u00e9cessaire";
   }catch(Exception ex){notice="Erreur de lecture: "+ex.GetType().Name;}
   finally{busy=false;if(!IsDisposed)Invalidate();}
  }  protected override void OnFormClosed(FormClosedEventArgs e){
   if(autoRefresh!=null){autoRefresh.Stop();autoRefresh.Dispose();}
   if(brandLogo!=null)brandLogo.Dispose();
   base.OnFormClosed(e);
  }
  protected override void OnMouseDown(MouseEventArgs e){
   base.OnMouseDown(e);
   if(closeBox.Contains(e.Location)){Close();return;}
   if(minBox.Contains(e.Location)){WindowState=FormWindowState.Minimized;return;}
   if(refreshBox.Contains(e.Location)){RefreshData(true);return;}
   if(e.Y<67){ReleaseCapture();SendMessage(this.Handle,0xA1,2,0);}
  }
 }
 static class Program {
  [DllImport("user32.dll")] static extern bool SetProcessDPIAware();
  [STAThread] static void Main(string[] args){
   try{SetProcessDPIAware();}catch{}
   try{
    if(args.Length>0&&args[0]=="--self-test"){Reader.Test();return;}
    if(args.Length>0&&args[0]=="--probe"){Console.WriteLine("INDEPENDENT_WEBVIEW2_REQUIRES_INTERACTIVE_LOGIN");return;}
   }catch(Exception e){Console.Error.WriteLine("QUOTAPULSE_ERROR="+e.Message);Environment.ExitCode=2;return;}
   Application.EnableVisualStyles();Application.SetCompatibleTextRenderingDefault(false);Application.Run(new Window(args.Length>0 && args[0]=="--preview"));
  }
 }
}
