CARROT = "CARROT"
MAX_YIELD_DAY = 3                                   # CROPS["CARROT"]["max_yield_day"]
PATCH = [(4, 4), (3, 4), (2, 4), (2, 3), (3, 3), (4, 3)]
SHED_TILE = (4, 4)                                  # shed-adjacent: DROP works here


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