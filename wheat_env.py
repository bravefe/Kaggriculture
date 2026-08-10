import gymnasium as gym
import numpy as np
from kaggle_environments import make

class KaggricultureEnv(gym.Env):
    def __init__(self):
        self.env = make("kaggriculture", debug=True)

        self.action_space = gym.spaces.Discrete(8)
        self.observation_space = gym.spaces.Box(
            low=-np.inf,
            high=np.inf,
            shape=(OBS_SIZE,),
            dtype=np.float32,
        )

    def reset(self, seed=None, options=None):
        self.env.reset()

        obs = self.env.state[0].observation
        return preprocess(obs), {}

    def step(self, action_id):
        action = decode_action(action_id)

        # opponent does nothing
        actions = [action, {"farmer": ["PASS"], "hands": [], "market": []}]

        self.env.step(actions)

        obs = self.env.state[0].observation

        reward = wheat_reward(obs)

        done = self.env.done

        return preprocess(obs), reward, done, False, {}