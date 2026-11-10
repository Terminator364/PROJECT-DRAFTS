package com.link2hp.app

import android.app.Activity
import android.content.Context
import android.content.Intent
import android.graphics.Color
import android.graphics.Typeface
import android.graphics.drawable.GradientDrawable
import android.graphics.drawable.RippleDrawable
import android.content.res.ColorStateList
import android.net.ConnectivityManager
import android.net.NetworkCapabilities
import android.net.NetworkRequest
import android.net.Uri
import android.os.Bundle
import android.os.Build
import android.view.WindowInsets
import android.os.SystemClock
import android.util.Base64
import android.view.Gravity
import android.view.View
import android.view.ViewGroup
import android.view.inputmethod.InputMethodManager
import android.widget.*
import java.util.concurrent.Executors

/** LINK2HP: one main action, explicit feedback, optional advanced networking. */
class MainActivity : Activity() {
    private val io = Executors.newSingleThreadExecutor()
    private lateinit var store: Store
    private lateinit var status: TextView
    private lateinit var detail: TextView
    private lateinit var spin: ProgressBar
    private lateinit var input: EditText
    private lateinit var history: LinearLayout
    private lateinit var pairButton: Button
    private lateinit var sendButton: Button
    private lateinit var networkInfo: TextView
    private lateinit var advanced: LinearLayout
    private var pairRunning = false
    private var healthRunning = false
    private var linked = false
    private var wifiWatcher: ConnectivityManager.NetworkCallback? = null
    private var lastAttempt = 0L
    private var lastSendFeedback = 0L

