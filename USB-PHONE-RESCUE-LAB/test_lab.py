"""Unit tests for simulation contracts; these never touch real USB or Windows."""
import unittest
from bridge_lab import RescueLab, Conditions, run_scenarios
from audio_sim import AudioProfile, synthesize, run_audio_scenarios

class BridgeTests(unittest.TestCase):
    def test_happy_usb(self):
        r = RescueLab().submit("health")
        self.assertEqual("SUCCESS", r["status"])
    def test_pc_cloud_is_not_required(self):
        r = RescueLab(Conditions(pc_internet=False)).submit("health")
        self.assertEqual("SUCCESS", r["status"])
        self.assertFalse(r["value"]["pc_internet"])
    def test_usb_removed_queues(self):
        r = RescueLab(Conditions(cable_plugged=False)).submit("ping")
        self.assertEqual(("QUEUED", "USB_CABLE_UNPLUGGED"), (r["status"],r["reason"]))
    def test_charge_only_queues(self):
        self.assertEqual("USB_DATA_UNAVAILABLE", RescueLab(Conditions(usb_network_enabled=False)).submit("ping")["reason"])
    def test_phone_cloud_offline_queues_and_recovers(self):
        lab = RescueLab(Conditions(phone_internet=False))
        self.assertEqual("QUEUED", lab.submit("health")["status"])
        lab.conditions.phone_internet = True
        self.assertEqual("SUCCESS", lab.flush()[0]["status"])
        self.assertFalse(lab.pending)
    def test_agent_down_requires_guardian(self):
        lab = RescueLab(Conditions(pc_agent_running=False))
        self.assertEqual("UNAVAILABLE", lab.submit("health")["status"])
        self.assertEqual("SUCCESS", lab.submit("restart_agent", approved=True)["status"])
        self.assertEqual("SUCCESS", lab.submit("ping")["status"])
    def test_dead_guardian_does_not_fake_recovery(self):
        lab = RescueLab(Conditions(pc_agent_running=False, supervisor_running=False))
        self.assertEqual("FAILED", lab.submit("restart_agent",approved=True)["status"])
        self.assertFalse(lab.conditions.pc_agent_running)
    def test_unauthorized_write_has_no_side_effects(self):
        lab = RescueLab()
        original = dict(lab.files)
        r = lab.submit("write_file", {"path":"/lab/a.txt","content":"new"})
        self.assertEqual("REJECTED", r["status"])
        self.assertEqual(original,lab.files)
    def test_approved_write_sandbox_only(self):
        lab = RescueLab()
        self.assertEqual("SUCCESS",lab.submit("write_file",{"path":"/lab/a.txt","content":"hello"},approved=True)["status"])
        self.assertEqual("hello",lab.submit("read_file",{"path":"/lab/a.txt"})["value"])
        self.assertEqual("REJECTED",lab.submit("read_file",{"path":"/lab/../outside"})["status"])
        self.assertEqual("REJECTED",lab.submit("write_file",{"path":"C:/Windows/test","content":"bad"},approved=True)["status"])
    def test_unpaired_rejected(self):
        lab = RescueLab(Conditions(device_paired=False))
        self.assertEqual("NOT_PAIRED",lab.submit("health")["reason"])
    def test_replay_rejected(self):
        lab = RescueLab()
        p = lab.packet("health")
        self.assertEqual("SUCCESS",lab.deliver(p)["status"])
        self.assertEqual("REPLAY",lab.deliver(p)["reason"])
    def test_mac_tamper(self):
        lab = RescueLab()
        p = lab.packet("health")
        p["envelope"]["action"] = "write_file"
        self.assertEqual("BAD_SIGNATURE",lab.deliver(p)["reason"])
    def test_wrong_target(self):
        lab = RescueLab()
        self.assertEqual("DEVICE_IDENTITY_MISMATCH",lab.deliver(lab.packet("ping", target="NO"))["reason"])
    def test_shell_does_not_exist(self):
        lab = RescueLab()
        self.assertEqual("ACTION_NOT_ALLOWED",lab.submit("shell",{"command":"echo hi"}, approved=True)["reason"])
    def test_no_false_work_while_sleeping(self):
        lab = RescueLab(Conditions(pc_awake=False))
        self.assertEqual("QUEUED",lab.submit("ping")["status"])
        lab.conditions.pc_awake = True
        self.assertEqual("SUCCESS",lab.flush()[0]["status"])
    def test_queue_order_preserved(self):
        lab = RescueLab(Conditions(cable_plugged=False))
        lab.submit("ping")
        lab.submit("health")
        lab.conditions.cable_plugged = True
        receipts = lab.flush()
        self.assertEqual([1,2],[r["sequence"] for r in receipts])
        self.assertTrue(all(r["status"]=="SUCCESS" for r in receipts))
    def test_fixed_scenario_catalog(self):
        r = run_scenarios()
        self.assertGreaterEqual(len(r),19)
        self.assertEqual("REPLAY",r["replay_rejected"]["reason"])

class AudioTests(unittest.TestCase):
    def test_clean_pcm(self):
        samples, report = synthesize(AudioProfile())
        self.assertEqual(4000,len(samples))
        self.assertGreater(report["rms"],0.30)
    def test_mute(self):
        _, r=synthesize(AudioProfile(muted=True))
        self.assertTrue(r["is_silent"])
    def test_clipping(self):
        _, r=synthesize(AudioProfile(gain=2.0))
        self.assertGreater(r["clipped_samples"],0)
    def test_packet_loss(self):
        _, r=synthesize(AudioProfile(packet_loss_rate=1.0))
        self.assertGreater(r["lost_packets"],0)
        self.assertTrue(r["is_silent"])
    def test_deterministic_seed(self):
        p=AudioProfile(packet_loss_rate=0.4,seed=5)
        self.assertEqual(synthesize(p),synthesize(p))
    def test_audio_catalog(self):
        self.assertEqual(6,len(run_audio_scenarios()))

if __name__ == "__main__":
    unittest.main()
