import action

def agent(obs):
    me = obs.farms[obs.player]
    private = obs.get("private", {})
    seeds = private.get("seeds", {})
    carrying = (private.get("inventories") or [{}])[0]
    fx, fy = me["farmer"]

    market = []
    in_shed = private.get("shed", {}).get(action.CARROT, 0)
    if in_shed > 0:
        market.append(["SELL", action.CARROT, in_shed])    # naive: dump everything (flaw #5, section 15)
    empty = sum(1 for (x, y) in action.PATCH if me["tiles"][y][x] is None)
    need = empty - seeds.get(action.CARROT, 0)
    if need > 0 and me["money"] >= 20 * need:
        market.append(["BUY_SEED", action.CARROT, need])

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
    if (fx, fy) in action.PATCH and here is not None:
        act = action.tile_needs(here, seeds, obs["day"])
        if act:
            return {"farmer": act, "hands": [], "market": market}
    for (x, y) in action.PATCH:
        tile = me["tiles"][y][x]
        if (x, y) != (fx, fy) and tile is not None and action.tile_needs(tile, seeds, obs["day"]):
            return {"farmer": action.step_toward((fx, fy), (x, y)), "hands": [], "market": market}

    # 2. Full basket (a whole row's worth): walk home and drop it so it can sell.
    if carrying.get(action.CARROT, 0) >= 9:
        if (fx, fy) == action.SHED_TILE:
            return {"farmer": ["DROP"], "hands": [], "market": market}
        return {"farmer": action.step_toward((fx, fy), action.SHED_TILE), "hands": [], "market": market}

    # 3. Planting: the tile underfoot first, then walk to an empty one.
    if (fx, fy) in action.PATCH and here is None and seeds.get(action.CARROT, 0) > 0:
        return {"farmer": ["PLANT", action.CARROT], "hands": [], "market": market}
    for (x, y) in action.PATCH:
        if (x, y) != (fx, fy) and me["tiles"][y][x] is None and seeds.get(action.CARROT, 0) > 0:
            return {"farmer": action.step_toward((fx, fy), (x, y)), "hands": [], "market": market}

    # 4. Nothing else to do: deliver whatever we hold.
    if carrying.get(action.CARROT, 0) > 0:
        if (fx, fy) == action.SHED_TILE:
            return {"farmer": ["DROP"], "hands": [], "market": market}
        return {"farmer": action.step_toward((fx, fy), action.SHED_TILE), "hands": [], "market": market}
    return {"farmer": ["PASS"], "hands": [], "market": market}