    private val navy = Color.rgb(19, 37, 65)
    private val muted = Color.rgb(91, 107, 130)
    private val blue = Color.rgb(20, 91, 224)
    private val green = Color.rgb(17, 121, 74)
    private val red = Color.rgb(174, 60, 55)
    private val surface = Color.rgb(247, 249, 253)
    private fun dp(x: Int) = (x * resources.displayMetrics.density).toInt()
    private fun shape(color: Int, radius: Int = 16) = GradientDrawable().apply {
        setColor(color); cornerRadius = dp(radius).toFloat()
    }
    private fun text(s: String, size: Float = 15f, bold: Boolean = false, color: Int = navy) =
        TextView(this).apply {
            text = s; textSize = size; setTextColor(color)
            includeFontPadding = true; setLineSpacing(dp(2).toFloat(), 1f)
            if (bold) setTypeface(Typeface.DEFAULT, Typeface.BOLD)
        }
    private fun button(s: String, primary: Boolean = true) = Button(this).apply {
        text = s; textSize = 15f; isAllCaps = false
        setTextColor(if (primary) Color.WHITE else blue)
        background = RippleDrawable(ColorStateList.valueOf(if (primary) Color.rgb(164, 200, 255) else Color.rgb(205, 221, 255)),
            shape(if (primary) blue else Color.rgb(232, 240, 255), 12), null)
        minHeight = dp(52); isHapticFeedbackEnabled = true
        setPadding(dp(12), dp(8), dp(12), dp(8))
        contentDescription = s
    }
    private fun add(column: LinearLayout, child: View, top: Int = 0) {
        val p = LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT)
        p.topMargin = dp(top); column.addView(child, p)
    }
    private fun card() = LinearLayout(this).apply {
        orientation = LinearLayout.VERTICAL; setPadding(dp(16), dp(16), dp(16), dp(16))
        background = shape(Color.WHITE)
        elevation = dp(1).toFloat()
    }
    private fun feedback(message: String) = Toast.makeText(this, message, Toast.LENGTH_SHORT).show()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        window.statusBarColor = surface
        window.navigationBarColor = surface
        @Suppress("DEPRECATION")
        window.decorView.systemUiVisibility = View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR or View.SYSTEM_UI_FLAG_LIGHT_NAVIGATION_BAR
        store = Store(this)
        val page = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(dp(18), dp(26), dp(18), dp(24))
            setBackgroundColor(surface)
        }
        add(page, text("LINK2HP", 26f, true))
        add(page, text("Un lien sur le téléphone. Le téléchargement sur le HP.", 13f, false, muted), 4)

        val connection = card()
        add(connection, text("MON ORDINATEUR", 12f, true, muted))
        status = text("Recherche du HP…", 18f, true)
        add(connection, status, 9)
        detail = text("Connexion locale en cours.", 13f, false, muted)
        add(connection, detail, 6)
        spin = ProgressBar(this, null, android.R.attr.progressBarStyleHorizontal).apply {
            isIndeterminate = true; visibility = View.GONE
        }
        add(connection, spin, 10)
        pairButton = button("Connecter au HP", false)
        pairButton.setOnClickListener {
            feedback("Recherche du HP lancée")
            startPair()
        }
        add(connection, pairButton, 12)
        add(page, connection, 19)

        val sender = card()
        add(sender, text("ENVOYER UN LIEN", 12f, true, muted))
        input = EditText(this).apply {
            hint = "Colle un lien ou un magnet"
            textSize = 15f; isSingleLine = false; minLines = 2; maxLines = 3
            background = shape(surface, 9)
            setPadding(dp(12), dp(12), dp(12), dp(12))
        }
        add(sender, input, 11)
        sendButton = button("Envoyer au HP")
        sendButton.setOnClickListener {
            it.performHapticFeedback(android.view.HapticFeedbackConstants.VIRTUAL_KEY)
            saveLink()
        }
        add(sender, sendButton, 11)
        add(sender, text("Tu peux aussi choisir « Partager → LINK2HP » dans ton navigateur.", 12f, false, muted), 10)
        add(page, sender, 13)

        val activity = card()
        add(activity, text("MES ENVOIS", 12f, true, muted))
        history = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL }
        add(activity, history, 8)
        val refresh = button("Actualiser", false)
        refresh.setOnClickListener {
            it.performHapticFeedback(android.view.HapticFeedbackConstants.VIRTUAL_KEY)
            feedback("Vérification en cours")
            retry(true)
        }
        add(activity, refresh, 12)
        add(page, activity, 13)

        val options = button("Options réseau (facultatif)", false)
        add(page, options, 15)
        advanced = card().apply { visibility = View.GONE }
        add(advanced, text("CONNEXION RÉSEAU", 12f, true, muted))
        networkInfo = text("Le téléphone peut rester sur l'extender 2,4 GHz. Le HP gère son Wi-Fi.", 13f, false, muted)
        add(advanced, networkInfo, 7)
        add(advanced, text("Les bandes 2,4 et 5 GHz fonctionnent ensemble si ton routeur et ton extender partagent le même réseau local.", 12f, false, muted), 8)
        val hpWifi = button("Réseaux visibles sur le HP", false)
        hpWifi.setOnClickListener { feedback("Recherche des réseaux du HP"); showHpNetworks() }
        add(advanced, hpWifi, 12)
        val phoneWifi = button("Changer le Wi-Fi du téléphone", false)
        phoneWifi.setOnClickListener { WifiCoordinator.openAndroidWifiPicker(this) }
        add(advanced, phoneWifi, 8)
        add(page, advanced, 8)
        options.setOnClickListener {
            advanced.visibility = if (advanced.visibility == View.VISIBLE) View.GONE else View.VISIBLE
            options.text = if (advanced.visibility == View.VISIBLE) "Masquer les options réseau" else "Options réseau (facultatif)"
            if (advanced.visibility == View.VISIBLE) updateNetworkInfo()
        }
        val scrolling = ScrollView(this).apply { isFillViewport = true; clipToPadding = false; addView(page) }
        // Android 15/16 enforce edge-to-edge for apps targeting API 35.
        // Honor the actual status/navigation bar insets on all screen densities.
        if (Build.VERSION.SDK_INT >= 30) {
            scrolling.setOnApplyWindowInsetsListener { v, insets ->
                val top = insets.getInsets(WindowInsets.Type.statusBars()).top
                val bottom = insets.getInsets(WindowInsets.Type.navigationBars()).bottom
                v.setPadding(0, top, 0, bottom)
                insets
            }
        } else scrolling.fitsSystemWindows = true
        setContentView(scrolling)
        displayRows()
        receiveShare(intent)
        watchWifi()
        if (store.pair() == null) startPair() else retry(false)
    }

    override fun onNewIntent(intent: Intent) { super.onNewIntent(intent); setIntent(intent); receiveShare(intent) }
    private fun render(title: String, explanation: String, busy: Boolean = false, online: Boolean = false) {
        runOnUiThread {
            linked = online
            status.text = title
            status.setTextColor(if (online) green else if (busy) navy else red)
            detail.text = explanation
            spin.visibility = if (busy) View.VISIBLE else View.GONE
            pairButton.isEnabled = !pairRunning && !busy
            pairButton.text = when { busy -> "Connexion en cours…"; online -> "Vérifier la connexion"; else -> "Réessayer la connexion" }
        }
    }
    private fun startPair() {
        if (pairRunning) { feedback("Recherche déjà en cours"); return }
        if (store.pair() != null) { retry(true); return }
        pairRunning = true
        render("Recherche du HP…", "Tu peux rester sur ton Wi-Fi 2,4 GHz. Aucun code à copier.", true)
        io.execute {
            try {
                Api.pair(this) { msg -> render("Association en cours…", msg, true) }
                render("HP connecté", "Association acceptée. Tu peux envoyer tes liens.", false, true)
                RetryJob.schedule(this)
                Api.process(this)
            } catch (e: Exception) {
                val wifi = WifiCoordinator.wifiConnected(this)
                render("HP introuvable", if (!wifi) {
                    "Active le Wi-Fi. Les demandes restent enregistrées sur le téléphone."
                } else {
                    "Vérifie que LINK2HP est ouvert sur le HP. Le 2,4 GHz fonctionne si les appareils sont sur le même réseau local."
                }, false)
            } finally {
                runOnUiThread { pairRunning = false; pairButton.isEnabled = true
                    pairButton.text = if (linked) "Vérifier la connexion" else "Réessayer la connexion"
                    displayRows()
                }
            }
        }
    }
    private fun retry(refresh: Boolean) {
        if (pairRunning || healthRunning) { feedback("Vérification déjà en cours"); return }
        val saved = store.pair()
        if (saved == null) { startPair(); return }
        healthRunning = true
        render("Vérification de la connexion…", "Recherche du HP sur ton réseau local.", true)
        io.execute {
            try {
                var pair = PairData.parse(saved)
                var healthy = try { Api.health(pair); true } catch (_: Exception) { false }
                if (!healthy) {
                    val found = Api.discover(this)
                    if (found != null && found.pin == pair.pin) {
                        pair = pair.copy(host = found.host, port = found.port)
                        store.savePair(pair.serialized())
                        Api.health(pair); healthy = true
                    }
                }
                if (!healthy) throw IllegalStateException("Le HP ne répond pas")
                render("HP connecté", "L'ordinateur est joignable. Les liens sont transmis automatiquement.", false, true)
                val again = Api.process(this, refresh)
                if (again) RetryJob.schedule(this)
            } catch (_: Exception) {
                RetryJob.schedule(this)
                render("HP hors ligne", "Le lien est conservé. Vérifie que LINK2HP fonctionne sur le HP et que les deux Wi-Fi communiquent.", false)
            } finally {
                runOnUiThread { healthRunning = false; pairButton.isEnabled = true
                    pairButton.text = if (linked) "Vérifier la connexion" else "Réessayer la connexion"
                    displayRows()
                }
            }
        }
    }
    private fun saveLink() {
        val raw = input.text.toString().trim()
        val value = Regex("(?:https?://[^\\s]+|magnet:\\?[^\\s]+)").find(raw)?.value
        if (value == null || value.length > 4096) {
            feedback("Colle d'abord un lien valide")
            input.error = "Lien HTTP(S) ou magnet attendu"
            return
        }
        val added = store.save("link", value)
        input.setText("")
        (getSystemService(Context.INPUT_METHOD_SERVICE) as? InputMethodManager)?.hideSoftInputFromWindow(input.windowToken, 0)
        if (added) {
            lastSendFeedback = SystemClock.elapsedRealtime()
            sendButton.text = "✓ Lien enregistré"
            sendButton.postDelayed({ if (SystemClock.elapsedRealtime() - lastSendFeedback >= 1400) sendButton.text = "Envoyer au HP" }, 1500)
            feedback(if (linked) "Envoi en cours vers le HP" else "Lien enregistré, en attente du HP")
            if (store.pair() != null) retry(false) else startPair()
        } else feedback("Ce lien a déjà été enregistré")
        displayRows()
    }
    private fun receiveShare(i: Intent?) {
        if (i?.action != Intent.ACTION_SEND) return
        val shared = i.getStringExtra(Intent.EXTRA_TEXT)
        if (!shared.isNullOrBlank()) { input.setText(shared); saveLink(); return }
        @Suppress("DEPRECATION") val uri = i.getParcelableExtra<Uri>(Intent.EXTRA_STREAM)
        if (uri?.scheme != "content") { feedback("Fichier non reconnu"); return }
        try {
            val data = java.io.ByteArrayOutputStream()
            contentResolver.openInputStream(uri)?.use { stream ->
                val chunk = ByteArray(8192); var total = 0
                while (true) {
                    val n = stream.read(chunk); if (n < 0) break; total += n
                    if (total > 5 * 1024 * 1024) throw IllegalArgumentException("Torrent trop volumineux")
                    data.write(chunk, 0, n)
                }
            } ?: throw IllegalArgumentException("Fichier inaccessible")
            val raw = data.toByteArray()
            if (raw.size < 12 || raw[0].toInt() != 100) throw IllegalArgumentException("Torrent invalide")
            val added = store.save("torrent_file", Base64.encodeToString(raw, Base64.NO_WRAP))
            feedback(if (added) "Torrent enregistré pour le HP" else "Torrent déjà enregistré")
            displayRows()
            if (added) { if (store.pair() != null) retry(false) else startPair() }
        } catch (e: Exception) { feedback("Import impossible : ${e.message}") }
    }
    private fun displayRows() {
        history.removeAllViews()
        val rows = store.rows().take(6)
        if (rows.isEmpty()) { add(history, text("Aucune demande pour le moment.", 13f, false, muted)); return }
        rows.forEach { item ->
            val label = when (item.state) {
                "QUEUED_PHONE" -> "En attente du HP"
                "COMPLETED" -> "Terminé"
                "HANDED_TO_QBITTORRENT" -> "Envoyé à qBittorrent"
                "FAILED" -> "Échec"
                "RUNNING" -> "Téléchargement"
                "WAIT_SELECTION" -> "Choix requis sur le HP"
                "QUEUED" -> "Reçu par le HP"
                else -> "Traitement : ${item.state}"
            }
            add(history, text("● ${if (item.kind == "torrent_file") "Torrent" else "Lien"} — $label", 13f, false, muted), 9)
        }
    }
    private fun updateNetworkInfo() {
        networkInfo.text = "Téléphone : ${WifiCoordinator.bandDescription(this)}. Le HP utilise son propre Wi-Fi."
    }
    private fun showHpNetworks() {
        val raw = store.pair()
        if (raw == null) { feedback("Connecte d'abord le HP"); return }
        io.execute {
            try {
                val info = Api.hpNetworks(PairData.parse(raw))
                val nets = info.optJSONArray("networks") ?: throw IllegalStateException("Liste indisponible")
                val rows = (0 until nets.length()).map { nets.getJSONObject(it) }
                val options = rows.map { o ->
                    val bands = o.optJSONArray("bands")?.let { a -> (0 until a.length()).map { a.optString(it) }.joinToString(" / ") } ?: ""
                    val state = when { o.optBoolean("current") -> "Actif"; o.optBoolean("saved") -> "Enregistré"; else -> "À configurer sur le HP" }
                    "${o.optString("ssid")} · $bands · $state"
                }.toTypedArray()
                runOnUiThread {
                    android.app.AlertDialog.Builder(this)
                        .setTitle("Réseaux visibles sur le HP")
                        .setMessage(if (options.isEmpty()) "Aucun réseau détecté par le HP." else null)
                        .apply { if (options.isNotEmpty()) setItems(options) { _, n -> chooseHpNetwork(rows[n].optString("ssid"), rows[n].optBoolean("saved")) } }
                        .setNegativeButton("Fermer", null).show()
                }
            } catch (_: Exception) {
                runOnUiThread { feedback("Le HP doit être connecté pour afficher ses réseaux") }
            }
        }
    }
    private fun chooseHpNetwork(ssid: String, saved: Boolean) {
        if (!saved) {
            android.app.AlertDialog.Builder(this).setTitle("Réseau non enregistré")
                .setMessage("Connecte d'abord ce réseau sur le HP pour que Windows enregistre son mot de passe.")
                .setPositiveButton("Compris", null).show()
            return
        }
        android.app.AlertDialog.Builder(this).setTitle("Connecter le HP à $ssid ?")
            .setMessage("Le HP changera de réseau. La connexion au téléphone peut se couper momentanément.")
            .setPositiveButton("Connecter") { _, _ ->
                val savedPair = store.pair() ?: return@setPositiveButton
                render("Changement réseau…", "Le HP se connecte à $ssid.", true)
                io.execute {
                    try {
                        val state = Api.hpSwitchNetwork(PairData.parse(savedPair), ssid).optString("state")
                        render(if (state == "ALREADY_CONNECTED") "HP connecté" else "Changement demandé au HP",
                            "Le téléphone recherchera de nouveau le HP si nécessaire.", false, state == "ALREADY_CONNECTED")
                        RetryJob.schedule(this)
                    } catch (_: Exception) { render("Connexion interrompue", "Vérifie le Wi-Fi du HP puis réessaye.") }
                }
            }.setNegativeButton("Annuler", null).show()
    }
    private fun watchWifi() {
        try {
            val cm = getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
            val request = NetworkRequest.Builder().addTransportType(NetworkCapabilities.TRANSPORT_WIFI).build()
            val cb = object : ConnectivityManager.NetworkCallback() {
                override fun onAvailable(network: android.net.Network) {
                    runOnUiThread {
                        if (advanced.visibility == View.VISIBLE) updateNetworkInfo()
                        if (SystemClock.elapsedRealtime() - lastAttempt >= 18000L) {
                            lastAttempt = SystemClock.elapsedRealtime()
                            if (store.pair() == null) { if (!pairRunning) startPair() }
                            else if (!healthRunning) retry(false)
                        }
                    }
                }
            }
            cm.registerNetworkCallback(request, cb); wifiWatcher = cb
        } catch (_: Exception) { }
    }
    override fun onDestroy() {
        wifiWatcher?.let { try { (getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager).unregisterNetworkCallback(it) } catch (_: Exception) {} }
        io.shutdown(); super.onDestroy()
    }
}
