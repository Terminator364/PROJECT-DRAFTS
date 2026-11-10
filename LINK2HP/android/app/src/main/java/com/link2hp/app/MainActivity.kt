package com.link2hp.app

import android.app.Activity
import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.util.Base64
import android.view.ViewGroup
import android.widget.*
import java.util.concurrent.Executors

class MainActivity:Activity() {
    private val io=Executors.newSingleThreadExecutor()
    private lateinit var store:Store
    private lateinit var state:TextView
    private lateinit var link:EditText
    private lateinit var pairing:EditText
    private lateinit var history:TextView
    private lateinit var networkMode:CheckBox
    override fun onCreate(savedInstanceState:Bundle?){
        super.onCreate(savedInstanceState)
        store=Store(this)
        val root=LinearLayout(this).apply {orientation=LinearLayout.VERTICAL;setPadding(25,20,25,20)}
        fun label(s:String):TextView=TextView(this).apply {text=s;textSize=16f;setPadding(0,9,0,9)}
        root.addView(label("LINK2HP · Envoyer vers mon ordinateur").apply{textSize=22f})
        state=label("Statut : configuration en cours");root.addView(state)
        link=EditText(this).apply {hint="Coller une URL / magnet";minLines=1;maxLines=4};root.addView(link)
        root.addView(Button(this).apply {text="Envoyer au HP";setOnClickListener{saveLink()}})
        root.addView(Button(this).apply {text="Réessayer / Actualiser";setOnClickListener{retry(true)}})
        root.addView(label("Première connexion : code indiqué par LINK2HP sur le HP"))
        pairing=EditText(this).apply {hint="L2H1|192.168...|...";minLines=1;maxLines=4;setSingleLine(false)};root.addView(pairing)
        root.addView(Button(this).apply {text="Associer mon HP";setOnClickListener{
            try{PairData.parse(pairing.text.toString());store.savePair(pairing.text.toString().trim());pairing.setText("");state.text="HP associé, test de connexion...";retry(false)}
            catch(e:Exception){state.text="Appairage : ${e.message}"}
        }})
        networkMode=CheckBox(this).apply {text="Autoriser réseau mesuré / point d'accès mobile";isChecked=store.allowMetered();setOnCheckedChangeListener{_,v->store.setMetered(v);RetryJob.schedule(this@MainActivity)}};root.addView(networkMode)
        root.addView(label("Activité (aucune URL confidentielle affichée)"))
        history=label("");root.addView(history)
        val scroll=ScrollView(this).apply{addView(root,ViewGroup.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,ViewGroup.LayoutParams.WRAP_CONTENT))}
        setContentView(scroll)
        refresh()
        receiveShare(intent)
        if(store.pair()!=null)retry(false)
    }
    override fun onNewIntent(intent:Intent){super.onNewIntent(intent);receiveShare(intent)}
    private fun saveLink(){
        val value=link.text.toString().trim()
        val url=Regex("(?:https?://[^\\s]+|magnet:\\?[^\\s]+)").find(value)?.value
        if(url==null||url.length>4096){state.text="Lien non valide";return}
        val added=store.save("link",url)
        link.setText("")
        state.text=if(added)"Conservé sur le téléphone · envoi demandé" else "Lien déjà présent"
        refresh();if(added)retry(false)
    }
    private fun receiveShare(i:Intent?){
        if(i?.action!=Intent.ACTION_SEND)return
        val shared=i.getStringExtra(Intent.EXTRA_TEXT)
        if(!shared.isNullOrBlank()){link.setText(shared);saveLink();return}
        @Suppress("DEPRECATION") val uri=i.getParcelableExtra<Uri>(Intent.EXTRA_STREAM)
        if(uri?.scheme!="content"){state.text="Fichier non reconnu";return}
        try{
            var total=0;val bytes=java.io.ByteArrayOutputStream()
            contentResolver.openInputStream(uri)?.use{input->
                val buf=ByteArray(8192)
                while(true){val count=input.read(buf);if(count<0)break;total+=count
                    if(total>5*1024*1024)throw IllegalArgumentException("Fichier .torrent trop volumineux")
                    bytes.write(buf,0,count)
                }
            }?:throw IllegalArgumentException("Fichier illisible")
            val b=bytes.toByteArray();if(b.size<12||b[0].toInt()!=100)throw IllegalArgumentException(".torrent invalide")
            val added=store.save("torrent_file",Base64.encodeToString(b,Base64.NO_WRAP))
            state.text=if(added)".torrent conservé en sécurité" else ".torrent déjà en file"
            refresh();if(added)retry(false)
        }catch(e:Exception){state.text="Import impossible : ${e.message}"}
    }
    private fun retry(refresh:Boolean){
        state.text="Connexion au HP..."
        io.execute{
            try{
                val retry=Api.process(this,refresh)
                if(retry)RetryJob.schedule(this)
                runOnUiThread{state.text=if(retry)"HP inaccessible : demande conservée" else "Synchronisation vérifiée";this.refresh()}
            }catch(e:Exception){
                RetryJob.schedule(this)
                runOnUiThread{state.text="Hors ligne : conservation locale";this.refresh()}
            }
        }
    }
    private fun refresh(){
        val paired=store.pair()!=null
        history.text=store.rows().take(12).joinToString("\n"){"${it.kind} · ${it.state}"}.ifEmpty{"Aucune demande"}
        if(!paired)state.text="HP non appairé · le partage sera conservé"
    }
    override fun onDestroy(){io.shutdown();super.onDestroy()}
}
