# =============================================================================
# File Information: Basic information about this Python file and its purpose.
# =============================================================================
# File: readiness_checker.py
# Purpose: Validate fictional contract-request data before human final review
#          and manual submission to an eSignature platform.
#
# This tool does not approve, sign, send, cancel, or manage contracts.
# It checks data quality and required approval readiness only.
#
# Creation Date: 08-13-2026
# Author: K
# =============================================================================


# =============================================================================
# Imports: Load standard Python tools used by this program.
# =============================================================================

# Read data from CSV files and create CSV output files.
import csv

# Check signer_email values against a basic email-format pattern.
import re

# Print controlled error messages and safely stop the program if needed.
import sys

# Create a unique ID for every audit-log event.
import uuid

# Count how many times each contract_id appears in the input CSV.
from collections import Counter

# Compare submission dates and create a UTC timestamp for each checker run.
from datetime import date, datetime, timezone

# Safely compare contract amounts and handle invalid numeric values.
from decimal import Decimal, InvalidOperation

# Build file paths safely across operating systems, including Windows.
from pathlib import Path


# =============================================================================
# File Locations: Define the project folder and CSV file locations.
# =============================================================================

# Find the project folder.
# readiness_checker.py is stored in src, so parents[1] refers to the project root.
PROJECT_DIR = Path(__file__).resolve().parents[1]

# Set the location of the fictional input contract-request CSV file.
INPUT_FILE = PROJECT_DIR / "data" / "contract_requests_sample.csv"

# Set the location for the latest readiness-results CSV file.
RESULTS_FILE = PROJECT_DIR / "output" / "readiness_results.csv"

# Set the location for the append-only audit-log CSV file.
AUDIT_LOG_FILE = PROJECT_DIR / "output" / "audit_log.csv"


# =============================================================================
# Field Definitions: Define the input, results, and audit-log CSV columns.
# =============================================================================

# Store the required input CSV columns in their expected output order.
INPUT_FIELDS = [
    "contract_id",
    "vendor_name",
    "contract_type",
    "contract_amount",
    "signer_email",
    "legal_approval",
    "finance_approval",
    "attachment_included",
    "submission_date",
]

# Add the readiness-checker output columns after the original input columns.
RESULT_FIELDS = INPUT_FIELDS + [
    "readiness_status",
    "validation_reasons",
    "checked_at",
    "review_required",
]

# Define the smaller set of fields required in the audit-log CSV.
AUDIT_FIELDS = [
    "audit_event_id",
    "checked_at",
    "contract_id",
    "readiness_status",
    "validation_reasons",
    "review_required",
]

# Define fields that are required for every contract request.
# Approval fields are not listed here because their requirement depends
# on the contract type and contract amount business rules.
REQUIRED_FIELDS = [
    "contract_id",
    "vendor_name",
    "contract_type",
    "contract_amount",
    "signer_email",
    "attachment_included",
    "submission_date",
]


# =============================================================================
# Business Rule Constants: Store approved values in one central location.
# =============================================================================

# Define the three allowed readiness-status values.
STATUS_READY = "Ready for eSignature"
STATUS_NEEDS_APPROVAL = "Needs Approval"
STATUS_NEEDS_CORRECTION = "Needs Correction"

# Define normalized values used for comparisons.
APPROVED_VALUE = "approved"
YES_VALUE = "yes"
NDA_TYPE = "NDA"

# Define the approval threshold for non-NDA contracts.
APPROVAL_AMOUNT_THRESHOLD = Decimal("10000")

# Define the required review flag for every output record.
REVIEW_REQUIRED_VALUE = "Yes"

# Define a basic email-format pattern for this MVP.
# This checks format only; it does not confirm that a mailbox exists.
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


# =============================================================================
# Data Cleaning: Prepare CSV values for reliable validation.
# =============================================================================

def clean_value(value):
    # Convert None to an empty string, convert other values to text,
    # and remove spaces at the beginning or end of the value.
    return str(value or "").strip()


# =============================================================================
# Input Loading: Read the input CSV and confirm its structure is valid.
# =============================================================================

