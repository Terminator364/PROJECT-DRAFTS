# Blessing BookHarvester V1.4.4 — fail-closed CLI patch

**Input:** experiments/Blessing-BookHarvester-V1.4.3-Sources.zip on branch feat/bookharvester-v14-random3-multibrowser-20261012.

## Evidence
- GitHub 38200720036: V1.4 Windows and 77 chapter Gutenberg text simulations passed.
- MBMPC: installed V1.4, matching release archive SHA256 1acaf0771ab869055797132df72a8450929696de7df5ddb62e3d5817b3bf8c21.
- MBMPC: V1.4 `--sample-three --sample-seed 20261012` tried Ranovel chapters **3, 105, 203** and received HTTP 403 for all three; report `SAMPLE_FAIL` but exit code was incorrectly **0**.
- Correction: `SAMPLE_FAIL` exits **3**, and incomplete/blocked normal collection exits **4**; no impact on the UI flow.
- Local tests after correction: **47/47 passed**. Windows V1.4.4 build **NOT YET QUALIFIED**, Ranovel live **NOT CERTIFIED**. Keep installed V1.4 until the next Windows gate.

## Reproducible patch

```diff
--- a/bookharvester.py
+++ b/bookharvester.py
@@
-VERSION = "1.4.0-multibrowser-random3"
+VERSION = "1.4.4-multibrowser-random3-gated"
@@
-            print(json.dumps(sample_three_chapters(args.book,root,args.url,args.count,seed=args.sample_seed,pattern=args.pattern,delay=max(1,args.delay)),ensure_ascii=False))
+            sample = sample_three_chapters(args.book,root,args.url,args.count,seed=args.sample_seed,pattern=args.pattern,delay=max(1,args.delay))
+            print(json.dumps(sample,ensure_ascii=False))
+            if sample['status'] != 'SAMPLE_PASS':
+                sys.exit(3)
         else:
-            print(retrieve(args.book,root,args.url,args.mode,count=args.count,pattern=args.pattern,delay=max(1,args.delay),profile=json.loads(args.profile.read_text(encoding="utf-8")) if args.profile else None))
+            result = retrieve(args.book,root,args.url,args.mode,count=args.count,pattern=args.pattern,delay=max(1,args.delay),profile=json.loads(args.profile.read_text(encoding="utf-8")) if args.profile else None)
+            print(json.dumps(result,ensure_ascii=False))
+            if result['blocked'] or result['failed'] or result['remaining']:
+                sys.exit(4)
```

## Ranovel gate

When Ranovel returns 403 in direct HTTP AND tested headless browsers, stop instead of retrying aggressively or bypassing controls. The next meaningful authorized test requires a browser profile where the selected pages actually display, and user approval for the optional Chromium extension. Draw **three distinct random chapter numbers** and verify the text and export; only then move to 236. Do not report success based on search-engine snippets, source-home HTTP 200, or synthetic pages alone.

Avoid automatic GitHub Actions triggers. Respect repository AGENTS.md CI budget.
