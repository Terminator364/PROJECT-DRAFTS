#pragma once
// G6 private, atomic, multi-network allowlist. No background tasks.
#include <windows.h>
#include <string>
#include <vector>
#include <algorithm>

struct RemoteApprovedNetwork {
    std::wstring ssid;
    std::wstring adapter;
};
static bool validName(const std::wstring& v,size_t limit){
    if(v.empty()||v.size()>limit) return false;
    for(wchar_t c:v) if(c<32||c==127||c==L'|'||c==L'\\')return false;
    return true;
}
static bool validEntry(const RemoteApprovedNetwork& n){
    return validName(n.ssid,64)&&validName(n.adapter,64);
}
static std::wstring approvedPath(){
    wchar_t* raw=nullptr;
    size_t len=0;
    _wdupenv_s(&raw,&len,L"LOCALAPPDATA");
    if(!raw)return L"";
    std::wstring root=raw;
    free(raw);
    return root+L"\\MBMPC-RemoteOneClick\\approved_networks.v2";
}
static std::wstring legacyPath(){
    auto s=approvedPath();
    return s.empty()?s:s.substr(0,s.find_last_of(L'\\'))+L"\\trusted_home_wifi.v1";
}
static std::wstring encodeEntries(const std::vector<RemoteApprovedNetwork>& entries){
    std::wstring text=L"\xFEFFMBMPC_G6_NETWORKS_V2\n";
    for(const auto& e:entries)text+=e.ssid+L"|"+e.adapter+L"\n";
    return text;
}
static bool loadUtf16File(const std::wstring& path,std::wstring& text,size_t maxBytes=8192){
    text.clear();
    if(path.empty())return false;
    HANDLE h=CreateFileW(path.c_str(),GENERIC_READ,FILE_SHARE_READ,nullptr,OPEN_EXISTING,FILE_ATTRIBUTE_NORMAL,nullptr);
    if(h==INVALID_HANDLE_VALUE)return false;
    DWORD n=GetFileSize(h,nullptr);
    if(n<4||n>maxBytes||(n%2)){CloseHandle(h);return false;}
    std::vector<wchar_t> buffer(n/2);
    DWORD read=0;
    BOOL ok=ReadFile(h,buffer.data(),n,&read,nullptr);
    CloseHandle(h);
    if(!ok||read!=n||buffer[0]!=0xFEFF)return false;
    text.assign(buffer.begin()+1,buffer.end());
    return true;
}
static bool parseNetworkEntries(const std::wstring& content,std::vector<RemoteApprovedNetwork>& out){
    out.clear();
    const std::wstring magic=L"MBMPC_G6_NETWORKS_V2\n";
    if(content.compare(0,magic.size(),magic)!=0)return false;
    size_t pos=magic.size();
    while(pos<content.size()){
        auto end=content.find(L'\n',pos);
        if(end==std::wstring::npos)return false;
        std::wstring line=content.substr(pos,end-pos);
        auto sep=line.find(L'|');
        if(sep==std::wstring::npos||line.find(L'|',sep+1)!=std::wstring::npos)return false;
        RemoteApprovedNetwork item{line.substr(0,sep),line.substr(sep+1)};
        if(!validEntry(item)||out.size()>=20)return false;
        auto same=[&](const RemoteApprovedNetwork& n){return n.ssid==item.ssid&&_wcsicmp(n.adapter.c_str(),item.adapter.c_str())==0;};
        if(std::any_of(out.begin(),out.end(),same))return false;
        out.push_back(item);
        pos=end+1;
    }
    return true;
}
static bool loadApproved(std::vector<RemoteApprovedNetwork>& out){
    out.clear();
    std::wstring raw;
    const auto path=approvedPath();
    DWORD attr=path.empty()?INVALID_FILE_ATTRIBUTES:GetFileAttributesW(path.c_str());
    if(attr!=INVALID_FILE_ATTRIBUTES){
        // Corrupt V2: fail closed, NEVER silently trust legacy again.
        return loadUtf16File(path,raw)&&parseNetworkEntries(raw,out);
    }
    // Migration reads existing G5 approval but does not trust any other network.
    const auto old=legacyPath();
    if(!loadUtf16File(old,raw,2048))return true;
    const auto sep=raw.find(L'\n');
    if(sep==std::wstring::npos||raw.find(L'\n',sep+1)!=std::wstring::npos)return true;
    RemoteApprovedNetwork e{raw.substr(0,sep),raw.substr(sep+1)};
    if(validEntry(e))out.push_back(e);
    return true;
}
static bool saveApproved(const std::vector<RemoteApprovedNetwork>& entries){
    if(entries.size()>20)return false;
    std::vector<RemoteApprovedNetwork> validated;
    for(auto& e:entries){
        if(!validEntry(e))return false;
        auto cmp=[&](const RemoteApprovedNetwork& n){return n.ssid==e.ssid&&_wcsicmp(n.adapter.c_str(),e.adapter.c_str())==0;};
        if(std::any_of(validated.begin(),validated.end(),cmp))return false;
        validated.push_back(e);
    }
    const auto final=approvedPath();if(final.empty())return false;
    const auto directory=final.substr(0,final.find_last_of(L'\\'));
    CreateDirectoryW(directory.c_str(),nullptr);
    std::wstring text=encodeEntries(entries);
    if(text.size()*2>8192)return false;
    const auto stage=final+L".tmp";
    HANDLE h=CreateFileW(stage.c_str(),GENERIC_WRITE,0,nullptr,CREATE_ALWAYS,FILE_ATTRIBUTE_NORMAL,nullptr);
    if(h==INVALID_HANDLE_VALUE)return false;
    DWORD n=(DWORD)(text.size()*sizeof(wchar_t)),written=0;
    BOOL ok=WriteFile(h,text.data(),n,&written,nullptr);
    if(ok&&written==n)ok=FlushFileBuffers(h);
    CloseHandle(h);
    if(!ok||written!=n){DeleteFileW(stage.c_str());return false;}
    if(!MoveFileExW(stage.c_str(),final.c_str(),MOVEFILE_REPLACE_EXISTING|MOVEFILE_WRITE_THROUGH)){
        DeleteFileW(stage.c_str());return false;
    }
    return true;
}
static bool hasApproved(const std::wstring& ssid,const std::wstring& adapter){
    std::vector<RemoteApprovedNetwork> list;
    if(!loadApproved(list))return false;
    for(auto& e:list)if(e.ssid==ssid&&_wcsicmp(e.adapter.c_str(),adapter.c_str())==0)return true;
    return false;
}
// Fail-closed cross-process mutex for settings saved by two simultaneous clicks.
struct ApprovedListWriteLock {
    HANDLE h=nullptr;
    bool acquired=false;
    ApprovedListWriteLock(){
        h=CreateMutexW(nullptr,FALSE,L"Local\\MBMPC_REMOTE_APPROVED_NETWORKS_V2");
        if(h){
            DWORD result=WaitForSingleObject(h,1300);
            acquired=(result==WAIT_OBJECT_0 || result==WAIT_ABANDONED);
        }
    }
    ~ApprovedListWriteLock(){
        if(h){if(acquired)ReleaseMutex(h);CloseHandle(h);}
    }
};
static bool grantApproved(const RemoteApprovedNetwork& entry){
    if(!validEntry(entry))return false;
    ApprovedListWriteLock guard;if(!guard.acquired)return false;
    std::vector<RemoteApprovedNetwork> list;
    if(!loadApproved(list))return false;
    for(auto& e:list)if(e.ssid==entry.ssid&&_wcsicmp(e.adapter.c_str(),entry.adapter.c_str())==0){
        // Existing G5 approval migrates to V2 on the first confirmation.
        return GetFileAttributesW(approvedPath().c_str())!=INVALID_FILE_ATTRIBUTES || saveApproved(list);
    }
    if(list.size()>=20)return false;
    list.push_back(entry);
    return saveApproved(list);
}
static bool revokeApproved(const RemoteApprovedNetwork& entry){
    ApprovedListWriteLock guard;if(!guard.acquired)return false;
    std::vector<RemoteApprovedNetwork> list;
    if(!loadApproved(list))return false;
    const auto old=list.size();
    list.erase(std::remove_if(list.begin(),list.end(),[&](const RemoteApprovedNetwork& e){
        return e.ssid==entry.ssid&&_wcsicmp(e.adapter.c_str(),entry.adapter.c_str())==0;
    }),list.end());
    return list.size()==old?false:saveApproved(list);
}
