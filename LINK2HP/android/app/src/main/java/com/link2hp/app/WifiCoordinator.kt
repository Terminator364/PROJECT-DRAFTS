package com.link2hp.app

import android.app.Activity
import android.content.Context
import android.content.Intent
import android.net.ConnectivityManager
import android.net.NetworkCapabilities
import android.net.wifi.WifiManager
import android.os.Build
import android.provider.Settings

/**
 * Respecte les permissions Android: aucune connexion forcée ou mot de passe Wi-Fi collecté.
 * L'OS choisit automatiquement les réseaux enregistrés. En cas d'échec, l'utilisateur
 * sélectionne son réseau dans le panneau Wi-Fi natif d'Android.
 */
internal object WifiCoordinator {
    const val PREFERRED_5G = "Starlink 5 GHz"
    const val FALLBACK_24G = "Starlink 2,4 GHz"

    fun wifiConnected(context:Context):Boolean = try {
        val manager=context.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
        manager.allNetworks.any { network ->
            manager.getNetworkCapabilities(network)?.hasTransport(NetworkCapabilities.TRANSPORT_WIFI)==true
        }
    } catch (_:Exception) { false }

    fun bandDescription(context:Context):String {
        if(!wifiConnected(context))return "Aucun Wi-Fi détecté sur ce téléphone"
        return try {
            val mgr=context.applicationContext.getSystemService(Context.WIFI_SERVICE) as WifiManager
            @Suppress("DEPRECATION") val frequency=mgr.connectionInfo.frequency
            when(frequency){
                in 4900..5899 -> "Wi-Fi 5 GHz connecté"
                in 2400..2499 -> "Wi-Fi 2,4 GHz connecté"
                in 5925..7125 -> "Wi-Fi 6 GHz connecté"
                else -> "Wi-Fi connecté"
            }
        } catch (_:Exception) { "Wi-Fi connecté" }
    }

    fun openAndroidWifiPicker(activity:Activity) {
        val intent=if(Build.VERSION.SDK_INT>=29) {
            Intent(Settings.Panel.ACTION_WIFI)
        } else {
            Intent(Settings.ACTION_WIFI_SETTINGS)
        }
        try { activity.startActivityForResult(intent,1976) }
        catch (_:Exception) { activity.startActivityForResult(Intent(Settings.ACTION_WIFI_SETTINGS),1976) }
    }
}
