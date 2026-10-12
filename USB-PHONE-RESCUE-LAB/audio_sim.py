"""Synthetic audio test rig: no access to a real microphone, no speech recognition."""
from __future__ import annotations
from dataclasses import dataclass
from math import pi, sin, sqrt
import random
import struct
import wave

@dataclass(frozen=True)
class AudioProfile:
    name: str = "normal"
    sample_rate: int = 8000
    duration_ms: int = 500
    tone_hz: float = 440.0
    gain: float = 0.5
    muted: bool = False
    packet_loss_rate: float = 0.0
    seed: int = 364

def synthesize(profile: AudioProfile):
    if profile.sample_rate < 1000 or profile.sample_rate > 96000:
        raise ValueError("invalid sample rate")
    if not 0 < profile.duration_ms <= 30000:
        raise ValueError("invalid duration")
    if not 0 <= profile.packet_loss_rate <= 1:
        raise ValueError("invalid packet loss")
    if profile.gain < 0:
        raise ValueError("invalid gain")
    rng = random.Random(profile.seed)
    n = int(profile.sample_rate * profile.duration_ms / 1000)
    samples = []
    clipped = 0
    lost_packets = 0
    # Process audio in 20 ms packets, rather than losing random individual samples.
    packet_samples = max(1, int(profile.sample_rate * 0.020))
    for start in range(0, n, packet_samples):
        dropped = rng.random() < profile.packet_loss_rate
        lost_packets += int(dropped)
        for i in range(start, min(n, start + packet_samples)):
            signal = 0.0 if profile.muted or dropped else profile.gain * sin(2*pi*profile.tone_hz*i/profile.sample_rate)
            if abs(signal) > 1.0:
                clipped += 1
            samples.append(int(max(-1, min(1, signal)) * 32767))
    rms = sqrt(sum(x*x for x in samples)/len(samples))/32767 if samples else 0
    peak = max((abs(x) for x in samples), default=0)/32767
    return samples, {"profile": profile.name, "samples": len(samples),
                     "sample_rate": profile.sample_rate, "duration_ms": profile.duration_ms,
                     "peak": round(peak, 4), "rms": round(rms, 4),
                     "clipped_samples": clipped, "lost_packets": lost_packets,
                     "packet_samples": packet_samples,
                     "is_silent": all(x == 0 for x in samples)}

def write_wav(path, samples, rate=8000):
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(rate)
        wav.writeframes(struct.pack("<" + "h"*len(samples), *samples))

def run_audio_scenarios():
    scenarios = [
        AudioProfile(name="clean"),
        AudioProfile(name="mic_muted", muted=True),
        AudioProfile(name="high_gain_clipping", gain=2.0),
        AudioProfile(name="audio_packet_loss_40pct", packet_loss_rate=0.40),
        AudioProfile(name="audio_packet_loss_100pct", packet_loss_rate=1.0),
        AudioProfile(name="low_volume", gain=0.001),
    ]
    return {p.name: synthesize(p)[1] for p in scenarios}

if __name__ == "__main__":
    import argparse
    import json
    parser = argparse.ArgumentParser()
    parser.add_argument("--wav", help="Path of optional synthetic WAV output")
    args = parser.parse_args()
    if args.wav:
        p = AudioProfile()
        samples, report = synthesize(p)
        write_wav(args.wav, samples, p.sample_rate)
        print("WAV generated:", args.wav)
    print(json.dumps(run_audio_scenarios(), indent=2))
