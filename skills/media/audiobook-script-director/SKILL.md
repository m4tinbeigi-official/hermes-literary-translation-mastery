---
name: audiobook-script-director
description: "Use when adapting novels, chapters, or prose into dramatized audio drama scripts, full-cast audiobooks, or TTS multi-voice pipelines. Formats character speaker tags, voice performance cues, mood directions, background ambience (BGM), and sound effects (SFX)."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [audiobook, audio-drama, voice-acting, tts, podcast, sound-design, scriptwriting, persian-audio]
    related_skills: [book-authoring-mastery, persian-orthography-and-style, literary-translation-pipeline]
---

# Audiobook & Audio Drama Script Director

## Overview
Transforms prose literature and narrative fiction into rich, production-ready audio drama scripts. Calibrates individual character voice profiles, pacing cues, emotional undertones, background music (BGM) shifts, and Foley/sound effect (SFX) triggers for multi-speaker TTS models or human voice actors.

## Core Scripting Format

Each audio script chunk follows this clean, parsable structure:

```markdown
[SCENE: مکان و زمان وقوع صحنه | اتمسفر کلی]
[BGM: نام ترک / نوع موسیقی پس‌زمینه | حجم صدا مثلاً FADE IN / LOW]
[SFX: صدای محیطی پیوسته مثل زوزه باد، همهمه تالار]

[NARRATOR] (با آرامش و وقار روایی):
متن توصیف صحنه یا فضا با رعایت کامل آهنگین بودن و تلفظ روان فارسی...

[CHARACTER_NAME] (حالت حسی: با خشم / با پچ‌پچ مضطربانه / با بغض):
«متن دیالوگ داخل گیومه با لحن اختصاصی کاراکتر.»

[SFX: صدای شکستن شیشه / بسته شدن در با صدای بَم]
```

## Voice Direction & Cast Matrix

Define the vocal register for every actor/voice node:
1. **Pitch & Timbre:** Deep baritone, raspy, melodic, nasal, youthful, gravelly.
2. **Tempo & Cadence:** Fast staccato, deliberate, hesitant, rhythmic.
3. **Emotional Delivery:** Subtext tags in brackets before lines:
   - `[با پوزخند تلخ]`
   - `[با لکنت و ترس شدید]`
   - `[با نیشخند تمسخرآمیز]`
   - `[فریاد از سر استیصال]`

## Step-by-Step Adaptation Workflow

1. **Extract Dialogue & Action Beats:** Separate raw narrative description from active spoken dialogue and physical action.
2. **Translate Internal Monologue to Audio:**
   - Convert internal character thoughts into a distinct whisper-track:
     `[HARRY (نجوا / صدای ذهنی)]: «چرا داره این‌طوری نگاهم می‌کنه؟»`
3. **Layer Sound Effects (SFX) & Ambience:**
   - Anchor physical actions into audio cues (footsteps on gravel, clinking potions bottles, spell crackles).
4. **Enforce Persian Audio Phrasing:**
   - Ensure conversational Iranian Persian rhythm in dialogues while keeping narrative voice elevated and poetic.
   - Zero em-dashes (`—`), strict Persian quotes (`«...»`).

## Common Pitfalls & Solutions

1. **Over-Crowded SFX:** Inserting a sound effect on every word, drowning out dialogue.
   - *Fix:* Use SFX only for scene transitions and significant physical beats.
2. **Robotic Dialogue Tags in Audio:** Leaving "او گفت" or "او با تعجب پرسید" in spoken narrator lines right after a character spoke.
   - *Fix:* Remove redundant attribution verbs when voice tags already identify the speaker.
3. **Inconsistent Voice Tones:** Characters shifting wildly from formal to colloquial without dramatic motivation.
   - *Fix:* Maintain a strict Cast Voice Matrix per character.

## Verification Checklist

- [ ] Every spoken line has a clear speaker tag (`[SPEAKER]`).
- [ ] Directing cues include emotional tone and volume guidance in parentheses.
- [ ] Ambient background sounds (SFX/BGM) clearly marked at scene openings.
- [ ] No residual em-dashes (`—`) in spoken dialogue.
- [ ] Redundant speech tags ("او گفت") stripped from narrator audio.
