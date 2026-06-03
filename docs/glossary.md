# Glossary

## Workstream

Flow's task evaluation and contribution infrastructure: the system for project guides, task queues, submission packets, automated checks, reviewer routing, evaluation sprints, revision loops, contribution records, payment status, and reputation signals.

## Project

A configured work program with its own guide, rules, checker policy, review policy, payout policy, and queue.

## Source

Where a task came from. In v0.1, sources are manual creation, controlled markdown import, or controlled CSV import.

## Origin

A future external task source that can submit tasks into Workstream through an adapter. External origin onboarding is not part of v0.1.

## Project Guide

The operating law of a project. Defines quality standards, submission format, reviewer expectations, payment policy, and common rejection reasons.

## Task

A unit of work inside a project.

## Task Contract

The normalized task fields required for Workstream to screen, assign, check, review, pay, and audit work.

## Submission Packet

The worker's submitted output plus summary, files, evidence, and metadata.

## Checker

An automated rule that validates a task or submission before human review.

## Checker Policy

The set of required and warning checks for a project.

## Human Review

The judgment layer where a reviewer accepts, rejects, or requests revision.

## Finding

A structured reviewer issue with severity, area, required fix, and evidence.

## Revision Replay

A resubmission record showing how each prior review finding was addressed.

## Evidence

Proof supporting task completion or review decision. Examples: logs, hashes, tests, screenshots, diffs, notes.

## Payment Ledger

The record of accepted amount, pending payout, paid amount, and payment state.

## Reputation Ledger

The outcome-based record of worker and reviewer performance.

## Contribution Record

The evidence-backed record that accepted work was completed under a locked project guide. Payment and reputation records attach to contribution records, but do not replace them.

## Human Owner

The person accountable for a submitted packet, even when agents or external tools helped produce the work.
