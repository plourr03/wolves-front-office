"""Assemble the One Summer voiceover track (clone or preview voice).

Pipeline: synthesize one clip per beat (ElevenLabs clone by name/id, or free
Edge TTS for previews) -> probe real durations -> RE-TIME the beats so each
line starts a natural pause after the previous one ends (the audio is the
master clock) -> print the timeline.ts starts to paste -> mix with a tail
fade per clip (no clipped breaths) plus a faint original clock-pulse bed ->
public/voiceover_clone.mp3 (or voiceover_ai.mp3 for the Edge preview).

Modes:
  python scripts/make_ai_vo.py --elevenlabs-name bobby    (the real one)
  python scripts/make_ai_vo.py --elevenlabs VOICE_ID
  python scripts/make_ai_vo.py --assemble-only            (mix existing clips)
  python scripts/make_ai_vo.py                            (Edge TTS preview)
  add --no-bed to skip the music bed

After it prints the new starts, update src/timeline.ts to match, then render:
  npx remotion render Clip out/one_summer_reel_clone_vo.mp4
      --props="{\"voiceoverSrc\":\"voiceover_clone.mp3\"}"
"""

import asyncio
import json
import math
import os
import struct
import subprocess
import sys
import time
import urllib.request
import wave

import edge_tts

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SEG_DIR = os.path.join(ROOT, "out", "vo_segments")
OUT = os.path.join(ROOT, "public", "voiceover_ai.mp3")
BED_WAV = os.path.join(ROOT, "out", "bed.wav")

VOICE = "en-US-AndrewMultilingualNeural"  # Edge preview voice

# Expressive settings for the clone: lower stability = more life, a bit of
# style exaggeration for the sports-desk energy.
ELEVEN_SETTINGS = {"stability": 0.30, "similarity_boost": 0.80, "style": 0.45}

# Per-line tweaks, merged over the base settings. h44: the hook read too slow
# (8.4s), so it gets the max delivery speed. unsig2: the extension line came
# out movie-trailer intense; calm it down.
SETTING_OVERRIDES = {
    "h44": {"speed": 1.15},
    "unsig2": {"stability": 0.55, "style": 0.12},
    # twomax2 read as a slow question; steady it and pick up the pace a touch.
    "twomax2": {"stability": 0.50, "style": 0.20, "speed": 1.07},
}

# Faint original clock-pulse bed (soft low thump / tick alternating). Peak
# gain of the bed relative to full scale; the voice peaks around 0.8.
BED_GAIN = 0.10
BED_BPM = 72

# (beat id, spoken line). Starts are COMPUTED from clip durations + gaps.
# Bobby's rewritten script (2026-07-14 kit edit), grammar normalized; flagged
# changes: "honestly" dropped (house banned word), "this summer" -> "that
# summer" (he means 2029), "similar clip then they have been" -> "the clip
# they have been."
SEGMENTS = [
    ("h44", "The odds of Ant leaving the Minnesota Timberwolves in his 2029 walk year sit somewhere near 44 percent."),
    ("h1", "The whole LaMelo trade comes down to that one summer."),
    ("y2029", "2029. Ant's walk year."),
    ("y2029b", "And history is not kind to teams with stars on walk years."),
    ("curve1", "Ant has two years left on his contract."),
    ("curve1c", "And his odds of leaving this year? Only about 1 percent."),
    ("curve1b", "But we're not worried about this year."),
    ("curve2", "In the walk year, the odds of Ant leaving skyrocket to 44 percent."),
    ("curve2s", "And that's if the Wolves keep winning at the clip they have been."),
    ("curve2b", "Let's say the Wolves have a bad year and win at just a 37-win pace?"),
    ("curve2c", "The odds of him leaving jump to 56."),
    ("curve3", "And this is based on forty years of data, not a gut feeling."),
    ("unsig", "Not only that, but LaMelo's deal ends the same July."),
    ("unsig2", "And we still have not extended him."),
    ("twomax", "So, we have two max guys."),
    ("twomaxb", "One summer that the next decade of basketball in Minnesota hinges on."),
    ("twomax2", "The Wolves and Hornets both made opposing bets on where that summer will land."),
    ("cta1", "What are the most likely futures for that summer?"),
    ("cta2", "Comment BILL and I'll send you the link to the Part 1 article."),
]

# Pause AFTER each beat's line ends (seconds). Tight inside a thought, bigger
# between ideas and after the heavy moments.
GAP_AFTER = {
    "h44": 0.6, "h1": 0.7, "y2029": 0.35, "y2029b": 0.7, "curve1": 0.35,
    "curve1c": 0.5, "curve1b": 0.8, "curve2": 0.7, "curve2s": 0.8,
    "curve2b": 0.35, "curve2c": 0.9, "curve3": 1.0, "unsig": 0.4,
    "unsig2": 0.9, "twomax": 0.4, "twomaxb": 0.6, "twomax2": 0.9, "cta1": 0.4,
}
CTA_HOLD = 2.4  # dwell on the CTA card after the line ends
LOOP_LEN = 0.5

