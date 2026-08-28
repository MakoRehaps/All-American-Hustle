# Loaded by every All-American Hustle stage.
# Paintown's embedded Python engine imports data/scripts/paintown.py as `paintown`.
import paintown


class AllAmericanHustleEngine(paintown.Engine):
    def __init__(self):
        paintown.Engine.__init__(self)

    def createWorld(self, world):
        # Paintown requires the base implementation to retain the engine world handle.
        paintown.Engine.createWorld(self, world)


paintown.register(AllAmericanHustleEngine())
