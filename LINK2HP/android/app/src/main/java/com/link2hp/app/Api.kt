package com.link2hp.app

import android.content.Context
import android.net.ConnectivityManager
import android.os.Build
import org.json.JSONObject
import java.net.DatagramPacket
import java.net.DatagramSocket
import java.net.Inet4Address
import java.net.InetAddress
import java.net.NetworkInterface
import java.net.SocketTimeoutException
import java.net.URL
import java.security.MessageDigest
import java.security.SecureRandom
import java.security.cert.X509Certificate
import java.util.UUID
import javax.net.ssl.HttpsURLConnection
import javax.net.ssl.SSLContext
import javax.net.ssl.TrustManager
import javax.net.ssl.X509TrustManager

internal data class PairData(val host:String,val port:Int,val token:String,val pin:String) {
    fun serialized():String="L2H1|$host|$port|$token|$pin"
    companion object {
        fun parse(raw:String):PairData {
            val p=raw.trim().split('|')
            require(p.size==5 && p[0]=="L2H1") {"Association non reconnue"}
            val parts=p[1].split('.').mapNotNull{it.toIntOrNull()}
            require(parts.size==4 && parts.all{it in 0..255}) {"Adresse invalide"}
            require(parts[0]==10||(parts[0]==192&&parts[1]==168)||(parts[0]==172&&parts[1] in 16..31)) {"Réseau local uniquement"}
            val port=p[2].toIntOrNull() ?: throw IllegalArgumentException("Port invalide")
            require(port in 1024..65535 && p[3].matches(Regex("[a-fA-F0-9]{64}")) && p[4].matches(Regex("[a-fA-F0-9]{64}"))) {"Identifiants invalides"}
            return PairData(p[1],port,p[3].lowercase(),p[4].lowercase())
        }
    }
}
internal object Api {
    private fun privateHost(host:String):Boolean {
        val x=host.split('.').mapNotNull{it.toIntOrNull()}
        return x.size==4&&x.all{it in 0..255}&&(x[0]==10||(x[0]==192&&x[1]==168)||(x[0]==172&&x[1] in 16..31))
    }
    private fun connection(pair:PairData,path:String,method:String,auth:Boolean=true):HttpsURLConnection {
        require(privateHost(pair.host)) {"Hôte local requis"}
        val trust=object:X509TrustManager {
            override fun getAcceptedIssuers():Array<X509Certificate> = emptyArray()
            override fun checkClientTrusted(chain:Array<X509Certificate>,authType:String) {throw java.security.cert.CertificateException("Client not supported")}
            override fun checkServerTrusted(chain:Array<X509Certificate>,authType:String) {
                if(chain.isEmpty())throw java.security.cert.CertificateException("No server certificate")
                val digest=MessageDigest.getInstance("SHA-256").digest(chain[0].encoded).joinToString(""){ "%02x".format(it) }
                if(digest!=pair.pin)throw java.security.cert.CertificateException("Le certificat du HP a changé")
                chain[0].checkValidity()
            }
        }
        val ssl=SSLContext.getInstance("TLS").apply{init(null,arrayOf<TrustManager>(trust),SecureRandom())}
        val c=URL("https://${pair.host}:${pair.port}$path").openConnection() as HttpsURLConnection
        c.sslSocketFactory=ssl.socketFactory
        // Identity is independently pinned to the exact self-signed certificate (SHA-256).
        c.hostnameVerifier=javax.net.ssl.HostnameVerifier{_,_->true}
        c.requestMethod=method;c.connectTimeout=4500;c.readTimeout=9500;c.instanceFollowRedirects=false
        if(auth)c.setRequestProperty("Authorization","Bearer ${pair.token}")
        c.setRequestProperty("Accept","application/json")
        return c
    }
    private fun json(conn:HttpsURLConnection,body:JSONObject?=null):JSONObject {
        if(body!=null){conn.doOutput=true;conn.setRequestProperty("Content-Type","application/json; charset=utf-8");conn.outputStream.use{it.write(body.toString().toByteArray(Charsets.UTF_8))}}
        try {
            val status=conn.responseCode
            val stream=if(status in 200..299)conn.inputStream else conn.errorStream
            val raw=stream?.bufferedReader()?.use{it.readText()} ?: "{}"
            if(status !in 200..299)throw IllegalStateException("HP : erreur $status")
            return JSONObject(raw)
        }finally{conn.disconnect()}
    }
    fun discover(ctx:Context,progress:((String)->Unit)?=null):PairData? = LanDiscovery.find(ctx,progress)

