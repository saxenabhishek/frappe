from typing import Any, Callable

from pypika import Query
from pypika.terms import ValueWrapper

import frappe


class Holder():
	payload = None

	def __init__(self, payload: Any) -> None:
		self.payload = payload

	def __getattr__(self, name: str) -> Any:
		if hasattr(self.payload, name):
			module = getattr(self.payload, name)
			if callable(module):
				return self.call_this(module)
			return module
		raise AttributeError(f" '{self.payload.__class__}' object has no attribute '{name}'")

	def call_this(self, module: Callable):
		raise NotImplementedError

	def __repr__(self) -> str:
		return self.payload.__repr__()

	def __str__(self)  -> str:
		return self.payload.__str__()


class PseudoMethods():
	def __init__(self,func) -> None:
		self.func = func

	def __call__(self, *args: Any, **kwds: Any) -> Any:
		result = self.func(*args, **kwds)
		if isinstance(result, str):
			return result

		return self.redirect(result)

	def redirect(self, holder):
		raise NotImplementedError

	def __repr__(self) -> str:
		return f"{self.__class__}<{self.func.__repr__()}>"


class RedirectToSanitiseFields(PseudoMethods):
	@staticmethod
	def redirect(holder):
		return SanitiseFields(holder)


class SanitiseFields(Holder):
	def __init__(self, query: Query):
		super().__init__(query)

	def _sanitise(self, criterion):
		if hasattr(criterion, "left"):
			self._sanitise(criterion.left)
		if hasattr(criterion, "right"):
			self._sanitise(criterion.right)

		if isinstance(criterion, ValueWrapper):
			criterion.value = frappe.db.escape(criterion.value)

	def where(self, criterion):
		self._sanitise(criterion)
		return self.payload.where(criterion)

	def set(self, field, value):
		value = frappe.db.escape(value)
		return self.payload.set(field, value)

	@staticmethod
	def call_this(module):
		return RedirectToSanitiseFields(module)
