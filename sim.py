import game
import sys

# class Agent:
    # def __init__(self):
        # pass

    # def Action(self, state):
        # return 

class Simulate:
    def __init__(self, round_num):
        self.agents = ['HungWei', 'Complete']
        self.sim_game = game.Game(self.agents, sim=True)
        self.tr = self.sim_game.temp_round
        self.round_num = round_num

    def simulate(self):
        counting = 0
        while(self.sim_game.round_count < self.round_num):
            if self.sim_game.round_count % 100 == 0 and self.sim_game.round_count // 100 == counting:
                print('round : %d' % self.sim_game.round_count)
                counting = counting + 1
            # self.tr.ProcessInput(None, None)
            # self.tr.Update()
            self.sim_game.ProcessInput([], [])
            self.sim_game.Update()
        return self.sim_game.scores

    # def LegalStart(self, cards):
        # month = np.zeros(12, dtype=int)
        # for card in cards:
            # m, o = card
            # month[m] = month[m] + 1
            # if month[m] >= 3:
                # return False
        # return True


if __name__ == '__main__':
    sim = Simulate(int(sys.argv[1]))
    print(sim.simulate())
    print(sim.agents)
