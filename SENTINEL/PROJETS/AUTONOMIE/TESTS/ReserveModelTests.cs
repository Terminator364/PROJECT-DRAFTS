using System;
using Sentinel.Incubation;
class ReserveModelTests {
    static void Eq(double a,double b){if(double.IsNaN(a)||Math.Abs(a-b)>0.0001)throw new Exception("Unexpected result");}
    static void Main(){
        Eq(ReserveModel.EffectiveReserve(40000,2,2000,5),2000);
        Eq(ReserveModel.EffectiveReserve(40000,8,2000,5),3200);
        Eq(ReserveModel.EffectiveReserve(40000,2,-1,5),2000);
        Eq(ReserveModel.SecondsToReserve(3000,2000,10),360);
        Eq(ReserveModel.SecondsToReserve(2000,2000,10),0);
        Eq(ReserveModel.SecondsToReserve(1900,2000,0),0);
        if(!double.IsNaN(ReserveModel.SecondsToReserve(3000,2000,0)))throw new Exception("Invalid watts");
        if(!double.IsNaN(ReserveModel.EffectiveReserve(-1,2,2000,5)))throw new Exception("Invalid full");
        Console.WriteLine("8 tests PASS");
    }
}
