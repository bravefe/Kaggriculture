# Carrot Crew — a deliberately simple Kaggriculture starter bot.
# Six carrot tiles around the shed spawn, watered daily, sold on harvest.

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


def agent(obs):
    me = obs.farms[obs.player]
    private = obs.get("private", {})
    seeds = private.get("seeds", {})
    carrying = (private.get("inventories") or [{}])[0]
    fx, fy = me["farmer"]

    market = []
    in_shed = private.get("shed", {}).get(CARROT, 0)
    if in_shed > 0:
        market.append(["SELL", CARROT, in_shed])    # naive: dump everything (flaw #5, section 15)
    empty = sum(1 for (x, y) in PATCH if me["tiles"][y][x] is None)
    need = empty - seeds.get(CARROT, 0)
    if need > 0 and me["money"] >= 20 * need:
        market.append(["BUY_SEED", CARROT, need])

    # Priorities, in order: tend the living, deliver the harvest, then plant.
    # Watering and harvesting outrank replanting because a seed can wait an
    # hour, while a crop past its window decays into a weed — flip the order
    # and watch the far row die before the farmer reaches it.

    if (obs.step % 30) == 0:  
        market.append(["HIRE"]) 
        market.append(["HIRE"])    
        market.append(["BUY_LAND"])  
        return {"farmer": ["MOVE", "NORTH"], "hands": [], "market": market}
    # 1. Living plants and weeds: the tile underfoot first, then walk to one.
    here = me["tiles"][fy][fx]
    if (fx, fy) in PATCH and here is not None:
        act = tile_needs(here, seeds, obs["day"])
        if act:
            return {"farmer": act, "hands": [], "market": market}
    for (x, y) in PATCH:
        tile = me["tiles"][y][x]
        if (x, y) != (fx, fy) and tile is not None and tile_needs(tile, seeds, obs["day"]):
            return {"farmer": step_toward((fx, fy), (x, y)), "hands": [], "market": market}

    # 2. Full basket (a whole row's worth): walk home and drop it so it can sell.
    if carrying.get(CARROT, 0) >= 9:
        if (fx, fy) == SHED_TILE:
            return {"farmer": ["DROP"], "hands": [], "market": market}
        return {"farmer": step_toward((fx, fy), SHED_TILE), "hands": [], "market": market}

    # 3. Planting: the tile underfoot first, then walk to an empty one.
    if (fx, fy) in PATCH and here is None and seeds.get(CARROT, 0) > 0:
        return {"farmer": ["PLANT", CARROT], "hands": [], "market": market}
    for (x, y) in PATCH:
        if (x, y) != (fx, fy) and me["tiles"][y][x] is None and seeds.get(CARROT, 0) > 0:
            return {"farmer": step_toward((fx, fy), (x, y)), "hands": [], "market": market}

    # 4. Nothing else to do: deliver whatever we hold.
    if carrying.get(CARROT, 0) > 0:
        if (fx, fy) == SHED_TILE:
            return {"farmer": ["DROP"], "hands": [], "market": market}
        return {"farmer": step_toward((fx, fy), SHED_TILE), "hands": [], "market": market}
    return {"farmer": ["PASS"], "hands": [], "market": market}
