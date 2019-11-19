import os
import sys
from enum import IntEnum
import typing
from typing import List
from typing import Union
from typing import Tuple
from typing import Dict
from typing import NewType

from TokenTypes import *
from Token import *
from Debug import *

LexerToken = NewType('Token', None)

def parse(tokens: List[LexerToken]) -> None:
	i = 0
	while i < len(tokens):
		t = tokens[i]
		if t.id == MD.HTML_BEGIN or t.id == MD.HTML_END:
			debug(t)
		i += 1