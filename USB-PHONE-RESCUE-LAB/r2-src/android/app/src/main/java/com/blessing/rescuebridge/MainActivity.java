package com.blessing.rescuebridge;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.Intent;
import java.io.InputStream;
import java.io.ByteArrayOutputStream;
import java.nio.charset.StandardCharsets;
import android.os.Bundle;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.text.InputType;
import android.view.View;
import android.view.Gravity;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import org.json.JSONObject;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/** Explicit local-USB operator UI, never a remote unbounded action service. */
public final class MainActivity extends Activity {
    private final ExecutorService io=Executors.newSingleThreadExecutor();
    private EditText host,port,secret,fileName,fileContent;
    private TextView status,console;
    private volatile boolean busy=false;
    private static final int PICK_MISSION_JSON = 2003;
    private String latestResult = "";
    private int accent=Color.rgb(61,203,222), surface=Color.rgb(20,32,52), white=Color.rgb(233,242,255);
    private LinearLayout screen;

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        getWindow().setStatusBarColor(Color.rgb(9,18,31));getWindow().setNavigationBarColor(Color.rgb(9,18,31));
        ScrollView sc=new ScrollView(this);sc.setFillViewport(true);sc.setBackgroundColor(Color.rgb(9,18,31));
        screen=new LinearLayout(this);screen.setOrientation(LinearLayout.VERTICAL);screen.setPadding(dp(20),dp(24),dp(20),dp(40));
        sc.addView(screen);setContentView(sc);
        label("BCP • USB RESCUE",12,accent,true);
        label("Passerelle PC de secours",27,white,true);
        label("Client Android local — edition pilote R1",14,Color.rgb(161,181,205),false);
        label("⚠️ PILOTE USB. Le mode reseau ne chiffre pas les donnees. Ne l'utilise pas sur un Wi-Fi public ni pour des documents sensibles.",13,Color.rgb(255,205,118),false);
        panelTitle("1  Connexion au PC");
        label("IP Windows de l'adaptateur USB",13,white,false);
        host=field("Ex. 192.168.42.123 (adresse Windows)",InputType.TYPE_CLASS_PHONE);host.setText(getPreferences(MODE_PRIVATE).getString("host",""));
        label("Trouve cette IP via DIAGNOSTIC.cmd sur le PC. L'adresse varie selon le partage USB.",12,Color.rgb(161,181,205),false);
        label("Port agent Windows",13,white,false);
        port=field("8766",InputType.TYPE_CLASS_NUMBER);port.setText("8766");
        label("Cle locale d'appairage (64 caracteres hex)",13,white,false);
        secret=field("Cle affichee dans pairing-key.txt",InputType.TYPE_CLASS_TEXT|InputType.TYPE_TEXT_VARIATION_PASSWORD);
        try {secret.setText(SecurePairingStore.load(this));} catch(Exception err) { append("Stockage de cle inaccessible; reappairer"); }
        buttons(new String[]{"Enregistrer la cle","Oublier la cle"},new Runnable[]{this::saveKey,this::forgetKey});
        panelTitle("2  Diagnostics autorises");
        status=label("Etat : non connecte",16,accent,true);
        buttons(new String[]{"Tester la connexion","Diagnostic Windows","Lister les fichiers","Journal"},new Runnable[]{
                ()->execute("/status",new JSONObject()),()->execute("/diagnostics",new JSONObject()),
                ()->execute("/files",new JSONObject()),()->execute("/audit",new JSONObject())});
        panelTitle("3  Espace de fichiers de test uniquement");
        label("Chemin relatif au dossier autorise",13,white,false);
        fileName=field("demo.txt",InputType.TYPE_CLASS_TEXT);fileName.setText("demo.txt");
        label("Contenu de test (64 KiB maximum)",13,white,false);
        fileContent=field("Texte de test",InputType.TYPE_CLASS_TEXT|InputType.TYPE_TEXT_FLAG_MULTI_LINE);
        fileContent.setMinLines(3);fileContent.setText("Bonjour depuis BCP USB Rescue (test seulement)");
        buttons(new String[]{"Lire fichier","Ecrire avec confirmation"},new Runnable[]{this::readFile,this::confirmWrite});
        panelTitle("4  Mission ChatGPT (transfert manuel)");
        label("Une mission JSON fournie dans le chat peut etre importee depuis les fichiers Android. Aucune connexion ChatGPT automatique n'est disponible.",13,white,false);
        buttons(new String[]{"Importer mission JSON","Partager dernier resultat"},new Runnable[]{this::pickMission,this::shareResult});
        panelTitle("5  Resultats / erreurs");
        console=label("En attente. Connecte le cable, active le partage USB et lance l'agent Windows.",13,Color.rgb(180,219,241),false);
        label("L'application ne commande ni l'ecran Windows, ni PowerShell arbitraire. Aucune connexion native a ChatGPT n'est encore integree.",12,Color.rgb(150,166,189),false);
    }
    private int dp(int n){return Math.round(n*getResources().getDisplayMetrics().density);}
    private GradientDrawable shape(int color){GradientDrawable d=new GradientDrawable();d.setColor(color);d.setCornerRadius(dp(11));return d;}
    private TextView label(String s,int size,int color,boolean bold){
        TextView t=new TextView(this);t.setText(s);t.setTextSize(size);t.setTextColor(color);
        t.setPadding(0,dp(7),0,dp(6));if(bold)t.setTypeface(null,Typeface.BOLD);
        screen.addView(t);return t;
    }
    private void panelTitle(String s){TextView t=label(s,18,white,true);t.setPadding(0,dp(24),0,dp(7));}
    private EditText field(String hint,int type){
        EditText e=new EditText(this);e.setSingleLine((type&InputType.TYPE_TEXT_FLAG_MULTI_LINE)==0);
        e.setInputType(type);e.setTextSize(14);e.setTextColor(white);e.setHintTextColor(Color.rgb(117,145,175));e.setHint(hint);
        e.setPadding(dp(12),dp(10),dp(12),dp(10));e.setBackground(shape(surface));
        LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-1,-2);lp.topMargin=dp(4);lp.bottomMargin=dp(7);screen.addView(e,lp);return e;
    }
    private void buttons(String[] captions,Runnable[] actions){
        LinearLayout col=new LinearLayout(this);col.setOrientation(LinearLayout.VERTICAL);screen.addView(col);
        for(int i=0;i<captions.length;i++){
            Button b=new Button(this);b.setAllCaps(false);b.setText(captions[i]);b.setTextColor(Color.rgb(6,27,42));
            b.setTextSize(15);b.setBackground(shape(accent));
            LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-1,dp(47));lp.bottomMargin=dp(7);col.addView(b,lp);
            Runnable a=actions[i];b.setOnClickListener(v->a.run());
        }
    }
    private void append(String message){
        if(console==null)return;
        String prior=console.getText().toString();String next=message+"\n\n"+prior;
        if(next.length()>8000)next=next.substring(0,8000);console.setText(next);
    }
    private void saveKey(){
        String k=secret.getText().toString().trim();
        if(!k.matches("[0-9a-fA-F]{64}")){append("ERREUR : cle attendue = 64 caracteres hex");return;}
        try{SecurePairingStore.save(this,k);getPreferences(MODE_PRIVATE).edit().putString("host",host.getText().toString().trim()).apply();append("Cle chiffree dans Android Keystore.");}
        catch(Exception e){append("ERREUR stockage: "+e.getClass().getSimpleName());}
    }
    private void forgetKey(){
        try{SecurePairingStore.clear(this);secret.setText("");append("Cle et cle de chiffrement Android effacees.");}
        catch(Exception err){append("ERREUR effacement cle: "+err.getClass().getSimpleName());}
    }
    private JSONObject args(String... values){JSONObject j=new JSONObject();try{for(int i=0;i<values.length;i+=2)j.put(values[i],values[i+1]);}catch(Exception ignored){}return j;}
    private void readFile(){execute("/read",args("path",fileName.getText().toString().trim()));}
    private void confirmWrite(){
        String path=fileName.getText().toString().trim();String data=fileContent.getText().toString();
        new AlertDialog.Builder(this).setTitle("Confirmer ecriture sur le PC reel / espace de test")
          .setMessage("Ecrire "+data.length()+" caracteres dans le fichier "+path+" sur le PC reel ? Une sauvegarde sera conservee si ce fichier existe. Cette action change le disque Windows.")
          .setNegativeButton("Annuler",(d,w)->append("Ecriture annulee"))
          .setPositiveButton("Confirmer",(d,w)->{JSONObject j=args("path",path,"content",data);
              try{j.put("approved",true);}catch(Exception ignored){}execute("/write",j);}).show();
    }
    private void pickMission(){
        Intent intent=new Intent(Intent.ACTION_OPEN_DOCUMENT);
        intent.addCategory(Intent.CATEGORY_OPENABLE);
        intent.setType("application/json");
        intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
        startActivityForResult(intent,PICK_MISSION_JSON);
    }
    @Override protected void onActivityResult(int requestCode,int resultCode,Intent data){
        super.onActivityResult(requestCode,resultCode,data);
        if(requestCode!=PICK_MISSION_JSON||resultCode!=RESULT_OK||data==null||data.getData()==null)return;
        try(InputStream in=getContentResolver().openInputStream(data.getData())){
            if(in==null)throw new IllegalStateException("Fichier inaccessible");
            ByteArrayOutputStream out=new ByteArrayOutputStream();
            byte[] buffer=new byte[4096];int n;
            while((n=in.read(buffer))!=-1){
                if(out.size()+n>32768)throw new IllegalArgumentException("Mission trop volumineuse (32 KiB maximum)");
                out.write(buffer,0,n);
            }
            JSONObject mission=new JSONObject(new String(out.toByteArray(),StandardCharsets.UTF_8));
            executeMission(mission);
        }catch(Exception ex){append("MISSION REFUSEE : "+ex.getMessage());}
    }
    private void executeMission(JSONObject mission)throws Exception{
        if(!"bcp-rescue-mission/1".equals(mission.optString("schema")))
            throw new IllegalArgumentException("Format de mission incorrect");
        String action=mission.optString("action","");
        if(!MissionPolicy.actionAllowed(action))
            throw new IllegalArgumentException("Action de mission interdite");
        long expires=mission.optLong("expires_unix_seconds",0L);
        long now=System.currentTimeMillis()/1000L;
        if(!MissionPolicy.validExpiry(now,expires))
            throw new IllegalArgumentException("Mission expiree ou duree superieure a 24h");
        JSONObject payload=mission.optJSONObject("payload");
        if(payload==null)payload=new JSONObject();
        payload.remove("approved"); // Ignore any remote assertion of user approval.
        if("read".equals(action)||"write".equals(action)){
            String file=payload.optString("path","");
            if(!MissionPolicy.safeRelativePath(file))
                throw new IllegalArgumentException("Chemin invalide ou dangereux");
        }
        if("write".equals(action)){
            String content=payload.optString("content",null);
            if(!MissionPolicy.validWriteContent(content))
                throw new IllegalArgumentException("Contenu absent ou superieur a 64 KiB");
            final JSONObject safePayload=payload;
            new AlertDialog.Builder(this)
                .setTitle("Mission : ecriture sur ton vrai PC")
                .setMessage("Fichier de test : "+payload.optString("path")+"\nOctets : "+content.getBytes(StandardCharsets.UTF_8).length+"\n\nConfirmer cette modification du PC ?")
                .setNegativeButton("Refuser",(d,w)->append("MISSION ANNULEE : ecriture refusee"))
                .setPositiveButton("Autoriser",(d,w)->{
                    try{safePayload.put("approved",true);execute("/write",safePayload);}
                    catch(Exception ex){append("Erreur mission : "+ex.getMessage());}
                }).show();
        }else{
            append("Mission JSON acceptee : "+action+" (transfert manuel)");
            execute("/"+action,payload);
        }
    }
    private void shareResult(){
        if(latestResult.isEmpty()){append("Aucun resultat a partager.");return;}
        Intent send=new Intent(Intent.ACTION_SEND);
        send.setType("text/plain");send.putExtra(Intent.EXTRA_TEXT,latestResult);
        startActivity(Intent.createChooser(send,"Partager le resultat de test"));
    }
    private void execute(String path,JSONObject payload){
        if(busy){append("Une operation est deja en cours.");return;}
        String address=host.getText().toString().trim();String ps=port.getText().toString().trim();
        String k=secret.getText().toString().trim();
        if(!k.matches("[0-9a-fA-F]{64}")){append("Ajoute une cle d'appairage valide.");return;}
        final BridgeClient client;
        try {client=new BridgeClient(address,Integer.parseInt(ps),k);}catch(Exception ex){append("Configuration: "+ex.getMessage());return;}
        busy=true;status.setText("Etat : verification en cours...");
        io.execute(()->{
            try{
                JSONObject r=client.perform(path,payload);
                runOnUiThread(()->{busy=false;status.setText(r.optBoolean("ok")?"Etat : lien signe (non chiffre)":"Etat : requete refusee");latestResult=path+"\n"+r.toString();append(latestResult);});
            }catch(Exception ex){runOnUiThread(()->{busy=false;status.setText("Etat : connexion echouee");append(path+" — "+ex.getClass().getSimpleName()+": "+ex.getMessage());});}
        });
    }
    @Override protected void onDestroy(){io.shutdownNow();super.onDestroy();}
}