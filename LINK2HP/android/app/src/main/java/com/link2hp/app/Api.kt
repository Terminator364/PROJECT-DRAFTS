package com.link2hp.app

import android.content.Context
import android.net.ConnectivityManager
import org.json.JSONObject
import java.net.URL
import java.security.MessageDigest
import java.security.SecureRandom
import java.security.cert.X509Certificate
import javax.net.ssl.HttpsURLConnection
import javax.net.ssl.SSLContext
import javax.net.ssl.TrustManager
import javax.net.ssl.X509TrustManager

internal data class PairData(val host:String,val port:Int,val token:String,val pin:String) {
    companion object {
        fun parse(raw:String):PairData {
            val p=raw.trim().split('|')
            require(p.size==5 && p[0]=="L2H1") {"Code d'appairage invalide"}
            require(p[1].matches(Regex("[0-9]{1,3}(\\.[0-9]{1,3}){3}"))){"Adresse invalide"}
            val address=p[1].split('.').map{it.toInt()}
            require(address.all{it in 0..255}){"Adresse invalide"}
            require(address[0]==10 || (address[0]==192 && address[1]==168) || (address[0]==172 && address[1] in 16..31)){"Adresse réseau local requise"}
            val port=p[2].toIntOrNull()?:throw IllegalArgumentException("Port invalide")
            require(port in 1024..65535){"Port invalide"}
            require(p[3].matches(Regex("[a-fA-F0-9]{64}")) && p[4].matches(Regex("[a-fA-F0-9]{64}"))){"Clé invalide"}
            return PairData(p[1],port,p[3].lowercase(),p[4].lowercase())
        }
    }
}
internal object Api {
    private fun connection(pair:PairData,path:String,method:String):HttpsURLConnection {
        val trust=object:X509TrustManager {
            override fun getAcceptedIssuers():Array<X509Certificate> = emptyArray()
            override fun checkClientTrusted(chain:Array<X509Certificate>,authType:String) {throw java.security.cert.CertificateException("client not supported")}
            override fun checkServerTrusted(chain:Array<X509Certificate>,authType:String) {
                if(chain.isEmpty())throw java.security.cert.CertificateException("empty certificate")
                val digest=MessageDigest.getInstance("SHA-256").digest(chain[0].encoded)
                    .joinToString(""){"%02x".format(it)}
                if(digest!=pair.pin)throw java.security.cert.CertificateException("empreinte TLS différente")
                chain[0].checkValidity()
            }
        }
        val ssl=SSLContext.getInstance("TLS").apply{init(null,arrayOf<TrustManager>(trust),SecureRandom())}
        val c=(URL("https://${pair.host}:${pair.port}$path").openConnection() as HttpsURLConnection)
        c.sslSocketFactory=ssl.socketFactory
        // Peer certificate SHA-256 pin above fully authenticates the exact server instance.
        c.hostnameVerifier=javax.net.ssl.HostnameVerifier{_,_->true}
        c.requestMethod=method;c.connectTimeout=6500;c.readTimeout=15000
        c.instanceFollowRedirects=false
        c.setRequestProperty("Authorization","Bearer ${pair.token}")
        c.setRequestProperty("Accept","application/json")
        return c
    }
    fun send(pair:PairData,item:Item):String {
        val conn=connection(pair,"/api/submit","POST")
        conn.doOutput=true;conn.setRequestProperty("Content-Type","application/json; charset=utf-8")
        val data=JSONObject().put("request_id",item.id).put("kind",item.kind).put("payload",item.payload).toString()
        conn.outputStream.use{it.write(data.toByteArray(Charsets.UTF_8))}
        try {
            val code=conn.responseCode
            val body=(if(code in 200..299)conn.inputStream else conn.errorStream)?.bufferedReader()?.use{it.readText()} ?: "{}"
            if(code !in 200..299)throw IllegalStateException("HTTP $code")
            return JSONObject(body).getJSONObject("task").getString("state")
        }finally {conn.disconnect()}
    }
    fun task(pair:PairData,id:String):String {
        val conn=connection(pair,"/api/tasks/$id","GET")
        try {
            val raw=conn.inputStream.bufferedReader().use{it.readText()}
            return JSONObject(raw).getJSONObject("task").getString("state")
        }finally{conn.disconnect()}
    }
    fun process(ctx:Context,refresh:Boolean=false):Boolean {
        val store=Store(ctx)
        val p=store.pair() ?: return false
        val pair=PairData.parse(p)
        val net=ctx.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
        if(net.activeNetwork==null||(!store.allowMetered()&&net.isActiveNetworkMetered))return false
        var retry=false
        for(item in store.rows(false)) {
            if(item.state!="QUEUED_PHONE" && !(refresh && item.state !in setOf("COMPLETED","FAILED")))continue
            try{
                val state=if(item.state=="QUEUED_PHONE")send(pair,item) else task(pair,item.id)
                store.update(item.id,state)
            }catch(e:Exception) {
                retry=true
                if(item.state=="QUEUED_PHONE")store.update(item.id,"QUEUED_PHONE","PC inaccessible, en attente")
            }
        }
        return retry
    }
}
