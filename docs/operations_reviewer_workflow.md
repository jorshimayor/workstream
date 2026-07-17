# Reviewer Workflow

## Status

This is the planned v0.1 operating contract. Reviewer routes and jobs remain
unavailable until their hidden REV behavior, exact AUTH activation, and the
REV-13 joint release complete. `spec_review_lifecycle.md` is normative.

## Reviewer Job

The reviewer decides whether one exact leased Submission satisfies the task and
the Project Guide context stamped on that Submission. The reviewer never rebases
guide context and does not use whatever guide happens to be active at read time.

The reviewer must have an exact active project `reviewer` grant represented by
canonical human `ActorProfile.id`. Submitter, adjudicator, administrative, or
token-role authority does not substitute. No-self-review and lifecycle guards
still apply.

## Current Work And Claim

The reviewer current-work operation returns an active lease, one server-selected
offer, or none. It never returns the complete backlog. A claim creates one
ReviewLease and immutable ReviewPacketManifest under PostgreSQL race guards.

The reviewer may read artifact bytes only for the exact Submission packet named
by the current active lease. Authorized history contains bounded metadata, not
prior or unrelated artifact bytes.

## Review Inputs

The planned Review Context contains:

- queue, lease, Submission, and admitting CheckerRun identity;
- stamped Project Guide identity, version, and activation sequence;
- task description and acceptance criteria;
- submission summary and exact packet bindings;
- checker results and bounded evidence;
- prior immutable Reviews and findings when relevant;
- revision preparation transition, submitter responses, and prior resolutions.

## Decisions

Allowed decisions are exactly `accept`, `needs_revision`, and `reject`.

Every valid decision appends one immutable Review. Every submitted finding and
later resolution is immutable. Every Review creates one reviewer
`completed_review` ContributionRecord and evaluates the ReviewLease-frozen
ContributionPolicyVersion, regardless of outcome.

`accept` means the Submission satisfies its stamped context. It additionally
creates one immutable FinalAcceptance, accepts the task, completes the
TaskAssignment, and creates the submitter `accepted_submission` from
FinalAcceptance. There is no direct Review-to-submitter contribution inference.

`needs_revision` means concrete blocking issues are fixable. It keeps the
TaskAssignment active, creates no FinalAcceptance, and creates no submitter
contribution.

`reject` means the work is not reasonably salvageable or violates the governing
contract. It requires a bounded human reason, blocks the same-task assignment,
sets the task to `rejected`, and creates no FinalAcceptance or submitter
contribution.

## Findings

A ReviewFinding contains:

- lifecycle meaning: `blocking` or `advisory`;
- area;
- issue and rationale;
- required change for blocking findings;
- optional finalized evidence binding.

`needs_revision` requires at least one unresolved blocking finding. Advisory
findings must not become preference-only acceptance requirements. Reject
requires its bounded reason; structured findings are optional when they add
useful evidence and are never fabricated merely to satisfy a field.

## Revision Review

For a revised Submission, the reviewer checks each required immutable
SubmissionFindingResponse and appends one FindingResolution with result
`resolved`, `unresolved`, or `not_applicable`. The reviewer does not edit the
prior finding or response.

The revised Submission initially returns to the reviewer who requested the
revision. Preference expiry, decline, or authority invalidation opens the same
queue entry without resetting its age.

## Decision Transaction

The route owns one transaction:

```text
AUTH prepared authority and final evaluation
-> append Review/findings/resolutions
-> consume ReviewLease and close ReviewQueueEntry
-> CON reviewer operation
-> accept: FinalAcceptance + task effects + CON submitter operation
   needs_revision: task effect only
   reject: assignment block + task effect
-> REV stages shared audit/outbox
-> commit once
```

The transaction performs no Artifact Storage call. Any participant failure rolls
back all lifecycle, contribution, award, audit, and outbox effects.

## Reviewer Checklist

Before any decision:

- confirm the exact active lease and packet;
- use the guide/policy context stamped on the Submission;
- verify the admitting CheckerRun belongs to that Submission;
- ground judgment in acceptance criteria and available evidence;
- check all required prior responses and resolutions;
- distinguish blocking requirements from advisory observations;
- confirm the decision-specific task, assignment, FinalAcceptance, and
  contribution effects can commit atomically.

Offline sampling and calibration may evaluate review quality, but they do not
create adjudication state, overturn a Review, or mutate immutable history.
