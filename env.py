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
]

MAX_WHEAT_TRANSACTION = 10

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

def wheat_reward(obs):

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

        reward = wheat_reward(obs)

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