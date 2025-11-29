# D&D Character Builder

A web app for creating, previewing, and exporting D&D 5e character sheets.
Frontend in **Next.js**. Backend in **Python (FastAPI)**.

---

## Overview

This project allows users to:

- Create a character sheet using race, class, level, and ability scores.
- Get **live preview** using a backend-powered rules engine.
- Automatically calculate:
  - Ability modifiers
  - Proficiency bonus
  - Movement speed
  - Class features (e.g. Sneak Attack dice)
- Export the final sheet to **PDF** using a template.
- (Future) Add homebrew options for classes, subclasses, spells, etc.

---

## Project Structure

dnd-character-tool/
frontend/ → Next.js (React + TypeScript)
backend/ → Python FastAPI
