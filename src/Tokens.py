import typing
from typing import List
from typing import NewType

MD_ENUM = NewType('MD_ENUM', int)

class Token:

	def __init__(self, id: MD_ENUM, begin: int = None, end: int = None) -> None:
		self.id = id
		self.begin = begin
		self.end = end

	
	def __str__(self) -> str:
		return f"\nToken:\n\tid:{self.id}\n\tbegin:{self.begin}\n\tend:{self.end}\n"


	def __repr__(self) -> str:
		return self.__str__()


class ListToken(Token):

	def __init__(self, id: MD_ENUM, begin: int = None, end: int = None, indent: int = None) -> None:
		super().__init__(id, begin, end)
		self.indent = indent

	
	def __str__(self) -> str:
		return f"\nListToken:\n\tid:{self.id}\n\tbegin:{self.begin}\n\tend:{self.end}\n\tindent:{self.indent}\n"


	def __repr__(self) -> str:
		return self.__str__()