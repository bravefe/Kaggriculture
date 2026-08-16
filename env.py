import gymnasium as gym
import numpy as np
from kaggle_environments import make

from data_format import (
    FEATURE_DIM,
    ACTION_TABLE,
    preprocess,
    wheat_reward,
    decode_action,
)


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

        self.action_space = gym.spaces.Discrete(
            len(ACTION_TABLE)
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