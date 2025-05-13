# JanusEngine: A hybrid engine implementing classical and neural techniques

## Table of contents
* [General info](#general-info)
* [Technologies](#technologies)
* [Features](#features)
* [Instructions](#instructions)
* [Implementation Details](#implementation-details)
* [Further development ideas](#further-development-ideas)

## General info
JanusEngine is a chess engine that bridges classical and neural approaches to chess AI. The project implements a hybrid system combining traditional alpha-beta search with deep reinforcement learning through self-play. Named after the Roman god who looks simultaneously to the past and future, JanusEngine leverages both time-tested minimax algorithms and modern neural network techniques.

The engine offers three playing modes:
- Traditional engine using alpha-beta search with optimizations
- Neural network-based engine using MCTS guided by learned policy and value networks
- Hybrid approach that integrates aspects of both methods

This project was developed as part of research into chess engine optimization techniques, focusing on the potential of self-learning systems to improve without explicit human knowledge.

## Technologies
* Python 3.8+
* PyTorch - Neural network implementation
* Pygame - Graphical user interface
* python-chess - Chess rules and board representation
* NumPy - Numerical operations and board state representation
* tqdm - Progress visualization during training

## Features
* Complete chess implementation with all standard rules
* Graphical user interface for gameplay
* Traditional alpha-beta search with:
  * Negamax implementation
  * Alpha-beta pruning
  * Quiescence search
  * Transposition tables
  * Move ordering optimizations
* Neural network components:
  * Residual neural network architecture
  * Policy and value heads
  * Board state encoding
* Monte Carlo Tree Search guided by neural networks
* Self-play training capability
* Opening book integration
* Various performance optimizations

## Instructions
### Installation:
1. Clone the repository
2. Install required dependencies:
   1. `pip install torch numpy pygame python-chess tqdm matplotlib`
3. Run the main application:
   1. `python ChessMain.py`

### Training the neural network:
1. To train the neural network through self-play:
   1. `python AlphaZero.py`
2. Adjust hyperparameters in the `args` dictionary to control training parameters

### Playing against the engine:
* White is controlled by the player by default, Black by the AI
* Click on a piece and then click on a destination square to move
* The engine will respond with its move

#### In-Game Controls:
* Press `z` to undo a move
* Press `r` to reset the game with new random openings
* Press `1` to toggle AI/human control for White
* Press `2` to toggle AI/human control for Black
* Press `3` to toggle between traditional and neural network mode

## Implementation Details
JanusEngine implements a dual-paradigm approach:

1. **Traditional Engine**: Uses alpha-beta pruning with a handcrafted evaluation function based on material counting and piece-square tables. Includes optimizations like quiescence search, transposition tables, and move ordering.

2. **Neural Engine**: Implements MCTS guided by a neural network with policy and value heads, trained through self-play reinforcement learning. The network learns chess strategies without explicit programming.

3. **Opening Book**: Incorporates a catalog of strong opening moves for both White and Black from grandmaster games to ensure strong early game play.

The system's architecture allows for comparing different AI approaches and leveraging their complementary strengths.

## Further development ideas
1. Implement NNUE (Efficiently Updatable Neural Networks) for faster neural evaluation
2. Enhance the hybrid system with better integration between traditional and neural components
3. Add distributed training capabilities for faster self-play learning
4. Implement endgame tablebases for perfect endgame play
5. Develop a more sophisticated position evaluation incorporating additional chess principles
6. Optimize memory usage for transposition tables to allow deeper search
7. Add support for chess variants (Fischer Random, Crazyhouse, etc.)
8. Implement a position analysis tool with visualization of engine evaluation
9. Add CECP/UCI protocol support for compatibility with chess GUIs
10. Create a progressive learning system with curriculum training

## Author
Marcel Ferreira - BSc Computer Science - University of Essex
