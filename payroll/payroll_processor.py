from collections.abc import Mapping
from decimal import Decimal, ROUND_HALF_UP

from .employee import Employee
from .employee_type import EmployeeType
from .pay_slip import PaySlip


class PayrollProcessor:
	@staticmethod
	def calculate_gross_pay(
		employee: Employee,
		hours_or_days: Decimal | int | float,
	) -> Decimal:
		if not isinstance(employee, Employee):
			raise TypeError("employee must be an Employee")
		if not isinstance(employee.employee_type, EmployeeType):
			raise TypeError("employee.employee_type must be an EmployeeType")
		if not isinstance(employee.pay_rate, Decimal):
			raise TypeError("employee.pay_rate must be a Decimal")
		if not employee.pay_rate.is_finite() or employee.pay_rate < 0:
			raise ValueError("employee.pay_rate must be finite and non-negative")
		if isinstance(hours_or_days, bool) or not isinstance(
			hours_or_days, (Decimal, int, float)
		):
			raise TypeError("hours_or_days must be a Decimal or number")

		work_amount = Decimal(str(hours_or_days))
		if not work_amount.is_finite() or work_amount < 0:
			raise ValueError("hours_or_days must be finite and non-negative")

		if employee.employee_type is EmployeeType.FULL_TIME:
			gross_pay = employee.pay_rate
		elif employee.employee_type is EmployeeType.PART_TIME:
			gross_pay = employee.pay_rate * min(work_amount, Decimal("120"))
		elif employee.employee_type is EmployeeType.CONTRACTOR:
			gross_pay = employee.pay_rate * work_amount
		else:
			raise ValueError("unsupported employee type")

		return gross_pay.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

	@staticmethod
	def calculate_tax(gross_pay: Decimal | int | float) -> Decimal:
		if isinstance(gross_pay, bool) or not isinstance(
			gross_pay, (Decimal, int, float)
		):
			raise TypeError("gross_pay must be a Decimal or number")

		gross_amount = Decimal(str(gross_pay))
		if not gross_amount.is_finite() or gross_amount < 0:
			raise ValueError("gross_pay must be finite and non-negative")

		zero = Decimal("0")
		first_bracket = min(max(gross_amount - Decimal("1000"), zero), Decimal("2000"))
		second_bracket = min(max(gross_amount - Decimal("3000"), zero), Decimal("2000"))
		third_bracket = max(gross_amount - Decimal("5000"), zero)
		tax_amount = (
			first_bracket * Decimal("0.10")
			+ second_bracket * Decimal("0.20")
			+ third_bracket * Decimal("0.30")
		)
		return tax_amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

	@staticmethod
	def calculate_deductions(
		employee: Employee,
		gross_pay: Decimal | int | float,
	) -> dict[str, Decimal]:
		if not isinstance(employee, Employee):
			raise TypeError("employee must be an Employee")
		if not isinstance(employee.employee_type, EmployeeType):
			raise TypeError("employee.employee_type must be an EmployeeType")
		if not isinstance(employee.is_union_member, bool):
			raise TypeError("employee.is_union_member must be a Boolean")
		if not isinstance(employee.has_retirement, bool):
			raise TypeError("employee.has_retirement must be a Boolean")
		if isinstance(gross_pay, bool) or not isinstance(
			gross_pay, (Decimal, int, float)
		):
			raise TypeError("gross_pay must be a Decimal or number")

		gross_amount = Decimal(str(gross_pay))
		if not gross_amount.is_finite() or gross_amount < 0:
			raise ValueError("gross_pay must be finite and non-negative")

		deductions: dict[str, Decimal] = {}
		if employee.employee_type is EmployeeType.FULL_TIME:
			deductions["health_insurance"] = Decimal("150.00")
		if employee.has_retirement:
			deductions["retirement"] = (gross_amount * Decimal("0.05")).quantize(
				Decimal("0.01"), rounding=ROUND_HALF_UP
			)
		if employee.is_union_member:
			deductions["union_dues"] = Decimal("50.00")
		return deductions

	@staticmethod
	def generate_pay_slip(
		employee: Employee,
		hours_or_days: Decimal | int | float,
	) -> PaySlip:
		gross_pay = PayrollProcessor.calculate_gross_pay(employee, hours_or_days)
		tax_amount = PayrollProcessor.calculate_tax(gross_pay)
		deductions = PayrollProcessor.calculate_deductions(employee, gross_pay)

		currency_quantum = Decimal("0.01")
		gross_pay = gross_pay.quantize(currency_quantum, rounding=ROUND_HALF_UP)
		tax_amount = tax_amount.quantize(currency_quantum, rounding=ROUND_HALF_UP)
		deductions = {
			name: amount.quantize(currency_quantum, rounding=ROUND_HALF_UP)
			for name, amount in deductions.items()
		}
		total_deductions = sum(deductions.values(), Decimal("0"))
		net_pay = (gross_pay - tax_amount - total_deductions).quantize(
			currency_quantum, rounding=ROUND_HALF_UP
		)

		return PaySlip(
			employee=employee,
			gross_pay=gross_pay,
			tax_amount=tax_amount,
			deductions=deductions,
			net_pay=net_pay,
		)

	@staticmethod
	def process_monthly_payroll(
		employee_list: list[Employee],
		work_amounts: Mapping[str, Decimal | int | float] | None = None,
	) -> list[PaySlip]:
		if not isinstance(employee_list, list):
			raise TypeError("employee_list must be a list")
		if any(not isinstance(employee, Employee) for employee in employee_list):
			raise TypeError("employee_list must contain only Employee objects")
		if not employee_list:
			return []
		if not isinstance(work_amounts, Mapping):
			raise TypeError("work_amounts must map employee IDs to hours or days")

		validated_work_amounts = []
		for employee in employee_list:
			if not isinstance(employee.employee_type, EmployeeType):
				raise TypeError("employee.employee_type must be an EmployeeType")
			if employee.employee_id not in work_amounts:
				raise ValueError(
					f"missing work amount for employee {employee.employee_id!r}"
				)
			work_amount = work_amounts[employee.employee_id]
			if isinstance(work_amount, bool) or not isinstance(
				work_amount, (Decimal, int, float)
			):
				raise TypeError(
					f"work amount for employee {employee.employee_id!r} must be numeric"
				)
			work_amount = Decimal(str(work_amount))
			if not work_amount.is_finite() or work_amount < 0:
				raise ValueError(
					f"work amount for employee {employee.employee_id!r} "
					"must be finite and non-negative"
				)
			validated_work_amounts.append(work_amount)

		return [
			PayrollProcessor.generate_pay_slip(employee, work_amount)
			for employee, work_amount in zip(employee_list, validated_work_amounts)
		]
