# Test Cases

## Purpose

This document records the fictional sample test cases used to validate the readiness checker.

## Sample Record Tests

| Test ID | Contract ID | Scenario | Expected status | Result |
|---|---|---|---|---|
| TC-01 | `CTR-1001` | Low-value non-NDA with complete required data | `Ready for eSignature` | Passed |
| TC-02 | `CTR-1002` | High-value non-NDA with Legal and Finance approved | `Ready for eSignature` | Passed |
| TC-03 | `CTR-1003` | NDA with Legal approved and Finance blank | `Ready for eSignature` | Passed |
| TC-04 | `CTR-1004` | High-value non-NDA with Legal approval pending | `Needs Approval` | Passed |
| TC-05 | `CTR-1005` | High-value non-NDA with Finance approval pending | `Needs Approval` | Passed |
| TC-06 | `CTR-1006` | NDA with Legal approval pending | `Needs Approval` | Passed |
| TC-07 | `CTR-1007` | Invalid signer email and duplicate `contract_id` | `Needs Correction` | Passed |
| TC-08 | `CTR-1008` | Future submission date using fixed test date `2099-01-01` | `Needs Correction` | Passed |
| TC-09 | `CTR-1009` | Attachment is not included | `Needs Correction` | Passed |
| TC-10 | `CTR-1007` | Blank `vendor_name` and duplicate `contract_id` | `Needs Correction` | Passed |

## Audit-Log Test

| Test ID | Test | Expected result | Result |
|---|---|---|---|
| TC-11 | Run the checker twice using the same 10-record input CSV | Audit log contains 21 lines: 1 header row and 20 audit events | Passed |

The first test run created 10 audit events. The second test run appended 10 new audit events without removing the first 10 events.

## Test Evidence

The checker was run with:

```bash
python src/readiness_checker.py
```

The audit-log line count was checked with:

```bash
wc -l output/audit_log.csv
```

The result was:

```text
21 output/audit_log.csv
```

Later runs append additional audit events. Therefore, the current audit-log line count may be greater than 21.

## Test Conclusion

All ten fictional sample records produced their expected readiness status.

The output CSV was created successfully. The audit log preserved prior records and appended new audit events on each additional run.