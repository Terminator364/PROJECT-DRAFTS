#pragma once
// G5 network/data budget policy: PURE, zero I/O, independent of WLAN and GUI.
// Unknown connection == NOT trusted, no exceptions. Existing agents are never touched.
enum class WifiClass { Unknown, NoWifi, PermissionDenied, Connected };
enum class DataCost { Unknown, Unmetered, Metered };
enum class PolicyAction { PreserveAgent, StartRemote, BlockUnknownNetwork, BlockUntrusted,
                          BlockMetered, BlockCostUnknown, BlockUnsecured };
struct PolicyInputs {
    bool agentAlreadyRunning=false;
    WifiClass wifi=WifiClass::Unknown;
    bool approvedHome=false;
    bool secured=false;
    DataCost cost=DataCost::Unknown;
};
inline PolicyAction decideRemote(const PolicyInputs& p) {
    if (p.agentAlreadyRunning) return PolicyAction::PreserveAgent;
    if (p.wifi!=WifiClass::Connected) return PolicyAction::BlockUnknownNetwork;
    if (!p.approvedHome) return PolicyAction::BlockUntrusted;
    if (!p.secured) return PolicyAction::BlockUnsecured;
    if (p.cost==DataCost::Metered) return PolicyAction::BlockMetered;
    if (p.cost!=DataCost::Unmetered) return PolicyAction::BlockCostUnknown;
    return PolicyAction::StartRemote;
}
