---
name: novel-art-direction-prompts
description: "Use when extracting key visual moments from novels, chapters, or scenes to generate high-fidelity cinematic image prompts for Midjourney, Stable Diffusion, DALL-E 3, or ComfyUI. Manages visual consistency, character art sheets, camera angles, color palettes, and lighting."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [art-direction, image-prompts, midjourney, stable-diffusion, illustration, book-cover, visual-worldbuilding]
    related_skills: [book-authoring-mastery, literary-translation-pipeline]
---

# Novel Art Direction & Visual Prompt Generator

## Overview
Extracts atmospheric, emotionally charged visual moments from literary text and translates them into structured, highly descriptive image generation prompts. Ensures visual continuity across character appearances, architectural environments, lighting aesthetics, and mood palettes.

## Prompt Engineering Blueprint

Each scene illustration prompt is constructed using a 6-layer formula:

```
[Subject & Micro-Action], [Character Facial Expression & Costume Details], [Environment & Architectural Architecture], [Lighting Dynamics & Atmosphere], [Camera Angle, Composition & Focal Depth], [Artistic Style & Rendering Medium]
```

### Example Structured Prompt:
> **Scene: Snape's Potions Dungeon (Chapter 8)**
> `Cinematic oil painting, dramatic chiaroscuro lighting. Professor Severus Snape with sallow skin, hooked nose, curtain of greasy black hair, wearing heavy billowing dark wool robes, staring down with cold piercing dark eyes. Standing in a gloomy subterranean dungeon cellar lined with hundreds of glowing glass jars containing preserved magical specimens. Flickering candlelight casting long menacing shadows against damp cobblestone walls. Low angle Dutch shot, deep focus, misty cold atmospheric vapor, mysterious dark fantasy aesthetic, masterpiece, intricate textures, 8k resolution --ar 16:9 --style raw`

## Visual Continuity Rules

### 1. Consistent Character Design Specs
Maintain fixed aesthetic tags for main characters:
- **Harry Potter:** `Messy jet-black unruly hair, thin round wireframe glasses, bright emerald green eyes, faint lightning bolt scar visible on forehead, slight build, oversized Hogwarts robes`.
- **Dumbledore:** `Sweeping silver-white beard tucked into belt, half-moon spectacles perched on crooked nose, luminous sky-blue piercing eyes, deep purple embroidered silk robes`.
- **Hagrid:** `Towering giant stature, bushy tangled dark beard and mane of hair, moleskin coat with deep cavernous pockets, warm beetle-black crinkled eyes`.

### 2. Lighting & Color Mood Palettes
- **Gryffindor Common Room:** Warm amber glow, crackling hearth fire, deep crimson and gold velvet, soft shadows.
- **Potions Dungeon:** Cold murky green, dim flickering candle, damp grey stone, sickly yellow specimen glow.
- **Forbidden Forest:** Cool moonlight filtering through towering ancient gnarlwood trees, silver mist, deep shadows, ominous cool blue tones.

## Step-by-Step Art Direction Workflow

1. **Scene Highlight Extraction:** Scan the chapter for the single most dramatic or iconic visual beat (Climax, First Encounter, Discovery).
2. **Layer Aesthetic Composition:** Specify camera lens (35mm wide, 85mm portrait, low-angle hero shot, Dutch tilt).
3. **Inject Atmospheric Density:** Add volumetric rays, dust particles, embers, rain streaks, or damp mist to give depth.
4. **Format for Engine:** Append engine parameters (`--ar 16:9`, `--v 6.1`, or ComfyUI checkpoint tags).

## Verification Checklist

- [ ] Character key visual features (hair, eyes, scars, clothing) match the character design spec.
- [ ] Lighting source and shadow direction are clearly specified.
- [ ] No generic filler words ("super realistic", "nice photo") — replace with concrete optical and material terms.
- [ ] Aspect ratio and composition match the intended medium (Chapter header: 16:9 / Book cover: 2:3).
