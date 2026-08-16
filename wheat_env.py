import gymnasium as gym
import numpy as np
from kaggle_environments import make
from kaggle_environments.envs.kaggriculture.kaggriculture import CROPS, ANIMALS

KIND_TO_IDX = {
    "NONE": 0,
    "WEED": 1,
    "PLANT": 2,
    "COOP": 3,
    "PASTURE": 4,
    "LOCKED": 5,
}

CROP_TO_IDX = {crop: idx for idx, crop in enumerate(CROPS.keys())}
ANIMAL_TO_IDX = {animal: idx for idx, animal in enumerate(ANIMALS.keys())}
FEATURE_DIM = len(KIND_TO_IDX) + len(CROP_TO_IDX) + len(ANIMAL_TO_IDX) + 3

ACTION_TABLE = [
    {"farmer": ["PASS"], "hands": [], "market": []},
    {"farmer": ["NORTH"], "hands": [], "market": []},
    {"farmer": ["SOUTH"], "hands": [], "market": []},
    {"farmer": ["EAST"], "hands": [], "market": []},
    {"farmer": ["WEST"], "hands": [], "market": []},
    {"farmer": ["PLANT", "WHEAT"], "hands": [], "market": []},
    {"farmer": ["WATER"], "hands": [], "market": []},
    {"farmer": ["HARVEST"], "hands": [], "market": []},
]


def tile_to_vector(tile):
    vec = np.zeros(FEATURE_DIM, dtype=np.float32)

    if tile is None:
        vec[KIND_TO_IDX["NONE"]] = 1.0
        return vec

    if tile == "LOCKED":
        vec[KIND_TO_IDX["LOCKED"]] = 1.0
        return vec

    if not isinstance(tile, dict):
        return vec

    kind = tile.get("kind")
    if kind in KIND_TO_IDX:
        vec[KIND_TO_IDX[kind]] = 1.0

    crop_offset = len(KIND_TO_IDX)
    animal_offset = crop_offset + len(CROP_TO_IDX)
    numeric_offset = animal_offset + len(ANIMAL_TO_IDX)

    if kind == "PLANT":
        crop = tile.get("crop", "")
        crop_idx = CROP_TO_IDX.get(crop)
        if crop_idx is not None:
            vec[crop_offset + crop_idx] = 1.0

        vec[numeric_offset + 0] = float(tile.get("yield_units", 0))
        vec[numeric_offset + 1] = 1.0 if tile.get("watered_today", False) else 0.0
        vec[numeric_offset + 2] = float(tile.get("fertilized_until_day", -1))

    elif kind in {"COOP", "PASTURE"}:
        animal = tile.get("animal", "")
        animal_idx = ANIMAL_TO_IDX.get(animal)
        if animal_idx is not None:
            vec[animal_offset + animal_idx] = 1.0

        vec[numeric_offset + 0] = float(tile.get("yield_units", 0))
        vec[numeric_offset + 1] = 1.0 if tile.get("fed_today", False) else 0.0
        vec[numeric_offset + 2] = float(tile.get("pending_care_bonus", 0))

    return vec


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
                    if isinstance(item, dict) and "tiles" in item:
                        return item["tiles"]

    return []


def preprocess(obs, player_index=0):
    tiles = extract_tiles(obs, player_index)
    if not tiles:
        return np.zeros((1, 1, FEATURE_DIM), dtype=np.float32)

    rows = len(tiles)
    cols = len(tiles[0]) if rows > 0 else 0
    board = np.zeros((rows, cols, FEATURE_DIM), dtype=np.float32)

    for y, row in enumerate(tiles):
        for x, tile in enumerate(row):
            board[y, x] = tile_to_vector(tile)

    return board


def wheat_reward(obs):
    try:
        if "farms" in obs and obs["farms"]:
            farm = obs["farms"][0]
            private = farm.get("private", {})
            shed = private.get("shed", {}) if isinstance(private, dict) else {}
            return float(shed.get("WHEAT", 0))

        if "private" in obs:
            shed = obs["private"].get("shed", {})
            return float(shed.get("WHEAT", 0))
    except Exception:
        pass
    return 0.0


def decode_action(action_id):
    if action_id < 0 or action_id >= len(ACTION_TABLE):
        action_id = 0
    return ACTION_TABLE[action_id]


class KaggricultureEnv(gym.Env):
    metadata = {"render_modes": []}

    def __init__(self):
        self.env = make("kaggriculture", debug=False)
        self.action_space = gym.spaces.Discrete(len(ACTION_TABLE))
        self.observation_space = gym.spaces.Box(
            low=-np.inf,
            high=np.inf,
            shape=(1, 1, FEATURE_DIM),
            dtype=np.float32,
        )
        self.player_index = 0

    def _get_current_obs(self):
        if hasattr(self.env, "state") and self.env.state:
            return self.env.state[0].observation
        return getattr(self.env, "observation", {})

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)

        if hasattr(self.env, "reset"):
            self.env.reset()

        obs = self._get_current_obs()
        obs_array = preprocess(obs, self.player_index)
        self.observation_space = gym.spaces.Box(
            low=-np.inf,
            high=np.inf,
            shape=obs_array.shape,
            dtype=np.float32,
        )
        return obs_array, {}

    def step(self, action_id):
        action = decode_action(action_id)

        opponent_action = {"farmer": ["PASS"], "hands": [], "market": []}
        self.env.step([action, opponent_action])

        obs = self._get_current_obs()
        obs_array = preprocess(obs, self.player_index)
        reward = wheat_reward(obs)
        done = bool(getattr(self.env, "done", False))

        self.observation_space = gym.spaces.Box(
            low=-np.inf,
            high=np.inf,
            shape=obs_array.shape,
            dtype=np.float32,
        )

        return obs_array, reward, done, False, {}

    def close(self):
        self.env.close()
        super().close()