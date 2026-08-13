# Validation Rules

## Purpose

This document defines the approved validation rules for the DTM-inspired pre-signature readiness checker.

The rules are deterministic. The tool does not use AI or make final business decisions.

## Input Fields

| Field | Requirement |
|---|---|
| `contract_id` | Required and unique within the input CSV |
| `vendor_name` | Required |
| `contract_type` | Required |
| `contract_amount` | Required, numeric, and not negative |
| `signer_email` | Required and must have a basic valid email format |
| `legal_approval` | Required only when the applicable approval rule requires it |
| `finance_approval` | Required only when the applicable approval rule requires it |
| `attachment_included` | Required and must be `Yes` |
| `submission_date` | Required, must use `YYYY-MM-DD`, and cannot be in the future |

## Approval Rules

| Contract condition | `legal_approval` | `finance_approval` | Result if required approval is missing |
|---|---|---|---|
| `NDA` | `Approved` required | Not required; may be blank | `Needs Approval` |
| Non-NDA contract of `$10,000` or more | `Approved` required | `Approved` required | `Needs Approval` |
| Non-NDA contract below `$10,000` | Not required | Not required | No approval issue |

## Data-Quality Rules

A request receives `Needs Correction` if one or more of these conditions apply:

- A required field is blank.
- A `contract_id` is duplicated within the same input CSV.
- `signer_email` does not match the basic email-format rule.
- `attachment_included` is not `Yes`.
- `submission_date` is in the future.
- `submission_date` does not use `YYYY-MM-DD`.
- `contract_amount` is not numeric or is negative.

## Status Priority

The checker applies the following priority order:

1. `Needs Correction`  
   Data-quality issues must be fixed first.

2. `Needs Approval`  
   Data is valid, but a required approval is missing.

3. `Ready for eSignature`  
   Data and required approvals are complete.

If a request has both a data-quality problem and an approval problem, the result is `Needs Correction`.

## Human Review Requirement

Every output record includes:

```text
review_required = Yes
```

`Ready for eSignature` means:

> Ready for human final review and manual submission to an eSignature platform.

It does not mean the tool automatically approves, signs, or sends the contract.

## Rule Scope

The duplicate-ID rule checks only the current input CSV.

This MVP does not check actual eSignature submission history, cancellations, resubmissions, contract versions, or records outside the input CSV.