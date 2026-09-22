package com.terminator364.timeplus

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent

class BootReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent?) {
        if (intent?.action != Intent.ACTION_BOOT_COMPLETED && intent?.action != Intent.ACTION_LOCKED_BOOT_COMPLETED) return
        val prefs = context.getSharedPreferences("timeplus_prefs", Context.MODE_PRIVATE)
        val target = prefs.getLong("alarm_at", 0L)
        if (target <= System.currentTimeMillis()) {
            prefs.edit().remove("alarm_at").apply()
            return
        }
        AlarmScheduler.schedule(
            context = context,
            targetMillis = target,
            sound = prefs.getBoolean("alarm_sound", true),
            vibrate = prefs.getBoolean("alarm_vibrate", true)
        )
    }
}
