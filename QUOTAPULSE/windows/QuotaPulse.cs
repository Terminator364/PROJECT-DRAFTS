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
  public static void Save(Quota q) {
   Directory.CreateDirectory(Path.GetDirectoryName(Store));
   File.WriteAllLines(Store,new[]{q.Used.ToString(),q.Limit.ToString(),q.Avg.ToString(),q.Reset,q.Seen.ToString("o")},Encoding.UTF8);
  }
  public static Quota Load() {
   try{
    string[] v=File.ReadAllLines(Store,Encoding.UTF8);
    long used=long.Parse(v[0]),limit=long.Parse(v[1]);if(used<0||limit<=0||used>limit)return null;
    return new Quota{Used=used,Limit=limit,Left=limit-used,Avg=int.Parse(v[2]),Reset=v[3],Seen=DateTime.Parse(v[4],null,DateTimeStyles.RoundtripKind),Status="Dernier relevé"};
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
   Console.WriteLine("TEST_PASS=2;USED=7811;LIMIT=10000;LEFT=2189;AVG=976;RESET=1 déc.");
  }
 }
 public sealed class Window:Form {
  Quota data; bool busy=false; string notice="Dernier relevé"; Rectangle closeBox=new Rectangle(377,14,28,30),minBox=new Rectangle(348,14,28,30),refreshBox=new Rectangle(22,409,376,45);
  Color bg=Color.FromArgb(10,16,33),card=Color.FromArgb(25,36,64),muted=Color.FromArgb(155,171,197),mint=Color.FromArgb(38,224,177),white=Color.White;
  [DllImport("user32.dll")] static extern bool ReleaseCapture();
  [DllImport("user32.dll")] static extern IntPtr SendMessage(IntPtr h,int m,int w,int l);
  public Window(){
   this.FormBorderStyle=FormBorderStyle.None;this.StartPosition=FormStartPosition.CenterScreen;this.ClientSize=new Size(420,478);
   this.BackColor=bg;this.DoubleBuffered=true;this.Font=new Font("Segoe UI",10f);this.Icon=SystemIcons.Application;this.ShowInTaskbar=true;
   this.Text="QuotaPulse";this.AutoScaleMode=AutoScaleMode.None;this.MinimumSize=this.MaximumSize=this.Size;
   data=Reader.Load();
   this.Shown+=(s,e)=>{if(IsEdgeVisible())RefreshData();else{notice=data==null?"Ouvrir Edge, puis Actualiser":"Relevé enregistré • actualisation manuelle";Invalidate();}};
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
   base.OnPaint(e);Graphics g=e.Graphics;g.SmoothingMode=SmoothingMode.AntiAlias;g.Clear(bg);
   Panel(g,new Rectangle(22,18,34,34),11,Color.FromArgb(35,111,138));
   Center(g,"Q",17,white,new RectangleF(22,18,34,34),FontStyle.Bold);
   Txt(g,"QuotaPulse",20,white,66,17,FontStyle.Bold);
   Txt(g,"—",16,muted,348,13);Txt(g,"×",18,muted,381,10);
   Txt(g,"Desktop Commander  •  quota mensuel",9,muted,24,62);
   Panel(g,new Rectangle(22,91,376,184),20,card);
   Txt(g,"APPELS RESTANTS",10,muted,42,110,FontStyle.Bold);
   string big=data==null?"—":data.Left.ToString("N0",CultureInfo.GetCultureInfo("fr-FR"));
   Txt(g,big,40,white,38,130,FontStyle.Bold);
   Txt(g,data==null?"Aucune mesure":("sur "+data.Limit.ToString("N0",CultureInfo.GetCultureInfo("fr-FR"))+" appels"),10,muted,43,210);
   float pct=data==null?0f:(float)data.Left/data.Limit;
   Panel(g,new Rectangle(43,234,334,11),6,Color.FromArgb(57,67,96));
   if(pct>0){Panel(g,new Rectangle(43,234,Math.Max(8,(int)(334*pct)),11),6,pct<.1f?Color.FromArgb(251,145,95):mint);}
   Txt(g,data==null?"NON SYNCHRONISÉ":(pct*100f).ToString("0.0",CultureInfo.GetCultureInfo("fr-FR"))+" % disponibles",9,pct<.1f?Color.FromArgb(251,145,95):mint,43,251,FontStyle.Bold);
   Panel(g,new Rectangle(22,289,181,81),15,card);Panel(g,new Rectangle(217,289,181,81),15,card);
   Txt(g,"CONSOMMÉS",9,muted,39,305,FontStyle.Bold);
   Txt(g,data==null?"—":data.Used.ToString("N0",CultureInfo.GetCultureInfo("fr-FR")),22,white,38,327,FontStyle.Bold);
   Txt(g,"RENOUVELLEMENT",9,muted,235,305,FontStyle.Bold);
   Txt(g,data==null?"—":data.Reset,16,white,234,332,FontStyle.Bold);
   string status=busy?"Actualisation en cours…":notice;
   if(!busy&&data!=null)status+="  ·  "+data.Seen.ToString("dd/MM HH:mm");
   Txt(g,status.Length>66?status.Substring(0,63)+"…":status,9,muted,24,382);
   Panel(g,refreshBox,13,busy?Color.FromArgb(52,101,112):mint);
   Center(g,busy?"LECTURE DU COMPTE…":"↻  ACTUALISER",12,busy?muted:bg,refreshBox,FontStyle.Bold);
   Txt(g,"Sans service de fond • 0 appel MCP",8,muted,82,461);
  }
  void RefreshData(){
   if(busy)return;busy=true;notice="Lecture du quota";Invalidate();
   Task.Run(()=>{
    try{
     Quota q=Reader.Read();Reader.Save(q);
     if(!IsDisposed)BeginInvoke((Action)(()=>{data=q;notice="Synchronisé";busy=false;Invalidate();}));
    }catch(Exception ex){
     if(!IsDisposed)BeginInvoke((Action)(()=>{notice=ex.Message;busy=false;Invalidate();}));
    }
   });
  }
  protected override void OnMouseDown(MouseEventArgs e){
   base.OnMouseDown(e);
   if(closeBox.Contains(e.Location)){Close();return;}
   if(minBox.Contains(e.Location)){WindowState=FormWindowState.Minimized;return;}
   if(refreshBox.Contains(e.Location)){RefreshData();return;}
   if(e.Y<67){ReleaseCapture();SendMessage(this.Handle,0xA1,2,0);}
  }
 }
 static class Program {
  [DllImport("user32.dll")] static extern bool SetProcessDPIAware();
  [STAThread] static void Main(string[] args){
   try{SetProcessDPIAware();}catch{}
   try{
    if(args.Length>0&&args[0]=="--self-test"){Reader.Test();return;}
    if(args.Length>0&&args[0]=="--probe"){Quota q=Reader.Read();Reader.Save(q);string result=Reader.Json(q);File.WriteAllText(@"%LOCALAPPDATA%\QuotaPulse\probe-result.json",result,Encoding.UTF8);Console.WriteLine(result);return;}
   }catch(Exception e){Console.Error.WriteLine("QUOTAPULSE_ERROR="+e.Message);Environment.ExitCode=2;return;}
   Application.EnableVisualStyles();Application.SetCompatibleTextRenderingDefault(false);Application.Run(new Window());
  }
 }
}
