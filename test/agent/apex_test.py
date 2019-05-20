import unittest

from agent.apex import Trainer
from agent.apex import Agent
from env.trade import Trade


class MyTestCase(unittest.TestCase):

    def __init__(self, s):
        super(MyTestCase, self).__init__(s)
        self.agent:Agent = None
        self.env   = None
        self.trainer:Trainer = None

    def setUp(self) -> None:
        self.agent = Agent()
        self.env = Trade()

        self.trainer = Trainer(self.env, self.agent)

        self.trainer.one_episode()

    def test_calc_q(self):
        self.trainer.calc_multi_step_q_value(0, 1)
        self.trainer.calc_multi_step_q_value(0, 2)
        self.trainer.calc_multi_step_q_value(1, 1)




if __name__ == '__main__':
    unittest.main()
