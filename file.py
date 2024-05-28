from __future__ import absolute_import, division, print_function
import copy, random
from game import Game

MOVES = {0: 'up', 1: 'left', 2: 'down', 3: 'right'}
MAX_PLAYER, CHANCE_PLAYER = 0, 1 

# Tree node. To be used to construct a game tree. 
class Node: 
    # Recommended: do not modify this __init__ function
    def __init__(self, state, player_type):
        self.state = (state[0], state[1])

        # to store a list of (direction, node) tuples
        self.children = []

        self.player_type = player_type
        self.preplacement = 4

    # returns whether this is a terminal state (i.e., no children)
    def is_terminal(self):
        #TODO: complete this
        return len(self.children) == 0


        

# AI agent. Determine the next move.
class AI:
    # Recommended: do not modify this __init__ function
    def __init__(self, root_state, search_depth=3): 
        self.root = Node(root_state, MAX_PLAYER)
        self.search_depth = search_depth
        self.simulator = Game(*root_state)

    # (Hint) Useful functions: 
    # self.simulator.current_state, self.simulator.set_state, self.simulator.move

    # TODO: build a game tree from the current node up to the given depth
    def build_tree(self, node=None, depth=0):
        if depth == 0 or (depth == 1 and node.player_type == CHANCE_PLAYER):
            return

        self.simulator.set_state(*node.state)
        if node.player_type == MAX_PLAYER:
            for move, moves_name in MOVES.items():
                if self.simulator.move(move):
                    if depth == 1:
                        # At depth 1, after MAX_PLAYER moves, it's a leaf node
                        new_state = self.simulator.current_state()
                        child_node = Node(new_state, None)
                        node.children.append((move, child_node))
                    else:
                        # Otherwise, we simulate the CHANCE_PLAYER's random tile placement
                        for pos in self.simulator.get_open_tiles():
                            self.simulator.tile_matrix[pos[0]][pos[1]] = 2
                            new_state = self.simulator.current_state()
                            child_node = Node(new_state, CHANCE_PLAYER)
                            node.children.append((move, child_node))
                            # Undo the tile placement for the next simulation
                            self.simulator.tile_matrix[pos[0]][pos[1]] = 0
                    # Undo the move to restore the state for the next move simulation
                    self.simulator.undo()
                

    # TODO: expectimax calculation.
    # Return a (best direction, expectimax value) tuple if node is a MAX_PLAYER
    # Return a (None, expectimax value) tuple if node is a CHANCE_PLAYER
    def expectimax(self, node):
        if node.is_terminal():
            # Terminal nodes are leaf nodes at depth 3, return their score
            return None, node.state[1]  # (None, score)
        best_move = None
        if node.player_type == MAX_PLAYER:
            max_value = float('-inf')
            for move, child in node.children:
                _, value = self.expectimax(child)
                if value > max_value:
                    max_value = value
                    best_move = move
            return best_move, max_value
        else:  # CHANCE_PLAYER
            total_value = 0
            num_children = len(node.children)
            for _, child in node.children:
                _, value = self.expectimax(child)
                total_value += value
            # Average the value over all possible chance moves
            return None, total_value / num_children
        

    # Return decision at the root
    def compute_decision(self):
        self.build_tree(self.root, self.search_depth)
        direction, _ = self.expectimax(self.root)
        return direction

    # TODO (optional): implement method for extra credits
    def compute_decision_ec(self):
        return random.randint(0, 3)

