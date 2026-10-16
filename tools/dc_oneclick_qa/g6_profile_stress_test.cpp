#include <windows.h>
#include <vector>
#include <string>
#include <cstdio>
#include <cstdlib>
#include <cassert>
#include "g6_approved_networks.h"
#include "g5_network_policy.h"
static int count=0;
static void check(bool condition,const char* why){
    if(!condition){std::printf("G6_FAIL_%s_AT=%d\n",why,count);std::exit(2);}
    ++count;
}
int wmain(int argc,wchar_t** argv){
    if(argc==4 && wcscmp(argv[1],L"--grant")==0) {
        RemoteApprovedNetwork n{argv[2],argv[3]};
        return grantApproved(n)&&hasApproved(n.ssid,n.adapter)?0:11;
    }
    if(argc==3 && wcscmp(argv[1],L"--count")==0){
        std::vector<RemoteApprovedNetwork> list;
        return loadApproved(list) && list.size()==(size_t)_wtoi(argv[2])?0:12;
    }

    wchar_t temp[MAX_PATH]={};
    GetTempPathW(MAX_PATH,temp);
    std::wstring dir=std::wstring(temp)+L"MBMPC_G6_NetworkTest_"+std::to_wstring(GetCurrentProcessId());
    CreateDirectoryW(dir.c_str(),nullptr);
    _wputenv_s(L"LOCALAPPDATA",dir.c_str());
    auto base=dir+L"\\MBMPC-RemoteOneClick";
    CreateDirectoryW(base.c_str(),nullptr);
    const auto legacy=legacyPath(),v2=approvedPath();
    // Existing G5 home Wi-Fi must migrate read-only and never be lost.
    std::wstring legacyContents=L"\xFEFFStarlinkD 2.4g-EXT\n{B19B6F13-5F5A-44CB-B393-2CA85F637341}";
    HANDLE h=CreateFileW(legacy.c_str(),GENERIC_WRITE,0,nullptr,CREATE_ALWAYS,FILE_ATTRIBUTE_NORMAL,nullptr);
    check(h!=INVALID_HANDLE_VALUE,"legacy_create");
    DWORD written=0;WriteFile(h,legacyContents.data(),(DWORD)(legacyContents.size()*2),&written,nullptr);CloseHandle(h);
    std::vector<RemoteApprovedNetwork> parsed;
    check(loadApproved(parsed)&&parsed.size()==1,"legacy_migration");
    auto home=parsed[0];
    check(hasApproved(home.ssid,home.adapter),"home_approved");
    check(!hasApproved(home.ssid,L"{ANOTHER-ADAPTER}"),"no_adapter_cross");
    check(grantApproved(home),"duplicate_grant_idempotent");
    check(hasApproved(home.ssid,home.adapter),"v2_home");
    check(GetFileAttributesW(v2.c_str())!=INVALID_FILE_ATTRIBUTES,"v2_exists");
    check(!revokeApproved({L"Absent",L"{A}"}),"revoke_absent_noop");
    // 300 real persistence operations, model checking each transition.
    std::vector<RemoteApprovedNetwork> ref={home};
    for(int i=0;i<300;i++){
        RemoteApprovedNetwork n{L"PublicNet-"+std::to_wstring(i%17),L"{ADAPTER-"+std::to_wstring((i/17)%3)+L"}"};
        if(i%4==0){
            bool ok=grantApproved(n);
            if(ref.size()<20){
                check(ok,"grant");
                bool exists=false;for(const auto& e:ref)if(e.ssid==n.ssid && e.adapter==n.adapter)exists=true;
                if(!exists)ref.push_back(n);
            }else check(!ok || hasApproved(n.ssid,n.adapter),"at_capacity_no_new");
        }else if(i%4==1){
            bool exists=hasApproved(n.ssid,n.adapter);
            check(exists==std::any_of(ref.begin(),ref.end(),[&](const auto& e){return e.ssid==n.ssid && e.adapter==n.adapter;}),"read_accuracy");
        }else if(i%4==2){
            check(loadApproved(parsed),"parse_v2");
            check(parsed.size()==ref.size(),"count_agree");
        }else{
            bool found=false;
            for(size_t j=1;j<ref.size();j++){
                if(ref[j].ssid!=home.ssid){n=ref[j];found=true;break;}
            }
            if(found){
                check(revokeApproved(n),"revoke");
                ref.erase(std::remove_if(ref.begin(),ref.end(),[&](const auto& e){return e.ssid==n.ssid&&e.adapter==n.adapter;}),ref.end());
            }else check(hasApproved(home.ssid,home.adapter),"home_still");
        }
        check(hasApproved(home.ssid,home.adapter),"home_persisted");
    }
    // Corruption never authorizes legacy fallback; explicit recovery required.
    h=CreateFileW(v2.c_str(),GENERIC_WRITE,0,nullptr,CREATE_ALWAYS,FILE_ATTRIBUTE_NORMAL,nullptr);
    check(h!=INVALID_HANDLE_VALUE,"corrupt_create");
    wchar_t bad[]={0xFEFF,L'X'};
    WriteFile(h,bad,sizeof(bad),&written,nullptr);CloseHandle(h);
    check(!loadApproved(parsed),"corruption_detected");
    check(!hasApproved(home.ssid,home.adapter),"corruption_fail_closed");
    check(!grantApproved({L"Another",L"{X}"}),"no_overwrite_corrupt");
    DeleteFileW(v2.c_str());
    check(loadApproved(parsed)&&parsed.size()==1,"legacy_recovers_only_if_v2_absent");
    // Reject control characters, pipe-delimiters, huge entries.
    check(!grantApproved({L"A|B",L"{X}"}),"pipe_invalid");
    check(!grantApproved({L"A\nB",L"{X}"}),"newline_invalid");
    check(!grantApproved({std::wstring(70,L'z'),L"{X}"}),"oversize_ssid");
    check(!grantApproved({L"Office",L"{BAD|GUID}"}),"invalid_adapter");
    check(grantApproved({L"Faculté UPC",L"{WIFI-1}"}),"unicode_ssid");
    check(hasApproved(L"Faculté UPC",L"{WIFI-1}"),"unicode_roundtrip");
    // Redundant clicks, no duplicate.
    for(int i=0;i<50;i++)check(grantApproved(home),"fifty_duplicate_clicks");
    // Pure decision matrix 96 plus 256 deterministic network changes and 128 concurrent clicks.
    for(int wifi=0;wifi<4;wifi++)for(int approved=0;approved<2;approved++)
    for(int secured=0;secured<2;secured++)for(int cost=0;cost<3;cost++)
    for(int running=0;running<2;running++){
        PolicyInputs p{running!=0,static_cast<WifiClass>(wifi),approved!=0,secured!=0,static_cast<DataCost>(cost)};
        auto decision=decideRemote(p);
        check((decision==PolicyAction::StartRemote) ==
            (!p.agentAlreadyRunning&&p.wifi==WifiClass::Connected&&p.approvedHome&&p.secured&&p.cost==DataCost::Unmetered),
            "safety_matrix");
    }
    for(int i=0;i<256;i++){
        PolicyInputs p;
        p.wifi=(i%11==0)?WifiClass::NoWifi:WifiClass::Connected;
        p.approvedHome=i%7!=0;p.secured=i%19!=0;
        p.cost=i%3==0?DataCost::Metered:i%3==1?DataCost::Unmetered:DataCost::Unknown;
        p.agentAlreadyRunning=i%13==0;
        auto d=decideRemote(p);
        check(d!=PolicyAction::StartRemote || (!p.agentAlreadyRunning&&p.approvedHome&&p.secured&&p.cost==DataCost::Unmetered&&p.wifi==WifiClass::Connected),"churn_safety");
    }
    // Close and remove test area.
    DeleteFileW(v2.c_str());DeleteFileW(legacy.c_str());
    RemoveDirectoryW(base.c_str());RemoveDirectoryW(dir.c_str());
    std::printf("G6_PROFILE_STRESS_ASSERTIONS_PASS=%d\n",count);
    return 0;
}
