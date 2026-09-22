package com.terminator364.timeplus;

import android.Manifest;
import android.app.Activity;
import android.app.AlarmManager;
import android.app.PendingIntent;
import android.app.TimePickerDialog;
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
import android.text.InputType;
import android.view.Gravity;
import android.view.View;
import android.view.inputmethod.InputMethodManager;
import android.widget.Button;
import android.widget.EditText;
import android.widget.HorizontalScrollView;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.SeekBar;
import android.widget.Space;
import android.widget.Switch;
import android.widget.TextView;
import android.widget.Toast;

import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Date;
import java.util.Locale;

public class TimePlusActivity extends Activity {
    static final String PREFS = "timeplus_prefs";
    private static final int REQ_NOTIFICATION = 1001;
    private static final int ALARM_REQUEST = 2407;

    private static final int BLUE = Color.rgb(45, 100, 246);
    private static final int BLUE_DARK = Color.rgb(25, 70, 220);
    private static final int TEXT = Color.rgb(17, 24, 39);
    private static final int MUTED = Color.rgb(103, 115, 139);
    private static final int BG = Color.rgb(246, 248, 252);
    private static final int BORDER = Color.rgb(224, 229, 238);
    private static final int SOFT_BLUE = Color.rgb(239, 244, 255);

    private final Handler tickerHandler = new Handler(Looper.getMainLooper());
    private TextView baseLabel, baseTime, baseMeta, targetTime, targetMeta, summaryHint, durationValue, status;
    private EditText durationInput, manualTimeInput;
    private Button nowMode, manualMode, chooseTime, cancelAlarm;
    private Switch alertSwitch, soundSwitch, vibrationSwitch;
    private SeekBar durationSeek;

    private int minutes = 30;
    private int manualHour;
    private int manualMinute;
    private boolean useManualStart;
    private long alarmTargetMillis;

    private final Runnable ticker = new Runnable() {
        @Override public void run() {
            if (!useManualStart && baseTime != null) {
                baseTime.setText(new SimpleDateFormat("HH:mm:ss", Locale.getDefault()).format(new Date()));
                calculate(false);
            }
            tickerHandler.postDelayed(this, 1000L);
        }
    };

    @Override protected void onCreate(Bundle state) {
        super.onCreate(state);
        getWindow().setStatusBarColor(BG);
        if (Build.VERSION.SDK_INT >= 23) {
            getWindow().getDecorView().setSystemUiVisibility(View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR);
        }

        SharedPreferences p = prefs();
        Calendar now = Calendar.getInstance();
        minutes = clamp(p.getInt("minutes", 30), 1, 9999);
        manualHour = p.getInt("manual_hour", now.get(Calendar.HOUR_OF_DAY));
        manualMinute = p.getInt("manual_minute", now.get(Calendar.MINUTE));
        useManualStart = p.getBoolean("manual_mode", false);

        setContentView(buildUi());
        alertSwitch.setChecked(p.getBoolean("default_alert", false));
        soundSwitch.setChecked(p.getBoolean("default_sound", true));
        vibrationSwitch.setChecked(p.getBoolean("default_vibrate", true));
        updateAlertDependencies();
        applyModeUi();
        setMinutes(minutes, true);
        refreshAlarmState();
    }

    @Override protected void onResume() {
        super.onResume();
        tickerHandler.removeCallbacks(ticker);
        tickerHandler.post(ticker);
        SharedPreferences p = prefs();
        alertSwitch.setChecked(p.getBoolean("default_alert", alertSwitch.isChecked()));
        soundSwitch.setChecked(p.getBoolean("default_sound", soundSwitch.isChecked()));
        vibrationSwitch.setChecked(p.getBoolean("default_vibrate", vibrationSwitch.isChecked()));
        updateAlertDependencies();
        refreshAlarmState();
    }

    @Override protected void onPause() {
        super.onPause();
        tickerHandler.removeCallbacks(ticker);
    }