def load_contract_requests():
    # Stop with a clear message if the expected input CSV does not exist.
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Input file not found: {INPUT_FILE}")

    # Open the CSV using utf-8-sig.
    # This also handles a possible UTF-8 byte-order mark created by Excel.
    with INPUT_FILE.open("r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        # A header row is required because this project reads fields by name.
        if reader.fieldnames is None:
            raise ValueError("Input CSV must include a header row.")

        # Identify any required columns that are missing from the input CSV.
        missing_columns = [
            field for field in INPUT_FIELDS if field not in reader.fieldnames
        ]

        # Stop with a clear message when the input CSV structure is incomplete.
        if missing_columns:
            missing_text = ", ".join(missing_columns)
            raise ValueError(
                f"Input CSV is missing required columns: {missing_text}"
            )

        # Convert the CSV reader into a list of contract-request records.
        return list(reader)


# =============================================================================
# Duplicate Check: Find contract IDs that appear more than once in the input.
# =============================================================================

def get_duplicate_ids(records):
    # Create a list of non-blank contract IDs from every input record.
    contract_ids = [
        clean_value(record.get("contract_id"))
        for record in records
        if clean_value(record.get("contract_id"))
    ]

    # Count the number of times each contract ID appears.
    id_counts = Counter(contract_ids)

    # Return only IDs that appear more than once.
    # Every matching record will receive Needs Correction.
    return {
        contract_id
        for contract_id, count in id_counts.items()
        if count > 1
    }


# =============================================================================
# Record Validation: Apply data-quality and approval rules to one request.
# =============================================================================

def validate_record(record, duplicate_ids, checked_at):
    # Clean all input-field values before applying validation rules.
    values = {
        field: clean_value(record.get(field))
        for field in INPUT_FIELDS
    }

    # Keep correction issues separate from approval issues.
    # This makes the status-priority rule clear and easy to maintain.
    correction_reasons = []
    approval_reasons = []

    # -------------------------------------------------------------------------
    # Required Field Rule: Confirm that required fields are not blank.
    # -------------------------------------------------------------------------
    for field in REQUIRED_FIELDS:
        if not values[field]:
            correction_reasons.append(f"Required field is blank: {field}.")

    # -------------------------------------------------------------------------
    # Unique Contract ID Rule: Check for duplicate IDs in this input CSV.
    # -------------------------------------------------------------------------
    if values["contract_id"] in duplicate_ids:
        correction_reasons.append("Duplicate contract_id found in input file.")

    # -------------------------------------------------------------------------
    # Signer Email Rule: Confirm that the signer email has a basic valid format.
    # -------------------------------------------------------------------------
    if values["signer_email"] and not EMAIL_PATTERN.fullmatch(
        values["signer_email"]
    ):
        correction_reasons.append("Signer email has an invalid format.")

    # -------------------------------------------------------------------------
    # Attachment Rule: Confirm that the required attachment is included.
    # -------------------------------------------------------------------------
    if (
        values["attachment_included"]
        and values["attachment_included"].lower() != YES_VALUE
    ):
        correction_reasons.append("Attachment must be included (Yes).")

    # -------------------------------------------------------------------------
    # Submission Date Rule: Confirm that the date is valid and not in the future.
    # -------------------------------------------------------------------------
    if values["submission_date"]:
        try:
            # Convert the text date into a Python date object.
            submission_date = datetime.strptime(
                values["submission_date"],
                "%Y-%m-%d",
            ).date()

            # Add a correction reason if the date is after today's date.
            if submission_date > date.today():
                correction_reasons.append("Submission date cannot be in the future.")

        # Add a correction reason if the date does not use YYYY-MM-DD format.
        except ValueError:
            correction_reasons.append(
                "Submission date must use YYYY-MM-DD format."
            )

    # -------------------------------------------------------------------------
    # Contract Amount Rule: Confirm that the amount is a valid, non-negative number.
    # -------------------------------------------------------------------------
    amount = None

    if values["contract_amount"]:
        try:
            # Decimal is used instead of float for reliable money comparisons.
            amount = Decimal(values["contract_amount"])

            # A negative contract amount is not valid for this MVP scenario.
            if amount < 0:
                correction_reasons.append("Contract amount cannot be negative.")

        # Add a correction reason if the amount is not a number.
        except InvalidOperation:
            correction_reasons.append(
                "Contract amount must be a valid number."
            )

    # Normalize values before comparing them with business-rule constants.
    contract_type = values["contract_type"].upper()
    legal_approval = values["legal_approval"].lower()
    finance_approval = values["finance_approval"].lower()

    # -------------------------------------------------------------------------
    # NDA Approval Rule: NDA requires Legal approval but not Finance approval.
    # -------------------------------------------------------------------------
    if contract_type == NDA_TYPE:
        if legal_approval != APPROVED_VALUE:
            approval_reasons.append(
                "Legal approval must be Approved for an NDA."
            )

    # -------------------------------------------------------------------------
    # High-Value Approval Rule: Non-NDA contracts of $10,000 or more require
    # Legal approval and Finance approval.
    # -------------------------------------------------------------------------
    elif amount is not None and amount >= APPROVAL_AMOUNT_THRESHOLD:
        if legal_approval != APPROVED_VALUE:
            approval_reasons.append(
                "Legal approval must be Approved for contracts of $10,000 or more."
            )

        if finance_approval != APPROVED_VALUE:
            approval_reasons.append(
                "Finance approval must be Approved for contracts of $10,000 or more."
            )

    # -------------------------------------------------------------------------
    # Status Priority Rule: Data corrections take priority over approval issues.
    # -------------------------------------------------------------------------
    if correction_reasons:
        readiness_status = STATUS_NEEDS_CORRECTION
        reasons = correction_reasons

    elif approval_reasons:
        readiness_status = STATUS_NEEDS_APPROVAL
        reasons = approval_reasons

    else:
        readiness_status = STATUS_READY
        reasons = [
            "Ready for human final review and manual submission."
        ]

    # Return the original cleaned fields plus all required output fields.
    return {
        **values,
        "readiness_status": readiness_status,
        "validation_reasons": " ".join(reasons),
        "checked_at": checked_at,
        # Every request requires human final review, including ready requests.
        "review_required": REVIEW_REQUIRED_VALUE,
    }


# =============================================================================
# Results Output: Create the latest readiness-results CSV for the current run.
# =============================================================================

def write_results(results):
    # Create the output folder if it does not already exist.
    RESULTS_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Open the results file in write mode.
    # Write mode replaces the previous results file with the current run's results.
    with RESULTS_FILE.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=RESULT_FIELDS)

        # Write the column headers, then write each completed result record.
        writer.writeheader()
        writer.writerows(results)


