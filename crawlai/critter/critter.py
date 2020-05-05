from godot import exposed, export

from crawlai.critter.mixins.ai_critter import AICritterMixin
from crawlai.critter.mixins.controllable_mixin import ControllableMixin
from crawlai.critter.base_critter import BaseCritter


@exposed
class Critter(ControllableMixin,
			  AICritterMixin,
			  BaseCritter):
	pass
