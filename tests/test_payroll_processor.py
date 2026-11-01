from decimal import Decimal
from typing import cast

import pytest

from payroll.employee import Employee
from payroll.employee_type import EmployeeType
from payroll.pay_slip import PaySlip
from payroll.payroll_processor import PayrollProcessor


@pytest.mark.parametrize(
	("employee_type", "pay_rate", "work_amount", "expected_gross"),
	[
		(EmployeeType.FULL_TIME, "4000", Decimal("12"), "4000.00"),
		(EmployeeType.PART_TIME, "20", Decimal("5"), "100.00"),
		(EmployeeType.CONTRACTOR, "300", Decimal("2"), "600.00"),
	],
)
def test_calculate_gross_pay_by_employee_type(
	employee_type: EmployeeType,
	pay_rate: str,
	work_amount: Decimal,
	expected_gross: str,
) -> None:
	employee = Employee("E1", "Test Employee", employee_type, Decimal(pay_rate))

	assert PayrollProcessor.calculate_gross_pay(employee, work_amount) == Decimal(
		expected_gross
	)


@pytest.mark.parametrize(
	("hours", "expected_gross"),
	[(Decimal("120"), "2400.00"), (Decimal("130"), "2400.00")],
)
def test_part_time_hours_are_limited_to_120(
	hours: Decimal, expected_gross: str
) -> None:
	employee = Employee("P1", "Part Time", EmployeeType.PART_TIME, Decimal("20"))

	assert PayrollProcessor.calculate_gross_pay(employee, hours) == Decimal(
		expected_gross
	)


@pytest.mark.parametrize(
	("gross_pay", "expected_tax"),
	[
		("0", "0.00"),
		("500", "0.00"),
		("1000", "0.00"),
		("2000", "100.00"),
		("3000", "200.00"),
		("4000", "400.00"),
		("5000", "600.00"),
		("6000", "900.00"),
	],
)
def test_calculate_progressive_tax(gross_pay: str, expected_tax: str) -> None:
	assert PayrollProcessor.calculate_tax(Decimal(gross_pay)) == Decimal(expected_tax)


@pytest.mark.parametrize(
	("employee_type", "is_union_member", "has_retirement"),
	[
		(employee_type, is_union_member, has_retirement)
		for employee_type in EmployeeType
		for is_union_member in (False, True)
		for has_retirement in (False, True)
	],
)
def test_calculate_all_deduction_combinations(
	employee_type: EmployeeType,
	is_union_member: bool,
	has_retirement: bool,
) -> None:
	employee = Employee(
		"E1",
		"Test Employee",
		employee_type,
		Decimal("20"),
		is_union_member,
		has_retirement,
	)
	expected: dict[str, Decimal] = {}
	if employee_type is EmployeeType.FULL_TIME:
		expected["health_insurance"] = Decimal("150.00")
	if has_retirement:
		expected["retirement"] = Decimal("50.00")
	if is_union_member:
		expected["union_dues"] = Decimal("50.00")

	assert PayrollProcessor.calculate_deductions(employee, Decimal("1000")) == expected


def test_retirement_deduction_rounds_half_up() -> None:
	employee = Employee(
		"E1", "Test Employee", EmployeeType.PART_TIME, Decimal("20"), has_retirement=True
	)

	assert PayrollProcessor.calculate_deductions(employee, Decimal("101.01")) == {
		"retirement": Decimal("5.05")
	}


def test_generate_pay_slip_calculates_net_pay() -> None:
	employee = Employee(
		"F1", "Full Time", EmployeeType.FULL_TIME, Decimal("4000"), True, True
	)

	pay_slip = PayrollProcessor.generate_pay_slip(employee, Decimal("0"))

	assert isinstance(pay_slip, PaySlip)
	assert pay_slip.gross_pay == Decimal("4000.00")
	assert pay_slip.tax_amount == Decimal("400.00")
	assert pay_slip.deductions == {
		"health_insurance": Decimal("150.00"),
		"retirement": Decimal("200.00"),
		"union_dues": Decimal("50.00"),
	}
	assert pay_slip.net_pay == Decimal("3200.00")


