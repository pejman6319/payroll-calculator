from dataclasses import dataclass
from decimal import Decimal

from .employee import Employee


@dataclass
class PaySlip:
	employee: Employee
	gross_pay: Decimal
	tax_amount: Decimal
	deductions: dict[str, Decimal]
	net_pay: Decimal

	def __post_init__(self) -> None:
		if not isinstance(self.employee, Employee):
			raise TypeError("employee must be an Employee")

		for field_name, amount in (
			("gross_pay", self.gross_pay),
			("tax_amount", self.tax_amount),
			("net_pay", self.net_pay),
		):
			if not isinstance(amount, Decimal):
				raise TypeError(f"{field_name} must be a Decimal")
			if not amount.is_finite():
				raise ValueError(f"{field_name} must be finite")
			if amount < 0:
				raise ValueError(f"{field_name} cannot be negative")

		if not isinstance(self.deductions, dict):
			raise TypeError("deductions must be a dict")
		for name, amount in self.deductions.items():
			if not isinstance(name, str) or not name.strip():
				raise ValueError("deduction names must be non-empty strings")
			if not isinstance(amount, Decimal):
				raise TypeError("deduction amounts must be Decimals")
			if not amount.is_finite():
				raise ValueError("deduction amounts must be finite")
			if amount < 0:
				raise ValueError("deduction amounts cannot be negative")