    fun pair(ctx:Context,progress:(String)->Unit):PairData {
        progress("Recherche du HP sur le réseau local…")
        val candidate=discover(ctx,progress)?:throw IllegalStateException("HP introuvable sur ce réseau. Tu peux laisser ton téléphone sur le Wi-Fi 2,4 GHz.")
        val preferences=ctx.getSharedPreferences("link2hp",Context.MODE_PRIVATE)
        var id=preferences.getString("device_id",null)
        if(id==null){id=UUID.randomUUID().toString();preferences.edit().putString("device_id",id).apply()}
        val name=(Build.MANUFACTURER+" "+Build.MODEL).take(48)
        val initial=json(connection(candidate,"/api/pair/init","POST",false),JSONObject().put("device_id",id).put("label",name))
        val pairId=initial.getString("pair_id")
        progress("Sur ton HP, clique « Autoriser ce téléphone ». Aucun code à copier.")
        repeat(50){
            Thread.sleep(1800)
            val status=json(connection(candidate,"/api/pair/status?id=$pairId&device_id=$id","GET",false))
            when(status.optString("state")) {
                "APPROVED" -> {
                    val token=status.getString("token")
                    val pair=PairData(candidate.host,candidate.port,token,candidate.pin)
                    PairData.parse(pair.serialized())
                    Store(ctx).savePair(pair.serialized())
                    return pair
                }
                "EXPIRED" -> throw IllegalStateException("Autorisation expirée. Relancer la recherche.")
            }
        }
        throw IllegalStateException("Autorisation non reçue sur le HP.")
    }
    fun health(pair:PairData):JSONObject =
        json(connection(pair,"/api/health","GET"))

    fun hpNetworks(pair:PairData):JSONObject =
        json(connection(pair,"/api/wifi/networks","GET"))
    fun hpSwitchNetwork(pair:PairData,ssid:String):JSONObject =
        json(connection(pair,"/api/wifi/connect","POST"), JSONObject().put("ssid",ssid))

    fun send(pair:PairData,item:Item):String {
        val body=JSONObject().put("request_id",item.id).put("kind",item.kind).put("payload",item.payload)
        return json(connection(pair,"/api/submit","POST"),body).getJSONObject("task").getString("state")
    }
    fun task(pair:PairData,id:String):String =json(connection(pair,"/api/tasks/$id","GET")).getJSONObject("task").getString("state")
    fun process(ctx:Context,refresh:Boolean=false):Boolean {
        val store=Store(ctx)
        var pair=store.pair()?.let{PairData.parse(it)}?:return false
        val net=ctx.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
        val wifi=net.allNetworks.firstOrNull{net.getNetworkCapabilities(it)?.hasTransport(android.net.NetworkCapabilities.TRANSPORT_WIFI)==true}
        if(wifi==null)return true
        // La présence d'un Wi-Fi local est suffisante, même sans Internet.
        // "Réseau mesuré" ne doit pas bloquer la communication LAN autorisée.
        var needsRetry=false
        for(item in store.rows(false)){
            if(item.state!="QUEUED_PHONE" && !(refresh && item.state !in setOf("COMPLETED","FAILED")))continue
            try {
                val status=if(item.state=="QUEUED_PHONE")send(pair,item) else task(pair,item.id)
                store.update(item.id,status)
            }catch(_:Exception){
                // L'adresse DHCP du HP peut changer après une bascule 5 GHz/2,4 GHz.
                // Ne réassocier qu'au même certificat TLS; ne jamais accepter un autre HP.
                try{
                    val found=discover(ctx)
                    if(found!=null && found.pin==pair.pin){
                        val refreshed=pair.copy(host=found.host,port=found.port)
                        PairData.parse(refreshed.serialized())
                        store.savePair(refreshed.serialized())
                        pair=refreshed
                        val state=if(item.state=="QUEUED_PHONE")send(pair,item) else task(pair,item.id)
                        store.update(item.id,state)
                        continue
                    }
                }catch(_:Exception){}
                needsRetry=true
                if(item.state=="QUEUED_PHONE")store.update(item.id,"QUEUED_PHONE","HP momentanément indisponible")
            }
        }
        return needsRetry
    }
}
