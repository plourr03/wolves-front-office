"""Assemble an AI-voice test VO for the One Summer reel.

Generates one Edge neural-TTS clip per spoken beat (free, no account), places
each at its beat's exact startSec from src/timeline.ts, mixes to a single
track normalized toward the brief's -14 LUFS, and writes
public/voiceover_ai.mp3. This is a PREVIEW/pace-check voice; the shipping
plan remains Bobby's own read (or a consented clone of it), and platforms
want realistic AI audio disclosed if this ever posts as-is.

Run from the one-summer project root:  python scripts/make_ai_vo.py
Then render:  npx remotion render Clip out/one_summer_reel_ai_vo.mp4
              --props="{\"voiceoverSrc\":\"voiceover_ai.mp3\"}"
"""

import asyncio
import json
import os
import subprocess
import sys
import urllib.request

import edge_tts

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SEG_DIR = os.path.join(ROOT, "out", "vo_segments")
OUT = os.path.join(ROOT, "public", "voiceover_ai.mp3")

VOICE = "en-US-AndrewMultilingualNeural"  # conversational, sports-desk adjacent

# (beat id, startSec, spoken line) -- keep in lockstep with src/timeline.ts.
SEGMENTS = [
    ("h44", 0.0, "The odds of Ant leaving in his 2029 walk year are somewhere around 44 percent."),
    ("h1", 5.8, "The whole LaMelo trade comes down to that one summer."),
    ("y2029", 10.8, "2029. Ant's walk year. And history is blunt about walk years."),
    ("curve1", 16.8, "With two years left on his deal, his odds of leaving this year are near 1 percent."),
    ("curve1b", 23.0, "But that isn't what we're worried about."),
    ("curve2", 27.6, "In the walk year, however? 44. And that's with the team winning."),
    ("curve2b", 33.6, "On a 37-win pace? It jumps to 56."),
    ("curve3", 38.6, "That cliff is forty years of stars, not a hot take."),
    ("unsig", 45.2, "And LaMelo's deal ends the same July. Still not extended."),
    ("twomax", 51.8, "Two max guys. One summer."),
    ("twomax2", 54.8, "The Wolves and Charlotte both making opposite bets on that summer."),
    ("cta", 59.2, "We priced all of it across fifty thousand futures. Comment BILL and I'll send you Part 1."),
]


async def synth():
    os.makedirs(SEG_DIR, exist_ok=True)
    for bid, _, text in SEGMENTS:
        path = os.path.join(SEG_DIR, f"{bid}.mp3")
        await edge_tts.Communicate(text, VOICE).save(path)
        print(f"  {bid}: {text[:50]}...")


