
from decimal import Decimal

from payroll.employee import Employee
from payroll.employee_type import EmployeeType
from payroll.payroll_processor import PayrollProcessor


# Gross Pay Tests
print("=== GROSS PAY TESTS ===")

employees = [
    Employee("1", "John", EmployeeType.FULL_TIME, Decimal("4000")),
    Employee("2", "Sarah", EmployeeType.PART_TIME, Decimal("20")),
    Employee("3", "Mike", EmployeeType.PART_TIME, Decimal("20")),
    Employee("4", "David", EmployeeType.PART_TIME, Decimal("20")),
    Employee("5", "Anna", EmployeeType.CONTRACTOR, Decimal("300")),
]

work_amounts = [0, 100, 120, 130, 10]

for employee, amount in zip(employees, work_amounts):
    result = PayrollProcessor.calculate_gross_pay(employee, amount)
    print(f"{employee.name}: Gross Pay = ${result:.2f}")


# Progressive Tax Tests
print("\n=== TAX TESTS ===")

test_amounts = [
    Decimal("500"),
    Decimal("1000"),
    Decimal("2000"),
    Decimal("3000"),
    Decimal("4000"),
    Decimal("5000"),
    Decimal("6000"),
]

for amount in test_amounts:
    tax = PayrollProcessor.calculate_tax(amount)
    print(f"Gross: ${amount:.2f} | Tax: ${tax:.2f}")

# Deductions Tests
print("\n=== DEDUCTIONS TESTS ===")

deduction_employees = [
    Employee(
        "6", "FullTime",
        EmployeeType.FULL_TIME,
        Decimal("4000"),
        True, True
    ),
    Employee(
        "7", "PartTime",
        EmployeeType.PART_TIME,
        Decimal("20"),
        False, True
    ),
    Employee(
        "8", "Contractor",
        EmployeeType.CONTRACTOR,
        Decimal("300"),
        True, False
    ),
    Employee(
        "9", "Basic",
        EmployeeType.PART_TIME,
        Decimal("20"),
        False, False
    ),
]

gross_amounts = [
    Decimal("4000"),
    Decimal("2000"),
    Decimal("3000"),
    Decimal("1000"),
]

for employee, gross in zip(deduction_employees, gross_amounts):
    deductions = PayrollProcessor.calculate_deductions(
        employee, gross
    )
    print(f"{employee.name}: {deductions}")

# PaySlip Tests
print("\n=== PAYSLIP TESTS ===")

payslip_employee = Employee(
    "10",
    "Robert",
    EmployeeType.FULL_TIME,
    Decimal("4000"),
    True,
    True,
)

payslip = PayrollProcessor.generate_pay_slip(
    payslip_employee, 0
)

print(f"Employee: {payslip.employee.name}")
print(f"Gross Pay: ${payslip.gross_pay:.2f}")
print(f"Tax: ${payslip.tax_amount:.2f}")
print(f"Deductions: {payslip.deductions}")
print(f"Net Pay: ${payslip.net_pay:.2f}")

# Monthly Payroll Tests
print("\n=== MONTHLY PAYROLL TESTS ===")

monthly_employees = [
    Employee("11", "John", EmployeeType.FULL_TIME, Decimal("4000"), True, True),
    Employee("12", "Sarah", EmployeeType.PART_TIME, Decimal("20"), False, True),
    Employee("13", "Mike", EmployeeType.PART_TIME, Decimal("20"), True, False),
    Employee("14", "David", EmployeeType.PART_TIME, Decimal("20"), False, False),
    Employee("15", "Anna", EmployeeType.CONTRACTOR, Decimal("300"), True, True),
    Employee("16", "Robert", EmployeeType.FULL_TIME, Decimal("5000"), False, False),
]

monthly_work_amounts = {
    "11": Decimal("0"),
    "12": Decimal("100"),
    "13": Decimal("120"),
    "14": Decimal("130"),
    "15": Decimal("10"),
    "16": Decimal("0"),
}

monthly_slips = PayrollProcessor.process_monthly_payroll(
    monthly_employees,
    monthly_work_amounts
)

for slip in monthly_slips:
    print(
        f"{slip.employee.name}: "
        f"Gross=${slip.gross_pay:.2f}, "
        f"Tax=${slip.tax_amount:.2f}, "
        f"Net=${slip.net_pay:.2f}"
    )
