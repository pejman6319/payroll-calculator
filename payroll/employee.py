from dataclasses import dataclass
from decimal import Decimal

from .employee_type import EmployeeType


@dataclass
class Employee:
	employee_id: str
	name: str
	employee_type: EmployeeType
	pay_rate: Decimal
	is_union_member: bool = False
	has_retirement: bool = False

	def __post_init__(self) -> None:
		if not isinstance(self.employee_id, str):
			raise TypeError("employee_id must be a string")
		if not self.employee_id.strip():
			raise ValueError("employee_id cannot be empty")
		if not isinstance(self.name, str):
			raise TypeError("name must be a string")
		if not self.name.strip():
			raise ValueError("name cannot be empty")
		if not isinstance(self.employee_type, EmployeeType):
			raise TypeError("employee_type must be an EmployeeType")
		if not isinstance(self.pay_rate, Decimal):
			raise TypeError("pay_rate must be a Decimal")
		if self.pay_rate < 0:
			raise ValueError("pay_rate cannot be negative")
		if not isinstance(self.is_union_member, bool):
			raise TypeError("is_union_member must be a Boolean")
		if not isinstance(self.has_retirement, bool):
			raise TypeError("has_retirement must be a Boolean")