def load_elevenlabs_key():
    """ELEVENLABS_API_KEY from the environment, or from the repo .env
    (gitignored, same file that holds the warehouse password)."""
    key = os.environ.get("ELEVENLABS_API_KEY")
    if key:
        return key
    env_path = os.path.normpath(os.path.join(ROOT, "..", "..", "..", ".env"))
    if os.path.exists(env_path):
        for line in open(env_path, encoding="utf-8"):
            line = line.strip()
            if line.startswith("ELEVENLABS_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


def synth_elevenlabs(voice_id, api_key):
    """Bobby's cloned voice via the ElevenLabs API, one clip per beat."""
    os.makedirs(SEG_DIR, exist_ok=True)
    for bid, _, text in SEGMENTS:
        req = urllib.request.Request(
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}?output_format=mp3_44100_128",
            data=json.dumps({
                "text": text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {"stability": 0.45, "similarity_boost": 0.75},
            }).encode("utf-8"),
            headers={"xi-api-key": api_key, "Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req) as resp:
            audio = resp.read()
        with open(os.path.join(SEG_DIR, f"{bid}.mp3"), "wb") as f:
            f.write(audio)
        print(f"  {bid}: {text[:50]}...")


# Remotion's bundled binaries, invoked directly (the npx.cmd shim routes args
# through cmd.exe, which mangles the | and ; inside filter strings).
COMPOSITOR = os.path.join(ROOT, "node_modules", "@remotion", "compositor-win32-x64-msvc")
FFMPEG = os.path.join(COMPOSITOR, "ffmpeg.exe")
FFPROBE = os.path.join(COMPOSITOR, "ffprobe.exe")


def ffprobe_duration(path):
    out = subprocess.run(
        [FFPROBE, "-v", "error", "-show_entries", "format=duration", "-of", "json", path],
        capture_output=True, text=True, cwd=ROOT
    )
    return float(json.loads(out.stdout)["format"]["duration"])


def main():
    global OUT
    # Modes:
    #   (default)              free Edge TTS preview -> public/voiceover_ai.mp3
    #   --elevenlabs VOICE_ID  Bobby's clone via API -> public/voiceover_clone.mp3
    #   --assemble-only        mix clips already in out/vo_segments (e.g. lines
    #                          downloaded by hand from the ElevenLabs UI, one
    #                          mp3 per beat id) -> public/voiceover_clone.mp3
    if "--assemble-only" in sys.argv:
        OUT = os.path.join(ROOT, "public", "voiceover_clone.mp3")
        print("assemble-only: using existing clips in out/vo_segments")
    elif "--elevenlabs" in sys.argv:
        OUT = os.path.join(ROOT, "public", "voiceover_clone.mp3")
        voice_id = sys.argv[sys.argv.index("--elevenlabs") + 1]
        api_key = load_elevenlabs_key()
        if not api_key:
            print("No ELEVENLABS_API_KEY found (env var or repo .env). Add it and re-run.")
            sys.exit(1)
        print(f"synthesizing {len(SEGMENTS)} segments with ElevenLabs voice {voice_id}...")
        synth_elevenlabs(voice_id, api_key)
    else:
        print(f"synthesizing {len(SEGMENTS)} segments with {VOICE}...")
        asyncio.run(synth())

    # Fit check: every clip must fit inside its beat window.
    print("fit check:")
    ok = True
    for i, (bid, start, _) in enumerate(SEGMENTS):
        dur = ffprobe_duration(os.path.join(SEG_DIR, f"{bid}.mp3"))
        window = (SEGMENTS[i + 1][1] - start) if i + 1 < len(SEGMENTS) else 7.2
        flag = "OK " if dur <= window else "OVER"
        if dur > window:
            ok = False
        print(f"  {bid:8s} start {start:5.1f}  clip {dur:5.2f}s  window {window:4.1f}s  {flag}")
    if not ok:
        print("SOME CLIPS OVERRUN THEIR WINDOW: widen those beats in timeline.ts and re-run.")
        sys.exit(1)

    # Mix: delay each clip to its beat start, sum, normalize toward -14 LUFS.
    inputs = []
    filters = []
    for i, (bid, start, _) in enumerate(SEGMENTS):
        inputs += ["-i", os.path.join(SEG_DIR, f"{bid}.mp3")]
        ms = int(round(start * 1000))
        filters.append(f"[{i}:a]adelay={ms}|{ms}[a{i}]")
    chain = "".join(f"[a{i}]" for i in range(len(SEGMENTS)))
    filters.append(f"{chain}amix=inputs={len(SEGMENTS)}:normalize=0[mix]")
    filters.append("[mix]loudnorm=I=-14:TP=-1.5:LRA=11[out]")
    cmd = (
        [FFMPEG, "-y"] + inputs +
        ["-filter_complex", ";".join(filters), "-map", "[out]", "-b:a", "192k", OUT]
    )
    print("mixing...")
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
    if r.returncode != 0:
        print(r.stderr[-1500:])
        sys.exit(1)
    print(f"wrote {OUT} ({ffprobe_duration(OUT):.1f}s)")


if __name__ == "__main__":
    main()
