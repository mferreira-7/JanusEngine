import chess
import math
import random
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import matplotlib.pyplot as plt

def getInitialState():
    return chess.Board()

def getMoveFromUCI(moveString):
    return chess.Move.from_uci(moveString)

def getOpponentValue(value):
    return -value

def getReshapedPolicy(policy, validMoves, xDim, yDim):
    newPolicy = []
    policy.reshape(xDim,yDim)
    for x in range(xDim):
        for y in range(yDim):
            if chess.Move(x, y) in validMoves:
                newPolicy.append(policy[x][y])
            else:
                newPolicy.append(0)
    return newPolicy

def softmax_move_selection(root):
    """Selects a move using softmax over visit counts."""
    visits = np.array([child.visitCount for child in root.children], dtype=np.float32)
    exp_visits = np.exp(visits - np.max(visits))  # Prevent overflow
    probabilities = exp_visits / np.sum(exp_visits)  # Normalize

    return np.random.choice(root.children, p=probabilities)

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

    def getValueAndTerminated(self):
        outcome = self.board.outcome()
        if outcome is not None:
            if outcome.winner is not None:
                return 1 if outcome.winner == self.player else -1, True  #normal win/loss case
            else:
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
    def __init__(self, numResBlocks=4, numHidden=64):
        super().__init__()
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

'''
# Test encoding
chessGame = Chess()
chessGame.applyMove(getMoveFromUCI("f2f3"))
chessGame.applyMove(getMoveFromUCI("e7e6"))
chessGame.applyMove(getMoveFromUCI("g2g4"))
chessGame.applyMove(getMoveFromUCI("d8h5"))
encodedBoard = chessGame.getEncodedBoard()
print(encodedBoard.shape)  # Should be (13, 8, 8)

# Test neural network forward pass
tensorBoard = torch.tensor(encodedBoard).unsqueeze(0)
model = ResNet()
policy, value = model(tensorBoard)
print(policy.shape, value.shape)  # Expect (1, 4096) and (1, 1)

# Convert policy to numpy and reshape to (64, 64)
policy_reshaped = policy.detach().cpu().numpy().reshape(64, 64)
# Get all valid moves
valid_moves = chessGame.getValidMoves()
# Extract policy values for valid moves
move_probs = [policy_reshaped[m.from_square][m.to_square] for m in valid_moves]

moveProbs = []
for x in range(64):
    for y in range(64):
        if chess.Move(x, y) in valid_moves:
            moveProbs.append(policy_reshaped[x][y])
        else:
            moveProbs.append(0)
print(len(moveProbs))
print("--")
print(len(moveProbs) - moveProbs.count(0))
print("--")
print(len(move_probs))
test = np.reshape(moveProbs, (64,64))
print("--")
print(move_probs)
test2 = []
for x in test:
    for y in x:
        if y != 0:
            test2.append(round(y,8))
print("--")
print(sorted(test2))
print(sorted(move_probs))

# Plot
plt.figure(figsize=(10, 5))
plt.bar(range(len(valid_moves)), move_probs)
plt.xticks(range(len(valid_moves)), [m.uci() for m in valid_moves], rotation=90)
plt.ylabel("Probability")
plt.title("Move Probabilities from MCTS Policy Head")
plt.show()
'''

class Node:
    def __init__(self, game, args, parent=None, actionTaken=None, prior = 0):
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
                new_game.board = new_board
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
        root = Node(self.game, self.args)
        for _ in range(self.args["numSearches"]):
            node = root
            while node.isFullyExpanded():
                node = node.select()

            value, isTerminal = node.game.getValueAndTerminated()
            value = getOpponentValue(value)

            if not isTerminal:
                policy, value = self.model(
                    torch.tensor(node.game.getEncodedBoard()).unsqueeze(0)
                )
                validMoves = node.game.getValidMoves()
                policyReshaped = policy.detach().cpu().numpy().reshape(64, 64)
                moveProbs = [policyReshaped[m.from_square][m.to_square] for m in validMoves]
                policy = list(zip(validMoves, moveProbs))


                """
                I NEED AN ACTION TO PASS TO THE BOARD AND A PROB OF THAT ACTION
                CURRENTLY I ONLY HAVE THE PROB AND THE BOARD LOCATION
                I NEED TO MATCH AN ACTION TO ITS PROB, THEN PASS THAT AS THE POLICY
                THIS MEANS I WOULD BE ABLE TO EXPAND BASED ON PROB OF SEPCIFIED ACTION
                """

                value = value.item()
                node.expand(policy)

            node.backpropagate(value)

        bestNode = softmax_move_selection(root)  # New, more balanced move selection
        return bestNode.actionTaken, bestNode.visitCount, [node.visitCount for node in root.children]

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
        print(f"[{movesC}] Black move:", move[0].uci(), "Move Value:", move[1], "Possible Values:", move[2])
        move = move[0]

    chessGame.applyMove(move)
    movesC += 1
    value, isTerminal = chessGame.getValueAndTerminated()

    if isTerminal:
        print(chessGame.board)
        print("Game Over. Winner:", "Black" if value == 1 else "White" if value == -1 else "Draw")
        break
