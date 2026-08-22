---
name: series-world-bible-continuity
description: "Use when maintaining lore consistency, fact-checking timelines, tracking character states, magical/tech rules, and building living world wikis for multi-book series and long-form novels. Prevents plot holes, character voice drift, and lore contradictions."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [worldbuilding, continuity, series-bible, lore, fact-checking, timeline-tracking, novel-wiki]
    related_skills: [book-authoring-mastery, literary-translation-pipeline]
---

# Series World Bible & Continuity Engine

## Overview
A systematic lore management and continuity tracking framework for authors and translators working on multi-volume books and expansive fictional universes. Automates chronological timeline tracking, character state monitoring (injuries, inventory, locations, secrets known), magic/tech constraint validation, and living wiki generation.

## Core Continuity Pillars

### 1. Character State Ledger (`character_ledger.json`)
Tracks dynamic attributes across chapters:
```json
{
  "harry_potter": {
    "current_location": "Gryffindor Dormitory",
    "inventory": ["Invisibility Cloak", "Holly Wand 11inch", "Hedwig"],
    "physical_state": ["Scar pain active"],
    "known_secrets": ["Fluffy guards the trapdoor", "Snape refereeing Quidditch"],
    "relationship_status": {
      "ron_weasley": "Best Friend",
      "hermione_granger": "Close Ally",
      "draco_malfoy": "Sworn Enemy"
    }
  }
}
```

### 2. Chronological Timeline & Date Grid
- Maintain a strict Day/Night and calendar event tracker to ensure characters don't arrive before they departed, or experience impossible seasons/lunar phases.
- Cross-reference travel times and distance logic between locations.

### 3. Magic & Technology Boundary Rules (Hard vs. Soft Systems)
- **Cost & Consequence:** Every spell, gadget, or ability must consume measurable stamina, resources, or risk.
- **Forbidden Actions:** Document what magic *cannot* do (e.g. Gamp's Law of Elemental Transfiguration: food cannot be created out of nothing; the dead cannot be truly resurrected).

## Workflow & Continuity Verification

1. **Chapter Lore Extraction:**
   - Scan new chapters for newly introduced terms, character appearances, item transfers, and lore claims.
2. **Contradiction Scan:**
   - Compare new claims against the established `world_bible.md`.
   - *Example Flag:* "Character holds wand in right hand, but was established as left-handed in Chapter 3."
   - *Example Flag:* "Character visits Hagrid at midnight, but was serving detention with Filch in previous scene."
3. **Living Universe Wiki Compilation:**
   - Compile markdown notes into an interactive single-file HTML or Obsidian-compatible vault with interlinked nodes.

## Common Pitfalls & Solutions

1. **Retcon Clashes:** Changing a world rule halfway through without updating early chapters.
   - *Fix:* Run a search across all chapter files for the modified concept before finalizing the change.
2. **Forgotten Wounds / Inventory:** A character is wounded in battle but acts completely unhindered in the next scene.
   - *Fix:* Check the `character_ledger.json` physical state before drafting subsequent scenes.

## Verification Checklist

- [ ] All newly introduced characters added to the character index.
- [ ] Timeline matches travel speeds and day/night transitions.
- [ ] Magic/technology behavior obeys the constraints in `world_bible.md`.
- [ ] Character relationships and secrets known are updated at chapter close.
