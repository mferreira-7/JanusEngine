import unittest
import chess
from ChessEngine import GameState, Move
import ChessAI
import AlphaZero
import torch


class IntegrationTests(unittest.TestCase):
    def setUp(self):
        self.game_state = GameState()
        self.chess_game = AlphaZero.Chess()
        self.device = torch.device("cpu")
        self.model = AlphaZero.ResNet(self.device, numResBlocks=1, numHidden=16)

    def testClassicalToNeuralBridge(self):
        fen = ChessAI.getFen(self.game_state)

        board = chess.Board(fen)

        self.assertTrue(board.is_valid())

        self.chess_game.board = board

        encoded_board = self.chess_game.getEncodedBoard()

        tensor_board = torch.tensor(encoded_board, device=self.device).unsqueeze(0)
        policy, value = self.model(tensor_board)

        self.assertEqual(policy.shape, (1, 4096))
        self.assertEqual(value.shape, (1, 1))

    def testMoveTranslation(self):
        valid_moves = self.game_state.getValidMoves()
        e2e4_move = None

        for move in valid_moves:
            if move.startRow == 6 and move.startCol == 4 and move.endRow == 4 and move.endCol == 4:
                e2e4_move = move
                break

        self.assertIsNotNone(e2e4_move)

        self.game_state.makeMove(e2e4_move)

        fen = ChessAI.getFen(self.game_state)

        board = chess.Board(fen)

        self.assertEqual(board.piece_at(chess.E4).symbol().lower(), 'p')
        self.assertIsNone(board.piece_at(chess.E2))

        d7d5_uci = "d7d5"
        d7d5_move = chess.Move.from_uci(d7d5_uci)

        board.push(d7d5_move)

        new_fen = board.fen()
        expected_fen_start = "rnbqkbnr/ppp1pppp/8/3p4/4P3/8/PPPP1PPP/RNBQKBNR"
        self.assertTrue(new_fen.startswith(expected_fen_start))

    def testFullEngineIntegration(self):
        fen = ChessAI.getFen(self.game_state)

        board = chess.Board(fen)
        self.chess_game.board = board
        encoded_board = self.chess_game.getEncodedBoard()
        tensor_board = torch.tensor(encoded_board, device=self.device).unsqueeze(0)

        policy, _ = self.model(tensor_board)

        legal_moves = list(board.legal_moves)
        self.assertTrue(len(legal_moves) > 0)

        selected_move = legal_moves[0]
        uci = selected_move.uci()

        self.assertEqual(len(uci), 4)

        from_square = (8 - int(uci[1]), ord(uci[0]) - ord('a'))
        to_square = (8 - int(uci[3]), ord(uci[2]) - ord('a'))

        valid_moves = self.game_state.getValidMoves()
        matching_move = None
        for move in valid_moves:
            if (move.startRow, move.startCol) == from_square and (move.endRow, move.endCol) == to_square:
                matching_move = move
                break

        self.assertIsNotNone(matching_move)
