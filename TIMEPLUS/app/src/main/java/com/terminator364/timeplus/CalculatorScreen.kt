package com.terminator364.timeplus

import android.Manifest
import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.content.SharedPreferences
import android.content.pm.PackageManager
import android.os.Build
import android.widget.Toast
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.rounded.AccessTime
import androidx.compose.material.icons.rounded.Add
import androidx.compose.material.icons.rounded.DeleteSweep
import androidx.compose.material.icons.rounded.History
import androidx.compose.material.icons.rounded.NotificationsActive
import androidx.compose.material.icons.rounded.Remove
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import java.util.Calendar
import java.util.Locale
import kotlinx.coroutines.delay

private enum class ReferenceMode { NOW, CUSTOM }

@OptIn(ExperimentalMaterial3Api::class)
@Composable
internal fun CalculatorScreen(
    prefs: SharedPreferences,
    history: List<HistoryItem>,
    onAddHistory: (HistoryItem) -> Unit,
    onClearHistory: () -> Unit,
    modifier: Modifier = Modifier
) {
    val context = LocalContext.current
    val now = Calendar.getInstance()

    var referenceMode by rememberSaveable {
        mutableStateOf(
            if (prefs.getBoolean("v2_custom_reference", false)) ReferenceMode.CUSTOM.name
            else ReferenceMode.NOW.name
        )
    }
    var customHour by rememberSaveable {
        mutableIntStateOf(prefs.getInt("v2_custom_hour", now.get(Calendar.HOUR_OF_DAY)))
    }
    var customMinute by rememberSaveable {
        mutableIntStateOf(prefs.getInt("v2_custom_minute", now.get(Calendar.MINUTE)))
    }
    var operation by rememberSaveable {
        mutableStateOf(prefs.getString("v2_operation", TimeOperation.PLUS.name) ?: TimeOperation.PLUS.name)
    }
    var durationMinutes by rememberSaveable {
        mutableIntStateOf(prefs.getInt("v2_duration", 30).coerceIn(1, 9999))
    }
    var durationText by rememberSaveable { mutableStateOf(durationMinutes.toString()) }
    var nowMillis by remember { mutableLongStateOf(System.currentTimeMillis()) }
    var showReferencePicker by remember { mutableStateOf(false) }
    var showDurationWheel by remember { mutableStateOf(false) }
    var pendingAlarmTarget by remember { mutableStateOf<Long?>(null) }

    val permissionLauncher = rememberLauncherForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { granted ->
        val target = pendingAlarmTarget
        pendingAlarmTarget = null
        if (granted && target != null) {
            scheduleAlarmNow(context, prefs, target)
        }
    }

    LaunchedEffect(referenceMode) {
        while (referenceMode == ReferenceMode.NOW.name) {
            nowMillis = System.currentTimeMillis()
            delay(1000L)
        }
    }

    val baseMillis = if (referenceMode == ReferenceMode.NOW.name) {
        nowMillis
    } else {
        TimeEngine.todayAt(customHour, customMinute, nowMillis)
    }
    val op = if (operation == TimeOperation.MINUS.name) TimeOperation.MINUS else TimeOperation.PLUS
    val calculation = TimeEngine.calculate(baseMillis, durationMinutes, op)
    val baseTime = if (referenceMode == ReferenceMode.NOW.name) formatTime(baseMillis, true) else formatTime(baseMillis)
    val resultTime = formatTime(calculation.resultMillis)
    val expression = baseTime + " " + (if (op == TimeOperation.PLUS) "+" else "−") + " " +
        TimeEngine.formatDuration(durationMinutes)
    val dayText = dayOffsetText(calculation.dayOffset)

    fun persist() {
        prefs.edit()
            .putBoolean("v2_custom_reference", referenceMode == ReferenceMode.CUSTOM.name)
            .putInt("v2_custom_hour", customHour)
            .putInt("v2_custom_minute", customMinute)
            .putString("v2_operation", operation)
            .putInt("v2_duration", durationMinutes)
            .apply()
    }

    fun scheduleResult() {
        var target = calculation.resultMillis
        while (target <= System.currentTimeMillis()) target += 86_400_000L
        if (
            Build.VERSION.SDK_INT >= 33 &&
            context.checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED
        ) {
            pendingAlarmTarget = target
            permissionLauncher.launch(Manifest.permission.POST_NOTIFICATIONS)
        } else {
            scheduleAlarmNow(context, prefs, target)
        }
    }

    if (showReferencePicker) {
        TimeSelectionDialog(
            title = "Heure de référence",
            initialHour = customHour,
            initialMinute = customMinute,
            onDismiss = { showReferencePicker = false },
            onConfirm = { h, m ->
                customHour = h
                customMinute = m
                referenceMode = ReferenceMode.CUSTOM.name
                showReferencePicker = false
                persist()
            }
        )
    }

    if (showDurationWheel) {
        DurationWheelSheet(
            initialMinutes = durationMinutes,
            onDismiss = { showDurationWheel = false },
            onConfirm = {
                durationMinutes = it.coerceIn(1, 9999)
                durationText = durationMinutes.toString()
                showDurationWheel = false
                persist()
            }
        )
    }

    LazyColumn(
        modifier = modifier.fillMaxSize(),
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(14.dp)
    ) {
        item {
            SectionTitle("Référence", "R")
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                FilterChip(
                    selected = referenceMode == ReferenceMode.NOW.name,
                    onClick = {
                        referenceMode = ReferenceMode.NOW.name
                        prefs.edit().putBoolean("v2_custom_reference", false).apply()
                    },
                    label = { Text("Maintenant") }
                )
                FilterChip(
                    selected = referenceMode == ReferenceMode.CUSTOM.name,
                    onClick = { showReferencePicker = true },
                    label = { Text("Heure choisie") }
                )
            }
            if (referenceMode == ReferenceMode.CUSTOM.name) {
                AssistChip(
                    onClick = { showReferencePicker = true },
                    label = {
                        Text(String.format(Locale.getDefault(), "%02d:%02d", customHour, customMinute))
                    },
                    leadingIcon = { Icon(Icons.Rounded.AccessTime, contentDescription = null) }
                )
            }
        }

        item {
            SectionTitle("Opération", "R ± Δ")
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                FilterChip(
                    selected = op == TimeOperation.PLUS,
                    onClick = {
                        operation = TimeOperation.PLUS.name
                        prefs.edit().putString("v2_operation", operation).apply()
                    },
                    label = { Text("+ Ajouter") },
                    leadingIcon = { Icon(Icons.Rounded.Add, contentDescription = null) }
                )
                FilterChip(
                    selected = op == TimeOperation.MINUS,
                    onClick = {
                        operation = TimeOperation.MINUS.name
                        prefs.edit().putString("v2_operation", operation).apply()
                    },
                    label = { Text("− Soustraire") },
                    leadingIcon = { Icon(Icons.Rounded.Remove, contentDescription = null) }
                )
            }
        }

        item {
            SectionTitle("Durée", "Δ")
            LazyRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                items(listOf(1, 2, 3, 5, 10, 15, 20, 30, 45, 60)) { preset ->
                    AssistChip(
                        onClick = {
                            durationMinutes = preset
                            durationText = preset.toString()
                            prefs.edit().putInt("v2_duration", preset).apply()
                        },
                        label = { Text(if (preset == 60) "1 h" else preset.toString() + " min") }
                    )
                }
            }

            Spacer(Modifier.height(8.dp))
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(10.dp)
            ) {
                OutlinedTextField(
                    value = durationText,
                    onValueChange = { raw ->
                        if (raw.length <= 4 && raw.all { it.isDigit() }) {
                            durationText = raw
                            raw.toIntOrNull()?.takeIf { it in 1..9999 }?.let {
                                durationMinutes = it
                                prefs.edit().putInt("v2_duration", it).apply()
                            }
                        }
                    },
                    label = { Text("Minutes") },
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                    singleLine = true,
                    modifier = Modifier.weight(1f)
                )
                OutlinedButton(onClick = { showDurationWheel = true }) {
                    Text("Roues")
                }
            }
        }

        item {
            ResultCard(
                expression = expression,
                resultTime = resultTime,
                dayText = dayText,
                onCopy = {
                    val clipboard = context.getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
                    clipboard.setPrimaryClip(ClipData.newPlainText("TimePlus", resultTime))
                    Toast.makeText(context, "Heure copiée", Toast.LENGTH_SHORT).show()
                },
                onReuse = {
                    val cal = Calendar.getInstance().apply { timeInMillis = calculation.resultMillis }
                    customHour = cal.get(Calendar.HOUR_OF_DAY)
                    customMinute = cal.get(Calendar.MINUTE)
                    referenceMode = ReferenceMode.CUSTOM.name
                    persist()
                    Toast.makeText(context, "Résultat devenu nouvelle référence", Toast.LENGTH_SHORT).show()
                }
            )
        }

        item {
            Button(
                onClick = {
                    persist()
                    onAddHistory(
                        HistoryItem(
                            expression,
                            resultTime + " " + dayText,
                            System.currentTimeMillis()
                        )
                    )
                    Toast.makeText(context, "Calcul mémorisé", Toast.LENGTH_SHORT).show()
                },
                modifier = Modifier.fillMaxWidth()
            ) {
                Icon(Icons.Rounded.History, contentDescription = null)
                Spacer(Modifier.width(8.dp))
                Text("Mémoriser ce calcul")
            }

            Spacer(Modifier.height(8.dp))

            OutlinedButton(
                onClick = { scheduleResult() },
                modifier = Modifier.fillMaxWidth()
            ) {
                Icon(Icons.Rounded.NotificationsActive, contentDescription = null)
                Spacer(Modifier.width(8.dp))
                Text("Programmer une alerte au résultat")
            }
        }

        if (history.isNotEmpty()) {
            item {
                Row(modifier = Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
                    Column(Modifier.weight(1f)) {
                        Text("Historique", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                        Text(
                            "Derniers calculs",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                    IconButton(onClick = onClearHistory) {
                        Icon(Icons.Rounded.DeleteSweep, contentDescription = "Effacer l'historique")
                    }
                }
            }
            items(history.take(8)) { historyItem ->
                HistoryCard(historyItem)
            }
        }
    }
}

private fun scheduleAlarmNow(
    context: Context,
    prefs: SharedPreferences,
    target: Long
) {
    val result = AlarmScheduler.schedule(
        context,
        target,
        prefs.getBoolean("default_sound", true),
        prefs.getBoolean("default_vibrate", true)
    )
    val message = if (result.precision == AlarmPrecision.EXACT) {
        "Alerte exacte • " + formatTime(target)
    } else {
        "Alerte ~" + formatTime(target) + " • autorise l’exactitude dans Paramètres"
    }
    Toast.makeText(context, message, Toast.LENGTH_LONG).show()
}