COMPOSITOR = os.path.join(ROOT, "node_modules", "@remotion", "compositor-win32-x64-msvc")
FFMPEG = os.path.join(COMPOSITOR, "ffmpeg.exe")
FFPROBE = os.path.join(COMPOSITOR, "ffprobe.exe")


async def synth_edge():
    os.makedirs(SEG_DIR, exist_ok=True)
    for bid, text in SEGMENTS:
        await edge_tts.Communicate(text, VOICE).save(os.path.join(SEG_DIR, f"{bid}.mp3"))
        print(f"  {bid}: {text[:50]}...")


def load_elevenlabs_key():
    key = os.environ.get("ELEVENLABS_API_KEY")
    if key:
        return key
    env_path = os.path.normpath(os.path.join(ROOT, "..", "..", "..", ".env"))
    if os.path.exists(env_path):
        for line in open(env_path, encoding="utf-8-sig"):
            line = line.strip()
            if line.startswith("ELEVENLABS_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


def api_call(req, retries=6, wait=2.0):
    """The key auths intermittently right after creation; retry through blips."""
    import urllib.error

    last = None
    for i in range(retries):
        try:
            with urllib.request.urlopen(req) as resp:
                return resp.read()
        except urllib.error.HTTPError as e:
            last = f"{e.code} {e.read().decode()[:160]}"
            print(f"    retry {i + 1}/{retries} ({e.code})...")
            time.sleep(wait)
    raise RuntimeError(f"ElevenLabs call failed after {retries} tries: {last}")


def resolve_voice_id(name, api_key):
    req = urllib.request.Request("https://api.elevenlabs.io/v1/voices", headers={"xi-api-key": api_key})
    voices = json.loads(api_call(req))["voices"]
    for v in voices:
        if v["name"].lower().strip() == name.lower().strip():
            print(f"voice '{v['name']}' ({v.get('category')}) -> {v['voice_id']}")
            return v["voice_id"]
    cloned = [f"{v['name']} ({v.get('category')})" for v in voices if v.get("category") != "premade"]
    raise RuntimeError(f"No voice named '{name}'. Non-stock voices on the account: {cloned}")


def synth_elevenlabs(voice_id, api_key, only=None):
    """One clip per beat, each generated WITH its neighbors as prosody context
    so lines flow into each other instead of restarting cold. `only` limits
    regeneration to a subset of beat ids (cheap single-line fixes)."""
    os.makedirs(SEG_DIR, exist_ok=True)
    for i, (bid, text) in enumerate(SEGMENTS):
        if only is not None and bid not in only:
            continue
        payload = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {**ELEVEN_SETTINGS, **SETTING_OVERRIDES.get(bid, {})},
        }
        if i > 0:
            payload["previous_text"] = SEGMENTS[i - 1][1]
        if i + 1 < len(SEGMENTS):
            payload["next_text"] = SEGMENTS[i + 1][1]
        req = urllib.request.Request(
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}?output_format=mp3_44100_128",
            data=json.dumps(payload).encode("utf-8"),
            headers={"xi-api-key": api_key, "Content-Type": "application/json"},
        )
        with open(os.path.join(SEG_DIR, f"{bid}.mp3"), "wb") as f:
            f.write(api_call(req))
        print(f"  {bid}: {text[:50]}...")


def ffprobe_duration(path):
    out = subprocess.run(
        [FFPROBE, "-v", "error", "-show_entries", "format=duration", "-of", "json", path],
        capture_output=True, text=True, cwd=ROOT
    )
    return float(json.loads(out.stdout)["format"]["duration"])


def make_faded_wav(bid):
    """Decode a clip to wav and bake in a 150ms tail fade (and a 10ms head
    fade), since the bundled ffmpeg has no afade filter. Kills the clipped
    breath at every line's end."""
    import numpy as np

    src = os.path.join(SEG_DIR, f"{bid}.mp3")
    dst = os.path.join(SEG_DIR, f"{bid}_faded.wav")
    tmp = os.path.join(SEG_DIR, f"{bid}_tmp.wav")
    subprocess.run([FFMPEG, "-v", "error", "-y", "-i", src, tmp], cwd=ROOT, capture_output=True)
    with wave.open(tmp) as w:
        params = w.getparams()
        frames = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).copy()
    ch = params.nchannels
    sr = params.framerate
    a = frames.reshape(-1, ch).astype(np.float64)
    tail = min(int(0.15 * sr), len(a))
    head = min(int(0.01 * sr), len(a))
    a[-tail:] *= np.linspace(1, 0, tail)[:, None]
    a[:head] *= np.linspace(0, 1, head)[:, None]
    with wave.open(dst, "w") as w:
        w.setparams(params)
        w.writeframes(a.astype(np.int16).tobytes())
    os.remove(tmp)
    return dst


