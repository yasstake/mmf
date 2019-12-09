import gym

from stable_baselines.common.policies import MlpPolicy
from stable_baselines.common.vec_env import DummyVecEnv
from stable_baselines.common.vec_env import SubprocVecEnv
from stable_baselines import PPO2

from env.rl import TradeEnv

def make_env(rank, seed=0):
    """
    Utility function for multiprocessed env.

    :param env_id: (str) the environment ID
    :param num_env: (int) the number of environments you wish to have in subprocesses
    :param seed: (int) the inital seed for RNG
    :param rank: (int) index of the subprocess
    """
    def _init():
        e = TradeEnv()
        e.seed(seed + rank)
        return e

    return _init


env = TradeEnv()
env = DummyVecEnv([lambda: env])  # The algorithms require a vectorized environment to run


#num_cpu = 1
#env = SubprocVecEnv([make_env(i) for i in range(num_cpu)])

model = PPO2(MlpPolicy, env, verbose=1)
model.learn(total_timesteps=10000)

obs = env.reset()
for i in range(1000):
    action, _states = model.predict(obs)
    obs, rewards, done, info = env.step(action)
    env.render()

