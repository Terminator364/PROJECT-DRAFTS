package com.quotapulse.monitor;

import android.app.Activity;
import android.content.Context;
import android.content.SharedPreferences;
import android.content.res.ColorStateList;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.Gravity;
import android.view.View;
import android.view.WindowManager;
import android.webkit.CookieManager;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.FrameLayout;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.ScrollView;
import android.widget.TextView;
import org.json.JSONTokener;
import java.text.DateFormat;
import java.text.NumberFormat;
import java.util.Date;
import java.util.Locale;

/** One compact native screen; browser is temporary, only for official authentication and reading. */
public final class MainActivity extends Activity {
  private static final String URL="https://mcp.desktopcommander.app/usage";
  private static final int BG=Color.rgb(10,15,30), PANEL=Color.rgb(25,35,60);
  private static final int FG=Color.rgb(246,249,255), GRAY=Color.rgb(154,172,197), GREEN=Color.rgb(46,222,172);
  private final Handler handler=new Handler(Looper.getMainLooper());
  private SharedPreferences prefs;
  private FrameLayout root, modal;
  private WebView browser;
  private TextView remaining, consumed, mean, reset, timestamp, message, state, percent, accountHint, change;
  private UsageChartView activityChart;
  private FrameLayout accountSheet;
  private LinearLayout activityCard;
  private boolean automaticRefresh=false;
  private long readingStartedAt=0;
  private ProgressBar meter;
  private QuotaParser.Data last;
  private long lastAt=0;
  private boolean busy=false, loginVisible=false, redirected=false, evaluating=false;
  private int reads=0;
  private long startedAt=0;
  private final Runnable scan=new Runnable() {
    @Override public void run() {
      if(!busy || browser==null)return;
      readPage();
      if(busy&&browser!=null)handler.postDelayed(this,loginVisible?5000:1500);
    }
  };

