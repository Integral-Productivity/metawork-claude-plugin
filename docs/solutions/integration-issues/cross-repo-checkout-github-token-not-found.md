---
title: Cross-repo actions/checkout fails with "Repository not found"
date: 2026-06-05
category: integration-issues
module: sync-methodology workflow
problem_type: integration_issue
component: tooling
symptoms:
  - "fatal: repository '.../metawork-methodology/' not found during actions/checkout"
  - "remote: Repository not found on a repo that demonstrably exists"
  - "a scheduled workflow fails every run since creation, never once green"
root_cause: missing_permission
resolution_type: config_change
severity: high
tags: [github-actions, github-token, cross-repo-checkout, create-github-app-token, ci-auth, internal-repo]
---

# Cross-repo actions/checkout fails with "Repository not found"

## Problem

A GitHub Actions workflow that checks out a *second, different* repository (here, `sync-methodology.yml` cloning `Integral-Productivity/metawork-methodology` from inside `metawork-claude-plugin`) fails at the cross-repo checkout with `fatal: repository '...' not found` — even though the repo exists and has the expected content. The methodology never synced; the daily job looked alive but did nothing for 16 consecutive runs.

## Symptoms

- `remote: Repository not found` / `fatal: repository '.../metawork-methodology/' not found` at the second `actions/checkout` step (the first checkout, of the home repo, succeeds).
- The named repo provably exists (`gh repo view` works for a human with org access).
- Every scheduled run red since the workflow was created — never a single success.

## What Didn't Work

- Reading "Repository not found" as a wrong repo name / typo. The name was correct; the word is misleading (see Why This Works).

## Solution

Mint a GitHub App token scoped to **both** repos and pass it to the cross-repo checkout (and, if the workflow opens PRs, to the PR step too). `actions/create-github-app-token@v1` is on the Integral-Productivity Actions allowlist.

```yaml
- name: Mint GitHub App token
  id: app-token
  uses: actions/create-github-app-token@v1
  with:
    app-id: ${{ secrets.METHODOLOGY_SYNC_APP_ID }}
    private-key: ${{ secrets.METHODOLOGY_SYNC_APP_PRIVATE_KEY }}
    owner: ${{ github.repository_owner }}
    repositories: |
      metawork-claude-plugin
      metawork-methodology

- name: Checkout methodology repo
  uses: actions/checkout@v4
  with:
    repository: Integral-Productivity/metawork-methodology
    path: .methodology-src
    ref: main
    token: ${{ steps.app-token.outputs.token }}   # <-- the fix
```

The App must be installed on both repos: the repo being written to needs Contents + Pull-requests write; the repo being read needs Contents read. An existing org App with the right permission surface (e.g. `ip-releaser`, installed on all repos) can be reused — only its App ID + private key need to be stored as the two secrets.

## Why This Works

Two facts combine:

1. **The built-in `GITHUB_TOKEN` is scoped only to the repo running the workflow.** It has no read grant on any other repo, even an INTERNAL/private one in the same org. `actions/checkout` of a different repo with no `token:` override silently reuses this single-repo token.
2. **GitHub returns 404 "Repository not found", not 403 Forbidden, for private repos a token can't see** — deliberately, so an unauthorized caller can't even confirm the repo exists. This makes an *authorization* gap present as a *wrong-name* problem.

A GitHub App token, scoped via `owner` + `repositories` to both repos (and installed on both), carries cross-repo read, so the clone succeeds. Bonus: PRs opened with an App token can trigger downstream workflows, which PRs opened with the built-in `GITHUB_TOKEN` deliberately cannot.

## Prevention

- **Any time a workflow checks out a repo other than its own, assume the default `GITHUB_TOKEN` cannot read it** and supply a cross-repo credential (App token preferred over PAT — not person-tied, auto-expiring, least-privilege).
- **Read "Repository not found" on a known-good repo name as an auth signal, not a naming bug.** Verify existence with a human-authed `gh repo view`; if it exists, the workflow token lacks access.
- **Smoke-test new scheduled workflows once at creation** (`gh workflow run <file>`). A scheduled-only workflow that ships broken fails silently on cron — here, 16 red runs accrued before anyone looked. A manual `workflow_dispatch` run on the first commit would have caught it on day one.

## Related Issues

- PR: Integral-Productivity/metawork-claude-plugin#5 (the fix)
- Issue: Integral-Productivity/metawork-claude-plugin#10 (App credential provisioning)
- ADR-0007 (`docs/adr/0007-github-app-token-for-cross-repo-ci.md`) — decision record, amends ADR-0003
