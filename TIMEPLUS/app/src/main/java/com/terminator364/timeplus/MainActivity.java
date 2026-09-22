package com.terminator364.timeplus;

import android.Manifest;
import android.app.Activity;
import android.app.AlarmManager;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.provider.Settings;
import android.view.Gravity;
import android.view.View;
import android.view.inputmethod.InputMethodManager;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.Switch;
import android.widget.TextView;
import android.widget.Toast;

import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Date;
import java.util.Locale;

public class MainActivity extends Activity {
    private static final int REQ_NOTIFICATION = 1001;
    private static final int ALARM_REQUEST = 2407;
    private static final String PREFS = "timeplus_prefs";
    private static final int PRIMARY = Color.rgb(51, 102, 255);
    private static final int TEXT = Color.rgb(16, 24, 40);
    private static final int MUTED = Color.rgb(102, 112, 133);
    private static final int BG = Color.rgb(244, 247, 251);

    private final Handler handler = new Handler(Looper.getMainLooper());
    private TextView nowView, targetView, dateView, statusView;
    private EditText customMinutes;
    private Switch alertSwitch, soundSwitch, vibrateSwitch;
    private Button cancelButton;
    private int selectedMinutes = 30;
    private long targetMillis;

    private final Runnable ticker = new Runnable() {
        @Override public void run() {
            nowView.setText(new SimpleDateFormat("HH:mm:ss", Locale.getDefault()).format(new Date()));
            handler.postDelayed(this, 1000);
        }
    };

