from crawlai.items.critter.base_critter import BaseCritter
from crawlai.items.critter.mixins.ai_mixin import AICritterMixin
from crawlai.items.critter.mixins.controllable_mixin import ControllableMixin


class Critter(ControllableMixin, AICritterMixin, BaseCritter):
    pass
