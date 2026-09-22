package com.terminator364.timeplus

import android.Manifest
import android.app.AlarmManager
import android.content.Intent
import android.content.SharedPreferences
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Build
import android.provider.Settings
import android.widget.Toast
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.rounded.ArrowBack
import androidx.compose.material.icons.rounded.DeleteSweep
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp

@OptIn(ExperimentalMaterial3Api::class)
@Composable
internal fun SettingsScreen(
    prefs: SharedPreferences,
    onBack: () -> Unit,
    onHistoryCleared: () -> Unit
) {
    val context = LocalContext.current
    var sound by rememberSaveable { mutableStateOf(prefs.getBoolean("default_sound", true)) }
    var vibration by rememberSaveable { mutableStateOf(prefs.getBoolean("default_vibrate", true)) }
    var alarmAt by remember { mutableLongStateOf(prefs.getLong("alarm_at", 0L)) }

    val exactAllowed = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
        (context.getSystemService(android.content.Context.ALARM_SERVICE) as AlarmManager)
            .canScheduleExactAlarms()
    } else true

    val notificationAllowed = Build.VERSION.SDK_INT < 33 ||
        context.checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) == PackageManager.PERMISSION_GRANTED

    Scaffold(
        contentWindowInsets = WindowInsets.safeDrawing,
        topBar = {
            TopAppBar(
                title = { Text("Paramètres") },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.Rounded.ArrowBack, contentDescription = "Retour")
                    }
                }
            )
        }
    ) { inner ->
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(inner)
                .consumeWindowInsets(inner),
            contentPadding = PaddingValues(16.dp),
            verticalArrangement = Arrangement.spacedBy(14.dp)
        ) {
            item {
                SettingsCard("Alertes", "Comportement par défaut") {
                    SettingSwitchRow(
                        "Son",
                        "Jouer une sonnerie à l’heure cible",
                        sound
                    ) {
                        sound = it
                        prefs.edit().putBoolean("default_sound", it).apply()
                    }

                    SettingSwitchRow(
                        "Vibration",
                        "Vibrer à l’heure cible",
                        vibration
                    ) {
                        vibration = it
                        prefs.edit().putBoolean("default_vibrate", it).apply()
                    }
                }
            }

            item {
                SettingsCard("Permissions", "État réel du téléphone") {
                    StatusRow("Notifications", notificationAllowed)
                    StatusRow("Alarmes exactes", exactAllowed)

                    if (!exactAllowed && Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
                        OutlinedButton(
                            onClick = {
                                runCatching {
                                    context.startActivity(
                                        Intent(
                                            Settings.ACTION_REQUEST_SCHEDULE_EXACT_ALARM,
                                            Uri.parse("package:" + context.packageName)
                                        )
                                    )
                                }
                            },
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            Text("Autoriser les alarmes exactes")
                        }
                    }
                }
            }

            if (alarmAt > System.currentTimeMillis()) {
                item {
                    SettingsCard("Alerte active", formatDateTime(alarmAt)) {
                        OutlinedButton(
                            onClick = {
                                AlarmScheduler.cancel(context)
                                alarmAt = 0L
                                Toast.makeText(
                                    context,
                                    "Alerte annulée",
                                    Toast.LENGTH_SHORT
                                ).show()
                            },
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            Text("Annuler l’alerte")
                        }
                    }
                }
            }

            item {
                SettingsCard(
                    "Données",
                    "Local uniquement, sans compte ni Internet"
                ) {
                    OutlinedButton(
                        onClick = {
                            onHistoryCleared()
                            Toast.makeText(
                                context,
                                "Historique effacé",
                                Toast.LENGTH_SHORT
                            ).show()
                        },
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Icon(Icons.Rounded.DeleteSweep, contentDescription = null)
                        Spacer(Modifier.width(8.dp))
                        Text("Effacer l’historique")
                    }
                }
            }

            item {
                SettingsCard(
                    "Application",
                    "Chaîne de mise à jour permanente"
                ) {
                    Text("Version 2.0.0 • versionCode 5")
                    Text(
                        "Package : com.terminator364.timeplus",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                    Text(
                        "Mise à jour installable par-dessus la version signée actuelle.",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }
        }
    }
}
