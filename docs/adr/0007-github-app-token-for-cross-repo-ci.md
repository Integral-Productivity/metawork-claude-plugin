# 7. Authenticate cross-repo CI access with a dedicated GitHub App token

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

- **Reuse an existing org App.** `ip-releaser` (App ID `3888182`) carries
  the needed permission surface (`contents: write`,
  `pull_requests: write`) and is installed on **all** org repos, so it
  could read `metawork-methodology` and write to `metawork-claude-plugin`
  today with no new App to register.
- **Mint a dedicated App** (e.g. `ip-methodology-sync`) installed on
  **only** the two repos this sync touches, with minimal permissions.

The decisive factor is **the blast radius of the stored private key**,
which is the key fact a first reading of this trade-off misses:

> `actions/create-github-app-token@v1`'s `repositories:` input narrows
> the *runtime token*, but never the *stored key*. A stored App private
> key can always mint a token for **any repo the App is installed on**.
> Least privilege therefore comes from the App's *installation scope*,
> not the workflow YAML.

Reusing `ip-releaser` would store, in this repo's secrets, a key that can
mint a `contents: write` + `pull_requests: write` token for **all ~34 org
repos**. Exfiltration of that one secret — via a malicious workflow
edit, a compromised runner, or a leaked secret — would be an org-wide
write credential, even though normal runs scope the token to two repos.
A dedicated App installed on only the two repos bounds the stored key's
blast radius to exactly: read `metawork-methodology`, write
`metawork-claude-plugin`.

This is also the **org's first ADR on cross-repo CI authentication**.
Whatever identity pattern it normalizes, the other ~33 repos inherit. A
least-privilege, dedicated-App-per-job pattern is the safer norm to set;
reusing one broad all-repos App as the convention would compound the
org-wide blast radius every time a new cross-repo job copies it.

## Decision

`sync-methodology.yml` authenticates cross-repo access with a **GitHub
App token** (option 2), minted via
`actions/create-github-app-token@v1` and scoped to both repos.

We **mint a dedicated App, `ip-methodology-sync`** (not reuse
`ip-releaser`), installed on **only** `metawork-claude-plugin` (Contents:
write, Pull requests: write) and `metawork-methodology` (Contents: read).
This makes the stored key least-privilege: its blast radius is exactly
those two repos. Its App ID is stored in the `METHODOLOGY_SYNC_APP_ID`
repo secret and its private key in `METHODOLOGY_SYNC_APP_PRIVATE_KEY`.

The minted token is passed to the plugin-repo checkout, the
methodology-repo checkout, and the PR-creation step (replacing the
built-in `GITHUB_TOKEN`).

**Authorship:** the workflow sets `git config user.name
"github-actions[bot]"`, so sync *commits* are attributed to
`github-actions[bot]`. The *PR* is opened under the App token's identity
(`ip-methodology-sync[bot]`). This split is intentional and unremarkable
for an automated `chore` PR; the dedicated App's name keeps the PR opener
self-describing.

**Downstream CI:** PRs opened with an App token (unlike the built-in
`GITHUB_TOKEN`) **can** trigger `pull_request` workflows. Today the only
check that runs on a PR is CodeQL default setup — there is **no**
workflow that validates the synced `references/` content. So this enables
future PR checks rather than guaranteeing snapshot validation now; adding
a `references/`-validation workflow is tracked separately.

**Smoke-test gate (part of this decision, not advisory):** because the
originating incident was 16 *silent* scheduled failures, a manual
`gh workflow run sync-methodology.yml` MUST pass green before this
workflow is trusted, and after any future key rotation.

## Consequences

**Positive:**

- The methodology sync can run — ADR-0003's mechanism works end-to-end
  for the first time.
- **Least-privilege stored key:** the secret's blast radius is exactly
  the two repos the sync touches, not the whole org. Exfiltration grants
  only read-methodology / write-plugin, not org-wide write.
- No personal credential in a shared CI path; the token is auto-expiring
  and per-run scoped to the two named repos.
- The App's lifecycle is **decoupled** from any release App — narrowing,
  rotating, or reinstalling `ip-releaser` for its release purpose can
  never silently break this sync.
- A clean bot identity (`ip-methodology-sync[bot]`) on the PR opener, and
  a least-privilege precedent for the org's other cross-repo jobs.

**Negative:**

- One more App and private key to provision and rotate — the cost
  rejected for `ip-releaser` reuse. Provisioning needs a one-time browser
  step (create the App, install it on the two repos, generate a key);
  there is no REST API to create an App's key.
- A GitHub App is a heavier mental model than a PAT for a contributor
  reading the workflow for the first time.
- No rotation cadence or compromise-response runbook is defined yet. A
  rotation-on-suspicion procedure (revoke the key in App settings →
  generate a new key → update `METHODOLOGY_SYNC_APP_PRIVATE_KEY` → smoke
  re-run) should be written; a key that is rotated without updating the
  secret breaks the sync, and (as this incident showed) it can break
  silently on cron.
- The threat model still assumes repo maintainers control who can edit
  `.github/workflows/` and read repo secrets. If the contributor base
  broadens, a CODEOWNERS rule on `.github/workflows/` and GHAS secret
  scanning / push protection are the compensating controls.

**Trigger to revisit:** if many cross-repo jobs accrue across the org and
per-job dedicated Apps become burdensome to manage, record an org-wide
convention in `devops-excellence` (a shared, *narrowly-scoped* CI App, or
App-lifecycle automation) rather than reverting to a broad all-repos App.
Revisit the dedicated-vs-shared call there, not per-repo.
