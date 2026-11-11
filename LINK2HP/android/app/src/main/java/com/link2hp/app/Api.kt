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

internal data class PairData(val host:String,val port:Int,val token:String,val pin:String,val remoteHost:String="") {
    fun serialized():String="L2H2|$host|$port|$token|$pin|" + (if(remoteHost.isEmpty()) "-" else remoteHost)
    companion object {
        fun lanAddress(host:String):Boolean {
            val a=host.split('.').mapNotNull{it.toIntOrNull()}
            return a.size==4&&a.all{it in 0..255}&&(a[0]==10||(a[0]==192&&a[1]==168)||(a[0]==172&&a[1] in 16..31))
        }
        fun tailAddress(host:String):Boolean {
            val a=host.split('.').mapNotNull{it.toIntOrNull()}
            return a.size==4&&a.all{it in 0..255}&&a[0]==100&&a[1] in 64..127
        }
        fun parse(raw:String):PairData {
            val p=raw.trim().split('|')
            require((p.size==5&&p[0]=="L2H1")||(p.size==6&&p[0]=="L2H2")) {"Association non reconnue"}
            val port=p[2].toIntOrNull()?:throw IllegalArgumentException("Port invalide")
            require((lanAddress(p[1])&&port in 1024..65535)||(tailAddress(p[1])&&port==17645)) {"Adresse du HP invalide"}
            require(p[3].matches(Regex("[a-fA-F0-9]{64}"))&&p[4].matches(Regex("[a-fA-F0-9]{64}"))) {"Identifiants invalides"}
            val remote=if(p.size==6&&p[5]!="-")p[5] else ""
            require(remote.isEmpty()||tailAddress(remote)) {"Adresse distante non reconnue"}
            return PairData(p[1],port,p[3].lowercase(),p[4].lowercase(),remote)
        }
    }
}
internal object Api {
    private fun privateHost(host:String):Boolean {
        val x=host.split('.').mapNotNull{it.toIntOrNull()}
        return x.size==4&&x.all{it in 0..255}&&(x[0]==10||(x[0]==192&&x[1]==168)||(x[0]==172&&x[1] in 16..31))
    }
    private fun connection(pair:PairData,path:String,method:String,auth:Boolean=true):HttpsURLConnection {
        require(privateHost(pair.host) || (PairData.tailAddress(pair.host) && pair.port==17645 && auth && pair.token.length==64)) {"Hôte autorisé requis"}
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
    private fun updatedRemote(ctx:Context,pair:PairData,health:JSONObject):PairData {
        val endpoint=health.optJSONObject("remote")
        val address=endpoint?.optString("host").orEmpty()
        val port=endpoint?.optInt("port",0)?:0
        if(port==17645 && PairData.tailAddress(address) && address!=pair.remoteHost) {
            val updated=pair.copy(remoteHost=address)
            Store(ctx).savePair(updated.serialized())
            return updated
        }
        return pair
    }
    private fun remote(pair:PairData):PairData? =
        pair.remoteHost.takeIf{PairData.tailAddress(it)}?.let{pair.copy(host=it,port=17645)}
    fun active(ctx:Context,stored:PairData):PairData {
        val cm=ctx.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
        val vpn=cm.allNetworks.any{cm.getNetworkCapabilities(it)?.hasTransport(android.net.NetworkCapabilities.TRANSPORT_VPN)==true}
        val candidates=mutableListOf<PairData>()
        val remoteEndpoint=remote(stored)
        if(vpn&&remoteEndpoint!=null)candidates.add(remoteEndpoint)
        candidates.add(stored)
        if(!vpn&&remoteEndpoint!=null)candidates.add(remoteEndpoint)
        for(candidate in candidates) {
            try{
                val h=health(candidate)
                if(h.optString("status")!="ONLINE")continue
                val refreshed=updatedRemote(ctx,stored,h)
                return candidate.copy(remoteHost=refreshed.remoteHost)
            }catch(_:Exception){}
        }
        val found=discover(ctx)
        if(found!=null && found.pin==stored.pin){
            val newLocal=stored.copy(host=found.host,port=found.port)
            val health=health(newLocal)
            if(health.optString("status")=="ONLINE"){
                val updated=updatedRemote(ctx,newLocal,health)
                Store(ctx).savePair(updated.serialized())
                return updated
            }
        }
        throw IllegalStateException("HP indisponible : Wi-Fi local ou Tailscale non joignable")
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
                    return try{active(ctx,pair)}catch(_:Exception){pair}
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
        val pair=store.pair()?.let{PairData.parse(it)}?:return false
        var endpoint=try{active(ctx,pair)}catch(_:Exception){return true}
        var needsRetry=false
        for(item in store.rows(false)){
            if(item.state!="QUEUED_PHONE" && !(refresh && item.state!="COMPLETED"))continue
            try{
                // Re-submission is idempotent; user refresh can retry an earlier FAILED job.
                val state=send(endpoint,item)
                store.update(item.id,state)
            }catch(_:Exception){
                try{
                    endpoint=active(ctx,PairData.parse(store.pair()?:pair.serialized()))
                    val state=send(endpoint,item)
                    store.update(item.id,state)
                    continue
                }catch(_:Exception){}
                needsRetry=true
                if(item.state=="QUEUED_PHONE")store.update(item.id,"QUEUED_PHONE","HP momentanément indisponible")
            }
        }
        return needsRetry
    }
}
