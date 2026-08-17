import numpy as np


# ============================================================
# TILE KIND
# ============================================================

KIND_TO_IDX = {
    "NONE": 0,
    "WEED": 1,
    "PLANT": 2,
    "COOP": 3,
    "PASTURE": 4,
    "LOCKED": 5,
}


# ============================================================
# CROP IDs
# ============================================================

CROP_TO_IDX = {
    "MELON": 0,
    "WHEAT": 1,
    "STRAWBERRY": 2,
    "CARROT": 3,
    "TOMATO": 4,
}


# ============================================================
# ANIMAL IDs
# ============================================================

ANIMAL_TO_IDX = {
    "GOOSE": 0,
    "COW": 1,
    "SHEEP": 2,
}


# Every tile has:
#
# [kind, crop/animal, yield_units, watered/fed, fertilizer/bonus]
#


FEATURE_DIM = 5


# ============================================================
# TILE ENCODING
# ============================================================

def tile_to_vector(tile):

    # Default:
    # [NONE, no crop/animal, 0 yield, 0 watered/fed, 0 bonus]
    vec = np.zeros(FEATURE_DIM, dtype=np.float32)

    # --------------------------------------------------------
    # NONE
    # --------------------------------------------------------

    if tile is None:
        vec[0] = KIND_TO_IDX["NONE"]
        return vec

    # --------------------------------------------------------
    # LOCKED
    # --------------------------------------------------------

    if tile == "LOCKED":
        vec[0] = KIND_TO_IDX["LOCKED"]
        return vec

    # --------------------------------------------------------
    # Invalid tile
    # --------------------------------------------------------

    if not isinstance(tile, dict):
        return vec

    kind = tile.get("kind")

    # --------------------------------------------------------
    # WEED
    # --------------------------------------------------------

    if kind == "WEED":
        return np.array([
            KIND_TO_IDX["WEED"],
            0,
            0,
            0,
            0
        ], dtype=np.float32)

    # --------------------------------------------------------
    # PLANT
    # --------------------------------------------------------

    if kind == "PLANT":

        crop = tile.get("crop", "")
        crop_id = CROP_TO_IDX.get(crop, 0)

        yield_units = float(
            tile.get("yield_units", 0)
        )

        watered_today = float(
            tile.get("watered_today", False)
        )

        fertilized_until_day = float(
            tile.get("fertilized_until_day", -1)
        )

        return np.array([
            KIND_TO_IDX["PLANT"],
            crop_id,
            yield_units,
            watered_today,
            fertilized_until_day
        ], dtype=np.float32)

    # --------------------------------------------------------
    # COOP
    # --------------------------------------------------------

    if kind == "COOP":

        animal = tile.get("animal", "")
        animal_id = ANIMAL_TO_IDX.get(animal, 0)

        yield_units = float(
            tile.get("yield_units", 0)
        )

        fed_today = float(
            tile.get("fed_today", False)
        )

        pending_care_bonus = float(
            tile.get("pending_care_bonus", 0)
        )

        return np.array([
            KIND_TO_IDX["COOP"],
            animal_id,
            yield_units,
            fed_today,
            pending_care_bonus
        ], dtype=np.float32)

    # --------------------------------------------------------
    # PASTURE
    # Same structure as COOP
    # --------------------------------------------------------

    if kind == "PASTURE":

        animal = tile.get("animal", "")
        animal_id = ANIMAL_TO_IDX.get(animal, 0)

        yield_units = float(
            tile.get("yield_units", 0)
        )

        fed_today = float(
            tile.get("fed_today", False)
        )

        pending_care_bonus = float(
            tile.get("pending_care_bonus", 0)
        )

        return np.array([
            KIND_TO_IDX["PASTURE"],
            animal_id,
            yield_units,
            fed_today,
            pending_care_bonus
        ], dtype=np.float32)

    return vec


# ============================================================
# EXTRACT TILES
# ============================================================

def extract_tiles(obs, player_index=0):

    if isinstance(obs, dict):

        if "farms" in obs and obs["farms"]:
            farm = obs["farms"][player_index]
            return farm.get("tiles", [])

        if "players" in obs and obs["players"]:

            player_obs = obs["players"][player_index]

            if isinstance(player_obs, dict):
                return player_obs.get("tiles", [])

            if isinstance(player_obs, (list, tuple)):

                for item in player_obs:

                    if (
                        isinstance(item, dict)
                        and "tiles" in item
                    ):
                        return item["tiles"]

            

    return []

def extract_context(obs, player_index=0):
    farms = obs.get("farms", [])
    farm = farms[player_index]
    money = float(farm.get("money", 0.0)) 
    farmer = farm.get("farmer", [0, 0])
    x, y = farmer
    farmer_x = x / 10.0
    farmer_y = y / 10.0

    opponent_index = 1 - player_index
    farm_op = farms[opponent_index]
    money_op = float(farm_op.get("money", 0.0)) 
    farmer_op = farm_op.get("farmer", [0, 0])
    x, y = farmer_op
    farmer_op_x = x / 10.0
    farmer_op_y = y / 10.0

    overage = float(obs.get("remainingOverageTime", 0))
    step = float(obs.get("step", 0)) / 719

    context = np.array(
        [money, farmer_x, farmer_y, money_op, farmer_op_x, farmer_op_y, step, overage],
        dtype=np.float32
    )

    return context

# ============================================================
# PREPROCESS
# ============================================================

def preprocess(obs, player_index=0):

    tiles = extract_tiles(
        obs,
        player_index
    )

    context = extract_context(
        obs,
        player_index
    )

    if not tiles:
        board = np.zeros(
            (1, 1, FEATURE_DIM),
            dtype=np.float32
        )
    else:
        rows = len(tiles)
        cols = len(tiles[0])

        board = np.zeros(
            (rows, cols, FEATURE_DIM),
            dtype=np.float32
        )

        for y, row in enumerate(tiles):
            for x, tile in enumerate(row):
                board[y, x] = tile_to_vector(tile)

    board_flat = board.flatten()

    output = np.concatenate([
        board_flat,
        context
    ])

    return output

# def preprocess(obs, player_index=0):

#     tiles = extract_tiles(
#         obs,
#         player_index
#     )

#     if not tiles:
#         return np.zeros(
#             (1, 1, FEATURE_DIM),
#             dtype=np.float32
#         )

#     rows = len(tiles)
#     cols = len(tiles[0])

#     board = np.zeros(
#         (rows, cols, FEATURE_DIM),
#         dtype=np.float32
#     )

#     for y, row in enumerate(tiles):

#         for x, tile in enumerate(row):

#             board[y, x] = tile_to_vector(tile)

#     return board


# def preprocess(obs, player_index=0):

#     tiles = extract_tiles(
#         obs,
#         player_index
#     )

#     context = extract_context(
#         obs,
#         player_index
#     )

#     if not tiles:
#         board = np.zeros(
#             (1, 1, FEATURE_DIM),
#             dtype=np.float32
#         )
#         return board, context

#     rows = len(tiles)
#     cols = len(tiles[0])

#     board = np.zeros(
#         (rows, cols, FEATURE_DIM),
#         dtype=np.float32
#     )

#     for y, row in enumerate(tiles):
#         for x, tile in enumerate(row):
#             board[y, x] = tile_to_vector(tile)

#     return board, context

