import unittest
import chess
from ChessEngine import GameState, Move
import ChessAI


class TestSearchAlgorithms(unittest.TestCase):
    def setUp(self):
        self.game = GameState()

    def testAlphaBetaSearch(self):
        valid_moves = self.game.getValidMoves()

        best_move = ChessAI.findMoveNegaMaxAlphaBeta(
            self.game, valid_moves, 2, -ChessAI.CHECKMATE, ChessAI.CHECKMATE, 1
        )

        self.assertIsNotNone(best_move[0])  #move
        self.assertIsNotNone(best_move[1])  #score

        self.assertIn(best_move[0], valid_moves)

    def testMoveOrdering(self):
        self.game.board = [
            ["rB", "nB", "bB", "qB", "kB", "bB", "nB", "rB"],
            ["pB", "pB", "pB", "pB", "pB", "pB", "pB", "pB"],
            ["--", "--", "--", "--", "pW", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["pW", "pW", "pW", "pW", "--", "pW", "pW", "pW"],
            ["rW", "nW", "bW", "qW", "kW", "bW", "nW", "rW"]
        ]

        self.game.whiteToMove = False

        valid_moves = self.game.getValidMoves()

        capture_moves = [move for move in valid_moves if move.pieceCaptured != "--"]
        non_capture_moves = [move for move in valid_moves if move.pieceCaptured == "--"]

        self.assertTrue(len(capture_moves) > 0)

        for capture_move in capture_moves:
            capture_score = ChessAI.scoreMove(capture_move, self.game)
            for non_capture_move in non_capture_moves:
                non_capture_score = ChessAI.scoreMove(non_capture_move, self.game)
                self.assertGreater(capture_score, non_capture_score)

    def testQuiescenceSearch(self):
        self.game.board = [
            ["rB", "nB", "bB", "qB", "kB", "bB", "nB", "rB"],
            ["pB", "pB", "pB", "pB", "--", "pB", "pB", "pB"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "pB", "--", "--", "--"],
            ["--", "--", "--", "--", "bW", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["pW", "pW", "pW", "pW", "--", "pW", "pW", "pW"],
            ["rW", "nW", "bW", "qW", "kW", "--", "nW", "rW"]
        ]

        self.game.whiteToMove = False

        basic_score = ChessAI.scoreBoard(self.game)

        quiescence_score = ChessAI.quiescenceSearch(
            self.game, -ChessAI.CHECKMATE, ChessAI.CHECKMATE, -1
        )

        self.assertLessEqual(quiescence_score, basic_score)

    def testTranspositionTable(self):
        ChessAI.transposition_table.clear()

        valid_moves = self.game.getValidMoves()

        ChessAI.findMoveNegaMaxAlphaBeta(
            self.game, valid_moves, 3, -ChessAI.CHECKMATE, ChessAI.CHECKMATE, 1
        )

        self.assertTrue(len(ChessAI.transposition_table) > 0)

        move = valid_moves[0]
        self.game.makeMove(move)
        valid_moves = self.game.getValidMoves()
        move2 = valid_moves[0]
        self.game.makeMove(move2)
        valid_moves = self.game.getValidMoves()
        self.game.undoMove()
        self.game.undoMove()

        position_hash = self.game.getHash(ChessAI.ZOBRIST_TABLE)
        self.assertIn(position_hash, ChessAI.transposition_table)

