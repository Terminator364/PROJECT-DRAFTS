#pragma once
#include <windows.h>
#include <wlanapi.h>
#include <netlistmgr.h>
#include <objbase.h>
#include <string>
#include <vector>
#include "g5_network_policy.h"
#pragma comment(lib, "wlanapi.lib")
#pragma comment(lib, "ole32.lib")
#pragma comment(lib, "uuid.lib")

struct NetworkSnapshot {
    WifiClass wifi=WifiClass::Unknown;
    DataCost cost=DataCost::Unknown;
    std::wstring ssid;
    std::wstring wifiAdapterId;
    bool secured=false;
    bool approvedHome=false;
    DWORD error=0;
};
static std::wstring envWide(const wchar_t* name) {
    DWORD n=GetEnvironmentVariableW(name,nullptr,0);
    if(!n || n>4096) return L"";
    std::wstring s(n,L'\0');
    auto k=GetEnvironmentVariableW(name,&s[0],n);
    if(!k || k>=n)return L"";
    s.resize(k);return s;
}
static std::wstring homeFilePath(){
    std::wstring path=envWide(L"LOCALAPPDATA");
    if(path.empty())return L"";
    return path+L"\\MBMPC-RemoteOneClick\\trusted_home_wifi.v1";
}
static std::wstring compactId(GUID guid){
    wchar_t out[64]={};
    if(StringFromGUID2(guid,out,64)<=0)return L"";
    return out;
}
static std::wstring utf8SSID(const DOT11_SSID& value){
    if(!value.uSSIDLength || value.uSSIDLength>DOT11_SSID_MAX_LENGTH) return L"";
    auto n=(int)value.uSSIDLength;
    int len=MultiByteToWideChar(CP_UTF8,MB_ERR_INVALID_CHARS,(const char*)value.ucSSID,n,nullptr,0);
    if(!len || len>64)return L"";
    std::wstring w(len,L'\0');
    MultiByteToWideChar(CP_UTF8,MB_ERR_INVALID_CHARS,(const char*)value.ucSSID,n,&w[0],len);
    for(wchar_t c:w)if(c<32)return L""; // refuse invalid or control-character SSIDs
    return w;
}
static bool loadHome(const std::wstring& ssid,const std::wstring& adapter) {
    std::wstring file=homeFilePath();
    if(file.empty() || ssid.empty() || adapter.empty())return false;
    HANDLE h=CreateFileW(file.c_str(),GENERIC_READ,FILE_SHARE_READ,nullptr,OPEN_EXISTING,FILE_ATTRIBUTE_NORMAL,nullptr);
    if(h==INVALID_HANDLE_VALUE)return false;
    DWORD size=GetFileSize(h,nullptr);
    if(size<4 || size>2048 || size%2){CloseHandle(h);return false;}
    std::vector<wchar_t> data(size/2+1);
    DWORD read=0;BOOL ok=ReadFile(h,data.data(),size,&read,nullptr);
    CloseHandle(h);
    if(!ok || read!=size)return false;
    if(data[0]!=0xFEFF)return false;
    std::wstring text(data.data()+1,size/2-1);
    return text == ssid+L"\n"+adapter;
}
static bool saveHome(const std::wstring& ssid,const std::wstring& adapter){
    if(ssid.empty() || ssid.size()>64 || adapter.empty() || adapter.size()>64)return false;
    auto base=envWide(L"LOCALAPPDATA")+L"\\MBMPC-RemoteOneClick";
    CreateDirectoryW(base.c_str(),nullptr);
    auto final=homeFilePath(), temp=final+L".new";
    if(final.empty())return false;
    std::wstring payload;payload.push_back((wchar_t)0xFEFF);
    payload+=ssid+L"\n"+adapter;
    HANDLE h=CreateFileW(temp.c_str(),GENERIC_WRITE,0,nullptr,CREATE_ALWAYS,FILE_ATTRIBUTE_NORMAL,nullptr);
    if(h==INVALID_HANDLE_VALUE)return false;
    DWORD w=0;auto size=(DWORD)(payload.size()*sizeof(wchar_t));
    BOOL ok=WriteFile(h,payload.data(),size,&w,nullptr);
    ok=ok && (w==size) && FlushFileBuffers(h);
    CloseHandle(h);
    if(!ok){DeleteFileW(temp.c_str());return false;}
    if(!MoveFileExW(temp.c_str(),final.c_str(),MOVEFILE_REPLACE_EXISTING|MOVEFILE_WRITE_THROUGH)) {
        DeleteFileW(temp.c_str());return false;
    }
    return true;
}
static DataCost getWindowsCost(){
    HRESULT init=CoInitializeEx(nullptr,COINIT_MULTITHREADED);
    bool uninit=SUCCEEDED(init);
    INetworkCostManager* mgr=nullptr;
    DataCost result=DataCost::Unknown;
    HRESULT hr=CoCreateInstance(CLSID_NetworkListManager,nullptr,CLSCTX_INPROC_SERVER|CLSCTX_LOCAL_SERVER,
                                IID_PPV_ARGS(&mgr));
    if(SUCCEEDED(hr) && mgr) {
        DWORD cost=0;
        if(SUCCEEDED(mgr->GetCost(&cost,nullptr))){
            if(cost&(NLM_CONNECTION_COST_VARIABLE|NLM_CONNECTION_COST_FIXED|
                     NLM_CONNECTION_COST_OVERDATALIMIT|NLM_CONNECTION_COST_ROAMING|
                     NLM_CONNECTION_COST_APPROACHINGDATALIMIT))result=DataCost::Metered;
            else if(cost==NLM_CONNECTION_COST_UNRESTRICTED)result=DataCost::Unmetered;
            // Congestion without explicit cost classification remains uncertain.
        }
        mgr->Release();
    }
    if(uninit)CoUninitialize();
    return result;
}
static NetworkSnapshot detectNetwork(){
    NetworkSnapshot s;
    if(envWide(L"MBMPC_LAB_MODE")==L"1"){
        auto wifi=envWide(L"MBMPC_LAB_WIFI");
        s.wifi= wifi==L"none"?WifiClass::NoWifi:wifi==L"denied"?WifiClass::PermissionDenied:
                wifi==L"unknown"?WifiClass::Unknown:WifiClass::Connected;
        s.ssid=wifi==L"home"?L"Lab Home WiFi":wifi==L"other"?L"Lab Campus Hotspot":L"";
        s.wifiAdapterId=L"{LAB-ADAPTER-01}";
        s.secured=envWide(L"MBMPC_LAB_OPEN")!=L"1";
        s.approvedHome=wifi==L"home" && envWide(L"MBMPC_LAB_TRUST")==L"1";
        auto cost=envWide(L"MBMPC_LAB_COST");
        s.cost=cost==L"free"?DataCost::Unmetered:cost==L"metered"?DataCost::Metered:DataCost::Unknown;
        return s;
    }
    HANDLE handle=nullptr;DWORD ver=0;
    DWORD r=WlanOpenHandle(2,nullptr,&ver,&handle);
    if(r!=ERROR_SUCCESS){s.error=r;return s;}
    PWLAN_INTERFACE_INFO_LIST interfaces=nullptr;
    r=WlanEnumInterfaces(handle,nullptr,&interfaces);
    if(r!=ERROR_SUCCESS){
        s.error=r;WlanCloseHandle(handle,nullptr);return s;
    }
    s.wifi=WifiClass::NoWifi;
    for(DWORD i=0;i<interfaces->dwNumberOfItems;i++){
        auto& nic=interfaces->InterfaceInfo[i];
        if(nic.isState!=wlan_interface_state_connected) continue;
        DWORD size=0;PVOID buffer=nullptr;
        r=WlanQueryInterface(handle,&nic.InterfaceGuid,wlan_intf_opcode_current_connection,
                             nullptr,&size,&buffer,nullptr);
        if(r==ERROR_ACCESS_DENIED){s.wifi=WifiClass::PermissionDenied;s.error=r;break;}
        if(r!=ERROR_SUCCESS || !buffer || size<sizeof(WLAN_CONNECTION_ATTRIBUTES)){
            s.wifi=WifiClass::Unknown;s.error=r;
            if(buffer)WlanFreeMemory(buffer);
            break;
        }
        auto* conn=(WLAN_CONNECTION_ATTRIBUTES*)buffer;
        s.ssid=utf8SSID(conn->wlanAssociationAttributes.dot11Ssid);
        s.wifiAdapterId=compactId(nic.InterfaceGuid);
        s.secured=conn->wlanSecurityAttributes.bSecurityEnabled!=FALSE;
        s.wifi=s.ssid.empty()?WifiClass::Unknown:WifiClass::Connected;
        WlanFreeMemory(buffer);
        break;
    }
    if(interfaces)WlanFreeMemory(interfaces);
    WlanCloseHandle(handle,nullptr);
    if(s.wifi==WifiClass::Connected){
        s.approvedHome=loadHome(s.ssid,s.wifiAdapterId);
        s.cost=getWindowsCost();
    }
    return s;
}
