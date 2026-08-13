# DTM Pre-Signature Readiness Checker

A DTM-inspired pre-signature workflow prototype that validates fictional contract-request data and approval readiness before human final review and manual submission to an eSignature platform.

## Business Problem

Before a contract request is manually sent to an eSignature platform, a business team must confirm that required request data, approvals, and attachments are complete.

Manual email and spreadsheet reviews can miss incomplete requests, missing approvals, invalid signer information, duplicate request IDs, and missing attachments. They can also make it difficult to keep a clear record of readiness checks.

## Solution Summary

This Python tool reads a fictional contract-request CSV file and applies clear validation and approval rules. It creates:

- A current readiness-results CSV with a status and reason for each request
- An append-only audit-log CSV that records each validation run
- A required human-review flag for every record

The tool does not approve, sign, send, cancel, or manage contracts.

## Scope

This MVP includes:

- CSV-based fictional contract-request input
- Required-field checks
- Duplicate `contract_id` checks within the input CSV
- Basic signer-email format checks
- Attachment and submission-date checks
- Approval rules for NDAs and high-value non-NDA contracts
- Readiness results and append-only audit logging
- Human final-review requirement for every request

## Non-Goals

This project does not include:

- A Digital Transaction Management platform
- Actual eSignature platform integration
- Electronic signatures, automatic approval, or automatic submission
- Real contracts, real company data, API keys, authentication, or cloud deployment
- Databases, n8n, Power Automate, AI, RAG, or browser automation
- Cancellation, resubmission, version control, or checks against actual submitted contracts

## Technology Used

- Python 3
- Python standard library: `csv`, `datetime`, `pathlib`, `re`, `decimal`, `uuid`
- CSV files
- Mermaid diagrams in Markdown documentation
- VS Code

No third-party Python packages are required.

## Project Structure

```text
dtm-pre-signature-readiness-checker/
├── README.md
├── requirements.txt
├── .gitignore
├── data/
│   └── contract_requests_sample.csv
├── src/
│   └── readiness_checker.py
├── output/
│   ├── readiness_results.csv
│   └── audit_log.csv
└── docs/
    ├── business_process.md
    ├── validation_rules.md
    ├── test_cases.md
    └── architecture.md

```

## How to Run

From the project root folder, run:

```bash
python src/readiness_checker.py
```

The program reads `data/contract_requests_sample.csv`.

It creates or updates:

- `output/readiness_results.csv`
- `output/audit_log.csv`

`readiness_results.csv` is replaced on each run with the latest results.

`audit_log.csv` is append-only. Each run adds one audit event for every checked contract request.

## Example Results

The sample data includes ten fictional requests:

| Result | Sample count | Examples |
|---|---:|---|
| `Ready for eSignature` | 3 | Complete standard contract, approved high-value contract, approved NDA |
| `Needs Approval` | 3 | Missing Legal approval, missing Finance approval, NDA without Legal approval |
| `Needs Correction` | 4 | Invalid email, future date, missing attachment, duplicate ID or required field |

`Ready for eSignature` means:

> Ready for human final review and manual submission to an eSignature platform.

It does not mean that the tool approved, signed, or sent the contract.

## Important Limitation

This project has no connection to DocuSign, Adobe Acrobat Sign, or another eSignature platform.

The audit log records that the readiness checker ran. It is not evidence that a contract was actually submitted, approved, cancelled, signed, or executed. Because the audit log is a CSV file, it is not tamper-proof.

## Documentation

- [Business process](docs/business_process.md)
- [Validation rules](docs/validation_rules.md)
- [Test cases](docs/test_cases.md)
- [Architecture](docs/architecture.md)

## What I Learned

- Translate a business workflow into clear data-validation rules
- Separate data-quality issues from approval-readiness issues
- Apply a clear status-priority rule: `Needs Correction` takes priority over `Needs Approval`
- Use CSV files to create simple, traceable output and audit records
- Design a workflow that keeps human final review in control
- Write maintainable Python with clear functions, constants, error handling, and comments

## Portfolio Summary

I built a DTM-inspired pre-signature workflow prototype in Python. The tool validates fictional contract-request data, checks approval readiness based on contract type and value, identifies data-quality exceptions, and creates an append-only audit log. Every result requires human final review before manual submission to an eSignature platform. This is a portfolio prototype, not a production DTM or eSignature system.    
