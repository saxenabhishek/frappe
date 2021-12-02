from typing import Any, Callable

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
