from random import seed, randint, choice
import numpy as np
import logging
from time import time
from ctypes import c_int
from multiprocessing import Process, Value, Array
from random import randint

from hexai.players.baseplayer import BasePlayer

log = logging.getLogger(__name__.split('.')[-1])

INF = 9999
LOSE = 1000

class AlphaBetaPlayer(BasePlayer):

    def __init__(self, evaluation, use_id, use_tt, max_depth=3, max_time=0.5, color=None, name="AlphaBeta"):
        super().__init__(name, color)
        self.max_depth = max_depth
        self.use_id = use_id
        self.use_tt = use_tt
        self.max_time = max_time
        if evaluation == "random":
            self.eval = self.eval_random
        elif evaluation == "dijkstra":
            self.eval = self.eval_dijkstra
        else:
            raise ValueError("Unkown evaluation function!")
        if self.use_tt:
            print()
        self.turn_timer = None

    def reset(self):
        pass

    def eval_random(self, color):
        self.eval_count += 1
        return self.local_random.randint(0, self.board.size*2)

    def eval_dijkstra(self, color):
        self.eval_count += 1
        return self.get_dijkstra_score(self.board.get_opposite_color(color)) - self.get_dijkstra_score(color)

    def dijkstra_update(self, color, scores, updated):
        log.debug("Starting dijkstra algorithm")
        updating = True
        while updating:
            updating = False
            for i, row in enumerate(scores):
                for j, point in enumerate(row):
                    if not updated[i][j]:
                        neighborcoords = self.board.get_neighbors((i, j))
                        for neighborcoord in neighborcoords:
                            target_coord = tuple(neighborcoord)
                            path_cost = LOSE
                            if self.board.is_empty(target_coord):
                                path_cost = 1
                            elif self.board.is_color(target_coord, color):
                                path_cost = 0
                            if scores[target_coord] > scores[i][j] + path_cost:
                                scores[target_coord] = scores[i][j] + path_cost
                                updated[target_coord] = False
                                updating = True
        return scores

    def timed_turn_loop(self):
        self.turn_timer = time()
        for depth in range(1, INF):
            result, move = self.alphabeta_nega(self.color, -INF, INF, depth)
            if result is not None and move is not None:
                if time() - self.turn_timer > self.max_time:
                    if result > best_score:
                        best_move = move
                        best_score = result
                else:
                    best_move = move
                    best_score = result
            if best_score >= LOSE or best_score <= -LOSE:
                break
        self.turn_timer = None
        return best_score, best_move

    def do_turn(self, verbose=0):
        assert self.board != None and self.color != None
        self.no_nodes_searched = 0
        self.no_cuts = 0
        self.turn_count += 1
        if verbose > 0:
            print("Player {} AI is thinking...".format(self.color))
        start_time = time()
        if self.use_id:
            best_score, best_move = self.timed_turn_loop()
        else:
            best_score, best_move = self.alphabeta_nega(self.color, -INF, INF, self.max_depth)
        turn_time = time() - start_time
        self.turn_time += turn_time
        self.board.place(best_move, self.color)
        if verbose > 0:
            print("AI took {:.4f} s to decide, visited {} states, and cut {} times".format(turn_time, self.no_nodes_searched, self.no_cuts))
            if self.use_tt:
                print("TT found {} full hits and {} half hits".format(self.tt_hits_full, self.tt_hits_half))
            print("Doing move: ", best_move, "With score:", best_score)

    def get_dijkstra_score(self, color):
        scores = np.array([[LOSE for i in range(self.board.size)] for j in range(self.board.size)])
        updated = np.array([[True for i in range(self.board.size)] for j in range(self.board.size)])
        alignment = (0, 1) if color == self.board.BLUE else (1, 0)
        for i in range(self.board.size):
            newcoord = tuple([i * j for j in alignment])
            updated[newcoord] = False
            if self.board.is_color(newcoord, color):
                scores[newcoord] = 0
            elif self.board.is_empty(newcoord):
                scores[newcoord] = 1
            else:
                scores[newcoord] = LOSE
        scores = self.dijkstra_update(color, scores, updated)
        results = [scores[alignment[0] * i - 1 + alignment[0]][alignment[1]*i - 1 + alignment[1]] for i in range(self.board.size)]
        best_result = min(results)
        log.debug("Best score for color {}: {}".format(color, best_result))
        return best_result

    def get_moves(self):
        return self.board.get_empty_cells()

    def alphabeta_nega(self, color, alpha, beta, depth):
        if self.turn_timer is not None and time() > self.turn_timer + self.max_time:
            return None, None
        best_move = None
        best_value = -INF
        if self.use_tt:
            hit, tt_move, tt_score = self.tt.lookup(depth, self.board.tostring())
            if hit == 1:
                self.tt_hits_half += 1
            elif hit == 2:
                self.tt_hits_full += 1
                log.debug("found move {} with score {}".format(tt_move, tt_score))
                return tt_score, tt_move
        if depth <= 0 or self.board.check_win(self.board.get_opposite_color(color)):
            best_value = self.eval(color)
            best_move = None
            return best_value, best_move
        else:
            self.no_nodes_searched += 1
            moves = self.get_moves()
            if self.use_tt and tt_move is not None:
                moves = [tt_move] + moves
            for move in moves:
                self.board.place(move, color)
                log.debug("Trying move {}".format(move))
                new_value, _ = self.alphabeta_nega(self.board.get_opposite_color(color), -beta, -alpha, depth-1)
                log.debug("try {} for color {}\tGot value: {}".format(move, color, new_value))
                if new_value is None:
                    self.board.take(move)
                    return best_value, best_move
                new_value = -new_value
                if new_value > best_value:
                    best_move = move
                    best_value = new_value
                self.board.take(move)
                alpha = max(alpha, best_value)
                if alpha >= beta:
                    self.no_cuts += 1
                    break
        if self.use_tt:
            assert best_move is not None
            assert best_value is not None
            self.tt.store(depth, self.board.tostring(), best_move, best_value)
        return best_value, best_move

if __name__ == "__main__":
    from hexai.hexboard import HexBoard
    logging.basicConfig(format='%(levelname)s:%(name)s: %(message)s',
                        level=logging.INFO)
    seed(42)
    board = HexBoard(5)
    player = AlphaBetaPlayer("dijkstra", use_id=False, use_tt=False, max_depth=1, color=HexBoard.BLUE)
    player.board = board
    board.place((0,3), HexBoard.BLUE)
    board.place((2,1), HexBoard.BLUE)
    board.place((1,2), HexBoard.BLUE)
    board.place((2,3), HexBoard.RED)
    board.place((2,4), HexBoard.RED)
    board.place((2,2), HexBoard.RED)
    board.place((3,0), HexBoard.RED)
    print(board)
    player.get_dijkstra_score(HexBoard.BLUE)