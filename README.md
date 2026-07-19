# Viral Video Edit Skills

Claude / Codex-compatible **skills** for making beat-perfect, effect-integrated short-form music video edits — the kind of dense, audio-reactive vertical edits used to promote songs on TikTok/Reels/Shorts.

These were extracted from a working production system and its accumulated field feedback: what actually made edits perform, what got rejected and why, and the exact technical recipes (librosa cut grids, matte-anchored FX, procedural GLSL renderers, grade formulas, hook-writing rules, footage QA gates) behind them.

## What's included

- **`skills/viral-video-edits/`** — the master skill. Start here. A compact `SKILL.md` with 10 non-negotiable "Laws" and a workflow, backed by 8 reference docs carrying every load-bearing constant:
  - `song-analysis.md` — beat/energy/section analysis, viral-window scoring, the onset-locked cut grid, envelope followers
  - `integrated-fx.md` — the core craft rule (effects fused into shots, never cutaway), the person-matte pipeline, three build architectures, compositing gotchas
  - `procedural-renderers.md` — headless moderngl/GLSL rendering (tunnels, portals, kaleidoscopes), the "near-black + emissive" art-direction law, footage/FX fusion
  - `cinematic-grade.md` — the exact filmic grade recipe, camera language, and iteration case studies
  - `hooks-and-text.md` — the 5-test hook QA gate, text kinetics, the adversarial-tournament method for creative decisions
  - `footage-sourcing.md` — vibe specs, source tiers, the shot-level quality gate, licensing
  - `delivery-qa.md` — encode settings, QA pass, verdict format
  - `design-docs.md` — how to plan a production before building it

- **`skills/song-edit-analysis/`**, **`skills/beat-synced-montage-builder/`**, **`skills/generated-media-sourcing/`**, **`skills/edit-delivery-qa/`** — a companion kit of narrower, script-bundled skills (from the [beat-synced-codex-edit-kit](https://github.com/) project) covering the same pipeline stage by stage, each with a runnable Python script (song analysis, source scanning, QA probing).

## Using these skills

### Claude Code / Claude (skills)

Copy (or symlink) the `skills/` directory you want into your project's `.claude/skills/`, or install the whole folder as your skills directory. Claude will pick up `viral-video-edits` automatically for edit-related requests, or you can invoke it explicitly.

### Codex / other agents

Each skill's `SKILL.md` is plain instructions — point any coding agent at the file and ask it to follow it. The bundled `agents/openai.yaml` files (where present) give a display name and default prompt for Codex-style skill registries.

## Requirements for the bundled scripts

The scripts under `skills/*/scripts/` expect `ffmpeg`/`ffprobe` on `PATH` and a Python environment with `librosa`, `numpy`, `scipy`, `pandas`, `scikit-learn`, `matplotlib`, and `soundfile`. The deeper techniques described in `viral-video-edits` (procedural GLSL rendering, Apple Vision person mattes) additionally need `moderngl` and, for the matte pipeline, macOS 14+ with Swift/Vision/AVFoundation.

## License

MIT — see `LICENSE`. Bring your own music and footage; nothing here includes or requires any copyrighted or private media.
