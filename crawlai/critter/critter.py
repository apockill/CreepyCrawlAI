from godot import exposed

from .ai_critter import AICritter
from .controllable_critter import ControllableCritter
from .base_critter import BaseCritter

@exposed
class Critter(ControllableCritter, BaseCritter, AICritter):
	pass
