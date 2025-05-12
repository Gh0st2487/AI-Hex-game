# AI-Hex-Game: Intelligent Hex Board Game AI

This project implements an AI for the classic board game **Hex**, using Python. The AI plays strategically using the **Minimax algorithm with Alpha-Beta pruning**, providing a challenging experience for human players. The game runs in the terminal and supports various modes of play.

## Features

* **Minimax AI with Alpha-Beta Pruning**: The AI searches the game tree efficiently to determine the best moves.
* **Human vs AI or Human vs Human**: Choose to play against the computer or a friend.
* **Custom Board Size**: Play Hex on different-sized boards to vary the difficulty.
* **Simple Terminal Interface**: Lightweight and easy to run without GUI dependencies.
* **Modular Codebase**: Organized structure for easy experimentation and enhancements.

## Getting Started

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/Gh0st2487/AI-Hex-game.git
   cd AI-Hex-game/hexai
   ```

2. **Run the Game**:

   ```bash
   python hexai.py
   ```

## Project Structure

* `hexai.py`: Main game loop and CLI interface.
* `board.py`: Logic for board representation and move validation.
* `minimax.py`: Minimax algorithm implementation with Alpha-Beta pruning.
* `player.py`: Handles human and AI player types.

## Contributing

Pull requests and feature suggestions are welcome. Feel free to fork the repo and submit improvements!
