---
name: metawork-set-up
description: Set up a new Meta Work Group — pick scope axes, name subject, walk the GTD Natural Planning Model, persist to your configured backend (OmniFocus or markdown).
---

Invoke the `metawork-set-up` skill with the user's arguments: $ARGUMENTS.

If no subject is provided, the skill should prompt for one.
If `~/.metawork/config.json` doesn't exist, the skill should bootstrap it
before doing anything else.
