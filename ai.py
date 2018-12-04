import numpy as np

class Simulate:
    def __init__(self):
        self.search_times = 10
        pass

    def MonteCarlo(self):
        #perform montecarlo search and return a good action dist as data
        return state, action_dist


class State:
    def __init__(self):
        self.oya = 1
        self.player = 1
        self.p1_state = []
        self.p2_state = []
        self.p1_temp_score = 0
        self.p2_temp_score = 0

    def RandState(self):
        # fix p1_state but change hand of p2 randomly
        pass

    def Transition(self, action):
        #update states
        pass

    def CheckRules(self):
        #check if a state scores or not

class Agent:
    def __init__(self):
        #learning model init
        pass

    def __init__(self, model_path):
        #load learning model from path
        pass

    def Train(self, data):
        #train by data from montecarlo tree search
        pass

    def Action(self, state):
        #perform action from input state
        pass

    def SaveModel(self):
        #save model
        pass
        

