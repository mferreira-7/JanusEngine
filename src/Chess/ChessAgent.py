import torch
import random
import numpy as np
from collections import deque
import ChessMain, ChessEngine, ChessAi

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LEARN_RATE = 0.001

class Agent:
    def __init__(self):
        self.nGames = 0
        self.epsilon = 0 #controls randomness
        self.gamma = 0 #discount rate
        self.memory = deque(maxlen=MAX_MEMORY)
        #model, trainer

    def getState(self, game):
        pass

    def remember(self, state, action, reward, nextState, done):
        pass

    def trainLongMemory(self):
        pass

    def trainShortMemory(self, state, action, reward, nextState, done):
        pass

    def getAction(self, state):
        pass

def train():
    plotScores = []
    plotMeanScores = []
    totalScore = 0
    record = 0
    agent = Agent()
    game = ChessMain
    while True:
        #get old state
        oldState = agent.getState(game)

        #get move
        finalMove = agent.getAction(oldState)

        #perform move and get new state
        reward, done, score = game.main() #should use finalMove
        newState = agent.getState(game)

        #train short memory
        agent.trainShortMemory(oldState, finalMove, reward, newState, done)

        #remember
        agent.remember(oldState, finalMove, reward, newState, done)

        if done:
            #train long memory (experience replay), plot results
            game.main() #should reset
            agent.nGames += 1
            agent.trainLongMemory()

            if score > record:
                record = score
                #agent.model.save()

            print("Game", agent.nGames, "score", score, "record", record)

            #Plot


if __name__ == "__main__":
    train()