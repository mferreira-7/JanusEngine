import unittest
import torch
import chess
import numpy as np
from AlphaZero import ResNet, Chess, MCTS, Node


class TestNeuralNetwork(unittest.TestCase):
    def setUp(self):
        self.device = torch.device("cpu")
        self.model = ResNet(self.device, numResBlocks=1, numHidden=16)
        self.game = Chess()
        self.args = {"C": 1.5, "numSearches": 2, "dirichletEpsilon": 0.25, "dirichletAlpha": 0.3}

    def testModelArchitecture(self):
        batch_size = 1
        input_tensor = torch.zeros((batch_size, 13, 8, 8), device=self.device)

        policy, value = self.model(input_tensor)

        self.assertEqual(policy.shape, (batch_size, 4096))
        self.assertEqual(value.shape, (batch_size, 1))

        self.assertTrue(torch.all(value >= -1) and torch.all(value <= 1))

    def testBoardEncoding(self):
        encoded_board = self.game.getEncodedBoard()

        self.assertEqual(encoded_board.shape, (13, 8, 8))

        white_pieces = encoded_board[:6].sum()
        self.assertEqual(white_pieces, 16)

        black_pieces = encoded_board[6:12].sum()
        self.assertEqual(black_pieces, 16)

        turn_plane = encoded_board[12]
        self.assertTrue(np.all(turn_plane == 1))

        move = list(self.game.board.legal_moves)[0]
        self.game.applyMove(move)

        encoded_board = self.game.getEncodedBoard()
        turn_plane = encoded_board[12]
        self.assertTrue(np.all(turn_plane == 0))

    def testMctsSearch(self):
        mcts = MCTS(self.game, self.args, self.model)

        move, visit_count, children = mcts.search()

        self.assertIsNotNone(move)

        self.assertIn(move, list(self.game.board.legal_moves))

        self.assertTrue(len(children) > 0)

        self.assertTrue(visit_count > 0)

    def testNodeExpansion(self):
        root = Node(self.game, self.args, visitCount=1)

        legal_moves = list(self.game.board.legal_moves)
        probs = [1.0 / len(legal_moves)] * len(legal_moves)
        policy = list(zip(legal_moves, probs))

        root.expand(policy)

        self.assertEqual(len(root.children), len(legal_moves))

        for child in root.children:
            self.assertIn(child.actionTaken, legal_moves)
            self.assertAlmostEqual(child.prior, 1.0 / len(legal_moves))

        selected = root.select()
        self.assertEqual(selected, root.children[0])

        root.children[1].visitCount = 5
        root.children[1].valueSum = 3

        selected = root.select()
        self.assertEqual(selected, root.children[1])

    def testPolicyTargetVector(self):
        from AlphaZero import get_policy_target_vector

        game = Chess()

        args = {"C": 1.5}
        children = []
        legal_moves = list(game.board.legal_moves)[:3]
        for i, move in enumerate(legal_moves):
            new_board, new_player = game.getNextState(move)
            new_game = Chess()
            new_game.board = new_board.copy()
            new_game.player = new_player
            child = Node(new_game, args, None, move, 0.1)
            child.visitCount = i + 1
            children.append(child)

        action_probs = [1 / 6, 2 / 6, 3 / 6]

        target = get_policy_target_vector(children, action_probs)

        self.assertEqual(target.shape, (4096,))

        self.assertAlmostEqual(np.sum(target), 1.0)

        for child, prob in zip(children, action_probs):
            move = child.actionTaken
            index = move.from_square * 64 + move.to_square
            self.assertAlmostEqual(target[index], prob)
