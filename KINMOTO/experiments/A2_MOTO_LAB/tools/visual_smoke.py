#!/usr/bin/env python3
"""Optional offline browser smoke. Needs local Playwright + Chromium/Xvfb; never contacts Vercel.

PLAYWRIGHT_CHROMIUM=/usr/bin/chromium xvfb-run -a python tools/visual_smoke.py
Not a phone hardware benchmark, nor a substitute for manual driving.
"""
import json,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
html=(ROOT/'dist/index.html').read_text()
# Local set_content() has about:blank rather than ?qa=1; expose only test hook in the throwaway QA page.
html=html.replace("if(location.search.includes('qa=1'))window.KINMOTO_QA=","if(true)window.KINMOTO_QA=")
try:from playwright.sync_api import sync_playwright
except ImportError:raise SystemExit('SKIP: Playwright optional developer tool unavailable')
summary={}
with sync_playwright() as p:
    bin=os.environ.get('PLAYWRIGHT_CHROMIUM','/usr/bin/chromium')
    browser=p.chromium.launch(executable_path=bin,headless=False,args=[
        '--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-webgl','--enable-unsafe-swiftshader',
        '--disable-dev-shm-usage'])
    for name,width,height in [('desktop',1100,720),('mobile_emulated',393,852)]:
        page=browser.new_page(viewport={'width':width,'height':height},device_scale_factor=1,
                              is_mobile=name!='desktop',has_touch=name!='desktop')
        errs=[]
        page.on('pageerror',lambda e:errs.append(str(e)))
        page.set_content(html,wait_until='load')
        page.wait_for_timeout(500)
        assert page.evaluate("typeof window.KINMOTO_DIAGNOSTIC==='function'"),'No game diagnostics: bundle syntax error'
        diag=page.evaluate('window.KINMOTO_DIAGNOSTIC()')
        assert diag['mode'] in ('webgl2','webgl1'),f'No WebGL on {name}: {diag}'
        page.locator('#play').click()
        page.wait_for_timeout(700)
        assert page.locator('#menu').evaluate('(e)=>e.classList.contains("hidden")')
        assert page.locator('#hud').is_visible()
        # Trigger physical mission pickup using QA-only hooks, without inventing interaction success.
        result=page.evaluate('''() => {
          const g=KINMOTO_QA.get();
          const p=g.mission.from;
          const target={matonge:{x:13,z:-73},victoire:{x:13,z:12},ecole:{x:-13,z:64},marche:{x:109,z:13},clinique:{x:-108,z:-13},restaurant:{x:13,z:157},station:{x:109,z:-13},residence:{x:-13,z:-78}}[p];
          KINMOTO_QA.forcePosition(target.x,target.z,0);
          return KINMOTO_QA.interact();
        }''')
        assert result['ok'] and result['type']=='pickup',result
        page.wait_for_function("!document.getElementById('comfortInfo').hidden",timeout=7000)
        print(name,'stage',page.evaluate('KINMOTO_QA.get().mission.stage'),'hidden',page.locator('#comfortInfo').evaluate('(e)=>e.hidden'),'playing',page.evaluate('KINMOTO_QA.get().playing'),'errors',errs[:5],'diagnostic',page.evaluate('window.KINMOTO_DIAGNOSTIC().steps'))
        assert not page.locator('#comfortInfo').evaluate('(e)=>e.hidden'),'Comfort UI invisible after pickup'
        assert page.locator('#navText').inner_text()!='','GPS not initialized'
        assert not errs,errs
        if name=='mobile_emulated':
            rects=page.evaluate('''() => Object.fromEntries(['mission','mapcard','navCue','drive-panel','touchControls'].map(id => {const el=['drive-panel','mission','mapcard'].includes(id)?document.querySelector('.'+id):document.getElementById(id);const r=el.getBoundingClientRect();return [id,{x:r.x,y:r.y,w:r.width,h:r.height}]}))''')
            def overlap(a,b):return max(0,min(a['x']+a['w'],b['x']+b['w'])-max(a['x'],b['x']))*max(0,min(a['y']+a['h'],b['y']+b['h'])-max(a['y'],b['y']))
            assert overlap(rects['mission'],rects['mapcard'])<1,('Map overlaps mission',rects)
            assert overlap(rects['drive-panel'],rects['touchControls'])<5,('Speed panel blocks controls',rects)
            summary['mobile_ui_rects']=rects
        page.wait_for_timeout(2900) # Let camera interpolation catch up after QA teleport; toast clears.
        page.screenshot(path=str(ROOT/'docs'/f'A2_v055_{name}_webgl.png'))
        summary[name]={'webgl':diag['mode'],'screenshot':f'docs/A2_v055_{name}_webgl.png',
                        'navigation':page.locator('#navText').inner_text(),
                        'comfort':page.locator('#comfortValue').inner_text(),
                        'fps_sample':page.evaluate('window.KINMOTO_DIAGNOSTIC().render.fps'),
                        'errors':errs}
        page.close()
    browser.close()
(ROOT/'docs'/'VISUAL_SMOKE_V055.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
print(json.dumps(summary,ensure_ascii=False,indent=2))
