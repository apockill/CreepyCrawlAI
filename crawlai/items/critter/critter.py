from crawlai.items.critter.mixins.ai_mixin import AICritterMixin
from crawlai.items.critter.mixins.controllable_mixin import ControllableMixin
from crawlai.items.critter.base_critter import BaseCritter


class Critter(ControllableMixin,
			  AICritterMixin,
			  BaseCritter):
	pass
