"""Single deterministic local report for the simulated lab, no external services."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from bridge_lab import run_scenarios
from audio_sim import run_audio_scenarios
from display_sim import DisplayProfile, simulate_stream

def report():
    bridge=run_scenarios()
    audio=run_audio_scenarios()
    display={name:simulate_stream(profile) for name,profile in {
      "motion":DisplayProfile(),
      "frozen":DisplayProfile(frozen=True),
      "black":DisplayProfile(black_screen=True),
      "every_second_frame_lost":DisplayProfile(dropped_every=2)
    }.items()}
    expected={
      "normal_usb":("SUCCESS","VIRTUAL_AGENT_RESPONSE"),
      "pc_cloud_offline_usb_still_works":("SUCCESS","VIRTUAL_AGENT_RESPONSE"),
      "cable_removed":("QUEUED","USB_CABLE_UNPLUGGED"),
      "charge_only":("QUEUED","USB_DATA_UNAVAILABLE"),
      "phone_offline":("QUEUED","PHONE_CLOUD_OFFLINE"),
      "phone_asleep":("QUEUED","PHONE_ASLEEP"),
      "pc_asleep":("QUEUED","PC_ASLEEP"),
      "pc_agent_crashed":("UNAVAILABLE","PC_AGENT_DOWN"),
      "guardian_repairs_agent":("SUCCESS","SUPERVISOR_RECOVERY_SIMULATED"),
      "supervisor_down":("FAILED","SUPERVISOR_DOWN"),
      "unpaired_phone":("REJECTED","NOT_PAIRED"),
      "mutation_requires_approval":("REJECTED","LOCAL_APPROVAL_REQUIRED"),
      "approved_sandbox_write":("SUCCESS","VIRTUAL_WRITE"),
      "sandbox_escape":("REJECTED","SANDBOX_PATH_REQUIRED"),
      "battery_critical":("QUEUED","PHONE_BATTERY_CRITICAL"),
      "valid_packet":("SUCCESS","VIRTUAL_AGENT_RESPONSE"),
      "replay_rejected":("REJECTED","REPLAY"),
      "tamper_rejected":("REJECTED","BAD_SIGNATURE"),
      "wrong_device_rejected":("REJECTED","DEVICE_IDENTITY_MISMATCH")
    }
    checks={name:bridge[name].get("status")==status and bridge[name].get("reason")==reason
      for name,(status,reason) in expected.items()}
    recovered=bridge["offline_queue_then_resume"]
    checks["offline_queue_then_resume"]=recovered["queued"]["status"]=="QUEUED" and len(recovered["flushed"])==1 and recovered["flushed"][0]["status"]=="SUCCESS"
    checks.update({
       "mic_mute":audio["mic_muted"]["is_silent"],
       "mic_clipping":audio["high_gain_clipping"]["clipped_samples"]>0,
       "audio_loss":audio["audio_packet_loss_100pct"]["is_silent"],
       "frozen_video":display["frozen"]["frozen_detected"],
       "motion_video":display["motion"]["unique_frames"]>1,
       "black_video":display["black"]["black_screen"],
       "video_loss":display["every_second_frame_lost"]["dropped_frames"]>0
    })
    return {"schema":"usb-rescue-lab-report/1",
      "scope":"SIMULATED_ONLY_NO_REAL_USB_ANDROID_WINDOWS_CHATGPT_CONTROL",
      "checks_passed":sum(checks.values()),"checks_total":len(checks),
      "all_passed":all(checks.values()),"checks":checks,
      "bridge":bridge,"audio":audio,"display":display,
      "field_gates":{"android_apk_on_avd":"NOT_RUN",
                     "android_apk_on_real_phone":"NOT_RUN",
                     "usb_connection_real_phone_windows":"NOT_RUN",
                     "windows_service_auto_restart":"NOT_RUN",
                     "chatgpt_authenticated_job_ingress":"NOT_IMPLEMENTED",
                     "real_remote_desktop_integration":"NOT_IMPLEMENTED"}}

if __name__=="__main__":
    parser=argparse.ArgumentParser(description="Run synthetic rescue bridge/audio/desktop scenarios.")
    parser.add_argument("--out",help="Optional path of JSON report")
    args=parser.parse_args()
    result=report()
    payload=json.dumps(result,ensure_ascii=False,indent=2)
    if args.out:
        path=Path(args.out)
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(payload+"\n",encoding="utf-8")
    print("SIMULATION:",result["checks_passed"],"/",result["checks_total"],"checks passed")
    print("FIELD: NOT RUN. The simulator is not proof of USB or remote access.")
    if args.out: print("Report:",args.out)
    if not result["all_passed"]: raise SystemExit(1)
