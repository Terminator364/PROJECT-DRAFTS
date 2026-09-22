package com.terminator364.timeplus

import android.content.SharedPreferences
import org.json.JSONArray
import org.json.JSONObject

data class HistoryItem(
    val expression: String,
    val result: String,
    val createdAt: Long
)

object HistoryStore {
    private const val KEY = "history_v2"
    private const val MAX_ITEMS = 24

    fun load(prefs: SharedPreferences): List<HistoryItem> {
        val raw = prefs.getString(KEY, "[]") ?: "[]"
        return runCatching {
            val array = JSONArray(raw)
            buildList {
                for (i in 0 until array.length()) {
                    val obj = array.optJSONObject(i) ?: continue
                    add(
                        HistoryItem(
                            expression = obj.optString("expression"),
                            result = obj.optString("result"),
                            createdAt = obj.optLong("createdAt")
                        )
                    )
                }
            }
        }.getOrDefault(emptyList())
    }

    fun add(prefs: SharedPreferences, item: HistoryItem): List<HistoryItem> {
        val items = (listOf(item) + load(prefs)).take(MAX_ITEMS)
        save(prefs, items)
        return items
    }

    fun clear(prefs: SharedPreferences) {
        prefs.edit().putString(KEY, "[]").apply()
    }

    private fun save(prefs: SharedPreferences, items: List<HistoryItem>) {
        val array = JSONArray()
        items.forEach {
            array.put(
                JSONObject()
                    .put("expression", it.expression)
                    .put("result", it.result)
                    .put("createdAt", it.createdAt)
            )
        }
        prefs.edit().putString(KEY, array.toString()).apply()
    }
}
