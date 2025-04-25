import unittest
import chess
from ChessEngine import GameState, Move
import ChessAI


class TestChessEngineCore(unittest.TestCase):
    def setUp(self):
        self.game = GameState()

    def testInitialBoardSetup(self):
        self.assertEqual(self.game.board[0][4], "kB")  # B king
        self.assertEqual(self.game.board[7][4], "kW")  # W king
        self.assertEqual(self.game.board[1][0], "pB")  # B pawn
        self.assertEqual(self.game.board[6][0], "pW")  # W pawn
        self.assertEqual(self.game.board[0][0], "rB")  # B rook

    def testPawnMovesGeneration(self):
        moves = self.game.getValidMoves()

        pawn_moves = [move for move in moves if self.game.board[move.startRow][move.startCol][0] == 'p']
        self.assertEqual(len(pawn_moves), 16)

        start = (6, 4)  # e2
        end = (4, 4)  # e4
        move = Move(start, end, self.game.board)
        self.game.makeMove(move)

        moves = self.game.getValidMoves()
        moved_pawn_moves = [m for m in moves if m.startRow == 4 and m.startCol == 4]
        self.assertEqual(len(moved_pawn_moves), 0)

    def testCastlingConditions(self):
        moves = self.game.getValidMoves()
        castle_moves = [move for move in moves if move.isCastleMove]
        self.assertEqual(len(castle_moves), 0)

        self.game.board[7][5] = "--"
        self.game.board[7][6] = "--"

        moves = self.game.getValidMoves()
        castle_moves = [move for move in moves if move.isCastleMove]
        self.assertEqual(len(castle_moves), 1)

    def testCheckDetection(self): #FAIL
        self.game.board = [
            ["rB", "nB", "bB", "qB", "kB", "bB", "nB", "rB"],
            ["pB", "pB", "pB", "pB", "pB", "pB", "pB", "pB"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["pW", "pW", "pW", "pW", "--", "pW", "pW", "pW"],
            ["rW", "nW", "bW", "qW", "kW", "bW", "nW", "rW"]
        ]

        self.game.board[3][4] = "qW"
        self.game.whiteToMove = False

        self.assertTrue(self.game.inCheck())

        moves = self.game.getValidMoves()
        self.assertTrue(len(moves) > 0)

    def testCheckmateDetection(self): #FAIL
        self.game.board = [
            ["rB", "nB", "bB", "qB", "kB", "bB", "nB", "rB"],
            ["pB", "pB", "pB", "pB", "--", "pB", "pB", "pB"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "pB", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "qW", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["pW", "pW", "pW", "pW", "pW", "pW", "pW", "pW"],
            ["rW", "nW", "bW", "--", "kW", "bW", "nW", "rW"]
        ]

        self.game.whiteToMove = False
        moves = self.game.getValidMoves()

        self.assertEqual(len(moves), 0)
        self.assertTrue(self.game.checkmate)

    def testFenConversion(self):
        fen = ChessAI.getFen(self.game)
        expected_fen_start = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w"
        self.assertTrue(fen.startswith(expected_fen_start))

        start = (6, 4)  # e2
        end = (4, 4)  # e4
        move = Move(start, end, self.game.board)
        self.game.makeMove(move)

        fen = ChessAI.getFen(self.game)
        expected_fen_after_e4 = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b"
        self.assertTrue(fen.startswith(expected_fen_after_e4))
