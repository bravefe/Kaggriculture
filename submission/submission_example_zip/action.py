import json

with open("config.json", "r") as f:
    config = json.load(f)

CARROT = config["CARROT"]
MAX_YIELD_DAY = config["MAX_YIELD_DAY"]
PATCH = [tuple(pos) for pos in config["PATCH"]]
SHED_TILE = tuple(config["SHED_TILE"])       


def step_toward(pos, target):
    (x, y), (tx, ty) = pos, target
    if x < tx: return ["EAST"]
    if x > tx: return ["WEST"]
    if y < ty: return ["SOUTH"]
    if y > ty: return ["NORTH"]
    return ["PASS"]


def tile_needs(tile, seeds, day):
    # What this patch tile wants right now, or None.
    if isinstance(tile, dict) and tile.get("kind") == "WEED":
        return ["DIG"]
    if tile is None:
        return ["PLANT", CARROT] if seeds.get(CARROT, 0) > 0 else None
    if isinstance(tile, dict) and tile.get("kind") == "PLANT":
        if not tile.get("watered_today"):
            return ["WATER"]                        # water first — today's bonus lands today
        if day - tile["planted_day"] >= MAX_YIELD_DAY and tile.get("yield_units", 0) > 0:
            return ["HARVEST"]
    return None