    @Override protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        getWindow().setStatusBarColor(BG);
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            getWindow().getDecorView().setSystemUiVisibility(View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR);
        }
        setContentView(buildUi());

        selectedMinutes = getSharedPreferences(PREFS, MODE_PRIVATE).getInt("minutes", 30);
        calculate(selectedMinutes);
        refreshAlarmState();
    }

    @Override protected void onResume() {
        super.onResume();
        handler.removeCallbacks(ticker);
        handler.post(ticker);
        refreshAlarmState();
    }

    @Override protected void onPause() {
        super.onPause();
        handler.removeCallbacks(ticker);
    }

    private View buildUi() {
        ScrollView scroll = new ScrollView(this);
        scroll.setBackgroundColor(BG);
        LinearLayout root = vertical();
        root.setPadding(dp(20), dp(28), dp(20), dp(28));
        scroll.addView(root, new ScrollView.LayoutParams(-1, -2));

        TextView title = text("TimePlus", 30, TEXT, true);
        root.addView(title);
        TextView subtitle = text("Ajoute une durée à maintenant, sans calcul mental.", 15, MUTED, false);
        subtitle.setPadding(0, dp(4), 0, 0);
        root.addView(subtitle);

        LinearLayout card = vertical();
        card.setPadding(dp(20), dp(18), dp(20), dp(18));
        card.setBackground(roundRect(Color.WHITE, 24, Color.rgb(228, 231, 236)));
        LinearLayout.LayoutParams cardLp = matchWrap();
        cardLp.setMargins(0, dp(22), 0, 0);
        root.addView(card, cardLp);

        card.addView(label("MAINTENANT"));
        nowView = text("--:--:--", 24, TEXT, true);
        nowView.setPadding(0, dp(4), 0, dp(18));
        card.addView(nowView);
        card.addView(label("HEURE CIBLE"));
        targetView = text("--:--", 44, PRIMARY, true);
        targetView.setPadding(0, dp(4), 0, 0);
        card.addView(targetView);
        dateView = text("Aujourd’hui • +30 min", 14, MUTED, false);
        dateView.setPadding(0, dp(2), 0, 0);
        card.addView(dateView);

        TextView quick = text("Durée rapide", 16, TEXT, true);
        quick.setPadding(0, dp(22), 0, dp(10));
        root.addView(quick);

        LinearLayout presets = new LinearLayout(this);
        presets.setOrientation(LinearLayout.HORIZONTAL);
        root.addView(presets, matchWrap());
        presets.addView(preset("+10 min", 10), weighted());
        addSpacer(presets, 8);
        presets.addView(preset("+30 min", 30), weighted());
        addSpacer(presets, 8);
        presets.addView(preset("+1 h", 60), weighted());

        customMinutes = new EditText(this);
        customMinutes.setHint("Durée personnalisée en minutes");
        customMinutes.setTextColor(TEXT);
        customMinutes.setHintTextColor(MUTED);
        customMinutes.setTextSize(16);
        customMinutes.setSingleLine(true);
        customMinutes.setInputType(android.text.InputType.TYPE_CLASS_NUMBER);
        LinearLayout.LayoutParams editLp = matchWrap();
        editLp.height = dp(56);
        editLp.setMargins(0, dp(12), 0, 0);
        root.addView(customMinutes, editLp);

        LinearLayout options = vertical();
        options.setPadding(dp(16), dp(12), dp(16), dp(12));
        options.setBackground(roundRect(Color.WHITE, 20, Color.rgb(228, 231, 236)));
        LinearLayout.LayoutParams optionsLp = matchWrap();
        optionsLp.setMargins(0, dp(18), 0, 0);
        root.addView(options, optionsLp);

        alertSwitch = switchView("Activer une alerte à l’heure cible", false);
        soundSwitch = switchView("Son", true);
        vibrateSwitch = switchView("Vibration", true);
        options.addView(alertSwitch);
        options.addView(soundSwitch);
        options.addView(vibrateSwitch);
        soundSwitch.setEnabled(false);
        vibrateSwitch.setEnabled(false);
        alertSwitch.setOnCheckedChangeListener((button, checked) -> {
            soundSwitch.setEnabled(checked);
            vibrateSwitch.setEnabled(checked);
        });

        Button calculate = actionButton("Calculer maintenant", true);
        LinearLayout.LayoutParams actionLp = matchWrap();
        actionLp.height = dp(56);
        actionLp.setMargins(0, dp(18), 0, 0);
        root.addView(calculate, actionLp);
        calculate.setOnClickListener(v -> calculateFromInput());

        Button schedule = actionButton("Programmer l’alerte", false);
        LinearLayout.LayoutParams scheduleLp = matchWrap();
        scheduleLp.height = dp(56);
        scheduleLp.setMargins(0, dp(10), 0, 0);
        root.addView(schedule, scheduleLp);
        schedule.setOnClickListener(v -> scheduleAlarm());

        cancelButton = new Button(this);
        cancelButton.setText("Annuler l’alerte programmée");
        cancelButton.setTextColor(MUTED);
        cancelButton.setTextSize(14);
        cancelButton.setAllCaps(false);
        cancelButton.setBackgroundColor(Color.TRANSPARENT);
        cancelButton.setVisibility(View.GONE);
        root.addView(cancelButton, matchWrap());
        cancelButton.setOnClickListener(v -> cancelAlarm());

        statusView = text("Prêt", 13, MUTED, false);
        statusView.setGravity(Gravity.CENTER);
        statusView.setPadding(0, dp(8), 0, 0);
        root.addView(statusView, matchWrap());
        return scroll;
    }

    private void calculateFromInput() {
        int value = readMinutes();
        if (value < 1) return;
        selectedMinutes = value;
        getSharedPreferences(PREFS, MODE_PRIVATE).edit().putInt("minutes", value).apply();
        calculate(value);
        statusView.setText("Calcul mis à jour");
        hideKeyboard();
    }

    private void calculate(int minutes) {
        targetMillis = System.currentTimeMillis() + minutes * 60_000L;
        targetView.setText(new SimpleDateFormat("HH:mm", Locale.getDefault()).format(new Date(targetMillis)));
        Calendar now = Calendar.getInstance();
        Calendar target = Calendar.getInstance();
        target.setTimeInMillis(targetMillis);
        boolean sameDay = now.get(Calendar.YEAR) == target.get(Calendar.YEAR)
                && now.get(Calendar.DAY_OF_YEAR) == target.get(Calendar.DAY_OF_YEAR);
        String day = sameDay ? "Aujourd’hui" : new SimpleDateFormat("EEE d MMM", Locale.getDefault()).format(new Date(targetMillis));
        dateView.setText(day + " • +" + prettyDuration(minutes));
    }

    private void scheduleAlarm() {
        int value = readMinutes();
        if (value < 1) return;
        selectedMinutes = value;
        calculate(value);

        if (!alertSwitch.isChecked()) {
            statusView.setText("Calcul prêt — alerte désactivée");
            Toast.makeText(this, "Active d’abord l’alerte.", Toast.LENGTH_SHORT).show();
            return;
        }
        if (Build.VERSION.SDK_INT >= 33 && checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {
            requestPermissions(new String[]{Manifest.permission.POST_NOTIFICATIONS}, REQ_NOTIFICATION);
            Toast.makeText(this, "Autorise les notifications puis relance l’alerte.", Toast.LENGTH_LONG).show();
            return;
        }

        AlarmManager manager = (AlarmManager) getSystemService(Context.ALARM_SERVICE);
        if (manager == null) return;
        Intent intent = new Intent(this, AlarmReceiver.class)
                .putExtra(AlarmReceiver.EXTRA_SOUND, soundSwitch.isChecked())
                .putExtra(AlarmReceiver.EXTRA_VIBRATE, vibrateSwitch.isChecked());
        PendingIntent pi = PendingIntent.getBroadcast(this, ALARM_REQUEST, intent,
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);

        boolean exact = true;
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S && !manager.canScheduleExactAlarms()) {
            exact = false;
            try {
                startActivity(new Intent(Settings.ACTION_REQUEST_SCHEDULE_EXACT_ALARM,
                        Uri.parse("package:" + getPackageName())));
            } catch (Exception ignored) { }
        }
        if (exact) {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) manager.setExactAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, targetMillis, pi);
            else manager.setExact(AlarmManager.RTC_WAKEUP, targetMillis, pi);
        } else {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) manager.setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, targetMillis, pi);
            else manager.set(AlarmManager.RTC_WAKEUP, targetMillis, pi);
        }

        getSharedPreferences(PREFS, MODE_PRIVATE).edit()
                .putLong("alarm_at", targetMillis)
                .putInt("minutes", value)
                .apply();
        cancelButton.setVisibility(View.VISIBLE);
        String time = new SimpleDateFormat("HH:mm", Locale.getDefault()).format(new Date(targetMillis));
        statusView.setText(exact ? "Alerte programmée pour " + time : "Alerte programmée pour ~" + time + " • autorise ‘Alarmes et rappels’ pour l’exactitude");
        Toast.makeText(this, "Alerte programmée", Toast.LENGTH_SHORT).show();
    }

    private void cancelAlarm() {
        AlarmManager manager = (AlarmManager) getSystemService(Context.ALARM_SERVICE);
        PendingIntent pi = PendingIntent.getBroadcast(this, ALARM_REQUEST, new Intent(this, AlarmReceiver.class),
                PendingIntent.FLAG_NO_CREATE | PendingIntent.FLAG_IMMUTABLE);
        if (manager != null && pi != null) {
            manager.cancel(pi);
            pi.cancel();
        }
        getSharedPreferences(PREFS, MODE_PRIVATE).edit().remove("alarm_at").apply();
        cancelButton.setVisibility(View.GONE);
        statusView.setText("Alerte annulée");
    }

    private void refreshAlarmState() {
        if (statusView == null) return;
        SharedPreferences prefs = getSharedPreferences(PREFS, MODE_PRIVATE);
        long at = prefs.getLong("alarm_at", 0L);
        if (at > System.currentTimeMillis()) {
            cancelButton.setVisibility(View.VISIBLE);
            statusView.setText("Alerte active pour " + new SimpleDateFormat("HH:mm", Locale.getDefault()).format(new Date(at)));
        } else {
            cancelButton.setVisibility(View.GONE);
            if (at != 0L) prefs.edit().remove("alarm_at").apply();
        }
    }

    private int readMinutes() {
        String raw = customMinutes.getText().toString().trim();
        if (raw.isEmpty()) return selectedMinutes;
        try {
            int value = Integer.parseInt(raw);
            if (value < 1 || value > 9999) throw new NumberFormatException();
            return value;
        } catch (NumberFormatException e) {
            customMinutes.setError("Entre 1 et 9999 minutes");
            return -1;
        }
    }

    private Button preset(String label, int minutes) {
        Button b = actionButton(label, false);
        b.setOnClickListener(v -> {
            selectedMinutes = minutes;
            customMinutes.setText("");
            calculate(minutes);
            hideKeyboard();
        });
        return b;
    }

    private Button actionButton(String label, boolean primary) {
        Button b = new Button(this);
        b.setText(label);
        b.setAllCaps(false);
        b.setTextSize(15);
        b.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        b.setTextColor(primary ? Color.WHITE : PRIMARY);
        b.setBackground(roundRect(primary ? PRIMARY : Color.rgb(245, 247, 255), 16, primary ? PRIMARY : Color.rgb(183, 197, 255)));
        return b;
    }

    private Switch switchView(String label, boolean checked) {
        Switch s = new Switch(this);
        s.setText(label);
        s.setTextColor(TEXT);
        s.setTextSize(15);
        s.setChecked(checked);
        s.setPadding(0, dp(4), 0, dp(4));
        return s;
    }

    private TextView label(String value) {
        TextView v = text(value, 12, MUTED, true);
        v.setLetterSpacing(0.08f);
        return v;
    }

    private TextView text(String value, int sp, int color, boolean bold) {
        TextView v = new TextView(this);
        v.setText(value);
        v.setTextSize(sp);
        v.setTextColor(color);
        if (bold) v.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        return v;
    }

    private LinearLayout vertical() {
        LinearLayout l = new LinearLayout(this);
        l.setOrientation(LinearLayout.VERTICAL);
        return l;
    }

    private LinearLayout.LayoutParams matchWrap() {
        return new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT);
    }

    private LinearLayout.LayoutParams weighted() {
        return new LinearLayout.LayoutParams(0, dp(52), 1f);
    }

    private void addSpacer(LinearLayout parent, int widthDp) {
        SpaceCompat spacer = new SpaceCompat(this);
        parent.addView(spacer, new LinearLayout.LayoutParams(dp(widthDp), 1));
    }

    private GradientDrawable roundRect(int fill, int radiusDp, int stroke) {
        GradientDrawable d = new GradientDrawable();
        d.setColor(fill);
        d.setCornerRadius(dp(radiusDp));
        d.setStroke(dp(1), stroke);
        return d;
    }

    private String prettyDuration(int minutes) {
        if (minutes % 60 == 0) return (minutes / 60) + " h";
        if (minutes > 60) return (minutes / 60) + " h " + (minutes % 60) + " min";
        return minutes + " min";
    }

    private int dp(int value) {
        return Math.round(value * getResources().getDisplayMetrics().density);
    }

    private void hideKeyboard() {
        View current = getCurrentFocus();
        if (current == null) return;
        InputMethodManager imm = (InputMethodManager) getSystemService(Context.INPUT_METHOD_SERVICE);
        if (imm != null) imm.hideSoftInputFromWindow(current.getWindowToken(), 0);
        current.clearFocus();
    }

    private static class SpaceCompat extends View {
        SpaceCompat(Context context) { super(context); }
    }
}
