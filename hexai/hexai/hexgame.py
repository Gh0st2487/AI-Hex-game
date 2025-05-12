from random import choice
from blessed import Terminal
from hexai.hexboard import HexBoard

t = Terminal()

class Hex:
    def __init__(self, board_size, players):
        assert board_size > 1 and board_size < 26
        assert len(players) == 2

        self.board_size = board_size
        self.players = players
        self.board = HexBoard(self.board_size)
    
    def prepare_game(self, player_start=None, start_move=None):
        self.board = HexBoard(self.board_size)
        
        if player_start == None:
            player_start = choice([0, 1])
        
        if start_move != None:
            self.board.place(start_move, self.board.RED)
            print(self.board)
        
        for i, player in enumerate(self.players):
            player.reset()
            if i == player_start:
                player.set_board_and_color(self.board, self.board.BLUE)
            else:
                player.set_board_and_color(self.board, self.board.RED)
                

    def play(self, player_start=None, start_move=None, verbose=2):
        player_num = player_start
        turn_count = 1
        
        self.prepare_game(player_start, start_move)
        
        while not self.board.check_win(self.board.get_opposite_color(self.players[player_num].color)):
            if verbose >= 2:
                print(t.clear())
                print("-----Hex turn {}-----\n".format(turn_count))
                print(self.board)
                print("")
            
            self.players[player_num].do_turn(verbose=verbose)
            player_num = (player_num + 1) % 2
            turn_count += 1
            
        if verbose >= 2:
            print(t.clear())
            print("-----Hex turn {}-----\n".format(turn_count))
            print(self.board)
            print("")
        
        winner = (player_num + 1) % 2
        
        for i, player in enumerate(self.players):
            player.games_played += 1
            if i == winner:
                player.games_won += 1
        
        if verbose >= 1:
            print("\nPlayer {} won the game against player {}!".format(self.players[winner].name, self.players[(winner + 1) % 2].name))
            first_player = player_start
            if start_move != None:
                first_player = (first_player + 1) % 2
            
            print("Player {} did the first move".format(self.players[first_player].name))
            if start_move is not None:
                print("With starter move {}".format(start_move))
            
            if verbose == 1:
                print(self.board)
            
            print("")
        
        return winner
