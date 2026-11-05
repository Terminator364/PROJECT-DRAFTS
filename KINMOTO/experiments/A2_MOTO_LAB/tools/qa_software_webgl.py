#!/usr/bin/env python3
"""Optional lab-only WebGL2 software renderer smoke test.

Run under Linux with Xvfb, Chromium and Playwright installed:
  xvfb-run -a python tools/qa_software_webgl.py

Uses about:blank + set_content on bundled HTML to avoid external navigation.
This is NOT a GPU/Android performance benchmark or a hosted service.
"""
import json
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
HTML = ROOT / 'dist' / 'KIN_MOTO_A2_LAB_JOUER.html'
OUT = ROOT / 'qa_local_swiftshader'
FLAGS = [
    '--no-sandbox', '--disable-dev-shm-usage', '--use-gl=angle',
    '--use-angle=swiftshader', '--enable-unsafe-swiftshader',
    '--enable-webgl', '--ignore-gpu-blocklist',
]


def run_case(p, name, width, height, mobile):
    browser = p.chromium.launch(executable_path='/usr/bin/chromium', headless=False, args=FLAGS)
    try:
        context = browser.new_context(viewport={'width': width, 'height': height},
                                      has_touch=mobile, is_mobile=mobile, device_scale_factor=1)
        page = context.new_page()
        exceptions = []
        page.on('pageerror', lambda error: exceptions.append(str(error)))
        page.goto('about:blank')
        page.set_content(HTML.read_text(encoding='utf-8'), wait_until='domcontentloaded')
        page.wait_for_function('typeof window.KINMOTO_DIAGNOSTIC === "function"')
        page.locator('#play').click()
        page.wait_for_timeout(2500)
        info = page.evaluate('''() => {
            const canvas = document.getElementById('world');
            const gl = canvas.getContext('webgl2');
            const ext = gl?.getExtension('WEBGL_debug_renderer_info');
            return {
                game: window.KINMOTO_DIAGNOSTIC(),
                webgl2: !!gl,
                gpu: gl ? (ext ? gl.getParameter(ext.UNMASKED_RENDERER_WEBGL) : gl.getParameter(gl.RENDERER)) : null,
                glVersion: gl?.getParameter(gl.VERSION) || null,
                errorVisible: !document.getElementById('errorScreen').classList.contains('hidden')
            };
        }''')
        page.screenshot(path=str(OUT / f'{name}_webgl2.png'))
        before = info['game']['player']['z']
        if mobile:
            button = page.locator('.controls [data-key="gas"]')
            button.dispatch_event('pointerdown', {'pointerId': 10})
            page.wait_for_timeout(1200)
            button.dispatch_event('pointerup', {'pointerId': 10})
        else:
            page.keyboard.down('ArrowUp')
            page.wait_for_timeout(1200)
            page.keyboard.up('ArrowUp')
        state = page.evaluate('window.KINMOTO_DIAGNOSTIC()')
        page.locator('#pause').click()
        paused = page.evaluate('window.KINMOTO_DIAGNOSTIC().paused')
        page.locator('#resume').click()
        resumed = page.evaluate('window.KINMOTO_DIAGNOSTIC().paused')
        result = {
            'mode': name, 'screen': [width, height], 'webgl2': info['webgl2'],
            'renderer': info['gpu'], 'glVersion': info['glVersion'],
            'gameStarted': info['game']['playing'],
            'movedMeters': round(before - state['player']['z'], 3),
            'pauseThenResume': paused and not resumed,
            'worldVertices': info['game']['render']['worldVertices'] if info['game']['render'] else None,
            'browserErrors': exceptions, 'errorScreen': info['errorVisible'],
            'reportedFPSSoftwareOnly': state['render']['fps'] if state['render'] else None,
        }
        assert result['webgl2'] and result['gameStarted'] and result['movedMeters'] > .1
        assert result['pauseThenResume'] and not result['browserErrors'] and not result['errorScreen']
        return result
    finally:
        browser.close()


def main():
    assert HTML.exists(), f'Build first: {HTML}'
    OUT.mkdir(exist_ok=True)
    reports = []
    with sync_playwright() as p:
        for args in [('desktop', 1280, 800, False), ('mobile', 393, 852, True)]:
            reports.append(run_case(p, *args))
    (OUT / 'REPORT.json').write_text(json.dumps(reports, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps(reports, ensure_ascii=False))


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print('QA_SOFTWARE_WEBGL_FAILED:', repr(exc), file=sys.stderr)
        sys.exit(1)
