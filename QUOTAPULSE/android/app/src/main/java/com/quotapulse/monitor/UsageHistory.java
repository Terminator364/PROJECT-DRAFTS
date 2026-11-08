package com.quotapulse.monitor;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Locale;

/** Tiny, local, real-measurement-only history. No daemon and no network traffic. */
public final class UsageHistory {
  private UsageHistory(){}
  public static final class Point {
    public final long at, used, limit;
    public Point(long at,long used,long limit){this.at=at;this.used=used;this.limit=limit;}
  }
  public static final class Update {
    public final List<Point> points;
    public final String serialized;
    public final boolean comparable, changedCycle;
    public final long increase;
    private Update(List<Point> pts,String text,boolean comp,boolean cycle,long difference){
      points=Collections.unmodifiableList(pts);serialized=text;comparable=comp;changedCycle=cycle;increase=difference;
    }
  }
  public static List<Point> parse(String raw) {
    List<Point> out=new ArrayList<>();
    if(raw==null||raw.isEmpty())return out;
    String[] items=raw.split(";");
    for(String item:items){
      String[] v=item.split(",");
      if(v.length!=3)continue;
      try{
        long at=Long.parseLong(v[0]),used=Long.parseLong(v[1]),limit=Long.parseLong(v[2]);
        if(at<=0||used<0||limit<=0||used>limit)continue;
        if(out.isEmpty()||at>=out.get(out.size()-1).at)out.add(new Point(at,used,limit));
      }catch(NumberFormatException ignored){}
    }
    if(out.size()>24)return new ArrayList<>(out.subList(out.size()-24,out.size()));
    return out;
  }
  public static Update record(String old,long previousAt,long previousUsed,long previousLimit,
                              long now,long used,long limit) {
    if(now<=0||used<0||limit<=0||used>limit)throw new IllegalArgumentException("Invalid usage reading");
    List<Point> points=parse(old);
    if(points.isEmpty()&&previousAt>0&&previousAt<now&&previousUsed>=0
        &&previousLimit>0&&previousUsed<=previousLimit)
      points.add(new Point(previousAt,previousUsed,previousLimit));
    Point before=points.isEmpty()?null:points.get(points.size()-1);
    boolean comparable=before!=null&&before.limit==limit&&used>=before.used;
    boolean changedCycle=before!=null&&!comparable;
    long difference=comparable?used-before.used:0;
    if(changedCycle)points.clear(); // never draw a false dip between billing cycles
    points.add(new Point(now,used,limit));
    if(points.size()>24)points=new ArrayList<>(points.subList(points.size()-24,points.size()));
    StringBuilder txt=new StringBuilder();
    for(Point p:points)txt.append(p.at).append(',').append(p.used).append(',').append(p.limit).append(';');
    return new Update(points,txt.toString(),comparable,changedCycle,difference);
  }
  public static String percentage(long remaining,long limit) {
    if(limit<=0||remaining<0)return "—";
    return String.format(Locale.FRANCE,"%.2f %%",remaining*100.0/limit);
  }
  public static String changeText(boolean comparable,boolean changedCycle,long difference) {
    if(changedCycle)return "Cycle réinitialisé ou compteur corrigé";
    if(!comparable)return "Premier relevé enregistré";
    if(difference==0)return "0 nouvel appel depuis le dernier relevé";
    return String.format(Locale.FRANCE,"+%,d appels depuis le dernier relevé",difference);
  }
}
