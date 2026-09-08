def agent(obs):
    me = obs.farms[obs.player]
    private = obs.get("private", {})
    fx, fy = me["farmer"]

    market = []
    hand = []

    if obs.step == 1:
        market.append(["BUY_SEED", "MELON", 1])
        return {"farmer": ["PASS"], "hands": hand, "market": market}

    if obs.step == 2:
        return {"farmer": ["PLANT", "MELON"], "hands": hand, "market": market}

    tile = me["tiles"][fy][fx]
    if isinstance(tile, dict) and tile.get("kind") == "PLANT":
        planted_day = tile.get("planted_day", obs.day)
        if obs.day - planted_day >= 10 and tile.get("yield_units", 0) > 0:
            return {"farmer": ["HARVEST"], "hands": hand, "market": market}
        return {"farmer": ["WATER"], "hands": hand, "market": market}

    carrying = (private.get("inventories") or [{}])[0]
    if carrying.get("MELON", 0) > 0:
        return {"farmer": ["DROP"], "hands": hand, "market": market}

    return {"farmer": ["PASS"], "hands": hand, "market": market}