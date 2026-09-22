package com.terminator364.timeplus

import java.util.Calendar
import kotlin.math.abs

enum class TimeOperation { PLUS, MINUS }

data class TimeCalculation(
    val baseMillis: Long,
    val resultMillis: Long,
    val durationMinutes: Int,
    val operation: TimeOperation,
    val dayOffset: Int
)

data class DifferenceCalculation(
    val minutes: Int,
    val crossedMidnight: Boolean
)

object TimeEngine {
    fun now(): Long = System.currentTimeMillis()

    fun todayAt(hour: Int, minute: Int, nowMillis: Long = now()): Long {
        val c = Calendar.getInstance().apply {
            timeInMillis = nowMillis
            set(Calendar.HOUR_OF_DAY, hour.coerceIn(0, 23))
            set(Calendar.MINUTE, minute.coerceIn(0, 59))
            set(Calendar.SECOND, 0)
            set(Calendar.MILLISECOND, 0)
        }
        return c.timeInMillis
    }

    fun calculate(baseMillis: Long, durationMinutes: Int, operation: TimeOperation): TimeCalculation {
        val safeDuration = durationMinutes.coerceIn(0, 9999)
        val delta = safeDuration * 60_000L * if (operation == TimeOperation.PLUS) 1L else -1L
        val result = baseMillis + delta
        return TimeCalculation(
            baseMillis = baseMillis,
            resultMillis = result,
            durationMinutes = safeDuration,
            operation = operation,
            dayOffset = dayOffset(baseMillis, result)
        )
    }

    fun difference(startHour: Int, startMinute: Int, endHour: Int, endMinute: Int, nextDayIfEarlier: Boolean): DifferenceCalculation {
        val start = startHour.coerceIn(0, 23) * 60 + startMinute.coerceIn(0, 59)
        var end = endHour.coerceIn(0, 23) * 60 + endMinute.coerceIn(0, 59)
        var crossed = false
        if (nextDayIfEarlier && end < start) {
            end += 24 * 60
            crossed = true
        }
        return DifferenceCalculation(abs(end - start), crossed)
    }

    fun dayOffset(baseMillis: Long, resultMillis: Long): Int {
        val base = Calendar.getInstance().apply {
            timeInMillis = baseMillis
            set(Calendar.HOUR_OF_DAY, 12)
            set(Calendar.MINUTE, 0)
            set(Calendar.SECOND, 0)
            set(Calendar.MILLISECOND, 0)
        }
        val result = Calendar.getInstance().apply {
            timeInMillis = resultMillis
            set(Calendar.HOUR_OF_DAY, 12)
            set(Calendar.MINUTE, 0)
            set(Calendar.SECOND, 0)
            set(Calendar.MILLISECOND, 0)
        }
        return ((result.timeInMillis - base.timeInMillis) / 86_400_000L).toInt()
    }

    fun formatDuration(totalMinutes: Int): String {
        val safe = totalMinutes.coerceAtLeast(0)
        val hours = safe / 60
        val minutes = safe % 60
        return when {
            hours == 0 -> "$minutes min"
            minutes == 0 -> "$hours h"
            else -> "$hours h $minutes min"
        }
    }

    fun parseHourMinute(text: String): Pair<Int, Int>? {
        val parts = text.trim().split(":")
        if (parts.size != 2) return null
        val h = parts[0].toIntOrNull() ?: return null
        val m = parts[1].toIntOrNull() ?: return null
        if (h !in 0..23 || m !in 0..59) return null
        return h to m
    }
}
