package com.quotapulse.monitor;

import java.util.Locale;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/** Strict parser of the provider's visible usage dashboard, never an MCP tool call. */
public final class QuotaParser {
    private QuotaParser() {}
    private static final String NUM = "([0-9]{1,3}(?: [0-9]{3})+|[0-9]+)";
    private static final Pattern PAIR = Pattern.compile("(?<![0-9])" + NUM + "\\s*(?:/|of|sur)\\s*" + NUM + "(?![0-9])", Pattern.CASE_INSENSITIVE);
    private static final Pattern LEFT = Pattern.compile(NUM + "\\s*(?:tool calls left|appels restants)", Pattern.CASE_INSENSITIVE);
    private static final Pattern AVG = Pattern.compile("(?:daily average|moyenne quotidienne)\\s*" + NUM, Pattern.CASE_INSENSITIVE);
    // Extract only the next valid calendar day + month, never upsell text.
    private static final Pattern RESET = Pattern.compile("(?:resets on|renouvellement le|réinitialisation le)\\s*([^,;|]{1,55})", Pattern.CASE_INSENSITIVE);
    private static final Pattern DAY_MONTH = Pattern.compile("(?iu)^(?:[^0-9]*?)\\b(\\d{1,2})\\s+([\\p{L}]{3,12}\\.?)");
    private static final Pattern MONTH_DAY = Pattern.compile("(?iu)^\\s*([\\p{L}]{3,12})\\s+(\\d{1,2})(?:\\b|$)");
    public static String cleanReset(String value) {
        if (value == null || value.trim().isEmpty()) return "À confirmer";
        String input=value.replace((char)160,' ').replace((char)8239,' ').trim();
        Matcher dm=DAY_MONTH.matcher(input);
        if(dm.find())return dm.group(1)+" "+dm.group(2);
        Matcher md=MONTH_DAY.matcher(input);
        if(md.find())return md.group(1)+" "+md.group(2);
        return "À confirmer";
    }

    public static final class Data {
        public final long used, limit, remaining;
        public final int dailyAverage;
        public final String reset;
        public Data(long used, long limit, long remaining, int dailyAverage, String reset) {
            this.used=used; this.limit=limit; this.remaining=remaining; this.dailyAverage=dailyAverage; this.reset=reset;
        }
    }

    public static Data parse(String raw) {
        if (raw == null || raw.trim().isEmpty()) return null;
        String text = raw.replace('\u00a0', ' ').replace('\u202f', ' ').replace('\u2009', ' ')
                .replaceAll("[\\r\\n\\t]+", " ").replaceAll(" +", " ").trim();
        String lower = text.toLowerCase(Locale.ROOT);
        if (!lower.contains("tool calls") && !lower.contains("appels d'outils")) return null;
        int anchor = lower.indexOf("tool calls this month");
        if (anchor < 0) anchor = lower.indexOf("appels d'outils");
        String scoped = anchor >= 0 ? text.substring(anchor, Math.min(text.length(), anchor + 260)) : text;
        Matcher m = PAIR.matcher(scoped);
        if (!m.find()) {
            m = PAIR.matcher(text);
            if (!m.find()) return null;
        }
        long used = number(m.group(1)), limit = number(m.group(2));
        if (used < 0 || limit <= 0 || used > limit || limit > 1000000000L) return null;
        long remaining = limit-used;
        Matcher left = LEFT.matcher(text);
        if (left.find() && number(left.group(1)) != remaining) return null;
        int avg = 0;
        Matcher a = AVG.matcher(text);
        if (a.find()) {
            long v = number(a.group(1));
            if (v >= 0) avg = (int)Math.min(1000000L, v);
        }
        String reset = "À confirmer";
        Matcher date = RESET.matcher(text);
        if(date.find())reset=cleanReset(date.group(1));
        return new Data(used,limit,remaining,avg,reset);
    }

    static long number(String s) {
        String digits=s.replaceAll("[^0-9]", "");
        if (digits.isEmpty() || digits.length()>12) return -1;
        try {return Long.parseLong(digits);} catch(NumberFormatException e) {return -1;}
    }
}
