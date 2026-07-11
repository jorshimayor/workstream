# Revision Replay Template

## Task

## Prior Review

## New Submission

## Revision Summary

## Revision Context

Contributor-visible fields:

| Field | Value |
| --- | --- |
| prior submission id | `<submission id>` |
| prior submission version | `<version>` |
| context rebased | yes or no |
| prior guide version | `<guide version>` |
| next guide version | `<guide version>` |
| prior submission artifact policy version | `<submission artifact policy version>` |
| next submission artifact policy version | `<submission artifact policy version>` |
| prior pre-submit checker bundle hash | `<pre-submit checker bundle hash>` |
| next pre-submit checker bundle hash | `<pre-submit checker bundle hash>` |
| prior post-submit checker policy version | `<post-submit checker policy version>` |
| next post-submit checker policy version | `<post-submit checker policy version>` |
| prior review policy version | `<review policy version>` |
| next review policy version | `<review policy version>` |
| prior revision policy version | `<revision policy version>` |
| next revision policy version | `<revision policy version>` |
| prior payment policy version | `<payment policy version>` |
| next payment policy version | `<payment policy version>` |
| rebase reason | `<reason>` |
| change summary shown to contributor | `<summary>` |

Reviewer and authorized recovery evidence fields:

| Field | Value |
| --- | --- |
| audit event id | `<audit event id>` |

## Finding Closure

Every high and medium prior finding must have one row. A resubmission cannot move to review if any required finding is unmapped.

| Prior Finding ID | Prior Severity | Area | Required Fix | Contributor Fix Summary | Evidence Ref | Contributor Claim Status | Reviewer Closure Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `<finding id>` | high / medium / low | `<area>` | `<required fix>` | `<what changed>` | `<evidence id>` | fixed / disputed / not_applicable | closed_fixed / closed_rebutted / partially_closed / still_open / obsolete |

## Checker Results After Revision

| checker | status | severity | message |
| --- | --- | --- | --- |

## Remaining Issues
