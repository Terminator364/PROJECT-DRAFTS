package com.terminator364.timeplus

import android.content.SharedPreferences
import android.widget.Toast
import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.rounded.History
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import java.util.Locale

@Composable
internal fun DifferenceScreen(
    prefs: SharedPreferences,
    onAddHistory: (HistoryItem) -> Unit,
    modifier: Modifier = Modifier
) {
    val context = LocalContext.current
    var startHour by rememberSaveable { mutableIntStateOf(prefs.getInt("v2_diff_start_h", 8)) }
    var startMinute by rememberSaveable { mutableIntStateOf(prefs.getInt("v2_diff_start_m", 0)) }
    var endHour by rememberSaveable { mutableIntStateOf(prefs.getInt("v2_diff_end_h", 17)) }
    var endMinute by rememberSaveable { mutableIntStateOf(prefs.getInt("v2_diff_end_m", 0)) }
    var nextDay by rememberSaveable { mutableStateOf(prefs.getBoolean("v2_diff_next_day", true)) }
    var pickerTarget by remember { mutableStateOf<String?>(null) }

    val diff = TimeEngine.difference(startHour, startMinute, endHour, endMinute, nextDay)
    val start = String.format(Locale.getDefault(), "%02d:%02d", startHour, startMinute)
    val end = String.format(Locale.getDefault(), "%02d:%02d", endHour, endMinute)

    pickerTarget?.let { target ->
        TimeSelectionDialog(
            title = if (target == "start") "Heure de départ" else "Heure d’arrivée",
            initialHour = if (target == "start") startHour else endHour,
            initialMinute = if (target == "start") startMinute else endMinute,
            onDismiss = { pickerTarget = null },
            onConfirm = { h, m ->
                if (target == "start") {
                    startHour = h
                    startMinute = m
                    prefs.edit()
                        .putInt("v2_diff_start_h", h)
                        .putInt("v2_diff_start_m", m)
                        .apply()
                } else {
                    endHour = h
                    endMinute = m
                    prefs.edit()
                        .putInt("v2_diff_end_h", h)
                        .putInt("v2_diff_end_m", m)
                        .apply()
                }
                pickerTarget = null
            }
        )
    }

    androidx.compose.foundation.lazy.LazyColumn(
        modifier = modifier.fillMaxSize(),
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(14.dp)
    ) {
        item {
            Text(
                "Durée entre deux heures",
                style = MaterialTheme.typography.headlineSmall,
                fontWeight = FontWeight.Bold
            )
            Text(
                "Choisis un départ et une arrivée. TimePlus gère aussi le passage à minuit.",
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }

        item {
            OutlinedCard {
                Column(
                    modifier = Modifier.fillMaxWidth().padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(10.dp)
                ) {
                    TimeChoiceRow("Départ", start) { pickerTarget = "start" }
                    HorizontalDivider()
                    TimeChoiceRow("Arrivée", end) { pickerTarget = "end" }
                    HorizontalDivider()

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Column(Modifier.weight(1f)) {
                            Text("Passage à minuit", fontWeight = FontWeight.SemiBold)
                            Text(
                                "Si l’arrivée est plus tôt, compter le lendemain",
                                style = MaterialTheme.typography.bodySmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                        }
                        Switch(
                            checked = nextDay,
                            onCheckedChange = {
                                nextDay = it
                                prefs.edit().putBoolean("v2_diff_next_day", it).apply()
                            }
                        )
                    }
                }
            }
        }

        item {
            Card(
                colors = CardDefaults.cardColors(
                    containerColor = MaterialTheme.colorScheme.primaryContainer
                )
            ) {
                Column(
                    Modifier.fillMaxWidth().padding(18.dp),
                    verticalArrangement = Arrangement.spacedBy(4.dp)
                ) {
                    Text(
                        "DURÉE",
                        style = MaterialTheme.typography.labelLarge,
                        color = MaterialTheme.colorScheme.onPrimaryContainer
                    )
                    Text(
                        TimeEngine.formatDuration(diff.minutes),
                        style = MaterialTheme.typography.displaySmall,
                        fontWeight = FontWeight.Bold,
                        color = MaterialTheme.colorScheme.onPrimaryContainer
                    )
                    val suffix = if (diff.crossedMidnight) " • lendemain" else ""
                    Text(
                        start + " → " + end + suffix,
                        color = MaterialTheme.colorScheme.onPrimaryContainer
                    )
                }
            }
        }

        item {
            Button(
                onClick = {
                    val expression = start + " → " + end
                    val result = TimeEngine.formatDuration(diff.minutes) +
                        if (diff.crossedMidnight) " • lendemain" else ""
                    onAddHistory(
                        HistoryItem(
                            expression = expression,
                            result = result,
                            createdAt = System.currentTimeMillis()
                        )
                    )
                    Toast.makeText(context, "Différence mémorisée", Toast.LENGTH_SHORT).show()
                },
                modifier = Modifier.fillMaxWidth()
            ) {
                Icon(Icons.Rounded.History, contentDescription = null)
                Spacer(Modifier.width(8.dp))
                Text("Mémoriser")
            }
        }
    }
}
