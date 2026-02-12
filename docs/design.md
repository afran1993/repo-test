# Architecture Snapshot

This document summarizes the core architecture for the planned open-world RPG.

- Hybrid ECS + OOP where ECS handles world entities and systems; OOP encapsulates rules.
- Data-driven content in `data/` and localization in `locales/`.
- Archetypes, items and equipment rules are validated at runtime.
- Elements, combat and world streaming are planned next; prototype focuses on rules + data.
