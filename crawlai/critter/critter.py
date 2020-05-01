from godot import exposed

from crawlai.critter.mixins.ai_critter import AICritter
from crawlai.critter.mixins.controllable_critter import ControllableCritter
from crawlai.critter.base_critter import BaseCritter


@exposed
class Critter(AICritter, ControllableCritter, BaseCritter):
	pass
