# KINMOTO / FACTORY 3.0 — A1-D BENCHMARK EVIDENCE — 2026-11-05

**Status: A1-D PARTIAL / ENGINE UNSELECTED / NO V1 RELEASE.** Based on MASTER CHARTER V3 §§9.1–9.4, 10, 15–16 and `tasks/A1-D-BENCHMARK-RUNTIME.md`.

## Pinned upstream source evidence (not production imports)

- Neon Mayhem: `pranshuparmar/neon-mayhem@cd19f934d9088392d1f10374c3b64a1b7eb683cf`, `js/vehicles.js` blob `e9f0dcd851db687c7b62e34bc7346b6addc0ec6f`, code Apache-2.0. Motorcycle spec in that commit: `maxSpeed:46, accel:22, grip:2.9, turn:3.1`. Its `js/analytics.js` invokes GoatCounter on publicly hosted pages; KINMOTO must not import analytics.
- Costa Vista: `fastrouter/experiments-costa-vista@23e87108a281ac827e2ea23691aa7bf4b544146e`; `src/physics/vehicleController.ts` blob `922d6403a0e3300c8ea513400c0e0708a9f54e70`; `vehicleTypes.ts` blob `8b51d46ddb9d6e8f33c9c256facc4cfaeff149df`. Code MIT **only**; `public/assets` separately attributed. The bike model is project-created with commercial asset tooling: NO COPY. Physics includes 4 **virtual** wheel outriggers with Rapier raycasts + stabilizer, so this is not an unassisted two-wheel simulation.
- KINMOTO source under test: exact archive `KINMOTO_A2_V056_DIAGNOSTIC_QA_20261105.zip`, SHA256 `576eb0442ba50c672ea0f5e61335fa8838e8981a2796d94b431abeed3e14ba0b`. Source `sim.js` SHA256 `f1c680c475127d43c3b8e6628d144966fac5628dcef46d7c533bf33e7d00b350`. 12 modules, local HTML 103029 bytes, SHA256 `fef699cd212c86989c55fbb8b09fa301f2d7757cca6af70d4f0c8c4f94bfa368`.
- Source pack `KINMOTO_FACTORY_SOURCE_PACK_V3_20261104.zip`: 15/15 SHA manifest checks PASS. A2 diagnostic source pack: 77/77 SHA manifest checks PASS.

## Stage 9.4: measured scope

Five CPU-scripted 60Hz KINMOTO scenarios **executed using real current sim.js**:
- S1 100m straight: 100.13m in 6.47s, no lateral drift.
- S2 six virtual slalom gates: 6/6 in 14.32s, max target lateral error 0.128m; **scripted controller, no human steering or physical cones**.
- S3 full braking from 50km/h: stop in 1.17s over 7.84m; ride feel unassessed.
- S4 road bump x≈0,z≈39: maximum road height 0.130m, pitch max 0.039rad. Note that `frontGrounded` / `rearGrounded` are **always true by construction**, not independent tire contact sensors.
- S5 near-miss predicate and overlap impact: correct logical hit, health decreases; these are two prepared states, **not** a played continuous scene.
- Three repeat passes produced byte-identical scenario metrics after excluding CPU wall-times.

Additional isolated benchmark source/math:
- **Neon:** partial flat-road driving mathematical adapter only, Apache-2.0 with license; 8/8 Node tests PASS. In this simplified adapter 0–50km/h ~0.700s.
- **Costa:** four pure vehicle math functions (launch force, suspension, steer limit, wet grip) ported TS→JS, MIT license included, 8/8 Node tests PASS. Costa bike declares 190kg, initial 3100N, max 34m/s; **actual 0–50km/h time UNMEASURED without Rapier full game**.
- **KINMOTO:** bare independent bike function 0–50km/h ~2.517s, not full gameplay. These speed values are **not valid overall engine scores**.

Counter-audit reproduced **S5 initial-overlap defect**: at 12m/s, initially centered inside a traffic car, one 1/60s step displaces bike 1.56283m in world position but odometer advances 0.19983m. Normal nonoverlapping first step stays coherent. A2 ticket proposed `A2-COLLISION-SWEPT-CONTACT`, **not patched during A1**.

## Re-run QA, scope limits

- `npm run check` PASS, `npm test` **165/165 PASS**, Python **22/22 PASS**, 12-module build PASS, 5-file local HTTP test PASS.
- Additional extracted math tests **16/16 PASS**.
- ZIP `KINMOTO_A1D_BENCHMARK_CONTRADICTOIRE_20261105.zip`: 330821 bytes, SHA256 `706103f8761d71955431c4732a8223f41c2409927263f89002b3a116d7e01768`, 99 entries (98 manifest tracked). **Fresh extraction** verified 98/98 manifest files, re-ran 165+22+8+8 tests and exact HTML rebuild PASS.
- A repeat real 3D Chromium/SwiftShader test **TIMED OUT**; status INCONCLUSIVE, not hardware PASS or FAIL. No real HP/Android/iPhone performance assertions.
- Full Neon/Costa source could not be downloaded into the CPU test environment (DNS blocked), and no native HP or Android session was executed. Do NOT label candidate math tests full-engine runs.

## Gates from master charter 9.4

1. History previously archived: unchanged. 
2. Code pins, licensing, candidate source review: **PARTIAL**; some exact asset files unacquired.
3. Three original games running unchanged on HP AND Android: **NOT_TESTED**.
4. Same S1–S5 with FPS/RAM/feel: **KINMOTO CPU ONLY**, Neon/Costa full game **NOT_TESTED**.
5. Isolate reusable module: **PURE MATH EXTRACTION PASS**, full vehicle controller **NOT_TESTED**.
6. Counter-audit: **PARTIAL**; collision finding proven, device/energy cost unmeasured.
7. Final scorecard 30/20/20/15/10/5: **ALL NULL**, ENGINE_UNSELECTED.
8. V1 rebuilt: **NOT AUTHORIZED** until 7.

**Next:** HP Windows (Opera + another browser) and real Galaxy A21s (Chrome Eco 15–20 min) across all 3 candidates, capture same 5 scenes, frame times / FPS / RAM / controls / camera / visual, audit binary model licenses/hashes; then select engine with owner GO. No main/STABLE merge, no public deployment, no hosted Actions, no Remote, no spend.

Private standalone evidence artifact: `KINMOTO_A1D_BENCHMARK_CONTRADICTOIRE_20261105.zip` contains scripts, all reports, original source, pure adapters and licenses. **Not automatically uploaded to GitHub or Drive.**
