using System;
namespace Sentinel.Incubation {
    // Independent, synthetic-testable model. Capacities: mWh; power: W.
    public static class ReserveModel {
        static bool Finite(double v) { return !double.IsNaN(v) && !double.IsInfinity(v); }
        public static double EffectiveReserve(double full, double windowsPct, double hardware, double fallbackPct) {
            if (!Finite(full) || full<=0 || !Finite(windowsPct) || windowsPct<0 || windowsPct>100 || !Finite(fallbackPct) || fallbackPct<0 || fallbackPct>100) return double.NaN;
            double reserve=Finite(hardware)&&hardware>0&&hardware<=full?hardware:full*fallbackPct/100.0;
            return Math.Max(reserve,full*windowsPct/100.0);
        }
        public static double SecondsToReserve(double remaining, double reserve, double watts) {
            if (!Finite(remaining)||remaining<0||!Finite(reserve)||reserve<0) return double.NaN;
            if (remaining<=reserve) return 0;
            if (!Finite(watts)||watts<=0) return double.NaN;
            return (remaining-reserve)*3.6/watts;
        }
    }
}
