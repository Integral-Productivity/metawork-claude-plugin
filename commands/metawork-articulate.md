---
name: metawork-articulate
description: Draft or extend the canonical Meta Work methodology document by interview. Output is a PR-ready markdown section for the metawork-methodology repo.
---

Invoke the `metawork-articulate` skill with the user's arguments: $ARGUMENTS.

If no topic is provided, prompt for one (a pillar name, an integration point,
a distinction to sharpen, a breakdown pattern, etc.).

If `~/GitHub/metawork-methodology/` is not cloned, write the draft to the
current working directory as `metawork-draft-<topic>.md` and instruct the
user how to land it.
