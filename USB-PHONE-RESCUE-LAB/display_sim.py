"""Generate purely synthetic desktop screenshots and simulated frame transport."""
from __future__ import annotations
import hashlib
from dataclasses import dataclass

@dataclass(frozen=True)
class DisplayProfile:
    width: int = 64
    height: int = 36
    black_screen: bool = False
    frozen: bool = False
    dropped_every: int = 0

def frame(profile: DisplayProfile, frame_id: int):
    if profile.width < 1 or profile.height < 1 or profile.width*profile.height > 1920*1080:
        raise ValueError("invalid virtual display geometry")
    if frame_id < 0:
        raise ValueError("invalid frame id")
    index = 0 if profile.frozen else frame_id
    pixels = bytearray()
    for y in range(profile.height):
        for x in range(profile.width):
            if profile.black_screen:
                pixels.extend((0,0,0))
            else:
                pixels.extend(((x*7+index*13)%256,(y*9+index*3)%256,(x+y+index*5)%256))
    return bytes(pixels)

def simulate_stream(profile: DisplayProfile, count=6):
    if not 0 < count <= 100:
        raise ValueError("invalid frame count")
    hashes = []
    drops = 0
    for i in range(count):
        if profile.dropped_every and (i+1)%profile.dropped_every==0:
            drops += 1
            continue
        hashes.append(hashlib.sha256(frame(profile,i)).hexdigest())
    return {"mode":"SIMULATED_NOT_REAL_DESKTOP", "expected_frames":count,
            "delivered_frames":len(hashes),"dropped_frames":drops,
            "unique_frames":len(set(hashes)),
            "frozen_detected":len(set(hashes))==1 and len(hashes)>1,
            "black_screen":profile.black_screen}

def write_ppm(path, profile=DisplayProfile(), frame_id=0):
    rgb=frame(profile,frame_id)
    with open(path,"wb") as out:
        out.write(f"P6\\n{profile.width} {profile.height}\\n255\\n".replace("\\n","\n").encode("ascii"))
        out.write(rgb)

if __name__=="__main__":
    import argparse,json
    p=argparse.ArgumentParser()
    p.add_argument("--ppm",help="Optional path for one synthetic screenshot")
    args=p.parse_args()
    if args.ppm:
        write_ppm(args.ppm)
    for mode, profile in [
        ("animated",DisplayProfile()),
        ("frozen",DisplayProfile(frozen=True)),
        ("black",DisplayProfile(black_screen=True)),
        ("packet_loss",DisplayProfile(dropped_every=2))]:
        print(mode,json.dumps(simulate_stream(profile)))
