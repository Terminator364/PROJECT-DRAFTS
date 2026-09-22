package com.terminator364.timeplus

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.consumeWindowInsets
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.safeDrawing
import androidx.compose.foundation.layout.weight
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.rounded.Schedule
import androidx.compose.material.icons.rounded.Settings
import androidx.compose.material.icons.rounded.SwapHoriz
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Tab
import androidx.compose.material3.TabRow
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight

internal const val PREFS = "timeplus_prefs"
private enum class AppPage { MAIN, SETTINGS }
private enum class MainTab { CALCULATOR, DIFFERENCE }

private val TimePlusColors = lightColorScheme(
    primary = Color(0xFF2D64F6),
    onPrimary = Color.White,
    primaryContainer = Color(0xFFE8EEFF),
    onPrimaryContainer = Color(0xFF0E2C7C),
    secondary = Color(0xFF5B6785),
    background = Color(0xFFF6F8FC),
    surface = Color.White,
    surfaceVariant = Color(0xFFF0F3F9),
    outline = Color(0xFFDCE2EC)
)

open class TimePlusActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        val prefs = getSharedPreferences(PREFS, MODE_PRIVATE)
        setContent {
            MaterialTheme(colorScheme = TimePlusColors) {
                var page by rememberSaveable { mutableStateOf(AppPage.MAIN.name) }
                var history by remember { mutableStateOf(HistoryStore.load(prefs)) }
                if (page == AppPage.SETTINGS.name) {
                    SettingsScreen(
                        prefs = prefs,
                        onBack = { page = AppPage.MAIN.name },
                        onHistoryCleared = {
                            HistoryStore.clear(prefs)
                            history = emptyList()
                        }
                    )
                } else {
                    MainScreen(
                        prefs = prefs,
                        history = history,
                        onAddHistory = { item -> history = HistoryStore.add(prefs, item) },
                        onClearHistory = {
                            HistoryStore.clear(prefs)
                            history = emptyList()
                        },
                        onOpenSettings = { page = AppPage.SETTINGS.name }
                    )
                }
            }
        }
    }
}

@Composable
private fun MainScreen(
    prefs: android.content.SharedPreferences,
    history: List<HistoryItem>,
    onAddHistory: (HistoryItem) -> Unit,
    onClearHistory: () -> Unit,
    onOpenSettings: () -> Unit
) {
    var tab by rememberSaveable { mutableStateOf(MainTab.CALCULATOR.name) }

    Scaffold(
        contentWindowInsets = WindowInsets.safeDrawing,
        topBar = {
            TopAppBar(
                title = {
                    Column {
                        Text("TimePlus", fontWeight = FontWeight.Bold)
                        Text(
                            "Calcul temporel rapide",
                            style = MaterialTheme.typography.labelMedium,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                },
                actions = {
                    IconButton(onClick = onOpenSettings) {
                        Icon(Icons.Rounded.Settings, contentDescription = "Paramètres")
                    }
                }
            )
        }
    ) { inner ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(inner)
                .consumeWindowInsets(inner)
        ) {
            TabRow(selectedTabIndex = if (tab == MainTab.CALCULATOR.name) 0 else 1) {
                Tab(
                    selected = tab == MainTab.CALCULATOR.name,
                    onClick = { tab = MainTab.CALCULATOR.name },
                    text = { Text("Calcul") },
                    icon = { Icon(Icons.Rounded.Schedule, contentDescription = null) }
                )
                Tab(
                    selected = tab == MainTab.DIFFERENCE.name,
                    onClick = { tab = MainTab.DIFFERENCE.name },
                    text = { Text("Différence") },
                    icon = { Icon(Icons.Rounded.SwapHoriz, contentDescription = null) }
                )
            }

            if (tab == MainTab.CALCULATOR.name) {
                CalculatorScreen(
                    prefs = prefs,
                    history = history,
                    onAddHistory = onAddHistory,
                    onClearHistory = onClearHistory,
                    modifier = Modifier.weight(1f)
                )
            } else {
                DifferenceScreen(
                    prefs = prefs,
                    onAddHistory = onAddHistory,
                    modifier = Modifier.weight(1f)
                )
            }
        }
    }
}
