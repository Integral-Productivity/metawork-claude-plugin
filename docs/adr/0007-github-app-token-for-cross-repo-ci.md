# 7. Authenticate cross-repo CI access with a GitHub App token

Date: 2026-06-05

## Status

Accepted

Amends [ADR-0003](0003-methodology-in-separate-repo.md).

## Context

[ADR-0003](0003-methodology-in-separate-repo.md) decided the methodology
lives in a separate repo and is pulled into `references/` by the
`sync-methodology.yml` workflow, which clones
`Integral-Productivity/metawork-methodology` from inside the
`metawork-claude-plugin` repo.

That workflow failed on **every** scheduled run from the day it shipped
(16 consecutive failures) at the cross-repo checkout step:

```
fatal: repository '.../metawork-methodology/' not found
```

The repo exists and has the expected content. The failure is an
authentication gap, not a missing repo:

- The built-in `GITHUB_TOKEN` is scoped **only to the repo running the
  workflow**. It has no read grant on a *different* repo, even one in
  the same org.
- `metawork-methodology` is **INTERNAL** (private). GitHub deliberately
  returns **404 "Repository not found"** — not 403 — for private repos a
  token can't see, to avoid leaking their existence. This disguised a
  permissions problem as a wrong-name problem and cost ~16 silent
  scheduled failures before anyone looked.

ADR-0003 did not specify how the cross-repo clone authenticates. This
ADR fills that gap.

Options considered for granting cross-repo read:

1. **Personal Access Token (PAT) stored as a secret** — simplest to set
   up, but tied to an individual, expires, needs per-org SAML SSO
   authorization, and needs manual rotation. Couples a shared CI path to
   one person's credential.
2. **A GitHub App token minted at runtime** via
   `actions/create-github-app-token@v1` (already on the org's Actions
   allowlist) — not tied to a person, auto-expiring per-run, scoped to
   exactly the repos listed. Requires an App installed on both repos.
3. **Make `metawork-methodology` public** — removes the auth need
   entirely, but the methodology is intentionally INTERNAL until its
   audience and licensing are settled; out of scope here.

Within option (2) there is a sub-choice of App identity:

- **Reuse an existing org App.** `ip-releaser` (App ID `3888182`)
  already carries exactly the permission surface this needs
  (`contents: write`, `pull_requests: write`) and is installed on all
  org repos, so it can read `metawork-methodology` and write to
  `metawork-claude-plugin` today.
- **Mint a dedicated App** (e.g. `ip-methodology-sync`) — cleaner
  identity (commits/PRs authored by a bot whose name says "methodology
  sync"), at the cost of one more App and private key to manage and
  rotate.

## Decision

`sync-methodology.yml` authenticates cross-repo access with a **GitHub
App token** (option 2), minted via
`actions/create-github-app-token@v1` and scoped to both
`metawork-claude-plugin` and `metawork-methodology`. The minted token is
passed to:

- the plugin-repo checkout,
- the methodology-repo checkout, and
- the PR-creation step (replacing the built-in `GITHUB_TOKEN`).

We **reuse the existing `ip-releaser` App** (App ID `3888182`) rather
than minting a dedicated App, because its permissions and installation
scope already match exactly. Its App ID is stored in the
`METHODOLOGY_SYNC_APP_ID` repo secret and its private key in
`METHODOLOGY_SYNC_APP_PRIVATE_KEY`.

A welcome side effect: because PRs opened with an App token (unlike the
built-in `GITHUB_TOKEN`) **can** trigger downstream workflows, the
`chore(references): sync` PRs will now fire the plugin's CI — closing
the gap the workflow comments had flagged as a future need.

## Consequences

**Positive:**

- The methodology sync can actually run — ADR-0003's mechanism works
  end-to-end for the first time.
- No personal credential in a shared CI path; the token is auto-expiring
  and per-run least-privilege (scoped to the two named repos).
- Sync PRs trigger downstream CI, so a bad snapshot is caught by the
  plugin's checks rather than merged blind.
- Reusing `ip-releaser` means zero new Apps or keys to provision and
  rotate.

**Negative:**

- Commits and PRs from the sync now appear authored by
  `ip-releaser[bot]` — an identity that says "releaser," not
  "methodology sync." Mild semantic bleed; acceptable for an automated
  `chore` PR, but it is a real readability cost.
- The sync now depends on the `ip-releaser` App's continued existence,
  permission surface, and key validity. If that App is repurposed,
  narrowed, or its key rotated without updating the secret, the sync
  breaks again — and (as this incident showed) it can break silently.
- A GitHub App is a heavier mental model than a PAT for a contributor
  reading the workflow for the first time.

**Trigger to revisit:** mint a dedicated `ip-methodology-sync` App and
repoint the two secrets if EITHER (a) the `ip-releaser[bot]` authorship
on sync PRs becomes confusing in practice, OR (b) `ip-releaser`'s
permissions/installation are changed for its primary release purpose in
a way that no longer covers this sync. Add a `workflow_dispatch` smoke
run to the workflow's acceptance checks so a future auth regression
surfaces immediately instead of accruing silent scheduled failures.
