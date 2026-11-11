package com.link2hp.app

import android.content.Context
import android.net.ConnectivityManager
import android.net.Network
import android.net.NetworkCapabilities
import org.json.JSONObject
import java.net.DatagramPacket
import java.net.DatagramSocket
import java.net.Inet4Address
import java.net.InetAddress
import java.net.SocketTimeoutException
import java.net.URL
import java.security.MessageDigest
import java.security.SecureRandom
import java.security.cert.X509Certificate
import java.util.concurrent.ExecutorCompletionService
import java.util.concurrent.Executors
import java.util.concurrent.TimeUnit
import javax.net.ssl.HttpsURLConnection
import javax.net.ssl.SSLContext
import javax.net.ssl.TrustManager
import javax.net.ssl.X509TrustManager

/**
 * No code copying. Prefer LAN UDP; when multicast/broadcast is isolated by an
 * extender, search ONLY the phone's local IPv4 /24 for the HP's TLS service.
 * Discovery carries NO credentials and cannot approve a phone: that approval
 * remains exclusively on the Windows dashboard.
 */
internal object LanDiscovery {
    private const val UDP_PORT = 17644
    private const val TLS_PORT = 17642
    private const val MAGIC = "LINK2HP_HERE_V2"

    private fun local(ip: String): Boolean {
        val p = ip.split('.').mapNotNull { it.toIntOrNull() }
        return p.size == 4 && p.all { it in 0..255 } &&
                (p[0] == 10 || (p[0] == 172 && p[1] in 16..31) || (p[0] == 192 && p[1] == 168))
    }

    private fun network(ctx: Context): Network? {
        val cm = ctx.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
        return cm.allNetworks.firstOrNull {
            cm.getNetworkCapabilities(it)?.hasTransport(NetworkCapabilities.TRANSPORT_WIFI) == true
        }
    }

    private fun hosts(ctx: Context, wifi: Network): List<String> {
        val cm = ctx.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
        val ip = cm.getLinkProperties(wifi)?.linkAddresses?.mapNotNull {
            it.address as? Inet4Address
        }?.firstOrNull()?.hostAddress ?: return emptyList()
        if (!local(ip)) return emptyList()
        val parts = ip.split('.')
        val prefix = parts.take(3).joinToString(".") + "."
        // Bounded to 254 private LAN addresses; never scan the Internet.
        return (1..254).map { prefix + it }.filter { it != ip }
    }

    private fun fromPacket(bytes: ByteArray, size: Int, ip: String): PairData? {
        if (!local(ip) || size !in 20..1000) return null
        return try {
            val j = JSONObject(String(bytes, 0, size, Charsets.UTF_8))
            val port = j.optInt("port", -1)
            val pin = j.optString("pin")
            if (j.optString("magic") == MAGIC && port == TLS_PORT && pin.matches(Regex("[a-fA-F0-9]{64}"))) {
                PairData(ip, port, "", pin.lowercase())
            } else null
        } catch (_: Exception) { null }
    }

    private fun viaUdp(wifi: Network, ips: List<String>): PairData? {
        DatagramSocket().use { socket ->
            wifi.bindSocket(socket)
            socket.broadcast = true
            socket.soTimeout = 650
            val query = "LINK2HP_DISCOVER_V2".toByteArray(Charsets.UTF_8)
            val broadcasts = linkedSetOf("255.255.255.255")
            if (ips.isNotEmpty()) broadcasts.add(ips.first().substringBeforeLast('.') + ".255")
            // First try normal broadcasts; then direct local unicast probes.
            for (host in broadcasts) try {
                socket.send(DatagramPacket(query, query.size, InetAddress.getByName(host), UDP_PORT))
            } catch (_: Exception) {}
            repeat(3) {
                try {
                    val buf = ByteArray(1024)
                    val reply = DatagramPacket(buf, buf.size)
                    socket.receive(reply)
                    fromPacket(buf, reply.length, reply.address.hostAddress ?: "")?.let { return it }
                } catch (_: SocketTimeoutException) {} catch (_: Exception) {}
            }
            // Some extenders drop broadcast but pass directed unicast.
            for (ip in ips) try {
                socket.send(DatagramPacket(query, query.size, InetAddress.getByName(ip), UDP_PORT))
            } catch (_: Exception) {}
            repeat(4) {
                try {
                    val buf = ByteArray(1024)
                    val reply = DatagramPacket(buf, buf.size)
                    socket.receive(reply)
                    fromPacket(buf, reply.length, reply.address.hostAddress ?: "")?.let { return it }
                } catch (_: SocketTimeoutException) {} catch (_: Exception) {}
            }
        }
        return null
    }

    private fun viaTls(wifi: Network, ip: String): PairData? {
        if (!local(ip)) return null
        // Trust-on-discovery ONLY: the certificate is SHA-256 pinned immediately,
        // and the actual pairing requires a click on the Windows HP.
        val trust = object : X509TrustManager {
            override fun getAcceptedIssuers(): Array<X509Certificate> = emptyArray()
            override fun checkClientTrusted(chain: Array<X509Certificate>, authType: String) {}
            override fun checkServerTrusted(chain: Array<X509Certificate>, authType: String) {
                if (chain.isEmpty()) throw java.security.cert.CertificateException("Missing certificate")
            }
        }
        val ssl = SSLContext.getInstance("TLS").apply {
            init(null, arrayOf<TrustManager>(trust), SecureRandom())
        }
        val connection = wifi.openConnection(URL("https://$ip:$TLS_PORT/api/discovery")) as HttpsURLConnection
        connection.sslSocketFactory = ssl.socketFactory
        connection.hostnameVerifier = javax.net.ssl.HostnameVerifier { _, _ -> true }
        connection.connectTimeout = 280
        connection.readTimeout = 450
        connection.instanceFollowRedirects = false
        return try {
            if (connection.responseCode != 200) return null
            val cert = connection.serverCertificates.firstOrNull() as? X509Certificate ?: return null
            cert.checkValidity()
            val pin = MessageDigest.getInstance("SHA-256").digest(cert.encoded)
                .joinToString("") { "%02x".format(it) }
            val response = connection.inputStream.bufferedReader().use { it.readText().take(1000) }
            val parsed = JSONObject(response)
            if (parsed.optString("magic") == MAGIC &&
                parsed.optInt("port") == TLS_PORT && parsed.optString("pin").lowercase() == pin) {
                PairData(ip, TLS_PORT, "", pin)
            } else null
        } catch (_: Exception) { null }
        finally { connection.disconnect() }
    }

    fun find(ctx: Context, progress: ((String) -> Unit)? = null): PairData? {
        val wifi = network(ctx) ?: return null
        val candidates = hosts(ctx, wifi)
        progress?.invoke("Recherche sur le Wi-Fi actuel…")
        viaUdp(wifi, candidates)?.let { return it }
        if (candidates.isEmpty()) return null
        progress?.invoke("Recherche directe du HP sur le réseau local…")
        val pool = Executors.newFixedThreadPool(20)
        try {
            val completion = ExecutorCompletionService<PairData?>(pool)
            for (ip in candidates) completion.submit(java.util.concurrent.Callable { viaTls(wifi, ip) })
            val deadline = System.nanoTime() + TimeUnit.SECONDS.toNanos(9)
            repeat(candidates.size) {
                val remaining = deadline - System.nanoTime()
                if (remaining <= 0) return null
                val completed = completion.poll(remaining, TimeUnit.NANOSECONDS) ?: return null
                completed.get()?.let { return it }
            }
        } finally { pool.shutdownNow() }
        return null
    }
}