    private View buildUi() {
        ScrollView scroll = new ScrollView(this);
        scroll.setFillViewport(true);
        scroll.setBackgroundColor(BG);

        LinearLayout root = column();
        root.setPadding(dp(16), statusBarInset() + dp(10), dp(16), navBarInset() + dp(28));
        scroll.addView(root, new ScrollView.LayoutParams(-1, -2));

        root.addView(header());
        root.addView(modeCard(), marginTop(14));
        root.addView(summaryCard(), marginTop(14));
        root.addView(quickSection(), marginTop(18));
        root.addView(durationCard(), marginTop(16));
        root.addView(alertCard(), marginTop(16));
        root.addView(actionRow(), marginTop(16));

        status = text("Prêt", 13, MUTED, false);
        status.setGravity(Gravity.CENTER);
        root.addView(status, marginTop(10));
        return scroll;
    }

    private View header() {
        LinearLayout row = new LinearLayout(this);
        row.setOrientation(LinearLayout.HORIZONTAL);
        row.setGravity(Gravity.CENTER_VERTICAL);

        ImageView logo = new ImageView(this);
        logo.setImageResource(getApplicationInfo().icon);
        logo.setScaleType(ImageView.ScaleType.CENTER_CROP);
        row.addView(logo, new LinearLayout.LayoutParams(dp(44), dp(44)));

        LinearLayout titles = column();
        LinearLayout.LayoutParams titlesLp = new LinearLayout.LayoutParams(0, -2, 1f);
        titlesLp.setMargins(dp(12), 0, dp(10), 0);
        row.addView(titles, titlesLp);
        titles.addView(text("TimePlus", 24, TEXT, true));
        titles.addView(text("Calcule ton heure cible, simplement.", 12, MUTED, false));

        Button settings = iconButton("⚙");
        settings.setContentDescription("Paramètres");
        settings.setOnClickListener(v -> startActivity(new Intent(this, SettingsActivity.class)));
        row.addView(settings, new LinearLayout.LayoutParams(dp(44), dp(44)));
        return row;
    }

    private View modeCard() {
        LinearLayout card = card();
        card.setPadding(dp(10), dp(10), dp(10), dp(10));

        LinearLayout tabs = new LinearLayout(this);
        tabs.setOrientation(LinearLayout.HORIZONTAL);
        nowMode = button("Maintenant", true);
        manualMode = button("Départ", false);
        tabs.addView(nowMode, new LinearLayout.LayoutParams(0, dp(46), 1f));
        tabs.addView(space(dp(8), 1));
        tabs.addView(manualMode, new LinearLayout.LayoutParams(0, dp(46), 1f));
        card.addView(tabs, matchWrap());

        LinearLayout manualRow = new LinearLayout(this);
        manualRow.setOrientation(LinearLayout.HORIZONTAL);
        manualRow.setGravity(Gravity.CENTER_VERTICAL);
        LinearLayout.LayoutParams manualLp = matchWrap();
        manualLp.setMargins(0, dp(8), 0, 0);
        card.addView(manualRow, manualLp);

        manualTimeInput = new EditText(this);
        manualTimeInput.setTextColor(TEXT);
        manualTimeInput.setHintTextColor(MUTED);
        manualTimeInput.setTextSize(17);
        manualTimeInput.setSingleLine(true);
        manualTimeInput.setHint("HH:mm");
        manualTimeInput.setInputType(InputType.TYPE_CLASS_DATETIME | InputType.TYPE_DATETIME_VARIATION_TIME);
        manualTimeInput.setBackground(roundRect(Color.WHITE, 14, BORDER));
        manualTimeInput.setPadding(dp(14), 0, dp(14), 0);
        manualRow.addView(manualTimeInput, new LinearLayout.LayoutParams(0, dp(48), 1f));

        manualRow.addView(space(dp(8), 1));
        chooseTime = button("Choisir", false);
        manualRow.addView(chooseTime, new LinearLayout.LayoutParams(dp(100), dp(48)));

        nowMode.setOnClickListener(v -> setManualMode(false));
        manualMode.setOnClickListener(v -> setManualMode(true));
        chooseTime.setOnClickListener(v -> showTimePicker());
        manualTimeInput.setOnEditorActionListener((v, actionId, event) -> {
            applyTypedStartTime();
            return true;
        });
        manualTimeInput.setOnFocusChangeListener((v, hasFocus) -> {
            if (!hasFocus && useManualStart) applyTypedStartTime();
        });
        return card;
    }

