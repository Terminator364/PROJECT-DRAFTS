package com.blessing.rescuebridge;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.Intent;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.text.InputType;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.FrameLayout;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import org.json.JSONObject;

/** User-first rescue console. USB/Windows work is bounded and requires a paired agent. */
public final class MainActivity extends Activity {
    private static final int PICK_MISSION_JSON=2003;
    private static final String PREFS="rescue_user_settings";
    private static final String LAST_SCREEN="screen";
    private final ExecutorService io=Executors.newSingleThreadExecutor();
    private final Handler mainHandler=new Handler(Looper.getMainLooper());
    private boolean busy=false;
    private boolean visible=false;
    private String latestResult="";
    private final int background=Color.rgb(245,247,251), surface=Color.WHITE,
            ink=Color.rgb(26,43,64), muted=Color.rgb(94,111,130),
            accent=Color.rgb(0,108,118),
            danger=Color.rgb(156,64,48);
    private LinearLayout page;
    private FrameLayout contentHost;
    private View homeScreen,missionsScreen,filesScreen,settingsScreen;
    private Button[] navButtons;
    private TextView status, explanation, localHint, lastAction, console;
    private EditText host,port,secret,fileName,fileContent;
    private String activeScreen="HOME";

    private final Runnable foregroundCheck=new Runnable() {
        @Override public void run() {
            if(!visible)return;
            if(!busy && isConfigured())execute("/status",new JSONObject(),true);
            mainHandler.postDelayed(this,60000);
        }
    };

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        getWindow().setStatusBarColor(Color.rgb(246,248,251));
        getWindow().setNavigationBarColor(Color.rgb(255,255,255));
        getWindow().getDecorView().setSystemUiVisibility(View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR|View.SYSTEM_UI_FLAG_LIGHT_NAVIGATION_BAR);
        LinearLayout shell=new LinearLayout(this);
        shell.setOrientation(LinearLayout.VERTICAL);
        shell.setBackgroundColor(background);
        contentHost=new FrameLayout(this);
        shell.addView(contentHost,new LinearLayout.LayoutParams(-1,0,1));
        homeScreen=buildHome();
        missionsScreen=buildMissions();
        filesScreen=buildFiles();
        settingsScreen=buildSettings();
        LinearLayout nav=new LinearLayout(this);
        nav.setOrientation(LinearLayout.HORIZONTAL);
        nav.setPadding(dp(4),dp(5),dp(4),dp(5));
        nav.setBackgroundColor(surface);
        navButtons=new Button[4];
        String[] labels={"Accueil","Missions","Fichiers","Réglages"};
        String[] codes={"HOME","MISSIONS","FILES","SETTINGS"};
        for(int i=0;i<labels.length;i++) {
            final String screen=codes[i];
            Button button=new Button(this);
            button.setAllCaps(false);
            button.setText(labels[i]);
            button.setTextSize(12);
            button.setMinHeight(dp(54));
            button.setPadding(dp(2),dp(7),dp(2),dp(7));
            button.setOnClickListener(v->showScreen(screen));
            nav.addView(button,new LinearLayout.LayoutParams(0,-2,1));
            navButtons[i]=button;
        }
        shell.addView(nav,new LinearLayout.LayoutParams(-1,-2));
        setContentView(shell);
        String saved=getSharedPreferences(PREFS,MODE_PRIVATE).getString(LAST_SCREEN,"HOME");
        showScreen(saved);
        refreshSetupState();
        localHint.setText("Réseau du téléphone : "+LocalLinkInspector.summary());
    }

    @Override protected void onResume() {
        super.onResume();
        visible=true;
        mainHandler.removeCallbacks(foregroundCheck);
        mainHandler.postDelayed(foregroundCheck,1000);
    }
    @Override protected void onPause() {
        visible=false;
        mainHandler.removeCallbacks(foregroundCheck);
        super.onPause();
    }
    @Override protected void onDestroy() {
        mainHandler.removeCallbacks(foregroundCheck);
        io.shutdownNow();
        super.onDestroy();
    }

    private ScrollView newPage(String eyebrow,String title,String subtitle) {
        ScrollView scroll=new ScrollView(this);
        scroll.setFillViewport(true);
        scroll.setClipToPadding(false);
        page=new LinearLayout(this);
        page.setOrientation(LinearLayout.VERTICAL);
        page.setPadding(dp(17),dp(20),dp(17),dp(34));
        scroll.addView(page);
        text(eyebrow,12,accent,true);
        text(title,25,ink,true);
        text(subtitle,13,muted,false);
        return scroll;
    }
    private View buildHome() {
        ScrollView v=newPage("BCP  /  USB RESCUE", "Mon ordinateur", "État de MBMPC et réparation guidée");
        LinearLayout state=card();
        state.addView(smallCaps("ÉTAT DU LIEN"));
        status=value("À vérifier",22,ink,true);
        state.addView(status);
        explanation=value(RescueAdvisor.problem("USB_UNAVAILABLE"),14,muted,false);
        state.addView(explanation);
        primary(state,"Diagnostiquer maintenant",()->execute("/status",new JSONObject(),false));
        secondary(state,"Diagnostic détaillé",()->execute("/diagnostics",new JSONObject(),false));
        LinearLayout guide=card();
        guide.addView(smallCaps("CONNEXION EN 3 ÉTAPES"));
        guide.addView(value("1. Brancher le téléphone avec un câble USB de données.\n2. Activer le partage de connexion USB sur Android.\n3. Sur Windows, lancer notre agent et enregistrer l'appairage dans Réglages.",14,ink,false));
        secondary(guide,"Configurer mon PC",()->showScreen("SETTINGS"));
        LinearLayout network=card();
        network.addView(smallCaps("INDICE RÉSEAU LOCAL"));
        localHint=value("Analyse locale disponible à l'ouverture",13,muted,false);
        network.addView(localHint);
        secondary(network,"Actualiser cet indice",()->localHint.setText("Réseau du téléphone : "+LocalLinkInspector.summary()));
        LinearLayout latest=card();
        latest.addView(smallCaps("DERNIÈRE OPÉRATION"));
        lastAction=value("Aucune opération réalisée",14,ink,false);
        latest.addView(lastAction);
        text("La vérification automatique est limitée à l'application ouverte. Aucun contrôle complet du bureau n'est activé.",12,muted,false);
        return v;
    }
    private View buildMissions() {
        ScrollView v=newPage("ACTIONS AUTORISÉES", "Mes missions", "Importer une mission préparée dans ChatGPT, sans connexion automatique au chat.");
        LinearLayout importCard=card();
        importCard.addView(smallCaps("IMPORT JSON"));
        importCard.addView(value("Fichier de mission JSON, valide au maximum 24 heures. Une écriture nécessite ta confirmation explicite.",14,ink,false));
        primary(importCard,"Importer une mission JSON",this::pickMission);
        secondary(importCard,"Partager le dernier résultat",this::shareResult);
        LinearLayout results=card();
        results.addView(smallCaps("JOURNAL LOCAL (NON PERSISTANT)"));
        console=value("Aucun résultat pour cette session.",13,ink,false);
        console.setTextIsSelectable(true);
        results.addView(console);
        secondary(results,"Consulter le journal Windows",()->execute("/audit",new JSONObject(),false));
        text("Les missions ne disposent ni d'un shell général ni d'un accès graphique Windows dans cette version.",12,muted,false);
        return v;
    }
    private View buildFiles() {
        ScrollView v=newPage("ESPACE ISOLÉ", "Fichiers de test", "Lecture et écriture dans le seul dossier autorisé par l'agent Windows.");
        LinearLayout actions=card();
        actions.addView(smallCaps("DOSSIER DE TEST WINDOWS"));
        primary(actions,"Lister les fichiers",()->execute("/files",new JSONObject(),false));
        filesInputLabel(actions,"Chemin relatif (ex. notes/essai.txt)");
        fileName=input(actions,"demo.txt",InputType.TYPE_CLASS_TEXT,"demo.txt");
        filesInputLabel(actions,"Texte de test");
        fileContent=input(actions,"Contenu du fichier",InputType.TYPE_CLASS_TEXT|InputType.TYPE_TEXT_FLAG_MULTI_LINE,"Essai BCP USB Rescue");
        fileContent.setMinLines(4);
        secondary(actions,"Lire le fichier",this::readFile);
        primary(actions,"Écrire avec confirmation",this::confirmWrite);
        text("Ce module n'expose pas tous les fichiers du PC : les chemins restent limités à l'espace de test.",12,muted,false);
        return v;
    }
    private View buildSettings() {
        ScrollView v=newPage("PARAMÈTRES AVANCÉS", "Connexion et appairage", "À configurer une seule fois, puis à conserver lors des mises à jour compatibles.");
        LinearLayout connection=card();
        connection.addView(smallCaps("MON PC WINDOWS"));
        filesInputLabel(connection,"Adresse IPv4 privée de MBMPC (via DIAGNOSTIC.cmd)");
        host=input(connection,"192.168.x.x",InputType.TYPE_CLASS_PHONE,
                getSharedPreferences(PREFS,MODE_PRIVATE).getString("host",""));
        filesInputLabel(connection,"Port");
        port=input(connection,"8766",InputType.TYPE_CLASS_NUMBER,
                getSharedPreferences(PREFS,MODE_PRIVATE).getString("port","8766"));
        filesInputLabel(connection,"Clé d'appairage locale (64 caractères hexadécimaux)");
        secret=input(connection,"Clé créée par l'agent Windows",InputType.TYPE_CLASS_TEXT|InputType.TYPE_TEXT_VARIATION_PASSWORD,"");
        try {secret.setText(SecurePairingStore.load(this));}catch(Exception ignored) {}
        primary(connection,"Enregistrer l'appairage",this::saveKey);
        secondary(connection,"Oublier l'appairage",this::confirmForgetKey);
        LinearLayout safety=card();
        safety.addView(smallCaps("SÉCURITÉ ET LIMITES"));
        safety.addView(value("Version pilote. Le canal HTTP utilise une signature HMAC mais ne chiffre pas les données. Réserve-le au réseau USB privé avec un PC de confiance. N'importe quel réseau Wi-Fi public est exclu.",14,danger,false));
        safety.addView(value("Le câble ne donne pas à ChatGPT l'autorisation d'exécuter des commandes. Les actions restent bornées par l'agent Windows et nécessitent les permissions applicables.",13,muted,false));
        text("BCP USB Rescue · 0.3.1 pilote · Android 8+ · aucune télémétrie externe ajoutée",12,muted,false);
        return v;
    }

    private void showScreen(String screen) {
        if(!"HOME".equals(screen)&&!"MISSIONS".equals(screen)&&!"FILES".equals(screen)&&!"SETTINGS".equals(screen)) screen="HOME";
        activeScreen=screen;
        View target="HOME".equals(screen)?homeScreen:"MISSIONS".equals(screen)?missionsScreen:"FILES".equals(screen)?filesScreen:settingsScreen;
        contentHost.removeAllViews();
        contentHost.addView(target,new FrameLayout.LayoutParams(-1,-1));
        if(navButtons!=null){
            String[] keys={"HOME","MISSIONS","FILES","SETTINGS"};
            for(int i=0;i<navButtons.length;i++){
                boolean selected=keys[i].equals(screen);
                navButtons[i].setTextColor(selected?accent:muted);
                navButtons[i].setBackground(shape(selected?Color.rgb(230,246,246):surface,10));
                navButtons[i].setContentDescription(navButtons[i].getText()+ (selected?" sélectionné":""));
            }
        }
        getSharedPreferences(PREFS,MODE_PRIVATE).edit().putString(LAST_SCREEN,screen).apply();
    }
    private boolean isConfigured(){return host!=null && secret!=null && BridgeClient.isPrivateIpv4(host.getText().toString().trim()) && secret.getText().toString().trim().matches("[0-9a-fA-F]{64}");}
    private void refreshSetupState(){
        if(!isConfigured()){
            status.setText("Configuration requise");
            explanation.setText(host.getText().length()==0?RescueAdvisor.problem("CONFIGURATION_MISSING"):RescueAdvisor.problem("PAIRING_REQUIRED"));
        }
    }

    private int dp(int n){return Math.round(n*getResources().getDisplayMetrics().density);}
    private GradientDrawable shape(int color,int radius){GradientDrawable d=new GradientDrawable();d.setColor(color);d.setCornerRadius(dp(radius));return d;}
    private TextView value(String s,int sp,int color,boolean bold){
        TextView t=new TextView(this);t.setText(s);t.setTextSize(sp);t.setTextColor(color);
        t.setPadding(0,dp(6),0,dp(7));
        if(bold)t.setTypeface(null,Typeface.BOLD);
        t.setBreakStrategy(android.text.Layout.BREAK_STRATEGY_HIGH_QUALITY);
        return t;
    }
    private TextView text(String s,int sp,int color,boolean bold){TextView t=value(s,sp,color,bold);page.addView(t);return t;}
    private TextView smallCaps(String s){TextView t=value(s,11,accent,true);t.setLetterSpacing(.07f);return t;}
    private LinearLayout card(){
        LinearLayout c=new LinearLayout(this);c.setOrientation(LinearLayout.VERTICAL);
        c.setPadding(dp(17),dp(15),dp(17),dp(16));c.setBackground(shape(surface,17));
        c.setElevation(dp(1));
        LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-1,-2);lp.topMargin=dp(14);
        page.addView(c,lp);return c;
    }
    private void filesInputLabel(LinearLayout c,String s){c.addView(value(s,13,ink,true));}
    private EditText input(LinearLayout parent,String hint,int type,String initial){
        EditText field=new EditText(this);
        field.setInputType(type);field.setSingleLine((type&InputType.TYPE_TEXT_FLAG_MULTI_LINE)==0);
        field.setTextSize(15);field.setTextColor(ink);field.setHintTextColor(muted);field.setHint(hint);
        field.setPadding(dp(13),dp(12),dp(13),dp(12));field.setBackground(shape(background,11));
        field.setText(initial);
        LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-1,-2);lp.topMargin=dp(4);lp.bottomMargin=dp(12);
        parent.addView(field,lp);return field;
    }
    private void button(LinearLayout parent,String title,Runnable handler,boolean main){
        Button b=new Button(this);b.setAllCaps(false);b.setText(title);b.setTextSize(14);
        b.setTextColor(main?Color.WHITE:accent);b.setBackground(shape(main?accent:Color.rgb(231,245,245),12));
        b.setMinHeight(dp(50));b.setPadding(dp(12),dp(10),dp(12),dp(10));
        LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-1,-2);lp.topMargin=dp(10);parent.addView(b,lp);
        b.setOnClickListener(v->handler.run());
    }
    private void primary(LinearLayout p,String title,Runnable r){button(p,title,r,true);}
    private void secondary(LinearLayout p,String title,Runnable r){button(p,title,r,false);}
    private JSONObject args(String... values){JSONObject j=new JSONObject();try{for(int i=0;i<values.length;i+=2)j.put(values[i],values[i+1]);}catch(Exception ignored){}return j;}

    private void append(String message){
        String old=console.getText().toString();
        String next=message+"\n\n"+old;
        if(next.length()>10000)next=next.substring(0,10000);
        console.setText(next);
        lastAction.setText(message.length()>400?message.substring(0,400)+"…":message);
    }
    private void saveKey(){
        String key=secret.getText().toString().trim();
        String address=host.getText().toString().trim();
        if(!key.matches("[0-9a-fA-F]{64}")){append("Clé invalide : exactement 64 caractères hexadécimaux.");return;}
        try {new BridgeClient(address,Integer.parseInt(port.getText().toString().trim()),key);
            SecurePairingStore.save(this,key);
            if(!getSharedPreferences(PREFS,MODE_PRIVATE).edit().putString("host",address).putString("port",port.getText().toString().trim()).commit())
                throw new IllegalStateException("Enregistrement de configuration refusé");
            append("Appairage sauvegardé localement. Teste maintenant la connexion.");
            showScreen("HOME");
            execute("/status",new JSONObject(),false);
        } catch(Exception e){append("Configuration refusée : "+e.getMessage());}
    }
    private void confirmForgetKey(){
        new AlertDialog.Builder(this).setTitle("Effacer l'appairage ?")
          .setMessage("La clé locale et sa protection Android Keystore seront effacées. Le PC ne sera pas modifié.")
          .setNegativeButton("Annuler",(d,w)->{})
          .setPositiveButton("Effacer",(d,w)->{
              try{SecurePairingStore.clear(this);secret.setText("");append("Appairage local effacé.");refreshSetupState();}
              catch(Exception e){append("Échec de l'effacement : "+e.getClass().getSimpleName());}
          }).show();
    }
    private void readFile(){execute("/read",args("path",fileName.getText().toString().trim()),false);}
    private void confirmWrite(){
        String path=fileName.getText().toString().trim(), data=fileContent.getText().toString();
        if(!MissionPolicy.safeRelativePath(path)||!MissionPolicy.validWriteContent(data)){
            append("Écriture refusée : chemin ou contenu invalide.");return;
        }
        new AlertDialog.Builder(this).setTitle("Écrire sur ton vrai PC ?")
         .setMessage("Fichier de test : "+path+"\nTaille : "+data.getBytes(StandardCharsets.UTF_8).length+" octets\n\nUne sauvegarde sera conservée si le fichier existe.")
         .setNegativeButton("Annuler",(d,w)->append("Écriture annulée"))
         .setPositiveButton("Autoriser",(d,w)->{
             JSONObject j=args("path",path,"content",data);
             try{j.put("approved",true);}catch(Exception ignored){}
             execute("/write",j,false);
         }).show();
    }
    private void pickMission(){
        Intent i=new Intent(Intent.ACTION_OPEN_DOCUMENT);
        i.addCategory(Intent.CATEGORY_OPENABLE);
        i.setType("application/json");
        i.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
        startActivityForResult(i,PICK_MISSION_JSON);
    }
    @Override protected void onActivityResult(int requestCode,int resultCode,Intent data){
        super.onActivityResult(requestCode,resultCode,data);
        if(requestCode!=PICK_MISSION_JSON||resultCode!=RESULT_OK||data==null||data.getData()==null)return;
        try(InputStream in=getContentResolver().openInputStream(data.getData())){
            if(in==null)throw new IllegalStateException("Mission illisible");
            ByteArrayOutputStream out=new ByteArrayOutputStream();byte[] buf=new byte[4096];int n;
            while((n=in.read(buf))!=-1){
                if(out.size()+n>32768)throw new IllegalArgumentException("Mission trop volumineuse (32 KiB max)");
                out.write(buf,0,n);
            }
            executeMission(new JSONObject(new String(out.toByteArray(),StandardCharsets.UTF_8)));
        }catch(Exception e){append("Mission refusée : "+e.getMessage());}
    }
    private void executeMission(JSONObject mission)throws Exception{
        if(!"bcp-rescue-mission/1".equals(mission.optString("schema")))throw new IllegalArgumentException("Schéma inconnu");
        String action=mission.optString("action","");
        if(!MissionPolicy.actionAllowed(action))throw new IllegalArgumentException("Action non autorisée");
        long now=System.currentTimeMillis()/1000L, expires=mission.optLong("expires_unix_seconds",0L);
        if(!MissionPolicy.validExpiry(now,expires))throw new IllegalArgumentException("Mission expirée ou trop longue");
        JSONObject payload=mission.optJSONObject("payload");if(payload==null)payload=new JSONObject();
        payload.remove("approved"); // ChatGPT cannot approve disk modifications on behalf of user.
        if("read".equals(action)||"write".equals(action)){
            if(!MissionPolicy.safeRelativePath(payload.optString("path","")))throw new IllegalArgumentException("Chemin dangereux");
        }
        if("write".equals(action)){
            String content=payload.optString("content",null);
            if(!MissionPolicy.validWriteContent(content))throw new IllegalArgumentException("Contenu invalide");
            JSONObject finalPayload=payload;
            new AlertDialog.Builder(this).setTitle("Confirmer la mission sur MBMPC")
              .setMessage("Écriture réelle dans l'espace de test : "+payload.optString("path")+"\n"+content.getBytes(StandardCharsets.UTF_8).length+" octets")
              .setNegativeButton("Refuser",(d,w)->append("Mission d'écriture refusée"))
              .setPositiveButton("Autoriser",(d,w)->{
                  try{finalPayload.put("approved",true);execute("/write",finalPayload,false);}
                  catch(Exception e){append("Erreur mission : "+e.getMessage());}
              }).show();
        } else {
            append("Mission JSON validée : "+action);
            execute("/"+action,payload,false);
        }
    }
    private void shareResult(){
        if(latestResult.isEmpty()){append("Aucun résultat à partager.");return;}
        Intent i=new Intent(Intent.ACTION_SEND);
        i.setType("text/plain");i.putExtra(Intent.EXTRA_TEXT,latestResult);
        startActivity(Intent.createChooser(i,"Partager le résultat du diagnostic"));
    }
    private void execute(String path,JSONObject payload,boolean silent){
        if(busy){if(!silent)append("Une autre opération est déjà en cours.");return;}
        String address=host.getText().toString().trim();
        String k=secret.getText().toString().trim();
        if(!BridgeClient.isPrivateIpv4(address)){
            status.setText("Configuration requise");explanation.setText(RescueAdvisor.problem("CONFIGURATION_MISSING"));
            if(!silent)showScreen("SETTINGS");return;
        }
        if(!k.matches("[0-9a-fA-F]{64}")){
            status.setText("Appairage requis");explanation.setText(RescueAdvisor.problem("PAIRING_REQUIRED"));
            if(!silent)showScreen("SETTINGS");return;
        }
        final BridgeClient client;
        try{client=new BridgeClient(address,Integer.parseInt(port.getText().toString().trim()),k);}
        catch(Exception e){if(!silent)append("Configuration : "+e.getMessage());return;}
        busy=true;
        status.setText("Vérification en cours…");
        explanation.setText("Test de réponse signée de l'agent Windows.");
        io.execute(()->{
            try{
                JSONObject result=client.perform(path,payload);
                runOnUiThread(()->{
                    busy=false;
                    boolean accepted=result.optBoolean("ok");
                    status.setText(accepted?"PC joignable":"Action refusée");
                    explanation.setText(accepted?RescueAdvisor.problem("LINK_VERIFIED"):
                        "L'agent a répondu mais n'a pas accepté l'action. Consulte la réponse.");
                    latestResult=path+"\n"+result.toString();
                    if(!silent||!accepted)append(latestResult);
                });
            }catch(Exception e){
                runOnUiThread(()->{
                    busy=false;status.setText("PC non accessible");
                    String code=RescueAdvisor.codeForException(e.getClass().getSimpleName());
                    explanation.setText(RescueAdvisor.problem(code));
                    if(!silent)append("Échec "+path+" : "+RescueAdvisor.problem(code));
                });
            }
        });
    }
}