package com.terminator364.timeplus;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.media.AudioAttributes;
import android.media.RingtoneManager;
import android.net.Uri;
import android.os.Build;

public class AlarmReceiver extends BroadcastReceiver {

    public static final String EXTRA_SOUND = "sound";
    public static final String EXTRA_VIBRATE = "vibrate";
    private static final int NOTIFICATION_ID = 36410;

    @Override
    public void onReceive(Context context, Intent intent) {
        boolean sound = intent.getBooleanExtra(EXTRA_SOUND, true);
        boolean vibrate = intent.getBooleanExtra(EXTRA_VIBRATE, true);

        NotificationManager manager = (NotificationManager) context.getSystemService(Context.NOTIFICATION_SERVICE);
        if (manager == null) return;

        String channelId = channelId(sound, vibrate);
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            NotificationChannel channel = new NotificationChannel(
                    channelId,
                    "Alertes TimePlus",
                    NotificationManager.IMPORTANCE_HIGH
            );
            channel.setDescription("Alertes programmées depuis TimePlus");
            channel.enableVibration(vibrate);
            if (vibrate) channel.setVibrationPattern(new long[]{0, 350, 180, 350, 180, 650});

            if (sound) {
                Uri alarmSound = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_ALARM);
                if (alarmSound == null) alarmSound = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION);
                AudioAttributes attributes = new AudioAttributes.Builder()
                        .setUsage(AudioAttributes.USAGE_ALARM)
                        .build();
                channel.setSound(alarmSound, attributes);
            } else {
                channel.setSound(null, null);
            }
            manager.createNotificationChannel(channel);
        }

        Intent openIntent = new Intent(context, MainActivity.class)
                .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP);
        PendingIntent contentIntent = PendingIntent.getActivity(
                context,
                0,
                openIntent,
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE
        );

        Notification.Builder builder = Build.VERSION.SDK_INT >= Build.VERSION_CODES.O
                ? new Notification.Builder(context, channelId)
                : new Notification.Builder(context);

        builder.setSmallIcon(android.R.drawable.ic_lock_idle_alarm)
                .setContentTitle("TimePlus")
                .setContentText("Le moment que tu as programmé est arrivé.")
                .setContentIntent(contentIntent)
                .setAutoCancel(true)
                .setCategory(Notification.CATEGORY_ALARM)
                .setPriority(Notification.PRIORITY_HIGH);

        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.O) {
            int defaults = 0;
            if (sound) defaults |= Notification.DEFAULT_SOUND;
            if (vibrate) defaults |= Notification.DEFAULT_VIBRATE;
            builder.setDefaults(defaults);
        }

        manager.notify(NOTIFICATION_ID, builder.build());

        context.getSharedPreferences("timeplus_prefs", Context.MODE_PRIVATE)
                .edit()
                .remove("alarm_at")
                .apply();
    }

    private String channelId(boolean sound, boolean vibrate) {
        if (sound && vibrate) return "timeplus_sound_vibrate";
        if (sound) return "timeplus_sound";
        if (vibrate) return "timeplus_vibrate";
        return "timeplus_quiet";
    }
}
