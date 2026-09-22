package com.terminator364.timeplus;

import android.app.Activity;
import android.content.SharedPreferences;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.os.Bundle;
import android.view.Gravity;
import android.view.View;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.Switch;
import android.widget.TextView;
import android.widget.Toast;

public class SettingsActivity extends Activity {
    private static final int BLUE = Color.rgb(45, 100, 246);
    private static final int TEXT = Color.rgb(17, 24, 39);
    private static final int MUTED = Color.rgb(103, 115, 139);
    private static final int BG = Color.rgb(246, 248, 252);
    private static final int BORDER = Color.rgb(224, 229, 238);
    private Switch alert, sound, vibration;

    @Override protected void onCreate(Bundle state) {
        super.onCreate(state);
        getWindow().setStatusBarColor(BG);
        if (android.os.Build.VERSION.SDK_INT >= 23) {
            getWindow().getDecorView().setSystemUiVisibility(View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR);
        }
        setContentView(buildUi());
        SharedPreferences p = prefs();
        alert.setChecked(p.getBoolean("default_alert", false));
        sound.setChecked(p.getBoolean("default_sound", true));
        vibration.setChecked(p.getBoolean("default_vibrate", true));
        updateEnabled();
    }

    private View buildUi() {
        ScrollView scroll = new ScrollView(this);
        scroll.setBackgroundColor(BG);
        LinearLayout root = column();
        root.setPadding(dp(16), statusBarInset() + dp(10), dp(16), navBarInset() + dp(24));
        scroll.addView(root, new ScrollView.LayoutParams(-1, -2));

        LinearLayout header = new LinearLayout(this);
        header.setGravity(Gravity.CENTER_VERTICAL);
        Button back = button("←", false);
        back.setOnClickListener(v -> finish());
        header.addView(back, new LinearLayout.LayoutParams(dp(48), dp(48)));
        TextView title = text("Paramètres", 24, TEXT, true);
        LinearLayout.LayoutParams titleLp = new LinearLayout.LayoutParams(0, -2, 1f);
        titleLp.setMargins(dp(10), 0, 0, 0);
        header.addView(title, titleLp);
        root.addView(header);
        root.addView(text("Personnalise TimePlus sans alourdir l’écran principal.", 13, MUTED, false), marginTop(6));

        LinearLayout alertCard = card("Alerte par défaut", "Définis le comportement des nouvelles alertes.");
        alert = switchRow("Activer une alerte", false);
        sound = switchRow("Son", true);
        vibration = switchRow("Vibration", true);
        alertCard.addView(alert, marginTop(12));
        alertCard.addView(sound, marginTop(6));
        alertCard.addView(vibration, marginTop(6));
        root.addView(alertCard, marginTop(16));
        alert.setOnCheckedChangeListener((v, checked) -> updateEnabled());

        LinearLayout appCard = card("Application", "Informations de cette version.");
        appCard.addView(infoBlock("Version", "1.2.1"), marginTop(12));
        appCard.addView(infoBlock("Mise à jour", "Installation par-dessus C3"), marginTop(10));
        appCard.addView(infoBlock("Mode hors ligne", "Oui"), marginTop(10));
        root.addView(appCard, marginTop(16));

        Button save = button("Enregistrer", true);
        save.setOnClickListener(v -> save());
        LinearLayout.LayoutParams saveLp = marginTop(18);
        saveLp.height = dp(54);
        root.addView(save, saveLp);
        return scroll;
    }

    private void updateEnabled() {
        sound.setEnabled(alert.isChecked());
        vibration.setEnabled(alert.isChecked());
    }

    private void save() {
        prefs().edit()
                .putBoolean("default_alert", alert.isChecked())
                .putBoolean("default_sound", sound.isChecked())
                .putBoolean("default_vibrate", vibration.isChecked())
                .apply();
        Toast.makeText(this, "Préférences enregistrées", Toast.LENGTH_SHORT).show();
        finish();
    }

    private SharedPreferences prefs() { return getSharedPreferences(TimePlusActivity.PREFS, MODE_PRIVATE); }

    private LinearLayout card(String title, String subtitle) {
        LinearLayout c = column();
        c.setPadding(dp(16), dp(16), dp(16), dp(16));
        c.setBackground(roundRect(Color.WHITE, 20, BORDER));
        c.addView(text(title, 18, TEXT, true));
        c.addView(text(subtitle, 13, MUTED, false), marginTop(4));
        return c;
    }

    private View infoBlock(String left, String right) {
        LinearLayout block = column();
        block.addView(text(left, 14, MUTED, true));
        block.addView(text(right, 17, TEXT, true), marginTop(4));
        return block;
    }

    private Switch switchRow(String label, boolean checked) {
        Switch s = new Switch(this);
        s.setText(label);
        s.setTextSize(15);
        s.setTextColor(TEXT);
        s.setChecked(checked);
        return s;
    }

    private Button button(String label, boolean primary) {
        Button b = new Button(this);
        b.setText(label);
        b.setAllCaps(false);
        b.setTextSize(15);
        b.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        b.setTextColor(primary ? Color.WHITE : BLUE);
        b.setBackground(roundRect(primary ? BLUE : Color.WHITE, 14, primary ? BLUE : Color.rgb(190, 204, 244)));
        return b;
    }

    private TextView text(String value, int sp, int color, boolean bold) {
        TextView t = new TextView(this);
        t.setText(value);
        t.setTextSize(sp);
        t.setTextColor(color);
        if (bold) t.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        return t;
    }

    private LinearLayout column() {
        LinearLayout l = new LinearLayout(this);
        l.setOrientation(LinearLayout.VERTICAL);
        return l;
    }

    private GradientDrawable roundRect(int fill, int radius, int stroke) {
        GradientDrawable d = new GradientDrawable();
        d.setColor(fill);
        d.setCornerRadius(dp(radius));
        d.setStroke(dp(1), stroke);
        return d;
    }

    private LinearLayout.LayoutParams marginTop(int top) {
        LinearLayout.LayoutParams p = new LinearLayout.LayoutParams(-1, -2);
        p.setMargins(0, dp(top), 0, 0);
        return p;
    }

    private int statusBarInset() {
        int id = getResources().getIdentifier("status_bar_height", "dimen", "android");
        return id > 0 ? getResources().getDimensionPixelSize(id) : dp(24);
    }

    private int navBarInset() {
        int id = getResources().getIdentifier("navigation_bar_height", "dimen", "android");
        return id > 0 ? getResources().getDimensionPixelSize(id) : dp(10);
    }

    private int dp(int v) { return Math.round(v * getResources().getDisplayMetrics().density); }
}
