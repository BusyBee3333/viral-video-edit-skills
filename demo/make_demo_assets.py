#!/usr/bin/env python3
"""Generate fully synthetic, IP-clean demo source assets: a percussive test
audio track (no copyrighted music) and simple procedural "footage" (no real
people, no licensed clips) with a matching person-matte sequence, purely for
demonstrating the bundled renderer scripts."""
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image

OUT = Path(__file__).parent / "assets"
OUT.mkdir(parents=True, exist_ok=True)

W, H, FPS = 540, 960, 30


def synth_beat(path: Path, dur: float = 18.0, bpm: float = 128.0, sr: int = 44100):
    import soundfile as sf
    n = int(dur * sr)
    y = np.zeros(n, dtype=np.float32)
    beat = 60.0 / bpm
    t = 0.0
    i = 0
    while t < dur:
        # kick: short decaying low sine burst
        kt = np.arange(int(0.18 * sr)) / sr
        amp = 0.9 if i % 4 == 0 else 0.6
        kick = amp * np.sin(2 * np.pi * 110 * kt) * np.exp(-kt * 22.0)
        s = int(t * sr)
        e = min(n, s + len(kick))
        y[s:e] += kick[: e - s]
        # hat on the off-beat: short noise burst
        if i % 2 == 1:
            ht = np.arange(int(0.05 * sr)) / sr
            hat = 0.25 * np.random.default_rng(i).standard_normal(len(ht)) * np.exp(-ht * 90.0)
            hs = int((t + beat * 0.5) * sr)
            he = min(n, hs + len(hat))
            if hs < n:
                y[hs:he] += hat[: he - hs]
        t += beat
        i += 1
    y = np.clip(y, -1.0, 1.0)
    sf.write(str(path), y, sr)
    print(f"wrote {path} ({dur}s @ {bpm} BPM synthetic kick+hat, no copyrighted content)")


def _plasma(w, h, t, hue=0.0, freq=1.0):
    x = np.linspace(0, 1, w)[None, :]
    y = np.linspace(0, 1, h)[:, None]
    tp = 2 * np.pi
    r = 0.5 + 0.5 * np.sin((x * 6 * freq + t * 0.6) * tp + hue * tp)
    g = 0.5 + 0.5 * np.sin((y * 5 * freq - t * 0.5) * tp + hue * tp + 2.09)
    b = 0.5 + 0.5 * np.sin(((x + y) * 4 * freq + t * 0.3) * tp + hue * tp + 4.18)
    return np.stack([np.broadcast_to(r, (h, w)), np.broadcast_to(g, (h, w)),
                     np.broadcast_to(b, (h, w))], axis=-1)


def _figure_alpha(w, h, t):
    """Soft-edged head+torso blob standing in for a 'person' — no real
    human likeness, purely a synthetic silhouette to prove the matte
    pipeline out."""
    X, Y = np.meshgrid(np.arange(w), np.arange(h))
    cx = w * 0.5 + 0.22 * w * np.sin(t * 0.9)
    cy = h * 0.56 + 0.03 * h * np.sin(t * 1.7)
    head_r = 0.075 * h
    hd = np.sqrt((X - cx) ** 2 + (Y - (cy - 0.16 * h)) ** 2) / head_r
    a_head = np.clip(1.6 - hd * 1.6, 0, 1)
    rx, ry = 0.11 * w, 0.20 * h
    nd = np.sqrt(((X - cx) / rx) ** 2 + ((Y - cy) / ry) ** 2)
    a_torso = np.clip(1.5 - nd * 1.5, 0, 1)
    return np.clip(a_head + a_torso, 0, 1)


def make_pattern_clip(path: Path, dur: float, hue: float, fps: int = FPS, w: int = W, h: int = H):
    ff = subprocess.Popen(
        ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}", "-r", str(fps), "-i", "-",
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", str(path)],
        stdin=subprocess.PIPE)
    n = int(dur * fps)
    for i in range(n):
        t = i / fps
        frame = (_plasma(w, h, t, hue) * 255).astype(np.uint8)
        ff.stdin.write(frame.tobytes())
    ff.stdin.close()
    ff.wait()
    print(f"wrote {path} ({dur}s, hue={hue})")


def make_person_clip(path: Path, mattes_dir: Path, dur: float, fps: int = FPS, w: int = W, h: int = H):
    mattes_dir.mkdir(parents=True, exist_ok=True)
    ff = subprocess.Popen(
        ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}", "-r", str(fps), "-i", "-",
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", str(path)],
        stdin=subprocess.PIPE)
    n = int(dur * fps)
    figure_color = np.array([0.92, 0.80, 0.62])  # warm neutral tone, not a real skin-tone claim
    for i in range(n):
        t = i / fps
        bg = _plasma(w, h, t, hue=0.15, freq=0.22)
        alpha = _figure_alpha(w, h, t)
        frame = bg * (1 - alpha[..., None]) + figure_color[None, None, :] * alpha[..., None]
        ff.stdin.write((frame * 255).astype(np.uint8).tobytes())
        Image.fromarray((alpha * 255).astype(np.uint8), mode="L").save(
            mattes_dir / f"proposal_{i:06d}.png")
    ff.stdin.close()
    ff.wait()
    print(f"wrote {path} + {n} matte frames in {mattes_dir}")


if __name__ == "__main__":
    synth_beat(OUT / "test_beat.wav", dur=18.0, bpm=128.0)
    make_person_clip(OUT / "person_clip.mp4", OUT / "person_mattes", dur=6.0)
    for name, hue in [("pattern_a", 0.0), ("pattern_b", 0.28), ("pattern_c", 0.55), ("pattern_d", 0.78)]:
        make_pattern_clip(OUT / f"{name}.mp4", dur=4.0, hue=hue)
    print("DONE")
