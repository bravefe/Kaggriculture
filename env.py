import gymnasium as gym
import numpy as np
from kaggle_environments import make

from data import (
    FEATURE_DIM,
    preprocess,
)

# ============================================================
# ACTIONS
# ============================================================

ACTION_TABLE = [
    {"farmer": ["PASS"], "hands": [], "market": []},
    {"farmer": ["NORTH"], "hands": [], "market": []},
    {"farmer": ["SOUTH"], "hands": [], "market": []},
    {"farmer": ["EAST"], "hands": [], "market": []},
    {"farmer": ["WEST"], "hands": [], "market": []},
    {"farmer": ["PLANT", "WHEAT"], "hands": [], "market": []},
    {"farmer": ["WATER"], "hands": [], "market": []},
    {"farmer": ["HARVEST"], "hands": [], "market": []},
    {"farmer": ["DROP"], "hands": [], "market": []},
    {"farmer": ["PICKUP", "WHEAT", 1], "hands": [], "market": []},
]

MAX_WHEAT_TRANSACTION = 10

ACTION_DESCRIPTION = (
    'Per-turn action of the form {"farmer": [op, ...args], '
    '"hands": [[op, ...args], ...], "market": [[op, ...args], ...]}. '
    'Farmer/hand ops: NORTH, SOUTH, EAST, WEST, PASS, PICKUP <item> [n], '
    'PLANT <crop>, WATER, HARVEST, DROP, FERTILIZE, BUILD_COOP, '
    'BUILD_PASTURE, DIG, PLACE <item> [n], FEED, COLLECT_FERTILIZER, CARE. '
    'Market ops: BUY_SEED <crop> <n>, BUY_PRODUCT <item> <n>, '
    'BUY_ANIMAL <animal> <n>, SELL <item> <n>, HIRE, BUY_LAND.'
)

# ============================================================
# ACTION DECODER
# ============================================================

def decode_action(action):

    action_values = np.asarray(action).reshape(-1)
    action_id = int(action_values[0]) if action_values.size else 0
    buy_wheat = int(action_values[1]) if action_values.size > 1 else 0
    sell_wheat = int(action_values[2]) if action_values.size > 2 else 0

    if (
        action_id < 0
        or action_id >= len(ACTION_TABLE)
    ):
        action_id = 0

    market = []
    if buy_wheat > 0:
        market.append(["BUY_SEED", "WHEAT", buy_wheat])
    if sell_wheat > 0:
        market.append(["SELL", "WHEAT", sell_wheat])

    farmer_action = ACTION_TABLE[action_id]
    return {
        "farmer": farmer_action["farmer"],
        "hands": [],
        "market": market,
    }

# ============================================================
# REWARD
# ============================================================

def _private_value(obs, key, default):

    private = obs.get("private", {})
    if not isinstance(private, dict):
        return default

    return private.get(key, default)


def _wheat_inventory(obs):

    inventories = _private_value(obs, "inventories", [])
    if not inventories or not isinstance(inventories[0], dict):
        return 0.0

    return float(inventories[0].get("WHEAT", 0))


def _wheat_shed(obs):

    shed = _private_value(obs, "shed", {})
    if not isinstance(shed, dict):
        return 0.0

    return float(shed.get("WHEAT", 0))


def _current_tile(obs, player_index):

    farms = obs.get("farms", [])
    if not farms or player_index >= len(farms):
        return None

    farm = farms[player_index]
    position = farm.get("farmer", [0, 0])
    tiles = farm.get("tiles", [])
    x, y = position

    if y < 0 or y >= len(tiles) or x < 0 or x >= len(tiles[y]):
        return None

    return tiles[y][x]


