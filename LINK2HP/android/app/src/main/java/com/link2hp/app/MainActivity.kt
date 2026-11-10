package com.link2hp.app

import android.app.Activity
import android.content.Context
import android.content.Intent
import android.graphics.Color
import android.graphics.Typeface
import android.graphics.drawable.GradientDrawable
import android.net.Uri
import android.net.ConnectivityManager
import android.net.NetworkCapabilities
import android.net.NetworkRequest
import android.os.Bundle
import android.util.Base64
import android.view.Gravity
import android.view.View
import android.view.ViewGroup
import android.widget.*
import java.util.concurrent.Executors

class MainActivity:Activity(){
    private val io=Executors.newSingleThreadExecutor()
    private lateinit var store:Store
    private lateinit var status:TextView
    private lateinit var input:EditText
    private lateinit var history:LinearLayout
    private lateinit var pairButton:Button
    private lateinit var wifiStatus:TextView
    private var pairRunning=false
    private var wifiPickerOpened=false
    private var wifiPromptShown=false
    private var networkCallback:ConnectivityManager.NetworkCallback?=null
    private var lastNetworkRetry=0L
    private lateinit var sendButton:Button
    private val ink=Color.rgb(24,39,64)
    private val muted=Color.rgb(91,107,130)
    private val blue=Color.rgb(20,91,224)
    private fun dp(v:Int)=(v*resources.displayMetrics.density).toInt()
    private fun bg(color:Int,radius:Int=15):GradientDrawable=GradientDrawable().apply{setColor(color);cornerRadius=dp(radius).toFloat()}
    private fun text(value:String,size:Float=15f,bold:Boolean=false,color:Int=ink):TextView=TextView(this).apply{
        text=value;textSize=size;setTextColor(color);includeFontPadding=true
        if(bold)setTypeface(Typeface.DEFAULT,Typeface.BOLD)
        setLineSpacing(dp(3).toFloat(),1f)
    }
    private fun button(title:String,primary:Boolean=true):Button=Button(this).apply{
        text=title;textSize=14f;isAllCaps=false
        setTextColor(if(primary)Color.WHITE else blue)
        background=bg(if(primary)blue else Color.rgb(231,240,255),12)
        minHeight=dp(52)
        setPadding(dp(12),dp(7),dp(12),dp(7))
    }
    private fun line(container:LinearLayout,view:View,top:Int=0){
        val p=LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,ViewGroup.LayoutParams.WRAP_CONTENT)
        p.topMargin=dp(top);container.addView(view,p)
    }
    override fun onCreate(savedInstanceState:Bundle?){
        super.onCreate(savedInstanceState)
        window.statusBarColor=Color.rgb(246,249,253)
        window.navigationBarColor=Color.rgb(246,249,253)
        @Suppress("DEPRECATION")
        window.decorView.systemUiVisibility=View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR or View.SYSTEM_UI_FLAG_LIGHT_NAVIGATION_BAR
        store=Store(this)
        val page=LinearLayout(this).apply{
            orientation=LinearLayout.VERTICAL
            setPadding(dp(18),dp(22),dp(18),dp(32))
            setBackgroundColor(Color.rgb(246,249,253))
        }
        line(page,text("LINK2HP",27f,true))
        line(page,text("Du téléphone vers mon HP, simplement.",14f,false,muted),4)
        val card=LinearLayout(this).apply {orientation=LinearLayout.VERTICAL;setPadding(dp(17),dp(16),dp(17),dp(18));background=bg(Color.WHITE)}
        line(card,text("CONNEXION",12f,true,muted))
        status=text("Recherche de ton ordinateur…",15f,true)
        line(card,status,9)
        pairButton=button("Rechercher mon HP",false)
        pairButton.setOnClickListener{startPair()}
        line(card,pairButton,13)
        line(page,card,20)
        val wifi=LinearLayout(this).apply{orientation=LinearLayout.VERTICAL;setPadding(dp(17),dp(14),dp(17),dp(17));background=bg(Color.WHITE)}
        line(wifi,text("RÉSEAU DE MON HP",12f,true,muted))
        wifiStatus=text("Wi-Fi du HP : recherche après association…",15f,true)
        line(wifi,wifiStatus,9)
        line(wifi,text("Le HP télécharge. Il privilégie Starlink 5 GHz, puis Starlink 2,4 GHz. Tu peux choisir un autre réseau détecté par le HP.",13f,false,muted),9)
        val wifiButton=button("Voir les réseaux détectés par le HP",false)
        wifiButton.setOnClickListener{showHpNetworks()}
        line(wifi,wifiButton,11)
        line(page,wifi,14)
        val share=LinearLayout(this).apply{orientation=LinearLayout.VERTICAL;setPadding(dp(17),dp(16),dp(17),dp(20));background=bg(Color.WHITE)}
        line(share,text("ENVOYER UN LIEN",12f,true,muted))
        input=EditText(this).apply{
            hint="Colle ici un lien ou un magnet";textSize=15f;isSingleLine=false;minLines=2;maxLines=4
            setPadding(dp(8),dp(12),dp(8),dp(12));background=bg(Color.rgb(246,249,253),9)
        }
        line(share,input,12)
        sendButton=button("Envoyer au HP")
        sendButton.setOnClickListener{saveLink()}
        line(share,sendButton,12)
        line(share,text("Astuce : dans ton navigateur, utilise aussi Partager → LINK2HP.",13f,false,muted),12)
        line(page,share,14)
        val detail=LinearLayout(this).apply{orientation=LinearLayout.VERTICAL;setPadding(dp(17),dp(14),dp(17),dp(17));background=bg(Color.WHITE)}
        line(detail,text("ACTIVITÉ",12f,true,muted))
        val retry=button("Actualiser l’activité",false)
        retry.setOnClickListener{retry(true)}
        line(detail,retry,10)
        history=LinearLayout(this).apply{orientation=LinearLayout.VERTICAL}
        line(detail,history,11)
        line(page,detail,14)
        val metered=CheckBox(this).apply{
            text="Autoriser le partage via un point d’accès mobile";textSize=13f;setTextColor(ink)
            isChecked=store.allowMetered()
            setOnCheckedChangeListener{_,checked->store.setMetered(checked);RetryJob.schedule(this@MainActivity)}
        }
        line(page,metered,10)
        val scroller=ScrollView(this).apply{isFillViewport=true;clipToPadding=false;addView(page)}
        setContentView(scroller)
        displayRows()
        receiveShare(intent)
        if(store.pair()==null)startPair() else retry(false)
        watchWifi()
    }
    override fun onNewIntent(intent:Intent){super.onNewIntent(intent);setIntent(intent);receiveShare(intent)}
    private fun show(message:String){runOnUiThread{status.text=message}}
    private fun startPair(){
        if(pairRunning)return
        pairRunning=true
        pairButton.isEnabled=false;show("Recherche automatique du HP sur le Wi-Fi…")
        io.execute{
            try{Api.pair(this){show(it)};show("✓ HP associé · prêt à recevoir");RetryJob.schedule(this)
                Api.process(this)
            }catch(e:Exception){
                val info=if(!WifiCoordinator.wifiConnected(this)) "Active le Wi-Fi pour joindre ton HP." else "HP introuvable sur ce réseau. Choisis celui du HP ci-dessous."
                show("${e.message?:"Recherche impossible"} — $info")
                runOnUiThread {
                    if(!wifiPromptShown && !wifiPickerOpened){
                        wifiPromptShown=true
                        android.app.AlertDialog.Builder(this)
                            .setTitle("Sélectionner le réseau du HP")
                            .setMessage("Choisis Starlink 5 GHz de préférence. S'il n'apparaît pas, choisis Starlink 2,4 GHz ou le réseau auquel le HP est connecté. Android gère la connexion et les mots de passe enregistrés.")
                            .setPositiveButton("Choisir le Wi-Fi"){_,_->wifiPickerOpened=true;WifiCoordinator.openAndroidWifiPicker(this)}
                            .setNegativeButton("Plus tard",null)
                            .show()
                    }
                }
            }
            finally{runOnUiThread{pairRunning=false;pairButton.isEnabled=true;displayRows()}}
        }
    }
    private fun showHpNetworks(){
        val saved=store.pair()
        if(saved==null){
            show("Le HP doit être associé avant la sélection réseau.")
            return
        }
        io.execute {
            try {
                val info=Api.hpNetworks(PairData.parse(saved))
                val nets=info.optJSONArray("networks")
                if(!info.optBoolean("available")||nets==null)throw IllegalStateException("Wi-Fi Windows indisponible")
                val rows=(0 until nets.length()).map { nets.getJSONObject(it) }
                val options=rows.map { row ->
                    val band=row.optJSONArray("bands")?.let{ a->(0 until a.length()).map{a.optString(it)}.joinToString(" / ") }?:""
                    val state=when {
                        row.optBoolean("current")->"Connecté"
                        row.optBoolean("saved")->"Prêt à connecter"
                        else->"À configurer sur le HP"
                    }
                    "${row.optString("ssid")}  ·  $band  ·  $state"
                }.toTypedArray()
                runOnUiThread {
                    wifiStatus.text="HP : ${info.optString("current","aucun réseau Wi-Fi")}" 
                    if(options.isEmpty()){
                        android.app.AlertDialog.Builder(this)
                            .setTitle("Réseaux détectés par le HP")
                            .setMessage("Aucun Wi-Fi visible par l'ordinateur. Vérifie sa carte Wi-Fi.")
                            .setPositiveButton("OK",null).show()
                    } else {
                        android.app.AlertDialog.Builder(this)
                            .setTitle("Choisir le réseau du HP")
                            .setItems(options){_,which-> requestHpSwitch(rows[which].optString("ssid"),rows[which].optBoolean("saved"))}
                            .setNegativeButton("Annuler",null).show()
                    }
                }
            } catch(e:Exception){show("Réseaux du HP indisponibles : ${e.message}. Le téléphone doit pouvoir joindre le HP.")}
        }
    }
    private fun requestHpSwitch(ssid:String,saved:Boolean){
        if(!saved){
            android.app.AlertDialog.Builder(this)
                .setTitle("Première connexion nécessaire sur le HP")
                .setMessage("Le réseau « $ssid » n'est pas encore enregistré dans Windows. Connecte le HP une première fois depuis ses réglages Wi-Fi pour enregistrer le mot de passe. LINK2HP ne demande jamais ton mot de passe Wi-Fi.")
                .setPositiveButton("Compris",null).show()
            return
        }
        android.app.AlertDialog.Builder(this)
            .setTitle("Connecter le HP à $ssid ?")
            .setMessage("La connexion entre téléphone et HP pourra être interrompue brièvement. Le téléphone retrouvera automatiquement le HP si les deux appareils restent joignables.")
            .setPositiveButton("Connecter le HP"){_,_->
                val raw=store.pair()?:return@setPositiveButton
                show("Le HP bascule vers $ssid…")
                io.execute {
                    try {
                        val result=Api.hpSwitchNetwork(PairData.parse(raw),ssid)
                        val state=result.optString("state")
                        show(when(state){
                            "SWITCH_PENDING"->"✓ Bascule demandée au HP. Reconnexion automatique en cours."
                            "ALREADY_CONNECTED"->"✓ Le HP utilise déjà ce réseau."
                            else->"État du HP : $state"
                        })
                        RetryJob.schedule(this)
                    }catch(e:Exception){show("Échec réseau : ${e.message}. Vérifie le Wi-Fi du HP.")}
                }
            }
            .setNegativeButton("Annuler",null).show()
    }
    private fun saveLink(){
        val raw=input.text.toString().trim()
        val value=Regex("(?:https?://[^\\s]+|magnet:\\?[^\\s]+)").find(raw)?.value
        if(value==null||value.length>4096){show("Lien invalide : colle une URL complète.");return}
        val added=store.save("link",value)
        input.setText("")
        show(if(added)"✓ Demande enregistrée · envoi au HP…" else "Ce lien figure déjà dans l’activité.")
        displayRows();if(added)retry(false)
    }
    private fun receiveShare(i:Intent?){
        if(i?.action!=Intent.ACTION_SEND)return
        val shared=i.getStringExtra(Intent.EXTRA_TEXT)
        if(!shared.isNullOrBlank()){input.setText(shared);saveLink();return}
        @Suppress("DEPRECATION")val uri=i.getParcelableExtra<Uri>(Intent.EXTRA_STREAM)
        if(uri?.scheme!="content"){show("Fichier non reconnu");return}
        try{
            val bytes=java.io.ByteArrayOutputStream()
            contentResolver.openInputStream(uri)?.use{source->
                val b=ByteArray(8192);var total=0
                while(true){val n=source.read(b);if(n<0)break;total+=n
                    if(total>5*1024*1024)throw IllegalArgumentException("Torrent trop volumineux")
                    bytes.write(b,0,n)
                }
            }?:throw IllegalArgumentException("Fichier inaccessible")
            val data=bytes.toByteArray()
            if(data.size<12||data[0].toInt()!=100)throw IllegalArgumentException("Torrent invalide")
            val added=store.save("torrent_file",Base64.encodeToString(data,Base64.NO_WRAP))
            show(if(added)"✓ Torrent enregistré" else "Torrent déjà présent")
            displayRows();if(added)retry(false)
        }catch(e:Exception){show("Import impossible : ${e.message}")}
    }
    private fun retry(refresh:Boolean){
        if(store.pair()==null){show("HP non associé · demande conservée sur le téléphone");return}
        io.execute{
            try{val again=Api.process(this,refresh);if(again)RetryJob.schedule(this)
                show(if(again)"HP temporairement inaccessible · reprise automatique" else "✓ Connexion et file synchronisées")
            }catch(_:Exception){RetryJob.schedule(this);show("HP hors ligne · tes demandes sont conservées")}
            finally{runOnUiThread{displayRows()}}
        }
    }
    private fun displayRows(){
        history.removeAllViews()
        val rows=store.rows().take(7)
        if(rows.isEmpty()){line(history,text("Aucun envoi pour le moment.",13f,false,muted));return}
        rows.forEach { entry ->
            val label=when(entry.state){"QUEUED_PHONE"->"En attente";"COMPLETED"->"Terminé";"HANDED_TO_QBITTORRENT"->"Transmis à qBittorrent";"FAILED"->"Échec";"RUNNING"->"Téléchargement";"WAIT_SELECTION"->"Choix nécessaire";else->entry.state}
            line(history,text("● ${if(entry.kind=="torrent_file")"Torrent" else "Lien"} · $label",13f,false,muted),9)
        }
    }
    @Suppress("DEPRECATION")
    override fun onActivityResult(requestCode:Int,resultCode:Int,data:Intent?){
        super.onActivityResult(requestCode,resultCode,data)
        if(requestCode==1976){
            wifiPickerOpened=false
            wifiPromptShown=false
            if(store.pair()==null)wifiStatus.text="HP non associé · téléphone : ${WifiCoordinator.bandDescription(this)}"
            if(store.pair()==null)startPair() else retry(true)
        }
    }
    private fun watchWifi(){
        val cm=getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
        try {
            val req=NetworkRequest.Builder().addTransportType(NetworkCapabilities.TRANSPORT_WIFI).build()
            val cb=object:ConnectivityManager.NetworkCallback(){
                override fun onAvailable(network:android.net.Network){
                    runOnUiThread {
                        if(store.pair()==null)wifiStatus.text="HP non associé · téléphone : ${WifiCoordinator.bandDescription(this@MainActivity)}"
                        val t=System.currentTimeMillis()
                        if(t-lastNetworkRetry>12000L && !wifiPickerOpened){
                            lastNetworkRetry=t
                            if(store.pair()==null)startPair() else retry(false)
                        }
                    }
                }
                override fun onLost(network:android.net.Network){runOnUiThread{if(store.pair()==null)wifiStatus.text="HP non associé · téléphone : ${WifiCoordinator.bandDescription(this@MainActivity)}"}}
            }
            cm.registerNetworkCallback(req,cb);networkCallback=cb
        }catch(_:SecurityException){}catch(_:IllegalArgumentException){}
    }
    override fun onDestroy(){
        networkCallback?.let{try{(getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager).unregisterNetworkCallback(it)}catch(_:Exception){}}
        io.shutdown();super.onDestroy()
    }
}