    private View summaryCard() {
        LinearLayout card = card();
        card.setPadding(dp(16), dp(16), dp(16), dp(16));

        LinearLayout startBlock = infoBlock("MAINTENANT", "--:--:--", "");
        baseLabel = (TextView) startBlock.getChildAt(0);
        baseTime = (TextView) startBlock.getChildAt(1);
        baseMeta = (TextView) startBlock.getChildAt(2);
        card.addView(startBlock, matchWrap());

        View divider = new View(this);
        divider.setBackgroundColor(BORDER);
        LinearLayout.LayoutParams dividerLp = new LinearLayout.LayoutParams(-1, dp(1));
        dividerLp.setMargins(0, dp(12), 0, dp(12));
        card.addView(divider, dividerLp);

        LinearLayout targetBlock = infoBlock("HEURE CIBLE", "--:--", "");
        targetTime = (TextView) targetBlock.getChildAt(1);
        targetTime.setTextColor(BLUE);
        targetTime.setTextSize(32);
        targetMeta = (TextView) targetBlock.getChildAt(2);
        card.addView(targetBlock, matchWrap());

        summaryHint = text("", 15, BLUE_DARK, true);
        summaryHint.setBackground(roundRect(SOFT_BLUE, 14, Color.rgb(220, 231, 255)));
        summaryHint.setPadding(dp(14), dp(12), dp(14), dp(12));
        card.addView(summaryHint, marginTop(14));
        return card;
    }

    private View quickSection() {
        LinearLayout section = column();
        section.addView(text("Durée rapide", 17, TEXT, true));
        section.addView(text("Raccourcis pour les valeurs les plus courantes.", 12, MUTED, false), marginTop(4));

        HorizontalScrollView scroller = new HorizontalScrollView(this);
        scroller.setHorizontalScrollBarEnabled(false);
        LinearLayout chips = new LinearLayout(this);
        chips.setOrientation(LinearLayout.HORIZONTAL);
        chips.setPadding(0, dp(10), 0, 0);
        scroller.addView(chips);
        addQuick(chips, "+10 min", 10);
        addQuick(chips, "+30 min", 30);
        addQuick(chips, "+1 h", 60);
        section.addView(scroller, matchWrap());
        return section;
    }

