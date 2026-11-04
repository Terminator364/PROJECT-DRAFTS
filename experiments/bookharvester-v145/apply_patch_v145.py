"""Apply tested V1.4.5 diagnostic CLI changes to verified V1.4.4 source."""
from pathlib import Path
p=Path("bookharvester.py")
s=p.read_text(encoding="utf-8")
a='VERSION = "1.4.4-multibrowser-random3-gated"'
b='VERSION = "1.4.5-multibrowser-site-diagnostic"'
assert s.count(a)==1, "Unexpected source version, abort packaging"
s=s.replace(a,b)
a='    parser.add_argument("--sample-three",action="store_true"'
b='    parser.add_argument("--diagnose-site",action="store_true",help="diagnostic 3 chapitres sans contournement des protections")\n'+a
assert s.count(a)==1
s=s.replace(a,b)
a='    if args.url:\n        if not args.permit_archive:'
b='''    if args.diagnose_site:
        if not args.url or args.count < 3:
            parser.error("--diagnose-site demande --url et --count >=3")
        from site_audit import audit_three,save
        seed=args.sample_seed if args.sample_seed is not None else random.SystemRandom().randint(1,2**31-1)
        r=audit_three(args.url,args.count,seed=seed,delay=max(1,args.delay),pattern=args.pattern)
        save(r,root/"site_diagnostic_report.json")
        print(json.dumps(r,ensure_ascii=False))
        if r["status"]!="SAMPLE_PASS":sys.exit(5)
        return
    if args.url:
        if not args.permit_archive:'''
assert s.count(a)==1
s=s.replace(a,b)
p.write_text(s,encoding="utf-8")
print("V1.4.5 patch applied")
