import chess
import math
import random
import torch
import torch.nn as nn
import torch.nn.functional as F
import os.path
import numpy as np
import matplotlib.pyplot as plt
from tqdm import trange

root = os.path.dirname(os.path.dirname(__file__))

def get_move_index(move):
    return move.from_square * 64 + move.to_square

def getInitialState():
    return chess.Board()

def getMoveFromUCI(moveString):
    return chess.Move.from_uci(moveString)

def getOpponentValue(value):
    return -value

def softmax_move_selection(root):
    """Selects a move using softmax over visit counts."""
    visits = np.array([child.visitCount for child in root.children], dtype=np.float32)
    exp_visits = np.exp(visits - np.max(visits))  # Prevent overflow
    probabilities = exp_visits / np.sum(exp_visits)  # Normalize

    return np.random.choice(root.children, p=probabilities)

def get_policy_target_vector(children, actionProbabilities):
    """
    Creates a fixed-size (4096) target vector for the policy head.
    For each child (move) from the current state, the corresponding index is:
      index = from_square * 64 + to_square.
    """
    target = np.zeros(4096, dtype=np.float32)
    for child, prob in zip(children, actionProbabilities):
        move = child.actionTaken
        index = move.from_square * 64 + move.to_square
        target[index] = prob
    return target

class Chess:
    def __init__(self):
        self.board = getInitialState()
        self.player = chess.WHITE
        self.size = 64

    def resetBoard(self):
        self.board = getInitialState()
        self.player = chess.WHITE

    def getNextState(self, action):
        new_board = self.board.copy()
        new_board.push(action)
        return new_board, not self.player

    def applyMove(self, action):
        self.board.push(action)
        self.player = not self.player

    def reverseAction(self):
        self.board.pop()
        self.player = not self.player

    def getValidMoves(self):
        return list(self.board.legal_moves)

    def checkWin(self):
        outcome = self.board.outcome()
        if outcome is not None:
            return outcome.winner
        return None

    def getValueAndTerminated(self): #TODO: NOT OVER BUT ISTERMINAL
        outcome = self.board.outcome()
        if outcome is not None:
            if outcome.winner is not None:
                #print("winner")
                return 1 if outcome.winner == self.player else -1, True  #normal win/loss case
            else:
                #print("not winner")
                evaluation = self.evaluatePosition()
                return evaluation, True  #assign a positional value for draws
        return 0, False

    def evaluatePosition(self):
        """Simple evaluation based on material count"""
        material_score = sum([self.getPieceValue(piece) for piece in self.board.piece_map().values()])
        return 0.5 * math.tanh(material_score / 10)  # Normalize using tanh

    def getPieceValue(self, piece):
        """Assign simple material values"""
        values = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3, chess.ROOK: 5, chess.QUEEN: 9}
        return values.get(piece.piece_type, 0) * (1 if piece.color == self.player else -1)

    def getEncodedBoard(self):
        encodedBoard = np.zeros((13, 8, 8), dtype=np.float32)  # 12 for pieces, 1 for turn
        piece_map = self.board.piece_map()

        for square, piece in piece_map.items():
            piece_idx = (piece.piece_type - 1) + (0 if piece.color == chess.WHITE else 6)
            row, col = divmod(square, 8)
            encodedBoard[piece_idx, row, col] = 1

        encodedBoard[12, :, :] = 1 if self.board.turn == chess.WHITE else 0
        return encodedBoard