  @Override public void onCreate(Bundle state) {
    super.onCreate(state);
    getWindow().setStatusBarColor(BG);getWindow().setNavigationBarColor(BG);
    getWindow().setSoftInputMode(WindowManager.LayoutParams.SOFT_INPUT_ADJUST_RESIZE);
    prefs=getSharedPreferences("local-quota",MODE_PRIVATE);
    long u=prefs.getLong("used",-1),lim=prefs.getLong("limit",0);
    if(u>=0&&lim>0&&u<=lim){
      last=new QuotaParser.Data(u,lim,lim-u,prefs.getInt("average",0),prefs.getString("reset","À confirmer"));
      lastAt=prefs.getLong("updated",0);
    }
    drawScreen();render();
    // Cached figures appear immediately. The foreground-only refresh is throttled.
    // Provider cookies remain in Android WebView; this only checks the last known state.
  }
  @Override protected void onResume(){
    super.onResume();
    if(prefs==null||busy)return;
    long now=System.currentTimeMillis();
    long ago=now-lastAt, sinceAttempt=now-prefs.getLong("last_auto_attempt",0);
    if(prefs.getBoolean("session_success",false) && ago>=20L*60*1000
        && sinceAttempt>=20L*60*1000) {
      prefs.edit().putLong("last_auto_attempt",now).apply();
      handler.postDelayed(()->{
        if(!isFinishing()&&!busy&&prefs.getBoolean("session_success",false)){
          automaticRefresh=true;refresh(false);
        }
      },600);
    }
  }
  private int dp(float n){return Math.round(n*getResources().getDisplayMetrics().density);}
  private LinearLayout vertical(){LinearLayout l=new LinearLayout(this);l.setOrientation(1);return l;}
  private LinearLayout horizontal(){LinearLayout l=new LinearLayout(this);l.setOrientation(0);l.setGravity(Gravity.CENTER_VERTICAL);return l;}
  private LinearLayout.LayoutParams lp(int w,int h){return new LinearLayout.LayoutParams(w<0?w:dp(w),h<0?h:dp(h));}
  private void pad(View v,int a,int b,int c,int d){v.setPadding(dp(a),dp(b),dp(c),dp(d));}
  private GradientDrawable bg(int color,int radius){GradientDrawable g=new GradientDrawable();g.setColor(color);g.setCornerRadius(dp(radius));return g;}
  private GradientDrawable gradient(){GradientDrawable g=new GradientDrawable(GradientDrawable.Orientation.LEFT_RIGHT,new int[]{GREEN,Color.rgb(56,208,236)});g.setCornerRadius(dp(13));return g;}
  private TextView text(String s,int size,int color,boolean strong){
    TextView v=new TextView(this);v.setText(s);v.setTextSize(size);v.setTextColor(color);v.setIncludeFontPadding(false);
    if(strong)v.setTypeface(Typeface.create("sans-serif",Typeface.BOLD));return v;
  }
  private TextView label(String s){TextView v=text(s,11,GRAY,true);v.setLetterSpacing(.05f);return v;}
  private LinearLayout card(){LinearLayout v=vertical();pad(v,17,18,17,18);v.setBackground(bg(PANEL,19));return v;}
  private TextView action(String s,boolean primary,View.OnClickListener click){
    TextView v=text(s,14,primary?BG:FG,true);v.setGravity(Gravity.CENTER);
    v.setBackground(primary?gradient():bg(Color.rgb(38,50,80),12));v.setOnClickListener(click);return v;
  }
  private void drawScreen(){
    root=new FrameLayout(this);root.setBackgroundColor(BG);
    root.setOnApplyWindowInsetsListener((v,insets)->{
      v.setPadding(0,insets.getSystemWindowInsetTop(),0,insets.getSystemWindowInsetBottom());return insets;
    });
    ScrollView scroll=new ScrollView(this);scroll.setFillViewport(true);scroll.setVerticalScrollBarEnabled(false);
    LinearLayout column=vertical();pad(column,19,18,19,24);scroll.addView(column);root.addView(scroll);setContentView(root);
    LinearLayout head=horizontal();
    ImageView logo=new ImageView(this);logo.setImageResource(R.drawable.ic_launcher);logo.setScaleType(ImageView.ScaleType.FIT_CENTER);
    LinearLayout.LayoutParams logoP=lp(44,44);logoP.rightMargin=dp(11);head.addView(logo,logoP);
    LinearLayout heading=vertical();heading.addView(text("QuotaPulse",22,FG,true));
    TextView subtitle=text("Desktop Commander · Mon quota",11,GRAY,false);LinearLayout.LayoutParams sub=lp(-1,-2);sub.topMargin=dp(4);heading.addView(subtitle,sub);
    head.addView(heading,new LinearLayout.LayoutParams(0,-2,1));
    ImageView account=new ImageView(this);account.setImageResource(android.R.drawable.ic_menu_myplaces);
    account.setColorFilter(FG);pad(account,11,11,11,11);
    account.setContentDescription("Informations sur mon compte");
    account.setBackground(bg(Color.rgb(34,45,73),12));account.setOnClickListener(v->showAccountSummary());
    head.addView(account,lp(42,42));column.addView(head);
    LinearLayout hero=card();
    LinearLayout.LayoutParams h=lp(-1,-2);h.topMargin=dp(21);column.addView(hero,h);
    LinearLayout small=horizontal();small.addView(label("APPELS DISPONIBLES"),new LinearLayout.LayoutParams(0,-2,1));
    state=text("●  EN ATTENTE",10,GRAY,true);small.addView(state);hero.addView(small);
    remaining=text("—",48,FG,true);LinearLayout.LayoutParams large=lp(-1,-2);large.topMargin=dp(15);hero.addView(remaining,large);
    TextView desc=text("appels restants",14,GRAY,false);hero.addView(desc);
    meter=new ProgressBar(this,null,android.R.attr.progressBarStyleHorizontal);meter.setMax(1000);meter.setProgress(0);
    meter.setProgressTintList(ColorStateList.valueOf(GREEN));meter.setProgressBackgroundTintList(ColorStateList.valueOf(Color.rgb(60,71,99)));
    LinearLayout.LayoutParams ml=lp(-1,8);ml.topMargin=dp(21);hero.addView(meter,ml);
    percent=text("À synchroniser",12,GREEN,true);LinearLayout.LayoutParams pp=lp(-1,-2);pp.topMargin=dp(10);hero.addView(percent,pp);
    change=text("Le prochain relevé indiquera la variation.",11,GRAY,false);
    LinearLayout.LayoutParams chp=lp(-1,-2);chp.topMargin=dp(10);hero.addView(change,chp);

    LinearLayout two=horizontal();LinearLayout.LayoutParams twop=lp(-1,-2);twop.topMargin=dp(12);column.addView(two,twop);
    LinearLayout left=card(),right=card();
    LinearLayout.LayoutParams l=new LinearLayout.LayoutParams(0,-2,1);l.rightMargin=dp(5);
    LinearLayout.LayoutParams r=new LinearLayout.LayoutParams(0,-2,1);r.leftMargin=dp(5);two.addView(left,l);two.addView(right,r);
    left.addView(label("UTILISÉS"));consumed=text("—",25,FG,true);
    LinearLayout.LayoutParams v1=lp(-1,-2);v1.topMargin=dp(11);left.addView(consumed,v1);
    right.addView(label("MOY. / JOUR"));mean=text("—",25,FG,true);
    LinearLayout.LayoutParams v2=lp(-1,-2);v2.topMargin=dp(11);right.addView(mean,v2);
    // Separate rows prevent the reset value from squeezing the label on narrow phones.
    LinearLayout next=card();LinearLayout.LayoutParams nextP=lp(-1,-2);nextP.topMargin=dp(11);column.addView(next,nextP);
    next.addView(label("RENOUVELLEMENT"));
    reset=text("—",19,FG,true);reset.setSingleLine(true);
    reset.setEllipsize(android.text.TextUtils.TruncateAt.END);
    LinearLayout.LayoutParams resetP=lp(-1,-2);resetP.topMargin=dp(9);next.addView(reset,resetP);
    activityCard=card();LinearLayout.LayoutParams chartP=lp(-1,-2);chartP.topMargin=dp(12);column.addView(activityCard,chartP);
    LinearLayout chartTitle=horizontal();chartTitle.addView(label("ACTIVITÉ RÉELLE"),new LinearLayout.LayoutParams(0,-2,1));
    TextView historyHint=text("10 derniers intervalles",10,GRAY,false);chartTitle.addView(historyHint);activityCard.addView(chartTitle);
    activityChart=new UsageChartView(this);
    LinearLayout.LayoutParams chartBounds=lp(-1,105);chartBounds.topMargin=dp(11);activityCard.addView(activityChart,chartBounds);

    LinearLayout buttons=horizontal();LinearLayout.LayoutParams bp=lp(-1,-2);bp.topMargin=dp(15);column.addView(buttons,bp);
    TextView refresh=action("↻  ACTUALISER",true,v->{automaticRefresh=false;refresh(false);});
    buttons.addView(refresh,new LinearLayout.LayoutParams(0,dp(49),2));
    TextView historyButton=action("GRAPHIQUE",false,v->{
      activityCard.setVisibility(activityCard.getVisibility()==View.VISIBLE?View.GONE:View.VISIBLE);
    });
    LinearLayout.LayoutParams hb=new LinearLayout.LayoutParams(0,dp(49),1);hb.leftMargin=dp(9);buttons.addView(historyButton,hb);
    message=text("Aucun relevé enregistré.",12,GRAY,false);message.setLineSpacing(dp(2),1f);
    LinearLayout.LayoutParams msg=lp(-1,-2);msg.topMargin=dp(13);column.addView(message,msg);
    timestamp=text("",11,GRAY,false);LinearLayout.LayoutParams stamp=lp(-1,-2);stamp.topMargin=dp(9);column.addView(timestamp,stamp);
  }
  private String number(long n){return NumberFormat.getIntegerInstance(Locale.FRANCE).format(n);}
  private void render(){
    if(last==null){
      remaining.setText("—");consumed.setText("—");mean.setText("—");reset.setText("—");
      meter.setProgress(0);percent.setText("À synchroniser");change.setText("Aucune variation mesurée.");activityChart.setReadings(UsageHistory.parse(prefs.getString("usage_history","")));timestamp.setText("Aucune mesure enregistrée");
      if(!busy)state.setText("●  EN ATTENTE");
      return;
    }
    remaining.setText(number(last.remaining));consumed.setText(number(last.used));
    mean.setText(last.dailyAverage>0?number(last.dailyAverage):"—");reset.setText(QuotaParser.cleanReset(last.reset));
    float p=(float)last.remaining/last.limit;meter.setProgress(Math.round(p*1000));
    percent.setText(UsageHistory.percentage(last.remaining,last.limit)+" disponibles · sur "+number(last.limit));
    change.setText(prefs.getString("last_change","Premier relevé enregistré"));
    activityChart.setReadings(UsageHistory.parse(prefs.getString("usage_history","")));
    timestamp.setText("Relevé "+DateFormat.getDateTimeInstance(DateFormat.SHORT,DateFormat.SHORT,Locale.FRANCE).format(new Date(lastAt)));
    if(!busy)state.setText("●  RELEVÉ CONSERVÉ");
  }
  private void save(QuotaParser.Data d){
    long now=System.currentTimeMillis();
    long oldUsed=last==null?-1:last.used, oldLimit=last==null?0:last.limit;
    UsageHistory.Update update=UsageHistory.record(prefs.getString("usage_history",""),
      lastAt,oldUsed,oldLimit,now,d.used,d.limit);
    long duration=Math.max(0,now-readingStartedAt);
    last=d;lastAt=now;
    prefs.edit().putLong("used",d.used).putLong("limit",d.limit).putInt("average",d.dailyAverage)
      .putString("reset",QuotaParser.cleanReset(d.reset)).putLong("updated",lastAt)
      .putString("usage_history",update.serialized)
      .putString("last_change",UsageHistory.changeText(update.comparable,update.changedCycle,update.increase))
      .putLong("last_latency_ms",duration).putBoolean("session_success",true).apply();
    CookieManager.getInstance().flush();
    message.setText("Actualisé en "+String.format(Locale.FRANCE,"%.1f",duration/1000.0)+" s · "+UsageHistory.changeText(update.comparable,update.changedCycle,update.increase));
    closeBrowser();automaticRefresh=false;render();
  }

