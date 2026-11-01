# Payroll Calculator

## 1. Project Overview

This project contains Python code for calculating employee gross pay, progressive tax, payroll deductions, and net pay slips. It supports full-time, part-time, and contractor employees, and can process a list of employees when work amounts are supplied for each employee.

The project is implemented as a Python package and has a print-based manual demonstration. The root `main.py` file is empty, so the existing files do not provide a separate application entry point or interactive application.

## 2. Requirements and Features

### Technical requirements

- Python 3.10 or later. The source uses union type syntax such as `Decimal | int | float` and built-in generic types such as `list[Employee]`.
- Runtime code uses Python standard-library modules: `dataclasses`, `decimal`, `enum`, and `collections.abc`.
- The pytest test suite imports `pytest`. The existing `requirements.txt` file is empty and does not declare dependencies or versions.
- No web framework, database, external service, or runtime third-party package is used by the payroll modules.

### Implemented functionality

- `EmployeeType` defines `FULL_TIME`, `PART_TIME`, and `CONTRACTOR`, with values `MONTHLY`, `HOURLY`, and `DAILY`.
- `Employee` stores an ID, name, employee type, Decimal pay rate, and optional union and retirement flags. It validates non-empty string IDs/names, enum/type values, and non-negative Decimal pay rates.
- Gross pay uses the fixed pay rate for full-time employees, hourly rate multiplied by work hours for part-time employees (capped at 120 hours), and daily rate multiplied by days for contractors.
- Progressive tax is calculated at 0% on the first $1,000, 10% on the next $2,000, 20% on the next $2,000, and 30% above $5,000.
- Deductions include $150 health insurance for full-time employees, a 5% retirement contribution when enabled, and $50 union dues when enabled.
- Currency calculations use `Decimal` and round to two decimal places with `ROUND_HALF_UP`.
- `PaySlip` stores the employee, gross pay, tax, deductions, and net pay. Its validation requires Decimal, finite, non-negative monetary amounts and a dictionary of named Decimal deductions.
- `generate_pay_slip` combines gross pay, tax, deductions, and net pay.
- `process_monthly_payroll` accepts a list of employees and a mapping from employee IDs to individual work amounts, then returns pay slips in employee-list order. It returns an empty list for an empty employee list.

## 3. Project Structure

```text
payroll-calculator/
|-- payroll/
|   |-- __init__.py
|   |-- employee.py
|   |-- employee_type.py
|   |-- pay_slip.py
|   `-- payroll_processor.py
|-- tests/
|   |-- __init__.py
|   `-- test_payroll_processor.py
|-- main.py
|-- requirements.txt
|-- test_manual.py
`-- SOLUTION.md
```

- `payroll/employee_type.py`: employee type enum and pay-basis values.
- `payroll/employee.py`: validated `Employee` dataclass.
- `payroll/pay_slip.py`: validated `PaySlip` dataclass.
- `payroll/payroll_processor.py`: gross pay, tax, deductions, pay slip generation, and monthly batch processing.
- `tests/test_payroll_processor.py`: pytest unit tests for the payroll processor.
- `test_manual.py`: top-level print-based examples of gross pay, taxes, deductions, pay slips, and batch processing.
- `main.py`: empty in the current project; it does not start an application.
- `requirements.txt`: empty in the current project.
- `payroll/__init__.py` and `tests/__init__.py`: empty package initializer files.
- `.pytest_cache/` and `__pycache__/` may appear after running tests or Python; they are generated files, not application modules.

## 4. Installation Instructions

Run the following commands from the project root in Windows PowerShell. Use Python 3.10 or later.

```powershell
python --version
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install pytest
```

The project has no declared runtime dependencies, and `requirements.txt` is empty. Pytest is needed to run the test module because the tests import it. The project does not specify a pytest version.

## 5. How to Run the Application

There is no application entry point in the current files: `main.py` is empty. Running it completes without output:

```powershell
.\.venv\Scripts\python.exe main.py
```

The available executable demonstration is `test_manual.py`. Run it from the project root:

```powershell
.\.venv\Scripts\python.exe test_manual.py
```

The script constructs sample employees and prints gross pay, tax, deductions, pay slip totals, and monthly payroll results. It uses work amounts defined directly in the script; no external configuration is required.

## 6. How to Run Pytest

From the project root, run the focused test module:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_payroll_processor.py -q
```

For verbose test names:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_payroll_processor.py -v
```

The explicit test path avoids collecting the root `test_manual.py` demonstration script.

## 7. Sample Output

The following excerpt is from the actual output of `python test_manual.py` in the current project:

```text
=== GROSS PAY TESTS ===
John: Gross Pay = $4000.00
Sarah: Gross Pay = $2000.00
Mike: Gross Pay = $2400.00
David: Gross Pay = $2400.00
Anna: Gross Pay = $3000.00

=== TAX TESTS ===
Gross: $4000.00 | Tax: $400.00
Gross: $5000.00 | Tax: $600.00
Gross: $6000.00 | Tax: $900.00

=== PAYSLIP TESTS ===
Employee: Robert
Gross Pay: $4000.00
Tax: $400.00
Deductions: {'health_insurance': Decimal('150.00'), 'retirement': Decimal('200.00'), 'union_dues': Decimal('50.00')}
Net Pay: $3200.00
```

The current focused pytest run completed with:

```text
53 passed
```

## 8. Assumptions and Design Decisions

### Explicitly documented decisions

Not specified in the existing project files. There are no separate configuration or design documents defining payroll policy.

### Decisions observable in the implementation

- The enum values associate full-time with monthly pay, part-time with hourly pay, and contractor with daily pay.
- The part-time work amount is capped at 120 hours in gross-pay calculation.
- Monthly tax uses marginal brackets; each percentage applies only to the portion inside that bracket.
- Monthly processing obtains hours or days from a mapping keyed by employee ID. A work amount is required for every employee in a non-empty list, including full-time employees whose gross-pay calculation ignores that amount.
- Work amounts passed to monthly processing may be `Decimal`, `int`, or `float`; booleans and non-finite or negative numbers are rejected.
- The exact monthly schedule is supplied by the caller; no work hours or days are stored on `Employee` or defaulted by the processor.
- The manual demonstration and tests use these rules directly; no separate payroll policy configuration exists.

## 9. Test Coverage

`tests/test_payroll_processor.py` contains parametrized pytest cases covering:

- Gross-pay calculations for all three employee types and the 120-hour part-time cap.
- Progressive-tax values from $0 through income above $5,000, including $4,000 producing $400 tax.
- All combinations of employee type, union membership, and retirement eligibility, plus retirement rounding.
- Pay slip contents and net pay.
- Monthly processing for six employees with individually keyed work amounts, returned order, and empty input.
- Rejection of invalid employee lists, missing work amounts, negative amounts, NaN, Infinity, booleans, and string amounts.
- Rejection of invalid gross-pay and tax inputs.

The current test file does not directly test the standalone validation behavior of the `Employee` and `PaySlip` constructors, the behavior for duplicate employee IDs in a batch, or how unused extra keys in the work-amount mapping are handled. Those cases are not specified by the existing tests.
