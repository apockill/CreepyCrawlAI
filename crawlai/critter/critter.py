from crawlai.critter.mixins.ai_mixin import AICritterMixin
from crawlai.critter.mixins.controllable_mixin import ControllableMixin
from crawlai.critter.base_critter import BaseCritter


class Critter(ControllableMixin,
			  AICritterMixin,
			  BaseCritter):
	pass
