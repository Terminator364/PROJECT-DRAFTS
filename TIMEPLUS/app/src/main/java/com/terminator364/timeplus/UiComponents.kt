package com.terminator364.timeplus

import android.widget.NumberPicker
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.rounded.ContentCopy
import androidx.compose.material.icons.rounded.History
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.viewinterop.AndroidView
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

@Composable
internal fun SectionTitle(title: String, hint: String) {
    Row(verticalAlignment = Alignment.CenterVertically) {
        Text(title, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
        Spacer(Modifier.width(8.dp))
        Text(hint, style = MaterialTheme.typography.labelMedium, color = MaterialTheme.colorScheme.primary)
    }
}

@Composable
internal fun ResultCard(
    expression: String,
    resultTime: String,
    dayText: String,
    onCopy: () -> Unit,
    onReuse: () -> Unit
) {
    Card(
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.primaryContainer),
        shape = RoundedCornerShape(24.dp)
    ) {
        Column(
            modifier = Modifier.fillMaxWidth().padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            Text("RÉSULTAT", style = MaterialTheme.typography.labelLarge, color = MaterialTheme.colorScheme.onPrimaryContainer)
            Text(
                resultTime,
                fontSize = 52.sp,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.onPrimaryContainer
            )
            Text(dayText, color = MaterialTheme.colorScheme.onPrimaryContainer)
            HorizontalDivider(color = MaterialTheme.colorScheme.onPrimaryContainer.copy(alpha = .18f))
            Text(expression, color = MaterialTheme.colorScheme.onPrimaryContainer)

            OutlinedButton(onClick = onReuse, modifier = Modifier.fillMaxWidth()) {
                Icon(Icons.Rounded.History, contentDescription = null)
                Spacer(Modifier.width(8.dp))
                Text("Continuer depuis ce résultat")
            }
            TextButton(onClick = onCopy, modifier = Modifier.align(Alignment.End)) {
                Icon(Icons.Rounded.ContentCopy, contentDescription = null)
                Spacer(Modifier.width(6.dp))
                Text("Copier")
            }
        }
    }
}

