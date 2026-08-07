def distance(x1, y1, x2, y2):
    """
    Manhattan distance between two tiles.
    """
    return abs(x1 - x2) + abs(y1 - y2)


def step_toward(fx, fy, tx, ty):
    """
    Return the next movement toward a target tile.
    """

    if tx > fx:
        return "EAST"

    if tx < fx:
        return "WEST"

    if ty > fy:
        return "SOUTH"

    if ty < fy:
        return "NORTH"

    return "PASS"

# ============================================
# State Analyzer
# ============================================

def analyze_state(obs):
    """
    Convert Kaggle observation into a simpler state dictionary.
    """

    player = obs["player"]

    state = {
        "player": player,
        "day": obs["day"],
        "hour": obs["hour"],
        "farm": obs["farms"][player],
        "private": obs["private"],
        "market": obs["market"],
        "town": obs["town"]
    }

    return state

# ============================================
# Farm Scanner (Improved)
# ============================================

def farm_scanner(state):

    tiles = state["farm"]["tiles"]

    harvest = []
    water = []
    empty = []
    weed = []
    animals = []
    locked = []

    for y, row in enumerate(tiles):

        for x, tile in enumerate(row):

            # -----------------------
            # Locked
            # -----------------------
            if tile == "LOCKED":
                locked.append((x, y))
                continue

            # -----------------------
            # Empty
            # -----------------------
            if tile is None:
                empty.append((x, y))
                continue

            kind = tile.get("kind")

            # -----------------------
            # Weed
            # -----------------------
            if kind == "WEED":
                weed.append((x, y))
                continue

            # -----------------------
            # Plant
            # -----------------------
            if kind == "PLANT":

                # Needs watering
                if tile["watered_today"] is False:
                    water.append((x, y))

                # Harvest detection
                #
                # We don't yet know the official rule.
                # Leave harvest empty for now.
                #
                # We'll discover it later.
                continue

            # -----------------------
            # Animal
            # -----------------------
            animals.append((x, y))

    return {
        "harvest": harvest,
        "water": water,
        "empty": empty,
        "weed": weed,
        "animals": animals,
        "locked": locked
    }

# ============================================
# Farmer Action Generator
# ============================================

def generate_farmer_actions(state, scan):

    actions = []

    seeds = state["private"]["seeds"]

    # ------------------------------------
    # Harvest (highest priority)
    # ------------------------------------

    for tile in scan["harvest"]:

        actions.append({
            "type": "HARVEST",
            "target": tile
        })

    # ------------------------------------
    # Water
    # ------------------------------------

    for tile in scan["water"]:

        actions.append({
            "type": "WATER",
            "target": tile
        })

    # ------------------------------------
    # Plant
    # ------------------------------------

    crop = None

    for seed, amount in seeds.items():

        if amount > 0:
            crop = seed
            break

    if crop is not None:

        for tile in scan["empty"]:

            actions.append({
                "type": "PLANT",
                "crop": crop,
                "target": tile
            })

    # ------------------------------------
    # Dig weeds
    # ------------------------------------

    for tile in scan["weed"]:

        actions.append({
            "type": "DIG",
            "target": tile
        })

    # ------------------------------------
    # Nothing to do
    # ------------------------------------

    if len(actions) == 0:

        actions.append({
            "type": "PASS",
            "target": None
        })

    return actions

# ============================================
# Intelligent Action Scorer
# ============================================

HARVEST_SCORE = 100
WATER_SCORE = 80
PLANT_SCORE = 60
DIG_SCORE = 40

DISTANCE_PENALTY = 2


def intelligent_score(state, action):

    if action["type"] == "PASS":
        return 0

    score = 0

    # ----------------------------
    # Base score
    # ----------------------------

    if action["type"] == "HARVEST":
        score += HARVEST_SCORE

    elif action["type"] == "WATER":
        score += WATER_SCORE

    elif action["type"] == "PLANT":
        score += PLANT_SCORE

    elif action["type"] == "DIG":
        score += DIG_SCORE

    # ----------------------------
    # Distance penalty
    # ----------------------------

    farmer_x, farmer_y = state["farm"]["farmer"]

    tx, ty = action["target"]

    distance = abs(farmer_x - tx) + abs(farmer_y - ty)

    score -= distance * DISTANCE_PENALTY

    return score

# ============================================
# Best Action Selector
# ============================================

def choose_best_action(state, actions):

    if len(actions) == 0:
        return {"type": "PASS", "target": None}, 0

    best_action = None
    best_score = float("-inf")

    for action in actions:

        score = intelligent_score(state, action)

        if score > best_score:
            best_score = score
            best_action = action

    return best_action, best_score

# ============================================
# Market Action Generator
# ============================================

def generate_market_actions(state):

    actions = []

    money = state["farm"]["money"]

    seeds = state["private"]["seeds"]

    shed = state["private"]["shed"]

    prices = state["market"]["prices"]

    # ------------------------------------
    # Buy Wheat Seed
    # ------------------------------------

    if seeds["WHEAT"] == 0:

        if money >= prices["WHEAT"]:

            actions.append([
                "BUY_SEED",
                "WHEAT",
                1
            ])

    # ------------------------------------
    # Sell Wheat
    # ------------------------------------

    if shed["WHEAT"] > 0:

        actions.append([
            "SELL",
            "WHEAT",
            shed["WHEAT"]
        ])

    return actions

# ============================================
# Convert Internal Action -> Kaggle Action
# ============================================

def convert_action_to_kaggle(state, action):

    if action["type"] == "PASS":
        return {
            "farmer": ["PASS"],
            "hands": [],
            "market": []
        }

    farmer = tuple(state["farm"]["farmer"])
    target = action["target"]

    # Already on target
    if farmer == target:

        if action["type"] == "PLANT":

            return {
                "farmer": ["PLANT", action["crop"]],
                "hands": [],
                "market": []
            }

        elif action["type"] == "WATER":

            return {
                "farmer": ["WATER"],
                "hands": [],
                "market": []
            }

        elif action["type"] == "HARVEST":

            return {
                "farmer": ["HARVEST"],
                "hands": [],
                "market": []
            }

        elif action["type"] == "DIG":

            return {
                "farmer": ["DIG"],
                "hands": [],
                "market": []
            }

    fx, fy = farmer
    tx, ty = target

    # Move one tile toward target
    if tx > fx:
        move = "EAST"

    elif tx < fx:
        move = "WEST"

    elif ty > fy:
        move = "SOUTH"

    elif ty < fy:
        move = "NORTH"

    else:
        move = "PASS"

    return {
        "farmer": [move],
        "hands": [],
        "market": []
    }

# ============================================
# Final Submission Agent
# ============================================

def submission_agent(obs, config=None):

    # Analyze current game state
    state = analyze_state(obs)

    # Scan farm
    scan = farm_scanner(state)

    # Generate farmer actions
    actions = generate_farmer_actions(state, scan)

    # Choose best action
    best_action, best_score = choose_best_action(state, actions)

    # Market actions
    market_actions = generate_market_actions(state)

    # Convert to Kaggle format
    kaggle_action = convert_action_to_kaggle(
        state,
        best_action
    )

    kaggle_action["market"] = market_actions

    return kaggle_action

# ============================================
# Kaggle Wrapper
# ============================================

def my_agent(obs, config):

    return submission_agent(obs)

def agent(obs, config):
    return submission_agent(obs, config)