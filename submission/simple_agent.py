def agent(obs):
    me = obs.farms[obs.player]
    private = obs.get("private", {})
    seeds = private.get("seeds", {})
    carrying = (private.get("inventories") or [{}])[0]
    fx, fy = me["farmer"]

    market = []
    hand = []

    if (obs.step == 1):
        return {"farmer": ["NORTH"], "hands": hand, "market": market}
    if (obs.step == 2):
        market.append(["BUY_ANIMAL", "GOOSE", 1])
        return {"farmer": ["BUILD_COOP"], "hands": hand, "market": market}
    if (obs.step == 3):
        return {"farmer": ["SOUTH"], "hands": hand, "market": market}
    if (obs.step == 4):
        return {"farmer": ["PICKUP", "GOOSE"], "hands": hand, "market": market}
    if (obs.step == 5):
        return {"farmer": ["NORTH"], "hands": hand, "market": market}
    if (obs.step == 6):
        return {"farmer": ["PLACE", "GOOSE"], "hands": hand, "market": market}
    if (obs.step == 7):
        return {"farmer": ["NORTH"], "hands": hand, "market": market}
    if (obs.step == 8):
        return {"farmer": ["BUILD_PASTURE"], "hands": hand, "market": market}
    if (obs.step == 9):
        return {"farmer": ["WEST"], "hands": hand, "market": market}