def test_process_monthly_payroll_with_six_employees() -> None:
	employees = [
		Employee("F1", "Full 1", EmployeeType.FULL_TIME, Decimal("4000")),
		Employee("P1", "Part 1", EmployeeType.PART_TIME, Decimal("20")),
		Employee("C1", "Contract 1", EmployeeType.CONTRACTOR, Decimal("300")),
		Employee("F2", "Full 2", EmployeeType.FULL_TIME, Decimal("5000")),
		Employee("P2", "Part 2", EmployeeType.PART_TIME, Decimal("15")),
		Employee("C2", "Contract 2", EmployeeType.CONTRACTOR, Decimal("100")),
	]
	work_amounts = {
		"F1": Decimal("0"),
		"P1": Decimal("5"),
		"C1": Decimal("2"),
		"F2": Decimal("0"),
		"P2": Decimal("130"),
		"C2": Decimal("8"),
	}

	pay_slips = PayrollProcessor.process_monthly_payroll(employees, work_amounts)

	assert len(pay_slips) == 6
	assert all(isinstance(pay_slip, PaySlip) for pay_slip in pay_slips)
	assert [pay_slip.employee for pay_slip in pay_slips] == employees
	assert [pay_slip.gross_pay for pay_slip in pay_slips] == [
		Decimal("4000.00"),
		Decimal("100.00"),
		Decimal("600.00"),
		Decimal("5000.00"),
		Decimal("1800.00"),
		Decimal("800.00"),
	]


def test_process_monthly_payroll_empty_list() -> None:
	assert PayrollProcessor.process_monthly_payroll([]) == []


@pytest.mark.parametrize(
	"employee_list",
	["not a list", (object(),), [object()]],
)
def test_process_monthly_payroll_rejects_invalid_employee_lists(
	employee_list: object,
) -> None:
	with pytest.raises(TypeError):
		PayrollProcessor.process_monthly_payroll(cast(list[Employee], employee_list))


def test_process_monthly_payroll_rejects_missing_work_amounts() -> None:
	employee = Employee("P1", "Part Time", EmployeeType.PART_TIME, Decimal("20"))

	with pytest.raises(TypeError):
		PayrollProcessor.process_monthly_payroll([employee])
	with pytest.raises(ValueError, match="missing work amount"):
		PayrollProcessor.process_monthly_payroll([employee], {})


@pytest.mark.parametrize(
	("work_amount", "exception"),
	[
		(Decimal("-1"), ValueError),
		(Decimal("NaN"), ValueError),
		(Decimal("Infinity"), ValueError),
		(Decimal("-Infinity"), ValueError),
		(float("nan"), ValueError),
		(float("inf"), ValueError),
		(True, TypeError),
		("8", TypeError),
	],
)
def test_process_monthly_payroll_rejects_invalid_work_amounts(
	work_amount: object, exception: type[Exception]
) -> None:
	employee = Employee("P1", "Part Time", EmployeeType.PART_TIME, Decimal("20"))

	with pytest.raises(exception):
		PayrollProcessor.process_monthly_payroll(
			[employee], {"P1": cast(Decimal | int | float, work_amount)}
		)


@pytest.mark.parametrize(
	("gross_pay", "exception"),
	[
		(Decimal("-1"), ValueError),
		(Decimal("NaN"), ValueError),
		(Decimal("Infinity"), ValueError),
		(Decimal("-Infinity"), ValueError),
		(True, TypeError),
		("4000", TypeError),
	],
)
def test_calculate_tax_rejects_invalid_inputs(
	gross_pay: object, exception: type[Exception]
) -> None:
	with pytest.raises(exception):
		PayrollProcessor.calculate_tax(cast(Decimal | int | float, gross_pay))


@pytest.mark.parametrize(
	("work_amount", "exception"),
	[
		(Decimal("-1"), ValueError),
		(Decimal("NaN"), ValueError),
		(Decimal("Infinity"), ValueError),
		(Decimal("-Infinity"), ValueError),
		(True, TypeError),
		("8", TypeError),
	],
)
def test_calculate_gross_pay_rejects_invalid_inputs(
	work_amount: object, exception: type[Exception]
) -> None:
	employee = Employee("P1", "Part Time", EmployeeType.PART_TIME, Decimal("20"))

	with pytest.raises(exception):
		PayrollProcessor.calculate_gross_pay(
			employee, cast(Decimal | int | float, work_amount)
		)