def wheat_reward(previous_obs, obs, action, player_index):

    farmer_action = action.get("farmer", [])
    reward = 0.0

    if farmer_action == ["PLANT", "WHEAT"]:
        before_tile = _current_tile(previous_obs, player_index)
        after_tile = _current_tile(obs, player_index)
        if (
            before_tile is None
            and isinstance(after_tile, dict)
            and after_tile.get("kind") == "PLANT"
            and after_tile.get("crop") == "WHEAT"
        ):
            reward += 1.0

    if farmer_action == ["WATER"]:
        before_tile = _current_tile(previous_obs, player_index)
        after_tile = _current_tile(obs, player_index)
        if (
            isinstance(before_tile, dict)
            and before_tile.get("kind") == "PLANT"
            and before_tile.get("crop") == "WHEAT"
            and not before_tile.get("watered_today", False)
            and isinstance(after_tile, dict)
            and after_tile.get("watered_today", False)
        ):
            reward += 1.0

    inventory_change = _wheat_inventory(obs) - _wheat_inventory(previous_obs)
    if farmer_action in (
        ["HARVEST"],
        ["PICKUP", "WHEAT", 1],
    ):
        reward += max(0.0, inventory_change)

    shed_change = _wheat_shed(previous_obs) - _wheat_shed(obs)
    if any(
        order[:2] == ["SELL", "WHEAT"]
        for order in action.get("market", [])
    ):
        reward += max(0.0, shed_change)

    return reward

    try:

        if "farms" in obs and obs["farms"]:

            farm = obs["farms"][0]

            private = farm.get(
                "private",
                {}
            )

            shed = (
                private.get("shed", {})
                if isinstance(private, dict)
                else {}
            )

            return float(
                shed.get("WHEAT", 0)
            )

        if "private" in obs:

            shed = obs["private"].get(
                "shed",
                {}
            )

            return float(
                shed.get("WHEAT", 0)
            )

    except Exception:
        pass

    return 0.0


# ============================================================
# GYM ENVIRONMENT
# ============================================================

class KaggricultureEnv(gym.Env):

    metadata = {
        "render_modes": []
    }

    def __init__(self):

        self.env = make(
            "kaggriculture",
            debug=False
        )
        self.env.specification.action.description = ACTION_DESCRIPTION

        self.action_space = gym.spaces.MultiDiscrete(
            [
                len(ACTION_TABLE),
                MAX_WHEAT_TRANSACTION + 1,
                MAX_WHEAT_TRANSACTION + 1,
            ]
        )

        self.observation_space = gym.spaces.Box(
            low=-np.inf,
            high=np.inf,
            shape=(1, 1, FEATURE_DIM),
            dtype=np.float32
        )

        self.player_index = 0

    # ========================================================
    # GET CURRENT OBSERVATION
    # ========================================================

    def _get_current_obs(self):

        if (
            hasattr(self.env, "state")
            and self.env.state
        ):
            return self.env.state[
                0
            ].observation

        return getattr(
            self.env,
            "observation",
            {}
        )

    # ========================================================
    # RESET
    # ========================================================

    def reset(
        self,
        seed=None,
        options=None
    ):

        super().reset(seed=seed)

        self.env.reset()

        obs = self._get_current_obs()

        obs_array = preprocess(
            obs,
            self.player_index
        )

        self.observation_space = gym.spaces.Box(
            low=-np.inf,
            high=np.inf,
            shape=obs_array.shape,
            dtype=np.float32
        )

        return obs_array, {}

    # ========================================================
    # STEP
    # ========================================================

    def step(self, action_id):

        previous_obs = self._get_current_obs()
        action = decode_action(
            action_id
        )

        opponent_action = {
            "farmer": ["PASS"],
            "hands": [],
            "market": []
        }

        self.env.step([
            action,
            opponent_action
        ])

        obs = self._get_current_obs()

        obs_array = preprocess(
            obs,
            self.player_index
        )

        reward = wheat_reward(
            previous_obs,
            obs,
            action,
            self.player_index,
        )

        done = bool(
            getattr(
                self.env,
                "done",
                False
            )
        )

        self.observation_space = gym.spaces.Box(
            low=-np.inf,
            high=np.inf,
            shape=obs_array.shape,
            dtype=np.float32
        )

        return (
            obs_array,
            reward,
            done,
            False,
            {}
        )

    # ========================================================
    # CLOSE
    # ========================================================

    def close(self):

        self.env.close()

        super().close()