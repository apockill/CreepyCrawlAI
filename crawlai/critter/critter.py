from godot import exposed

from crawlai.critter.mixins.ai_critter import AICritter
from crawlai.critter.mixins.controllable_critter import ControllableCritter
from .base_critter import BaseCritter


@exposed
class Critter(ControllableCritter, BaseCritter, AICritter):
	pass
