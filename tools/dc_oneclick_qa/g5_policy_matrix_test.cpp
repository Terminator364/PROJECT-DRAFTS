#include <cassert>
#include <cstdio>
#include <cstdlib>
#include "g5_network_policy.h"
// 4 Wi-Fi states x 2 trust x 2 encryption x 3 costs x 2 agent states = 96
int main(){
  unsigned count=0;
  for(int wifi=0;wifi<4;wifi++) for(int home=0;home<2;home++)
  for(int secure=0;secure<2;secure++) for(int cost=0;cost<3;cost++)
  for(int running=0;running<2;running++){
    PolicyInputs p;
    p.wifi=static_cast<WifiClass>(wifi);
    p.approvedHome=(home==1);
    p.secured=(secure==1);
    p.cost=static_cast<DataCost>(cost);
    p.agentAlreadyRunning=(running==1);
    auto actual=decideRemote(p);
    PolicyAction expected;
    if(running)expected=PolicyAction::PreserveAgent;
    else if(wifi!=(int)WifiClass::Connected)expected=PolicyAction::BlockUnknownNetwork;
    else if(!home)expected=PolicyAction::BlockUntrusted;
    else if(!secure)expected=PolicyAction::BlockUnsecured;
    else if(cost==(int)DataCost::Metered)expected=PolicyAction::BlockMetered;
    else if(cost==(int)DataCost::Unknown)expected=PolicyAction::BlockCostUnknown;
    else expected=PolicyAction::StartRemote;
    assert(actual==expected);
    if(running)assert(actual!=PolicyAction::StartRemote);
    if(!running && actual==PolicyAction::StartRemote)
      assert(wifi==3 && home==1 && secure==1 && cost==1);
    count++;
  }
  // Additional replay: 144 transitions simulating network changes and repeated click.
  for(int i=0;i<144;i++){
    PolicyInputs p;
    p.wifi=WifiClass::Connected; p.approvedHome=true;p.secured=true;p.cost=DataCost::Unmetered;
    if(i%2)p.wifi=WifiClass::NoWifi;
    if(i%3==0)p.cost=DataCost::Metered;
    if(i%5==0)p.approvedHome=false;
    if(i%7==0)p.agentAlreadyRunning=true;
    auto result=decideRemote(p);
    if(p.agentAlreadyRunning)assert(result==PolicyAction::PreserveAgent);
    else if(result==PolicyAction::StartRemote)assert(p.wifi==WifiClass::Connected && p.approvedHome && p.cost==DataCost::Unmetered);
    count++;
  }
  printf("G5_POLICY_MATRIX_PASS=%u\n",count);
  return count==240?0:1;
}