class ResNet(nn.Module):
    def __init__(self, device, numResBlocks=3, numHidden=32):
        super().__init__()
        self.device = device
        self.startBlock = nn.Sequential(
            nn.Conv2d(13, numHidden, kernel_size=3, padding=1),
            nn.BatchNorm2d(numHidden),
            nn.ReLU()
        )
        self.backBone = nn.ModuleList([ResBlock(numHidden) for _ in range(numResBlocks)])
        self.policyHead = nn.Sequential(
            nn.Conv2d(numHidden, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.Flatten(),
            nn.Linear(32 * 8 * 8, 4096)  # Output space for chess moves
        )
        self.valueHead = nn.Sequential(
            nn.Conv2d(numHidden, 3, kernel_size=3, padding=1),
            nn.BatchNorm2d(3),
            nn.ReLU(),
            nn.Flatten(),
            nn.Linear(3 * 8 * 8, 1),
            nn.Tanh()
        )
        self.to(device)

    def forward(self, x):
        x = self.startBlock(x)
        for resBlock in self.backBone:
            x = resBlock(x)
        return self.policyHead(x), self.valueHead(x)

class ResBlock(nn.Module):
    def __init__(self, numHidden):
        super().__init__()
        self.conv1 = nn.Conv2d(numHidden, numHidden, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(numHidden)
        self.conv2 = nn.Conv2d(numHidden, numHidden, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(numHidden)

    def forward(self, x):
        residual = x
        x = F.relu(self.bn1(self.conv1(x)))
        x = self.bn2(self.conv2(x))
        return F.relu(x + residual)

class Node:
    def __init__(self, game, args, parent=None, actionTaken=None, prior = 0, visitCount = 0):
        self.game = game
        self.args = args
        self.parent = parent
        self.actionTaken = actionTaken
        self.children = []
        self.visitCount = 0
        self.valueSum = 0
        self.prior = prior

    def isFullyExpanded(self):
        return len(self.children) > 0

    def select(self):
        bestChild = max(self.children, key=self.getUCB)
        return bestChild

    def getUCB(self, child):
        if child.visitCount == 0:
            qValue = 0
        else:
            qValue = 1 - ((child.valueSum / child.visitCount) + 1) / 2
        return qValue + self.args["C"] * (math.sqrt(self.visitCount) / (child.visitCount + 1)) * child.prior

    def expand(self, policy):
        for (action, prob) in policy:
            if prob > 0 :
                new_board, new_player = self.game.getNextState(action)
                new_game = Chess()
                new_game.board = new_board.copy()
                new_game.player = new_player

                child = Node(new_game, self.args, self, action, prob)
                self.children.append(child)

    def backpropagate(self, value):
        self.valueSum += value
        self.visitCount += 1

        value = getOpponentValue(value)
        if self.parent is not None:
            self.parent.backpropagate(value)

class MCTS:
    def __init__(self, game, args, model):
        self.game = game
        self.args = args
        self.model = model

    @torch.no_grad()
    def search(self):
        root = Node(self.game, self.args, visitCount = 1)

        policy, _ = self.model(
            torch.tensor(root.game.getEncodedBoard(), device=self.model.device).unsqueeze(0)
        )
        policyReshaped = policy.detach().cpu().numpy().flatten()
        policyReshaped = (1 - self.args["dirichletEpsilon"]) * policyReshaped + self.args["dirichletEpsilon"] * np.random.dirichlet([self.args["dirichletAlpha"]] * len(policyReshaped))

        validMoves = root.game.getValidMoves()
        moveProbs = [policyReshaped[get_move_index(m)] for m in validMoves]

        policy = list(zip(validMoves, moveProbs))

        root.expand(policy)

        for _ in range(self.args["numSearches"]):
            node = root
            while node.isFullyExpanded():
                node = node.select()

            value, isTerminal = node.game.getValueAndTerminated()
            value = getOpponentValue(value)

            if not isTerminal:
                policy, value = self.model(
                    torch.tensor(node.game.getEncodedBoard(), device=self.model.device).unsqueeze(0)
                )
                validMoves = node.game.getValidMoves()
                policyReshaped = policy.detach().cpu().numpy().reshape(64, 64)
                moveProbs = [policyReshaped[m.from_square][m.to_square] for m in validMoves]
                policy = list(zip(validMoves, moveProbs))

                value = value.item()

                node.expand(policy)

            node.backpropagate(value)

        if len(root.children) == 0 and len(root.game.getValidMoves()) > 0:
            root.children.extend([Node(self.game, self.args, root, move, 0) for move in root.game.getValidMoves()])

        bestNode = softmax_move_selection(root)  # New, more balanced move selection

        return bestNode.actionTaken, bestNode.visitCount, [node for node in root.children]

class AlphaZero:
    def __init__(self, model, optimizer, game, args):
        self.model = model
        self.optimizer = optimizer
        self.game = game
        self.args = args
        self.mcts = MCTS(game, args, model)

    def selfPlay(self):
        memory = []
        state = Chess()
        prevFromSqr = None

        while True:
            neutralGame = Chess()
            neutralGame.board = state.board
            neutralGame.player = not state.player

            search = MCTS(neutralGame, self.args, self.model).search()
            children = search[2]
            nodeVisitCounts = [child.visitCount for child in children]
            total_visits = sum(nodeVisitCounts)

            if total_visits == 0:
                actionProbabilities = [1 / len(children)] * len(children)
            else:
                actionProbabilities = [vc / total_visits for vc in nodeVisitCounts]

            # Convert variable-length move list into a fixed 4096-dimensional vector
            policyTarget = get_policy_target_vector(children, actionProbabilities)

            # Store the encoded board, fixed policy target, and current player
            memory.append((neutralGame.getEncodedBoard(), policyTarget, state.player))

            actionProbabilitiesTemperature = [prob ** (1 / self.args["temperature"]) for prob in actionProbabilities]
            chosen = np.random.choice(children, p=actionProbabilities)

            action = chosen.actionTaken

            if action.to_square == prevFromSqr:
                action = np.random.choice(children).actionTaken
                print("random") #TODO: Change this from a random selection to the next best node, if there isnt a next best then we can do random

            state.applyMove(action)
            prevFromSqr = action.from_square
            print("move made", action)

            value, isTerminal = state.getValueAndTerminated()

            if isTerminal:
                print("isTerminal", "WHITE" if state.player else "BLACK")
                print(state.board)
                returnMemory = []
                for histNeutralState, histActionProbabilities, histPlayer in memory:
                    histOutcome = value if histPlayer == state.player else getOpponentValue(value)
                    returnMemory.append((
                        histNeutralState,
                        histActionProbabilities,
                        histOutcome
                    ))
                return returnMemory

            state.player = not state.player

    def train(self, memory):
        random.shuffle(memory)
        for batchIdx in range(0, len(memory), self.args["batchSize"]):
            sample = memory[batchIdx:min(len(memory)-1, batchIdx+self.args["batchSize"])]
            if not sample:
                continue
            state, policyTargets, valueTargets = zip(*sample) #transpose lists

            state, policyTargets, valueTargets = np.array(state), np.array(policyTargets), np.array(valueTargets).reshape(-1, 1)

            state = torch.tensor(state, dtype=torch.float32, device=self.model.device)
            policyTargets = torch.tensor(policyTargets, dtype=torch.float32, device=self.model.device)
            valueTargets = torch.tensor(valueTargets, dtype=torch.float32, device=self.model.device)

            outPolicy, outValue = self.model(state)

            log_probs = F.log_softmax(outPolicy, dim=1)
            policyLoss = -torch.mean(torch.sum(policyTargets * log_probs, dim=1))

            #policyLoss = F.cross_entropy(outPolicy, policyTargets)
            valueLoss = F.mse_loss(outValue, valueTargets)
            loss = policyLoss + valueLoss

            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()

    def learn(self):
        for iteration in trange(self.args["numIterations"]):
            memory = []

            self.model.eval()
            for selfPlayIteration in trange(self.args["numSelfPlayIterations"]):
                memory += self.selfPlay()

            self.model.train()
            for epoch in trange(self.args["numEpochs"]):
                self.train(memory)

            torch.save(self.model.state_dict(), f"model_{iteration}.pt")
            torch.save(self.optimizer.state_dict(), f"optimizer_{iteration}.pt")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = ResNet(device)
optimizer = torch.optim.Adam(model.parameters(), lr=0.001, weight_decay=0.0001)
#chessGame = Chess()
'''
args = {
    "C": 1.5,
    "numSearches": 15, #for me (20-30) optimally (100 -> 200)
    "numIterations": 10, #for me 3 optimally (50 -> 100)
    "numSelfPlayIterations": 5, #for me 3 optimally (25 -> 50)
    "numEpochs": 5, #for me 3 optimally (10 -> 20)
    "batchSize": 8, #for me 16 or 32 optimally 64
    "temperature": 1.5, #exploitation vs exploration
    "dirichletEpsilon": 0.5,
    "dirichletAlpha": 0.5
}

alphaZero = AlphaZero(model, optimizer, chessGame, args)
#alphaZero.learn()

# Test encoding
chessGame = Chess()
chessGame.applyMove(random.choice(chessGame.getValidMoves()))
chessGame.applyMove(random.choice(chessGame.getValidMoves()))
chessGame.applyMove(random.choice(chessGame.getValidMoves()))
encodedBoard = chessGame.getEncodedBoard() 
print(chessGame.board)

# Test neural network forward pass
tensorBoard = torch.tensor(encodedBoard, device=device).unsqueeze(0)
model = ResNet(device)
for iter in range(args["numIterations"]):
    model.load_state_dict(torch.load(f"model_{iter}.pt", map_location=device))
    model.eval()
    policy, value = model(tensorBoard)
    print(policy.shape, value.shape)  # Expect (1, 4096) and (1, 1)
    print(value.item())
    # Convert policy to numpy and reshape to (64, 64)
    policy_reshaped = policy.detach().cpu().numpy().reshape(64, 64)
    # Get all valid moves
    valid_moves = chessGame.getValidMoves()
    # Extract policy values for valid moves
    move_probs = [policy_reshaped[m.from_square][m.to_square] for m in valid_moves]

    # Plot
    plt.figure(figsize=(10, 5))
    plt.bar(range(len(valid_moves)), move_probs)
    plt.xticks(range(len(valid_moves)), [m.uci() for m in valid_moves], rotation=90)
    plt.ylabel("Probability")
    plt.title(f"Move Probabilities from MCTS Policy Head: Level {iter}")
    plt.show()
'''

def getAzMove(fenString, modelStrength):
    game = Chess()
    fenBoard = chess.Board(fenString)
    game.board = fenBoard.copy()
    encodedBoard = game.getEncodedBoard()
    tensorBoard = torch.tensor(encodedBoard, device=device).unsqueeze(0)
    model.load_state_dict(torch.load(os.path.join(root, "minmax", f"model_{modelStrength}.pt"), map_location=device))
    model.eval()
    pol, _ = model(tensorBoard)
    policyReshaped = pol.detach().cpu().numpy().reshape(64, 64)
    validMoves = game.getValidMoves()
    moveProbs = [policyReshaped[m.from_square][m.to_square] for m in validMoves]
    nonZeroMoveProbs = [0 if mp < 0 else mp for mp in moveProbs]
    normalizedMoveProbs = [mp / sum(nonZeroMoveProbs) for mp in nonZeroMoveProbs]
    chosenMove = np.random.choice(validMoves, p=normalizedMoveProbs)
    return chosenMove.uci()


'''
chessGame = Chess()
args = {"C": 2, "numSearches": 1000}
model = ResNet()
mcts = MCTS(chessGame, args, model)

movesC = 1
while True:#maybe implement a one error allowance flag
    print(chessGame.board, "\n")
    if chessGame.player == chess.WHITE:
        try:
            #move = random.choice(chessGame.getValidMoves())
            move = getMoveFromUCI(input("Enter move: "))
            if move not in chessGame.getValidMoves():
                raise ValueError("Invalid move")
            print(f"[{movesC}] White move:", move.uci())
        except:
            print("Action not valid\n")
            continue
    else:
        move = mcts.search()
        print(f"[{movesC}] Black move:", move[0].uci(), "Move Value:", move[1], f"Possible Values: {[x.visitCount for x in move[2]]}")
        move = move[0]

    chessGame.applyMove(move)
    movesC += 1
    value, isTerminal = chessGame.getValueAndTerminated()

    if isTerminal:
        print(chessGame.board)
        print("Game Over. Winner:", "Black" if value == 1 else "White" if value == -1 else "Draw")
        break
'''