# -*- coding: utf-8 -*-
import numpy as np
import tensorflow as tf
import random
class Agent:
    def __init__(self,act_dim,algorithm,e_greed=0.1,e_greed_decrement=0):
        self.act_dim = act_dim
        self.algorithm = algorithm
        self.e_greed = e_greed
        self.e_greed_decrement = e_greed_decrement
    
    def sample(self, station):

        pred_move, pred_act = self.algorithm.model.predict(station)
        # print(pred_move)
        print("self.e_greed:", self.e_greed)
        pred_move = pred_move.numpy()
        pred_act = pred_act.numpy()

        sample = np.random.rand()  
        if sample < self.e_greed:
            print("random move")
            move = random.randint(0, 5)
        else:
            move = np.argmax(pred_move)
        
        self.e_greed = max(
            0.03, self.e_greed - self.e_greed_decrement)

        sample = np.random.rand() 
        if sample < self.e_greed:
            print("random act")
            act = random.randint(0, 4)
        else:
            act = np.argmax(pred_act)

        self.e_greed = max(
            0.03, self.e_greed - self.e_greed_decrement)
        return move, act