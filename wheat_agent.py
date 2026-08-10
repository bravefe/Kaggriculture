# I Want to create an agent that maximize wheat

def agent(obs):
    farms = obs.get("farms", [])
    player = obs.get("player", 0)
    private = obs.get("private", {}) or {}
    if not farms or player >= len(farms):
        return {"farmer": ["PASS"], "hands": [], "market": []}

    farm = farms[player]
    board_size = len(farm["tiles"])
    fx, fy = farm["farmer"]
    tile = farm["tiles"][fy][fx]
    day = obs.get("day", 0)

    seeds = private.get("seeds", {})
    shed = private.get("shed", {})
    market_prices = (obs.get("market", {}) or {}).get("prices", {})
    wheat_price = market_prices.get("WHEAT", 0)

    farmer = []
    hand = []
    market = []
    
    # action the the agent can make = ["NORTH"], ["SOUTH"], ["EAST"], ["WEST"], ["PLANT", "WHEAT"], ["HARVEST"], ["WATER"]
    # reward = live time wheat gain 
    
    wheat_in_shed = shed.get("WHEAT", 0)

    return {"farmer": farmer, "hands": hand, "market": market}