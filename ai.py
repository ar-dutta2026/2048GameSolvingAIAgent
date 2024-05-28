from __future__ import absolute_import, division, print_function
import copy, random
from game import Game

MOVES = {0: 'up', 1: 'left', 2: 'down', 3: 'right'}
MAX_PLAYER, CHANCE_PLAYER = 0, 1 

# Tree node. To be used to construct a game tree. 
class Node: 
    # Recommended: do not modify this __init__ function
    def __init__(self, state, player_type, monotonicity = 0, open_tiles = 0):
        self.state = (state[0], state[1])

        # to store a list of (direction, node) tuples
        self.children = []

        self.player_type = player_type
        self.monotonicity = monotonicity  # Store the monotonicity of the node
        self.open_tiles = open_tiles


    # returns whether this is a terminal state (i.e., no children)
    def is_terminal(self):
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
        if node is None:
            node = self.root

        # Check if the current depth has reached the search depth limit
        if depth < 0:
            return
        if node.player_type == MAX_PLAYER:
            for move_direction in range(0,4):

                self.simulator.set_state(copy.deepcopy(node.state[0]), node.state[1])

                if self.simulator.move(move_direction):

                    new_state = self.simulator.current_state()

                    child_node = Node(new_state, CHANCE_PLAYER)

                    node.children.append((move_direction, child_node))

                    self.build_tree(child_node, depth - 1)

        elif node.player_type == CHANCE_PLAYER:
            empty_tiles = self.simulator.get_open_tiles()
            for tile in empty_tiles:

                self.simulator.set_state(copy.deepcopy(node.state[0]), node.state[1])

                self.simulator.tile_matrix[tile[0]][tile[1]] = 2
                new_state = self.simulator.current_state()

                child_node = Node(new_state, MAX_PLAYER)

                node.children.append((None, child_node))

                self.build_tree(child_node, depth - 1)

    # TODO: expectimax calculation.
    # Return a (best direction, expectimax value) tuple if node is a MAX_PLAYER
    # Return a (None, expectimax value) tuple if node is a CHANCE_PLAYER
    def expectimax(self, node=None):
        if node is None:
            node = self.root

        if node.is_terminal():
            return None, node.state[1]

        if node.player_type == MAX_PLAYER:
            best_value = float('-inf')
            best_move = None
            for move, child in node.children:
                _, value = self.expectimax(child)
                if value > best_value:
                    best_value = value
                    best_move = move
            return best_move, best_value

        elif node.player_type == CHANCE_PLAYER:
            total_value = 0
            for _,child in node.children:
                move, value = self.expectimax(child)
                total_value += value
            average_value = total_value / len(node.children) if node.children else 0
            return None, average_value



    # Return decision at the root
    def compute_decision(self):
        self.build_tree(self.root, self.search_depth)
        direction, _ = self.expectimax(self.root)
        return direction


    def calculate_monotonicity(self, tile_matrix):
        rows = len(tile_matrix)
        cols = len(tile_matrix[0])
        monotonicity_up_down = 0
        monotonicity_left_right = 0

        for x in range(cols):
            current = 0
            next_tile = current + 1
            while next_tile < rows:
                while next_tile < rows and tile_matrix[next_tile][x] == 0:
                    next_tile += 1
                if next_tile >= rows:
                    next_tile -= 1
                current_value = tile_matrix[current][x]
                next_value = tile_matrix[next_tile][x]
                if current_value > next_value:
                    monotonicity_up_down += next_value - current_value
                elif current_value < next_value:
                    monotonicity_up_down += current_value - next_value
                current = next_tile
                next_tile += 1

        for x in range(rows):
            current = 0
            next_tile = current + 1
            while next_tile < cols:
                while next_tile < cols and tile_matrix[x][next_tile] == 0:
                    next_tile += 1
                if next_tile >= cols:
                    next_tile -= 1
                current_value = tile_matrix[x][current]
                next_value = tile_matrix[x][next_tile]
                if current_value > next_value:
                    monotonicity_left_right += next_value - current_value
                elif current_value < next_value:
                    monotonicity_left_right += current_value - next_value
                current = next_tile
                next_tile += 1
        return monotonicity_left_right + monotonicity_up_down


    def build_tree_ec(self, node=None, depth=0):
        if node is None:
            node = self.root

        if depth < 0:
            return

        if node.player_type == MAX_PLAYER:
            for move_direction in range(0, 4):
                self.simulator.set_state(copy.deepcopy(node.state[0]), node.state[1])
                if self.simulator.move(move_direction):
                    new_state = self.simulator.current_state()

                    monotonicity = self.calculate_monotonicity(new_state[0])
                    open_tiles = len(self.simulator.get_open_tiles())

                    child_node = Node(new_state, CHANCE_PLAYER, monotonicity, open_tiles)
                    node.children.append((move_direction, child_node))
                    self.build_tree(child_node, depth - 1)

        elif node.player_type == CHANCE_PLAYER:
            empty_tiles = self.simulator.get_open_tiles()
            for tile in empty_tiles:

                self.simulator.set_state(copy.deepcopy(node.state[0]), node.state[1])

                self.simulator.tile_matrix[tile[0]][tile[1]] = 2
                new_state = self.simulator.current_state()

                child_node = Node(new_state, MAX_PLAYER)

                node.children.append((None, child_node))

                self.build_tree(child_node, depth - 1)


    def expectimax_ec(self, node=None, depth=0):
        if node is None:
            node = self.root

        if node.is_terminal():
            
            return None, node.state[1]

        if node.player_type == MAX_PLAYER:
            best_value = float('-inf')
            best_move = None
            for move, child in node.children:
            # Incorporate smoothness into the evaluation of the node
                _, child_value = self.expectimax_ec(child, depth - 1)
                value_with_heuristic = child_value + child.open_tiles + child.monotonicity
                if value_with_heuristic > best_value:
                    best_value = value_with_heuristic
                    best_move = move
            return best_move, best_value

        elif node.player_type == CHANCE_PLAYER:
            total_value = 0
            for _, child in node.children:
                _, child_value = self.expectimax_ec(child, depth - 1)
                total_value += child_value 
            average_value = total_value / len(node.children) if node.children else 0
            return None, average_value



    # TODO (optional): implement method for extra credits
    def compute_decision_ec(self):
        self.build_tree_ec(self.root, self.search_depth)
        direction, _ = self.expectimax_ec(self.root)
        return direction
