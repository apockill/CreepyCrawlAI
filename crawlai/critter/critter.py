from godot import exposed, export

from crawlai.critter.mixins.ai_critter import AICritterMixin
from crawlai.critter.mixins.controllable_critter import ControllableMixin
from crawlai.critter.mixins.observative_critter import ObservativeMixin
from crawlai.critter.base_critter import BaseCritter


@exposed
class Critter(ObservativeMixin,
			  ControllableMixin,
			  AICritterMixin,
			  BaseCritter):