  private void refresh(boolean showAccount){
    if(busy){if(showAccount)showBrowser();return;}
    busy=true;loginVisible=false;redirected=false;evaluating=false;reads=0;startedAt=System.currentTimeMillis();readingStartedAt=startedAt;
    state.setText("●  ACTUALISATION");message.setText("Connexion au compteur…");
    modal=new FrameLayout(this);modal.setBackgroundColor(BG);
    browser=new WebView(this);
    WebSettings s=browser.getSettings();s.setJavaScriptEnabled(true);s.setDomStorageEnabled(true);
    s.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);
    s.setCacheMode(WebSettings.LOAD_DEFAULT);s.setSupportMultipleWindows(false);
    CookieManager cookies=CookieManager.getInstance();cookies.setAcceptCookie(true);
    cookies.setAcceptThirdPartyCookies(browser,true);
    browser.setWebChromeClient(new WebChromeClient());
    browser.setWebViewClient(new WebViewClient(){
      @Override public void onPageStarted(WebView v,String url,android.graphics.Bitmap icon){
        if(busy&&LoginPolicy.isAuthenticationUrl(url))showBrowser();
      }
      @Override public void onPageFinished(WebView v,String url){
        if(!busy)return;CookieManager.getInstance().flush();
        if(LoginPolicy.isAuthenticationUrl(url))showBrowser();
        readPage();
      }
      @Override public void onReceivedError(WebView v,WebResourceRequest req,WebResourceError err){
        if(busy&&req.isForMainFrame()){
          if(automaticRefresh){
            message.setText("Réseau indisponible. Dernier relevé conservé.");
            closeBrowser();automaticRefresh=false;render();
          }else{
            showBrowser();
            message.setText("Réseau indisponible. Tu peux réessayer sans perdre ton relevé.");
            if(accountHint!=null)accountHint.setText("Chargement interrompu. Appuie sur ↻ pour réessayer.");
          }
        }
      }
    });
    LinearLayout overlay=vertical();overlay.setBackgroundColor(BG);
    LinearLayout top=horizontal();pad(top,12,6,12,6);
    TextView close=action("✕",false,v->{message.setText("Dernier relevé conservé.");closeBrowser();render();});
    top.addView(close,lp(46,46));
    LinearLayout titles=vertical();pad(titles,12,0,0,0);
    titles.addView(text("Mon compte",17,FG,true));
    accountHint=text("Connecte-toi une fois, sans limite de saisie.",11,GRAY,false);
    LinearLayout.LayoutParams hint=lp(-1,-2);hint.topMargin=dp(4);titles.addView(accountHint,hint);
    top.addView(titles,new LinearLayout.LayoutParams(0,-2,1));overlay.addView(top,lp(-1,62));
    overlay.addView(browser,new LinearLayout.LayoutParams(-1,0,1));
    LinearLayout bar=horizontal();pad(bar,12,6,12,10);
    TextView retry=action("↻",false,v->{if(browser!=null)browser.reload();});bar.addView(retry,lp(48,45));
    TextView getQuota=action("LIRE LE QUOTA",true,v->{
      if(browser==null)return;accountHint.setText("Chargement du compteur…");browser.loadUrl(URL);
    });
    LinearLayout.LayoutParams get=new LinearLayout.LayoutParams(0,dp(45),1);get.leftMargin=dp(9);
    bar.addView(getQuota,get);overlay.addView(bar,lp(-1,62));
    modal.addView(overlay,new FrameLayout.LayoutParams(-1,-1));
    modal.setVisibility(showAccount?View.VISIBLE:View.INVISIBLE);
    root.addView(modal,new FrameLayout.LayoutParams(-1,-1));
    browser.loadUrl(URL);handler.removeCallbacks(scan);handler.postDelayed(scan,1000);
  }
  private void showBrowser(){
    if(modal==null)return;
    if(automaticRefresh) {
      // An actual provider login redirect invalidates the success hint, not the cookies.
      // This prevents reattempting authentication on every app launch.
      prefs.edit().putBoolean("session_success",false).apply();
      message.setText("Session expirée. Compte → Se connecter si nécessaire.");
      closeBrowser();automaticRefresh=false;render();return;
    }
    modal.setVisibility(View.VISIBLE);loginVisible=true;
    if(accountHint!=null)accountHint.setText("Connexion officielle : aucune fermeture automatique pendant la saisie.");
  }
  private void readPage(){
    if(!busy||browser==null||evaluating)return;
    if(LoginPolicy.isAuthenticationUrl(browser.getUrl())){showBrowser();return;}
    evaluating=true;final WebView active=browser;reads++;
    active.evaluateJavascript("(function(){return document.body?document.body.innerText:'';})()",raw->{
      evaluating=false;
      if(!busy||active!=browser)return;
      String page="";
      try{Object v=new JSONTokener(raw).nextValue();if(v instanceof String)page=(String)v;}catch(Exception ignored){}
      final String url=active.getUrl();
      if(LoginPolicy.isAuthenticationUrl(url)||LoginPolicy.isLoginPage(page)){showBrowser();return;}
      QuotaParser.Data d=QuotaParser.parse(page);
      if(d!=null){save(d);return;}
      if(!redirected&&LoginPolicy.canNavigateToUsage(url,page)){
        redirected=true;active.loadUrl(URL);return;
      }
      if(System.currentTimeMillis()-startedAt>18000 && !loginVisible) {
        message.setText("Lecture lente : dernier relevé conservé. Actualise quand le réseau est meilleur.");
        closeBrowser();automaticRefresh=false;render();
        return;
      }
      if(reads>25&&loginVisible&&accountHint!=null)
        accountHint.setText("Connexion en cours : termine la procédure librement.");
    });
  }
  private void closeBrowser(){
    busy=false;evaluating=false;handler.removeCallbacks(scan);
    if(browser!=null){
      WebView old=browser;browser=null;try{
        CookieManager.getInstance().flush();old.stopLoading();
        if(modal!=null)modal.removeAllViews();old.destroy();
      }catch(Exception ignored){}
    }
    if(modal!=null){root.removeView(modal);modal=null;}
    loginVisible=false;
  }
  /** Purely native account summary. Never navigates to the provider to show this tab. */
  private void showAccountSummary() {
    if(accountSheet!=null)return;
    accountSheet=new FrameLayout(this);accountSheet.setBackgroundColor(Color.argb(225,5,10,22));
    accountSheet.setOnClickListener(v->dismissAccountSummary());
    LinearLayout panel=vertical();pad(panel,22,22,22,20);panel.setBackground(bg(PANEL,22));
    panel.setOnClickListener(v->{});
    panel.addView(text("Mon compte",23,FG,true));
    TextView statusText=text(prefs.getBoolean("session_success",false)?
      "● Session enregistrée sur ce téléphone":"● Session à vérifier",13,
      prefs.getBoolean("session_success",false)?GREEN:GRAY,true);
    LinearLayout.LayoutParams st=lp(-1,-2);st.topMargin=dp(12);panel.addView(statusText,st);
    TextView summary=text(last==null?"Aucun relevé disponible":
      "Disponible : "+number(last.remaining)+" / "+number(last.limit)+
      "\nUtilisés : "+number(last.used)+"  ·  "+UsageHistory.percentage(last.remaining,last.limit)+" restants"+
      "\nVariation : "+prefs.getString("last_change","Aucune")+
      "\nDernière actualisation : "+DateFormat.getDateTimeInstance(DateFormat.MEDIUM,DateFormat.SHORT,Locale.FRANCE).format(new Date(lastAt))+
      "\nDurée de la dernière lecture : "+String.format(Locale.FRANCE,"%.1f s",prefs.getLong("last_latency_ms",0)/1000.0),
      14,FG,false);
    summary.setLineSpacing(dp(7),1.05f);
    LinearLayout.LayoutParams ss=lp(-1,-2);ss.topMargin=dp(18);panel.addView(summary,ss);
    TextView instructions=text("La connexion officielle est conservée dans la session Android. Aucun mot de passe enregistré par QuotaPulse.",11,GRAY,false);
    LinearLayout.LayoutParams ins=lp(-1,-2);ins.topMargin=dp(18);panel.addView(instructions,ins);
    LinearLayout buttons=horizontal();LinearLayout.LayoutParams bb=lp(-1,-2);bb.topMargin=dp(18);panel.addView(buttons,bb);
    TextView close=action("FERMER",false,v->dismissAccountSummary());
    buttons.addView(close,new LinearLayout.LayoutParams(0,dp(47),1));
    TextView refresh=action("ACTUALISER",true,v->{dismissAccountSummary();automaticRefresh=false;refresh(false);});
    LinearLayout.LayoutParams rr=new LinearLayout.LayoutParams(0,dp(47),1);rr.leftMargin=dp(10);buttons.addView(refresh,rr);
    // Reconnection is an explicit, separate action; account tab itself never opens the website.
    if(!prefs.getBoolean("session_success",false)) {
      TextView connect=action("SE CONNECTER",false,v->{dismissAccountSummary();automaticRefresh=false;refresh(true);});
      LinearLayout.LayoutParams cc=lp(-1,45);cc.topMargin=dp(12);panel.addView(connect,cc);
    }
    FrameLayout.LayoutParams frame=new FrameLayout.LayoutParams(-1,-2,Gravity.BOTTOM);
    frame.leftMargin=dp(12);frame.rightMargin=dp(12);frame.bottomMargin=dp(12);
    accountSheet.addView(panel,frame);
    root.addView(accountSheet,new FrameLayout.LayoutParams(-1,-1));
  }
  private void dismissAccountSummary(){
    if(accountSheet!=null){root.removeView(accountSheet);accountSheet=null;}
  }
  @Override public void onBackPressed(){
    if(accountSheet!=null){dismissAccountSummary();return;}
    if(modal!=null){
      if(browser!=null&&modal.getVisibility()==View.VISIBLE&&browser.canGoBack()){browser.goBack();return;}
      message.setText("Connexion fermée, dernier relevé conservé.");closeBrowser();render();return;
    }
    super.onBackPressed();
  }
  @Override protected void onPause(){if(browser!=null)CookieManager.getInstance().flush();super.onPause();}
  @Override protected void onDestroy(){closeBrowser();super.onDestroy();}
}