@Composable
internal fun HistoryCard(item: HistoryItem) {
    OutlinedCard {
        Column(Modifier.fillMaxWidth().padding(14.dp)) {
            Text(item.expression, fontWeight = FontWeight.SemiBold)
            Text(item.result, color = MaterialTheme.colorScheme.primary)
            Text(
                SimpleDateFormat("dd MMM • HH:mm", Locale.getDefault()).format(Date(item.createdAt)),
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
internal fun DurationWheelSheet(
    initialMinutes: Int,
    onDismiss: () -> Unit,
    onConfirm: (Int) -> Unit
) {
    var hours by remember { mutableIntStateOf((initialMinutes / 60).coerceIn(0, 166)) }
    var minutes by remember { mutableIntStateOf((initialMinutes % 60).coerceIn(0, 59)) }

    ModalBottomSheet(onDismissRequest = onDismiss) {
        Column(
            modifier = Modifier.fillMaxWidth().padding(horizontal = 20.dp, vertical = 8.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text("Choisir une durée", style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Bold)
            Text("Fais glisser les roues", color = MaterialTheme.colorScheme.onSurfaceVariant)
            Spacer(Modifier.height(12.dp))

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.Center,
                verticalAlignment = Alignment.CenterVertically
            ) {
                WheelNumberPicker(hours, 0, 166, { hours = it }, Modifier.weight(1f))
                Text("h", style = MaterialTheme.typography.titleLarge)
                WheelNumberPicker(minutes, 0, 59, { minutes = it }, Modifier.weight(1f))
                Text("min", style = MaterialTheme.typography.titleLarge)
            }

            Spacer(Modifier.height(12.dp))
            Button(
                onClick = { onConfirm((hours * 60 + minutes).coerceAtLeast(1)) },
                modifier = Modifier.fillMaxWidth()
            ) {
                Text("Utiliser " + TimeEngine.formatDuration((hours * 60 + minutes).coerceAtLeast(1)))
            }
            Spacer(Modifier.height(24.dp))
        }
    }
}

@Composable
private fun WheelNumberPicker(
    value: Int,
    min: Int,
    max: Int,
    onValueChange: (Int) -> Unit,
    modifier: Modifier = Modifier
) {
    AndroidView(
        modifier = modifier.height(170.dp),
        factory = { context ->
            NumberPicker(context).apply {
                minValue = min
                maxValue = max
                wrapSelectorWheel = true
                descendantFocusability = NumberPicker.FOCUS_BLOCK_DESCENDANTS
                setOnValueChangedListener { _, _, newVal -> onValueChange(newVal) }
            }
        },
        update = { picker ->
            if (picker.value != value) picker.value = value.coerceIn(min, max)
        }
    )
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
internal fun TimeSelectionDialog(
    title: String,
    initialHour: Int,
    initialMinute: Int,
    onDismiss: () -> Unit,
    onConfirm: (Int, Int) -> Unit
) {
    val state = rememberTimePickerState(
        initialHour = initialHour.coerceIn(0, 23),
        initialMinute = initialMinute.coerceIn(0, 59),
        is24Hour = true
    )

    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text(title) },
        text = {
            Box(modifier = Modifier.fillMaxWidth(), contentAlignment = Alignment.Center) {
                TimePicker(state = state)
            }
        },
        confirmButton = {
            TextButton(onClick = { onConfirm(state.hour, state.minute) }) { Text("Valider") }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) { Text("Annuler") }
        }
    )
}

@Composable
internal fun TimeChoiceRow(label: String, value: String, onClick: () -> Unit) {
    Row(modifier = Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
        Column(Modifier.weight(1f)) {
            Text(label, fontWeight = FontWeight.SemiBold)
            Text(
                value,
                style = MaterialTheme.typography.headlineSmall,
                color = MaterialTheme.colorScheme.primary
            )
        }
        OutlinedButton(onClick = onClick) { Text("Choisir") }
    }
}

@Composable
internal fun SettingsCard(
    title: String,
    subtitle: String,
    content: @Composable ColumnScope.() -> Unit
) {
    OutlinedCard(shape = RoundedCornerShape(20.dp)) {
        Column(
            modifier = Modifier.fillMaxWidth().padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(10.dp)
        ) {
            Text(title, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
            Text(
                subtitle,
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
            HorizontalDivider()
            content()
        }
    }
}

@Composable
internal fun SettingSwitchRow(
    title: String,
    subtitle: String,
    checked: Boolean,
    onChecked: (Boolean) -> Unit
) {
    Row(modifier = Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
        Column(Modifier.weight(1f)) {
            Text(title, fontWeight = FontWeight.SemiBold)
            Text(
                subtitle,
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
        Switch(checked = checked, onCheckedChange = onChecked)
    }
}

@Composable
internal fun StatusRow(title: String, ok: Boolean) {
    Row(modifier = Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
        Text(title, modifier = Modifier.weight(1f))
        Text(
            if (ok) "OK" else "À autoriser",
            color = if (ok) Color(0xFF0A7B45) else MaterialTheme.colorScheme.primary,
            fontWeight = FontWeight.SemiBold
        )
    }
}

internal fun formatTime(millis: Long, withSeconds: Boolean = false): String =
    SimpleDateFormat(if (withSeconds) "HH:mm:ss" else "HH:mm", Locale.getDefault())
        .format(Date(millis))

internal fun formatDateTime(millis: Long): String =
    SimpleDateFormat("dd MMM yyyy • HH:mm", Locale.getDefault()).format(Date(millis))

internal fun dayOffsetText(offset: Int): String = when {
    offset == 0 -> "Aujourd’hui"
    offset == 1 -> "Demain"
    offset == -1 -> "Hier"
    offset > 1 -> "Dans " + offset + " jours"
    else -> "Il y a " + (-offset) + " jours"
}
