import unittest

from ray import tune
from ray.rllib.examples.env.stateless_cartpole import StatelessCartPole
from ray.rllib.models.catalog import ModelCatalog
from ray.rllib.models.tf.attention_net import GTrXLNet


class TestAttentionNetLearning(unittest.TestCase):

    config = {
        "env": StatelessCartPole,
        "gamma": 0.99,
        "num_envs_per_worker": 20,
        # "framework": "tf",
    }

    stop = {
        "episode_reward_mean": 180.0,
        "timesteps_total": 5000000,
    }

    def test_ppo_attention_net_learning(self):
        ModelCatalog.register_custom_model("attention_net", GTrXLNet)
        config = dict(
            self.config, **{
                "num_workers": 0,
                "entropy_coeff": 0.001,
                "vf_loss_coeff": 1e-5,
                "num_sgd_iter": 5,
                "model": {
                    "custom_model": "attention_net",
                    "max_seq_len": 10,
                    "custom_model_config": {
                        "num_transformer_units": 1,
                        "attn_dim": 32,
                        "num_heads": 1,
                        "memory_tau": 5,
                        "head_dim": 32,
                        "ff_hidden_dim": 32,
                    },
                },
            })
        tune.run("PPO", config=config, stop=self.stop, verbose=1)

    def test_impala_attention_net_learning(self):
        ModelCatalog.register_custom_model("attention_net", GTrXLNet)
        config = dict(
            self.config, **{
                "num_workers": 4,
                "num_gpus": 0,
                "entropy_coeff": 0.01,
                "vf_loss_coeff": 0.001,
                "lr": 0.0008,
                "model": {
                    "custom_model": "attention_net",
                    "max_seq_len": 65,
                    "custom_model_config": {
                        "num_transformer_units": 1,
                        "attn_dim": 64,
                        "num_heads": 1,
                        "memory_tau": 10,
                        "head_dim": 32,
                        "ff_hidden_dim": 32,
                    },
                },
            })
        tune.run("IMPALA", config=config, stop=self.stop, verbose=1)


if __name__ == "__main__":
    import pytest
    import sys
    sys.exit(pytest.main(["-v", __file__]))
