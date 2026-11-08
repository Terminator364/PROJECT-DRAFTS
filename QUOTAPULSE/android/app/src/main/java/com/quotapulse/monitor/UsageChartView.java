package com.quotapulse.monitor;

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.RectF;
import android.view.View;
import java.util.ArrayList;
import java.util.List;

/** Tiny Canvas bar graph of measured increases only. Never fabricates dates or values. */
public final class UsageChartView extends View {
  private final Paint paint=new Paint(Paint.ANTI_ALIAS_FLAG);
  private final ArrayList<Long> increments=new ArrayList<>();
  private int text=Color.rgb(159,176,201),accent=Color.rgb(52,225,181);
  private float density;
  public UsageChartView(Context context) {
    super(context);
    density=getResources().getDisplayMetrics().density;
    setMinimumHeight((int)(105*density));
  }
  public void setReadings(List<UsageHistory.Point> list){
    increments.clear();
    if(list!=null)for(int i=1;i<list.size();i++){
      UsageHistory.Point a=list.get(i-1),b=list.get(i);
      if(a.limit==b.limit&&b.used>=a.used)increments.add(b.used-a.used);
    }
    while(increments.size()>10)increments.remove(0);
    invalidate();
  }
  @Override protected void onDraw(Canvas canvas){
    super.onDraw(canvas);
    final float w=getWidth(),h=getHeight(),left=8*density,right=w-8*density;
    if(w<120*density||h<60*density)return;
    paint.setColor(text);paint.setStyle(Paint.Style.FILL);
    paint.setTextSize(11*density);
    if(increments.isEmpty()){
      canvas.drawText("Graphique après deux relevés réels",left, h*.55f,paint);
      return;
    }
    long max=1;for(Long v:increments)max=Math.max(max,v);
    float top=17*density,bottom=h-25*density;
    paint.setColor(Color.rgb(65,79,107));paint.setStrokeWidth(density);
    canvas.drawLine(left,bottom,right,bottom,paint);
    int count=increments.size();
    float step=(right-left)/Math.max(count,5);
    float col=Math.min(28*density,step*.53f);
    float start=left+((right-left)-step*count)*.5f;
    paint.setTextAlign(Paint.Align.CENTER);
    for(int i=0;i<count;i++){
      long delta=increments.get(i);
      float barHeight=delta==0?3*density:Math.max(6*density,(bottom-top)*delta/max);
      float cx=start+step*(i+.5f);
      paint.setColor(accent);
      canvas.drawRoundRect(new RectF(cx-col/2,bottom-barHeight,cx+col/2,bottom),5*density,5*density,paint);
      paint.setTextSize(10*density);paint.setColor(text);
      String value=delta==0?"0":"+"+delta;
      canvas.drawText(value,cx,Math.max(11*density,bottom-barHeight-5*density),paint);
    }
    paint.setTextAlign(Paint.Align.LEFT);
    paint.setTextSize(10*density);paint.setColor(text);
    canvas.drawText(count+" intervalle"+(count>1?"s":""),left,h-4*density,paint);
  }
}