def write_bed(end_sec):
    """Original minimal heartbeat bed: a soft 54 Hz thump every other beat,
    nothing in the highs (the earlier tick poked through speech and read as
    'ticking noise'). Felt more than heard. Synthesized, nothing to license."""
    sr = 44100
    n = int(end_sec * sr)
    buf = [0.0] * n
    period = 60.0 / BED_BPM
    t = 0.0
    beat = 0
    while t < end_sec:
        start = int(t * sr)
        if beat % 2 == 0:  # thump only; offbeats stay silent
            for j in range(int(0.25 * sr)):
                if start + j >= n:
                    break
                x = j / sr
                buf[start + j] += math.sin(2 * math.pi * 54 * x) * math.exp(-x / 0.045)
        t += period
        beat += 1
    fade = int(0.6 * sr)
    for j in range(min(fade, n)):
        buf[j] *= j / fade
        buf[n - 1 - j] *= j / fade
    peak = max(abs(v) for v in buf) or 1.0
    scale = BED_GAIN / peak
    with wave.open(BED_WAV, "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(b"".join(struct.pack("<h", int(max(-1, min(1, v * scale)) * 32767)) for v in buf))
    print(f"bed: {end_sec:.1f}s clock pulse at {BED_BPM} bpm, peak {BED_GAIN}")


def main():
    global OUT
    clone = "--elevenlabs" in sys.argv or "--elevenlabs-name" in sys.argv or "--assemble-only" in sys.argv
    if clone:
        OUT = os.path.join(ROOT, "public", "voiceover_clone.mp3")

    if "--assemble-only" in sys.argv:
        print("assemble-only: using existing clips in out/vo_segments")
    elif clone:
        api_key = load_elevenlabs_key()
        if not api_key:
            print("No ELEVENLABS_API_KEY found (env var or repo .env). Add it and re-run.")
            sys.exit(1)
        if "--elevenlabs-name" in sys.argv:
            voice_id = resolve_voice_id(sys.argv[sys.argv.index("--elevenlabs-name") + 1], api_key)
        else:
            voice_id = sys.argv[sys.argv.index("--elevenlabs") + 1]
        # --only h44,unsig2 regenerates just those lines; the rest are reused.
        only = None
        if "--only" in sys.argv:
            only = set(sys.argv[sys.argv.index("--only") + 1].split(","))
        print(f"synthesizing {len(only) if only else len(SEGMENTS)} segments (expressive settings, with context)...")
        synth_elevenlabs(voice_id, api_key, only)
    else:
        print(f"synthesizing {len(SEGMENTS)} segments with {VOICE}...")
        asyncio.run(synth_edge())

    # Re-time: each beat starts a natural pause after the previous line ends.
    durs = {bid: ffprobe_duration(os.path.join(SEG_DIR, f"{bid}.mp3")) for bid, _ in SEGMENTS}
    starts = {}
    t = 0.0
    for bid, _ in SEGMENTS:
        starts[bid] = round(t, 1)
        t = starts[bid] + durs[bid] + GAP_AFTER.get(bid, CTA_HOLD)
    last = SEGMENTS[-1][0]
    loop_start = round(starts[last] + durs[last] + CTA_HOLD, 1)
    end_sec = round(loop_start + LOOP_LEN, 1)

    print("\nPASTE INTO src/timeline.ts (keep the captions):")
    for bid, _ in SEGMENTS:
        print(f"  {bid}: startSec {starts[bid]}   (clip {durs[bid]:.2f}s)")
    print(f"  loop: startSec {loop_start}")
    print(f"  END_SEC = {end_sec}\n")

    # Mix: tail-fade each clip (no clipped breaths), delay to its start, add
    # the bed unless --no-bed, sum, normalize toward -14 LUFS.
    use_bed = "--no-bed" not in sys.argv
    if use_bed:
        write_bed(end_sec)
    inputs, filters, labels = [], [], []
    for i, (bid, _) in enumerate(SEGMENTS):
        inputs += ["-i", make_faded_wav(bid)]
        ms = int(round(starts[bid] * 1000))
        filters.append(f"[{i}:a]adelay={ms}|{ms}[a{i}]")
        labels.append(f"[a{i}]")
    if use_bed:
        idx = len(SEGMENTS)
        inputs += ["-i", BED_WAV]
        filters.append(f"[{idx}:a]anull[a{idx}]")
        labels.append(f"[a{idx}]")
    filters.append(f"{''.join(labels)}amix=inputs={len(labels)}:normalize=0[mix]")
    filters.append("[mix]loudnorm=I=-14:TP=-1.5:LRA=11[out]")
    cmd = [FFMPEG, "-y"] + inputs + ["-filter_complex", ";".join(filters), "-map", "[out]", "-b:a", "192k", OUT]
    print("mixing...")
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
    if r.returncode != 0:
        print(r.stderr[-1500:])
        sys.exit(1)
    print(f"wrote {OUT} ({ffprobe_duration(OUT):.1f}s)")


if __name__ == "__main__":
    main()
