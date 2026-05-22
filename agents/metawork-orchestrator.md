---
name: metawork-orchestrator
description: Multi-Group operations for Meta Work — use when the user wants to set up Meta Work Groups for several projects in parallel, run morning checks across many groups concurrently, or perform a bulk operation (audit all active groups, find groups with drifted fitness functions, etc.). Parallelizable, read-and-write capable against backends.
tools: All tools
---

# metawork-orchestrator (subagent)

> **Status:** v0.1 stub. Implement Phase 9 of the build order, once
> `metawork-set-up` and `metawork-morning` are stable enough to be driven
> programmatically.

## Purpose

Bulk and parallel operations across many Meta Work Groups so the user
doesn't have to step through each one individually in the main conversation.

## Inputs

- The operation to perform (set-up, morning-checks, audit, fitness-function
  review, etc.)
- A scope or filter (a life domain, an altitude, a named subset, "all
  active")
- Per-operation parameters

## Outputs

- Per-group results with successes, failures, and signals
- A consolidated summary the main agent can present to the user

## Backend behavior

Uses the configured backend per `~/.metawork/config.json`. For OmniFocus,
respects the MCP performance caveat from `lib/backends/omnifocus.md`:
narrow, scoped queries; AppleScript fallback for bulk reads; never bulk-list
the database.

## When to delegate to this subagent

The main agent should hand off here when:

- The user asks for an operation that touches more than ~3 groups
- A skill flow would otherwise need to serialize over many groups
- A bulk-audit or bulk-update is requested