# =============================================================================
# Audit Logging: Append one audit event for every checked contract request.
# =============================================================================

def append_audit_log(results):
    # Create the output folder if it does not already exist.
    AUDIT_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Check whether the audit log already contains data and a header row.
    file_has_content = (
        AUDIT_LOG_FILE.exists()
        and AUDIT_LOG_FILE.stat().st_size > 0
    )

    # Open the audit log in append mode.
    # Append mode preserves all existing audit-log records.
    with AUDIT_LOG_FILE.open("a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=AUDIT_FIELDS)

        # Write the header only when creating a new or empty audit-log file.
        if not file_has_content:
            writer.writeheader()

        # Create one audit event for every contract request that was checked.
        for result in results:
            writer.writerow(
                {
                    # Generate a unique audit-event ID for traceability.
                    "audit_event_id": str(uuid.uuid4()),

                    # Use the same UTC timestamp recorded in the results file.
                    "checked_at": result["checked_at"],

                    # Record the contract request that was checked.
                    "contract_id": result["contract_id"],

                    # Record the readiness decision.
                    "readiness_status": result["readiness_status"],

                    # Record the explanation for the readiness decision.
                    "validation_reasons": result["validation_reasons"],

                    # Confirm that human review is still required.
                    "review_required": result["review_required"],
                }
            )


# =============================================================================
# Main Process: Run the complete readiness-checker workflow.
# =============================================================================

def main():
    # Create one consistent UTC timestamp for every record in this run.
    checked_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    # Read the contract-request CSV file.
    records = load_contract_requests()

    # Find duplicate contract IDs before validating individual records.
    duplicate_ids = get_duplicate_ids(records)

    # Validate each contract request and collect all results.
    results = [
        validate_record(record, duplicate_ids, checked_at)
        for record in records
    ]

    # Create the current readiness-results CSV.
    write_results(results)

    # Append the current run's audit events without deleting prior events.
    append_audit_log(results)

    # Print a short confirmation message after successful completion.
    print(f"Checked {len(results)} contract request(s).")
    print(f"Results created: {RESULTS_FILE}")
    print(f"Audit events appended: {AUDIT_LOG_FILE}")


# =============================================================================
# Program Entry Point: Run main only when this file is executed directly.
# =============================================================================

if __name__ == "__main__":
    try:
        # Start the readiness-checker workflow.
        main()

    # Handle expected input-file, CSV-structure, encoding, and file-access errors.
    except (
        FileNotFoundError,
        ValueError,
        UnicodeDecodeError,
        csv.Error,
        OSError,
    ) as error:
        print(f"Readiness checker error: {error}", file=sys.stderr)
        sys.exit(1)