    private View durationCard() {
        LinearLayout card = card();
        card.setPadding(dp(16), dp(16), dp(16), dp(16));
        card.addView(text("Durée personnalisée", 17, TEXT, true));

        LinearLayout stepper = new LinearLayout(this);
        stepper.setGravity(Gravity.CENTER_VERTICAL);
        Button minus = circleButton("−");
        Button plus = circleButton("+");
        durationValue = text("30", 30, BLUE_DARK, true);
        durationValue.setGravity(Gravity.CENTER);
        durationValue.setBackground(roundRect(SOFT_BLUE, 18, BORDER));
        stepper.addView(minus, new LinearLayout.LayoutParams(dp(52), dp(52)));
        LinearLayout.LayoutParams valueLp = new LinearLayout.LayoutParams(0, dp(76), 1f);
        valueLp.setMargins(dp(14), 0, dp(14), 0);
        stepper.addView(durationValue, valueLp);
        stepper.addView(plus, new LinearLayout.LayoutParams(dp(52), dp(52)));
        card.addView(stepper, marginTop(12));

        durationSeek = new SeekBar(this);
        durationSeek.setMax(239);
        card.addView(durationSeek, marginTop(10));

        durationInput = new EditText(this);
        durationInput.setSingleLine(true);
        durationInput.setHint("Ou tape un nombre de minutes");
        durationInput.setInputType(InputType.TYPE_CLASS_NUMBER);
        durationInput.setTextColor(TEXT);
        durationInput.setHintTextColor(MUTED);
        durationInput.setTextSize(15);
        durationInput.setBackground(roundRect(Color.WHITE, 14, BORDER));
        durationInput.setPadding(dp(14), 0, dp(14), 0);
        LinearLayout.LayoutParams inputLp = marginTop(8);
        inputLp.height = dp(48);
        card.addView(durationInput, inputLp);

        minus.setOnClickListener(v -> setMinutes(Math.max(1, minutes - 1), true));
        plus.setOnClickListener(v -> setMinutes(Math.min(9999, minutes + 1), true));
        durationSeek.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
            @Override public void onProgressChanged(SeekBar bar, int progress, boolean fromUser) {
                if (fromUser) setMinutes(progress + 1, false);
            }
            @Override public void onStartTrackingTouch(SeekBar bar) { }
            @Override public void onStopTrackingTouch(SeekBar bar) { calculate(false); }
        });
        return card;
    }

    private View alertCard() {
        LinearLayout card = card();
        card.setPadding(dp(16), dp(16), dp(16), dp(16));
        card.addView(text("Options d’alerte", 17, TEXT, true));

        alertSwitch = switchRow("Activer une alerte", false);
        soundSwitch = switchRow("Son", true);
        vibrationSwitch = switchRow("Vibration", true);
        card.addView(alertSwitch, marginTop(10));
        card.addView(soundSwitch, marginTop(4));
        card.addView(vibrationSwitch, marginTop(4));

        alertSwitch.setOnCheckedChangeListener((v, checked) -> {
            prefs().edit().putBoolean("default_alert", checked).apply();
            updateAlertDependencies();
        });
        soundSwitch.setOnCheckedChangeListener((v, checked) -> prefs().edit().putBoolean("default_sound", checked).apply());
        vibrationSwitch.setOnCheckedChangeListener((v, checked) -> prefs().edit().putBoolean("default_vibrate", checked).apply());
        return card;
    }

    private View actionRow() {
        LinearLayout block = column();

        Button calculate = button("Calculer", true);
        LinearLayout.LayoutParams calcLp = matchWrap();
        calcLp.height = dp(54);
        block.addView(calculate, calcLp);

        Button schedule = button("Programmer l’alerte", false);
        LinearLayout.LayoutParams schedLp = marginTop(10);
        schedLp.height = dp(54);
        block.addView(schedule, schedLp);

        cancelAlarm = new Button(this);
        cancelAlarm.setText("Annuler l’alerte programmée");
        cancelAlarm.setAllCaps(false);
        cancelAlarm.setTextColor(MUTED);
        cancelAlarm.setBackgroundColor(Color.TRANSPARENT);
        cancelAlarm.setVisibility(View.GONE);
        block.addView(cancelAlarm, marginTop(4));

        calculate.setOnClickListener(v -> {
            if (!readDurationInput()) return;
            if (useManualStart && !applyTypedStartTime()) return;
            calculate(true);
            hideKeyboard();
            status.setText("Calcul mis à jour");
        });
        schedule.setOnClickListener(v -> scheduleAlarm());
        cancelAlarm.setOnClickListener(v -> cancelAlarm());
        return block;
    }

    private void addQuick(LinearLayout row, String label, int value) {
        Button b = button(label, value == minutes);
        b.setPadding(dp(20), 0, dp(20), 0);
        LinearLayout.LayoutParams p = new LinearLayout.LayoutParams(-2, dp(48));
        if (row.getChildCount() > 0) p.setMargins(dp(8), 0, 0, 0);
        row.addView(b, p);
        b.setOnClickListener(v -> setMinutes(value, true));
    }

    private void setManualMode(boolean manual) {
        useManualStart = manual;
        prefs().edit().putBoolean("manual_mode", manual).apply();
        applyModeUi();
        calculate(false);
    }

    private void applyModeUi() {
        if (nowMode == null) return;
        styleSelected(nowMode, !useManualStart);
        styleSelected(manualMode, useManualStart);
        View manualRow = (View) manualTimeInput.getParent();
        manualRow.setVisibility(useManualStart ? View.VISIBLE : View.GONE);
        manualTimeInput.setText(String.format(Locale.getDefault(), "%02d:%02d", manualHour, manualMinute));
        baseLabel.setText(useManualStart ? "HEURE DE DÉPART" : "MAINTENANT");
    }

    private boolean applyTypedStartTime() {
        String raw = manualTimeInput.getText().toString().trim();
        String[] parts = raw.split(":");
        if (parts.length != 2) {
            manualTimeInput.setError("Format HH:mm");
            return false;
        }
        try {
            int h = Integer.parseInt(parts[0]);
            int m = Integer.parseInt(parts[1]);
            if (h < 0 || h > 23 || m < 0 || m > 59) throw new NumberFormatException();
            manualHour = h;
            manualMinute = m;
            prefs().edit().putInt("manual_hour", h).putInt("manual_minute", m).apply();
            manualTimeInput.setText(String.format(Locale.getDefault(), "%02d:%02d", h, m));
            calculate(false);
            return true;
        } catch (NumberFormatException e) {
            manualTimeInput.setError("Heure invalide");
            return false;
        }
    }

    private void showTimePicker() {
        new TimePickerDialog(this, (view, h, m) -> {
            manualHour = h;
            manualMinute = m;
            manualTimeInput.setText(String.format(Locale.getDefault(), "%02d:%02d", h, m));
            prefs().edit().putInt("manual_hour", h).putInt("manual_minute", m).apply();
            calculate(false);
        }, manualHour, manualMinute, true).show();
    }

    private void setMinutes(int value, boolean syncInput) {
        minutes = clamp(value, 1, 9999);
        prefs().edit().putInt("minutes", minutes).apply();
        if (durationValue != null) durationValue.setText(minutes + "\nmin");
        if (durationSeek != null) durationSeek.setProgress(Math.min(239, minutes - 1));
        if (syncInput && durationInput != null) durationInput.setText(String.valueOf(minutes));
        calculate(false);
    }

    private boolean readDurationInput() {
        String raw = durationInput.getText().toString().trim();
        if (raw.isEmpty()) return true;
        try {
            int v = Integer.parseInt(raw);
            if (v < 1 || v > 9999) throw new NumberFormatException();
            setMinutes(v, true);
            return true;
        } catch (NumberFormatException e) {
            durationInput.setError("Entre 1 et 9999 minutes");
            return false;
        }
    }

    private void calculate(boolean explicit) {
        Calendar base = Calendar.getInstance();
        if (useManualStart) {
            base.set(Calendar.HOUR_OF_DAY, manualHour);
            base.set(Calendar.MINUTE, manualMinute);
            base.set(Calendar.SECOND, 0);
            base.set(Calendar.MILLISECOND, 0);
            baseTime.setText(String.format(Locale.getDefault(), "%02d:%02d", manualHour, manualMinute));
            baseMeta.setText("Heure choisie");
        } else {
            baseTime.setText(new SimpleDateFormat("HH:mm:ss", Locale.getDefault()).format(base.getTime()));
            baseMeta.setText(new SimpleDateFormat("EEE d MMM", Locale.getDefault()).format(base.getTime()));
        }

        Calendar target = (Calendar) base.clone();
        target.add(Calendar.MINUTE, minutes);
        targetTime.setText(new SimpleDateFormat("HH:mm", Locale.getDefault()).format(target.getTime()));
        boolean sameDay = base.get(Calendar.YEAR) == target.get(Calendar.YEAR)
                && base.get(Calendar.DAY_OF_YEAR) == target.get(Calendar.DAY_OF_YEAR);
        targetMeta.setText((useManualStart ? (sameDay ? "Même jour" : "Jour suivant")
                : (sameDay ? "Aujourd’hui" : "Jour suivant")) + " • +" + pretty(minutes));
        summaryHint.setText(useManualStart
                ? String.format(Locale.getDefault(), "Depuis %02d:%02d → %s", manualHour, manualMinute,
                new SimpleDateFormat("HH:mm", Locale.getDefault()).format(target.getTime()))
                : "Dans " + pretty(minutes));
        if (explicit) status.setText("Résultat calculé");
    }

    private long nextAlarmMillis() {
        if (!useManualStart) return System.currentTimeMillis() + minutes * 60_000L;
        Calendar target = Calendar.getInstance();
        target.set(Calendar.HOUR_OF_DAY, manualHour);
        target.set(Calendar.MINUTE, manualMinute);
        target.set(Calendar.SECOND, 0);
        target.set(Calendar.MILLISECOND, 0);
        target.add(Calendar.MINUTE, minutes);
        if (target.getTimeInMillis() <= System.currentTimeMillis()) target.add(Calendar.DAY_OF_YEAR, 1);
        return target.getTimeInMillis();
    }

    private void scheduleAlarm() {
        if (!readDurationInput()) return;
        if (useManualStart && !applyTypedStartTime()) return;
        calculate(false);
        if (!alertSwitch.isChecked()) {
            Toast.makeText(this, "Active d’abord l’alerte.", Toast.LENGTH_SHORT).show();
            return;
        }
        if (Build.VERSION.SDK_INT >= 33 && checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {
            requestPermissions(new String[]{Manifest.permission.POST_NOTIFICATIONS}, REQ_NOTIFICATION);
            Toast.makeText(this, "Autorise les notifications puis réessaie.", Toast.LENGTH_LONG).show();
            return;
        }

        alarmTargetMillis = nextAlarmMillis();
        AlarmManager manager = (AlarmManager) getSystemService(Context.ALARM_SERVICE);
        if (manager == null) return;
        Intent intent = new Intent(this, AlarmReceiver.class)
                .putExtra(AlarmReceiver.EXTRA_SOUND, soundSwitch.isChecked())
                .putExtra(AlarmReceiver.EXTRA_VIBRATE, vibrationSwitch.isChecked());
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
            if (Build.VERSION.SDK_INT >= 23) manager.setExactAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, alarmTargetMillis, pi);
            else manager.setExact(AlarmManager.RTC_WAKEUP, alarmTargetMillis, pi);
        } else {
            if (Build.VERSION.SDK_INT >= 23) manager.setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, alarmTargetMillis, pi);
            else manager.set(AlarmManager.RTC_WAKEUP, alarmTargetMillis, pi);
        }

        prefs().edit().putLong("alarm_at", alarmTargetMillis).apply();
        cancelAlarm.setVisibility(View.VISIBLE);
        String when = new SimpleDateFormat("HH:mm", Locale.getDefault()).format(new Date(alarmTargetMillis));
        status.setText((exact ? "Alerte " : "Alerte ~") + when);
        Toast.makeText(this, "Alerte programmée pour " + when, Toast.LENGTH_SHORT).show();
    }

    private void cancelAlarm() {
        AlarmManager manager = (AlarmManager) getSystemService(Context.ALARM_SERVICE);
        PendingIntent pi = PendingIntent.getBroadcast(this, ALARM_REQUEST, new Intent(this, AlarmReceiver.class),
                PendingIntent.FLAG_NO_CREATE | PendingIntent.FLAG_IMMUTABLE);
        if (manager != null && pi != null) manager.cancel(pi);
        prefs().edit().remove("alarm_at").apply();
        cancelAlarm.setVisibility(View.GONE);
        status.setText("Alerte annulée");
    }

    private void refreshAlarmState() {
        if (status == null) return;
        long at = prefs().getLong("alarm_at", 0L);
        if (at > System.currentTimeMillis()) {
            cancelAlarm.setVisibility(View.VISIBLE);
            status.setText("Alerte active • " + new SimpleDateFormat("HH:mm", Locale.getDefault()).format(new Date(at)));
        } else {
            cancelAlarm.setVisibility(View.GONE);
            if (at != 0L) prefs().edit().remove("alarm_at").apply();
        }
    }

    private void updateAlertDependencies() {
        boolean enabled = alertSwitch.isChecked();
        soundSwitch.setEnabled(enabled);
        vibrationSwitch.setEnabled(enabled);
    }

    private SharedPreferences prefs() { return getSharedPreferences(PREFS, MODE_PRIVATE); }
    private int clamp(int v, int min, int max) { return Math.max(min, Math.min(max, v)); }

    private String pretty(int value) {
        if (value < 60) return value + " min";
        if (value % 60 == 0) return (value / 60) + " h";
        return (value / 60) + " h " + (value % 60) + " min";
    }

    private void hideKeyboard() {
        View focused = getCurrentFocus();
        if (focused == null) return;
        InputMethodManager imm = (InputMethodManager) getSystemService(Context.INPUT_METHOD_SERVICE);
        if (imm != null) imm.hideSoftInputFromWindow(focused.getWindowToken(), 0);
        focused.clearFocus();
    }

    private int statusBarInset() {
        int id = getResources().getIdentifier("status_bar_height", "dimen", "android");
        return id > 0 ? getResources().getDimensionPixelSize(id) : dp(24);
    }

    private int navBarInset() {
        int id = getResources().getIdentifier("navigation_bar_height", "dimen", "android");
        return id > 0 ? getResources().getDimensionPixelSize(id) : dp(10);
    }

    private LinearLayout infoBlock(String title, String value, String meta) {
        LinearLayout block = column();
        TextView t1 = label(title);
        TextView t2 = text(value, 28, TEXT, true);
        TextView t3 = text(meta, 13, MUTED, false);
        t3.setPadding(0, dp(6), 0, 0);
        block.addView(t1);
        block.addView(t2);
        block.addView(t3);
        return block;
    }

    private Button iconButton(String value) {
        Button b = new Button(this);
        b.setText(value);
        b.setAllCaps(false);
        b.setTextSize(18);
        b.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        b.setTextColor(BLUE_DARK);
        b.setBackground(roundRect(Color.WHITE, 14, Color.rgb(190, 204, 244)));
        return b;
    }

    private LinearLayout column() {
        LinearLayout v = new LinearLayout(this);
        v.setOrientation(LinearLayout.VERTICAL);
        return v;
    }

    private LinearLayout card() {
        LinearLayout v = column();
        v.setBackground(roundRect(Color.WHITE, 20, BORDER));
        return v;
    }

    private TextView text(String value, int sp, int color, boolean bold) {
        TextView t = new TextView(this);
        t.setText(value);
        t.setTextSize(sp);
        t.setTextColor(color);
        if (bold) t.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        return t;
    }

    private TextView label(String value) {
        TextView t = text(value, 11, MUTED, true);
        t.setLetterSpacing(.06f);
        return t;
    }

    private Button button(String value, boolean selected) {
        Button b = new Button(this);
        b.setText(value);
        b.setAllCaps(false);
        b.setTextSize(14);
        b.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        styleSelected(b, selected);
        return b;
    }

    private Button circleButton(String value) {
        Button b = button(value, false);
        b.setTextSize(23);
        b.setBackground(roundRect(Color.WHITE, 999, BORDER));
        return b;
    }

    private Switch switchRow(String value, boolean checked) {
        Switch s = new Switch(this);
        s.setText(value);
        s.setTextSize(15);
        s.setTextColor(TEXT);
        s.setChecked(checked);
        s.setPadding(0, dp(3), 0, dp(3));
        return s;
    }

    private void styleSelected(Button b, boolean selected) {
        b.setTextColor(selected ? Color.WHITE : BLUE_DARK);
        b.setBackground(roundRect(selected ? BLUE : Color.WHITE, 14, selected ? BLUE_DARK : Color.rgb(190, 204, 244)));
    }

    private GradientDrawable roundRect(int fill, int radius, int stroke) {
        GradientDrawable d = new GradientDrawable();
        d.setColor(fill);
        d.setCornerRadius(dp(radius));
        d.setStroke(dp(1), stroke);
        return d;
    }

    private LinearLayout.LayoutParams matchWrap() { return new LinearLayout.LayoutParams(-1, -2); }
    private LinearLayout.LayoutParams marginTop(int top) {
        LinearLayout.LayoutParams p = matchWrap();
        p.setMargins(0, dp(top), 0, 0);
        return p;
    }
    private View space(int w, int h) {
        Space s = new Space(this);
        s.setLayoutParams(new LinearLayout.LayoutParams(w, h));
        return s;
    }
    private int dp(int v) { return Math.round(v * getResources().getDisplayMetrics().density); }
}
