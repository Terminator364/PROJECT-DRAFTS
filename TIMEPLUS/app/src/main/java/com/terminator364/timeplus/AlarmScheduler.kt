package com.terminator364.timeplus

import android.app.AlarmManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.os.Build

enum class AlarmPrecision { EXACT, INEXACT }

data class AlarmScheduleResult(
    val targetMillis: Long,
    val precision: AlarmPrecision
)

object AlarmScheduler {
    const val REQUEST_CODE = 2407
    private const val PREFS = "timeplus_prefs"

    fun schedule(context: Context, targetMillis: Long, sound: Boolean, vibrate: Boolean): AlarmScheduleResult {
        val manager = context.getSystemService(Context.ALARM_SERVICE) as AlarmManager
        val intent = Intent(context, AlarmReceiver::class.java)
            .putExtra(AlarmReceiver.EXTRA_SOUND, sound)
            .putExtra(AlarmReceiver.EXTRA_VIBRATE, vibrate)
        val pending = PendingIntent.getBroadcast(
            context,
            REQUEST_CODE,
            intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        val exactAllowed = Build.VERSION.SDK_INT < Build.VERSION_CODES.S || manager.canScheduleExactAlarms()
        if (exactAllowed) {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
                manager.setExactAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, targetMillis, pending)
            } else {
                manager.setExact(AlarmManager.RTC_WAKEUP, targetMillis, pending)
            }
        } else {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
                manager.setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, targetMillis, pending)
            } else {
                manager.set(AlarmManager.RTC_WAKEUP, targetMillis, pending)
            }
        }

        context.getSharedPreferences(PREFS, Context.MODE_PRIVATE).edit()
            .putLong("alarm_at", targetMillis)
            .putBoolean("alarm_sound", sound)
            .putBoolean("alarm_vibrate", vibrate)
            .apply()

        return AlarmScheduleResult(targetMillis, if (exactAllowed) AlarmPrecision.EXACT else AlarmPrecision.INEXACT)
    }

    fun cancel(context: Context) {
        val manager = context.getSystemService(Context.ALARM_SERVICE) as AlarmManager
        val pending = PendingIntent.getBroadcast(
            context,
            REQUEST_CODE,
            Intent(context, AlarmReceiver::class.java),
            PendingIntent.FLAG_NO_CREATE or PendingIntent.FLAG_IMMUTABLE
        )
        pending?.let {
            manager.cancel(it)
            it.cancel()
        }
        context.getSharedPreferences(PREFS, Context.MODE_PRIVATE).edit().remove("alarm_at").apply()
    }
}
