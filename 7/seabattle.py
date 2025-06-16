#!/usr/bin/env python3
"""
Sea Battle CLI Game

A Python implementation of the classic Sea Battle (Battleship) game.
Enhanced for maximum readability and maintainability.

This module implements a complete battleship game with a clean, modular architecture
following SOLID principles and best practices for code organization.
"""

import random
import sys
from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Tuple, Optional, Dict

# Game Constants
DEFAULT_BOARD_SIZE = 10
DEFAULT_NUMBER_OF_SHIPS = 3
DEFAULT_SHIP_LENGTH = 3
MAX_SHIP_PLACEMENT_ATTEMPTS = 100

# Board Cell States
WATER_SYMBOL = '~'
SHIP_SYMBOL = 'S'
HIT_SYMBOL = 'X'
MISS_SYMBOL = 'O'

# Game Messages
MESSAGE_BOARDS_CREATED = 'Boards created.'
MESSAGE_PLAYER_HIT = 'PLAYER HIT!'
MESSAGE_PLAYER_MISS = 'PLAYER MISS.'
MESSAGE_CPU_HIT_TEMPLATE = 'CPU HIT at {location}!'
MESSAGE_CPU_MISS_TEMPLATE = 'CPU MISS at {location}.'
MESSAGE_CPU_TURN_HEADER = "\n--- CPU's Turn ---"
MESSAGE_CPU_TARGETS_TEMPLATE = 'CPU targets: {location}'
MESSAGE_SHIP_SUNK_BY_PLAYER = 'You sunk an enemy battleship!'
MESSAGE_SHIP_SUNK_BY_CPU = 'CPU sunk your battleship!'
MESSAGE_DUPLICATE_GUESS = 'You already guessed that location!'
MESSAGE_PLAYER_WINS = '\n*** CONGRATULATIONS! You sunk all enemy battleships! ***'
MESSAGE_CPU_WINS = '\n*** GAME OVER! The CPU sunk all your battleships! ***'
MESSAGE_EXIT_GAME = '\nThanks for playing!'
MESSAGE_SHIPS_PLACED_TEMPLATE = '{count} ships placed randomly for {player}.'
MESSAGE_GAME_START_TEMPLATE = "\nLet's play Sea Battle!\nTry to sink the {count} enemy ships."

# Input Validation Messages
ERROR_INVALID_INPUT_LENGTH = 'Oops, input must be exactly two digits (e.g., 00, 34, 98).'
ERROR_INVALID_COORDINATES_TEMPLATE = 'Oops, please enter valid row and column numbers between 0 and {max_coord}.'
INPUT_PROMPT = 'Enter your guess (e.g., 00): '

# Player Names
HUMAN_PLAYER_NAME = 'Player'
CPU_PLAYER_NAME = 'CPU'

# CPU Modes
CPU_MODE_HUNT = 'hunt'
CPU_MODE_TARGET = 'target'

# Ship Orientations
SHIP_ORIENTATION_HORIZONTAL = 'horizontal'
SHIP_ORIENTATION_VERTICAL = 'vertical'

# Hit Status
HIT_STATUS_EMPTY = ''
HIT_STATUS_HIT = 'hit'


class ShipOrientation(Enum):
    """Enumeration for ship placement orientations."""
    HORIZONTAL = SHIP_ORIENTATION_HORIZONTAL
    VERTICAL = SHIP_ORIENTATION_VERTICAL


class CPUMode(Enum):
    """Enumeration for CPU player behavior modes."""
    HUNT = CPU_MODE_HUNT
    TARGET = CPU_MODE_TARGET


class BoardPosition:
    """Represents a position on the game board with row and column coordinates."""
    
    def __init__(self, row: int, column: int):
        """Initialize a board position.
        
        Args:
            row: Zero-based row index
            column: Zero-based column index
        """
        self.row = row
        self.column = column
    
    def to_string_coordinate(self) -> str:
        """Convert position to string coordinate format (e.g., '23' for row 2, col 3)."""
        return f"{self.row}{self.column}"
    
    @classmethod
    def from_string_coordinate(cls, coordinate: str) -> 'BoardPosition':
        """Create BoardPosition from string coordinate.
        
        Args:
            coordinate: String coordinate like '23'
            
        Returns:
            BoardPosition instance
            
        Raises:
            ValueError: If coordinate format is invalid
        """
        if len(coordinate) != 2:
            raise ValueError(f"Invalid coordinate format: {coordinate}")
        
        try:
            row, column = int(coordinate[0]), int(coordinate[1])
            return cls(row, column)
        except ValueError as error:
            raise ValueError(f"Invalid coordinate format: {coordinate}") from error
    
    def get_adjacent_positions(self) -> List['BoardPosition']:
        """Get all adjacent positions (up, down, left, right)."""
        return [
            BoardPosition(self.row - 1, self.column),  # Up
            BoardPosition(self.row + 1, self.column),  # Down
            BoardPosition(self.row, self.column - 1),  # Left
            BoardPosition(self.row, self.column + 1),  # Right
        ]
    
    def __eq__(self, other) -> bool:
        """Check equality with another BoardPosition."""
        if not isinstance(other, BoardPosition):
            return False
        return self.row == other.row and self.column == other.column
    
    def __hash__(self) -> int:
        """Make BoardPosition hashable for use in sets and dictionaries."""
        return hash((self.row, self.column))
    
    def __str__(self) -> str:
        """String representation of the position."""
        return f"Position({self.row}, {self.column})"


class Ship:
    """Represents a naval ship with its positions and damage tracking.
    
    This class manages the state of a single ship, including its board positions
    and which parts have been hit by enemy attacks.
    """
    
    def __init__(self, board_positions: List[str]):
        """Initialize a ship with its board positions.
        
        Args:
            board_positions: List of string coordinates where the ship is placed
        """
        self._validate_positions(board_positions)
        self.positions = board_positions
        self.hit_status = [HIT_STATUS_EMPTY] * len(board_positions)
    
    def _validate_positions(self, positions: List[str]) -> None:
        """Validate that ship positions are valid."""
        if not positions:
            raise ValueError("Ship must have at least one position")
        
        for position in positions:
            if len(position) != 2 or not position.isdigit():
                raise ValueError(f"Invalid position format: {position}")
    
    def is_hit_at_position(self, target_position: str) -> bool:
        """Check if the ship has been hit at the specified position.
        
        Args:
            target_position: String coordinate to check
            
        Returns:
            True if ship is hit at this position, False otherwise
        """
        return (target_position in self.positions and 
                self.hit_status[self.positions.index(target_position)] == HIT_STATUS_HIT)
    
    def attempt_hit(self, target_position: str) -> bool:
        """Attempt to hit the ship at the specified position.
        
        Args:
            target_position: String coordinate of the attack
            
        Returns:
            True if hit was successful (position is part of ship and not already hit)
        """
        if target_position not in self.positions:
            return False
        
        position_index = self.positions.index(target_position)
        if self.hit_status[position_index] != HIT_STATUS_HIT:
            self.hit_status[position_index] = HIT_STATUS_HIT
            return True
        
        return False
    
    def is_completely_destroyed(self) -> bool:
        """Check if the ship has been completely destroyed.
        
        Returns:
            True if all ship positions have been hit
        """
        return all(status == HIT_STATUS_HIT for status in self.hit_status)
    
    def get_remaining_positions(self) -> List[str]:
        """Get list of ship positions that haven't been hit yet."""
        return [pos for pos, status in zip(self.positions, self.hit_status) 
                if status != HIT_STATUS_HIT]


class GameBoard:
    """Manages the game board state and naval operations.
    
    This class handles the game grid, ship placement, attack processing,
    and provides methods for querying board state.
    """
    
    def __init__(self, board_dimensions: int):
        """Initialize a square game board.
        
        Args:
            board_dimensions: Size of the square board (e.g., 10 for 10x10)
        """
        self.board_size = board_dimensions
        self.game_grid = self._create_empty_grid()
        self.deployed_ships: List[Ship] = []
    
    def _create_empty_grid(self) -> List[List[str]]:
        """Create an empty game grid filled with water symbols."""
        return [[WATER_SYMBOL for _ in range(self.board_size)] 
                for _ in range(self.board_size)]
    
    def is_position_within_bounds(self, board_position: BoardPosition) -> bool:
        """Check if a position is within the board boundaries.
        
        Args:
            board_position: Position to validate
            
        Returns:
            True if position is valid, False otherwise
        """
        return (0 <= board_position.row < self.board_size and 
                0 <= board_position.column < self.board_size)
    
    def get_cell_content(self, board_position: BoardPosition) -> str:
        """Get the content of a specific board cell.
        
        Args:
            board_position: Position to query
            
        Returns:
            Cell content or empty string if position is invalid
        """
        if self.is_position_within_bounds(board_position):
            return self.game_grid[board_position.row][board_position.column]
        return ''
    
    def update_cell_content(self, board_position: BoardPosition, new_content: str) -> None:
        """Update the content of a specific board cell.
        
        Args:
            board_position: Position to update
            new_content: New content for the cell
        """
        if self.is_position_within_bounds(board_position):
            self.game_grid[board_position.row][board_position.column] = new_content
    
    def deploy_ship(self, ship: Ship, make_visible: bool = False) -> None:
        """Deploy a ship to the board.
        
        Args:
            ship: Ship instance to deploy
            make_visible: Whether to show ship positions on the grid
        """
        self.deployed_ships.append(ship)
        
        if make_visible:
            for position_str in ship.positions:
                position = BoardPosition.from_string_coordinate(position_str)
                self.update_cell_content(position, SHIP_SYMBOL)
    
    def can_accommodate_ship(self, start_position: BoardPosition, ship_length: int, 
                           orientation: ShipOrientation) -> bool:
        """Check if a ship can be placed at the specified position and orientation.
        
        Args:
            start_position: Starting position for ship placement
            ship_length: Length of the ship to place
            orientation: Orientation of the ship
            
        Returns:
            True if ship can be placed without conflicts
        """
        ship_positions = self._calculate_ship_positions(start_position, ship_length, orientation)
        
        for position in ship_positions:
            if (not self.is_position_within_bounds(position) or
                self.get_cell_content(position) != WATER_SYMBOL):
                return False
        
        return True
    
    def _calculate_ship_positions(self, start_position: BoardPosition, ship_length: int,
                                orientation: ShipOrientation) -> List[BoardPosition]:
        """Calculate all positions a ship would occupy."""
        positions = []
        
        for i in range(ship_length):
            if orientation == ShipOrientation.HORIZONTAL:
                new_position = BoardPosition(start_position.row, start_position.column + i)
            else:  # VERTICAL
                new_position = BoardPosition(start_position.row + i, start_position.column)
            
            positions.append(new_position)
        
        return positions
    
    def place_ship_at_random_location(self, ship_length: int, make_visible: bool = False) -> bool:
        """Attempt to place a ship randomly on the board.
        
        Args:
            ship_length: Length of the ship to place
            make_visible: Whether to make the ship visible on the grid
            
        Returns:
            True if ship was successfully placed
        """
        for _ in range(MAX_SHIP_PLACEMENT_ATTEMPTS):
            orientation = random.choice(list(ShipOrientation))
            start_position = self._generate_random_start_position(ship_length, orientation)
            
            if self.can_accommodate_ship(start_position, ship_length, orientation):
                ship_positions = self._calculate_ship_positions(start_position, ship_length, orientation)
                position_strings = [pos.to_string_coordinate() for pos in ship_positions]
                
                new_ship = Ship(position_strings)
                self.deploy_ship(new_ship, make_visible)
                return True
        
        return False
    
    def _generate_random_start_position(self, ship_length: int, 
                                      orientation: ShipOrientation) -> BoardPosition:
        """Generate a random valid starting position for ship placement."""
        if orientation == ShipOrientation.HORIZONTAL:
            max_row = self.board_size - 1
            max_col = self.board_size - ship_length
        else:  # VERTICAL
            max_row = self.board_size - ship_length
            max_col = self.board_size - 1
        
        return BoardPosition(
            random.randint(0, max_row),
            random.randint(0, max_col)
        )
    
    def process_incoming_attack(self, target_coordinate: str) -> Tuple[bool, bool]:
        """Process an attack on the board.
        
        Args:
            target_coordinate: String coordinate of the attack
            
        Returns:
            Tuple of (hit_successful, ship_destroyed)
        """
        target_position = BoardPosition.from_string_coordinate(target_coordinate)
        
        for ship in self.deployed_ships:
            if ship.attempt_hit(target_coordinate):
                self.update_cell_content(target_position, HIT_SYMBOL)
                return True, ship.is_completely_destroyed()
        
        self.update_cell_content(target_position, MISS_SYMBOL)
        return False, False
    
    def count_remaining_ships(self) -> int:
        """Count the number of ships that are not completely destroyed."""
        return sum(1 for ship in self.deployed_ships if not ship.is_completely_destroyed())


class Player(ABC):
    """Abstract base class defining the player interface.
    
    This class establishes the contract that all player types must implement,
    ensuring consistent behavior across human and AI players.
    """
    
    def __init__(self, player_name: str, game_board: GameBoard):
        """Initialize a player with a name and associated game board.
        
        Args:
            player_name: Display name for the player
            game_board: The game board this player will attack
        """
        self.display_name = player_name
        self.target_board = game_board
        self.attack_history: List[str] = []
    
    @abstractmethod
    def generate_attack_coordinate(self) -> str:
        """Generate the next attack coordinate.
        
        This method must be implemented by all player subclasses.
        
        Returns:
            String coordinate for the next attack
        """
        pass
    
    def has_previously_attacked(self, target_coordinate: str) -> bool:
        """Check if this coordinate has been attacked before.
        
        Args:
            target_coordinate: Coordinate to check
            
        Returns:
            True if coordinate was previously attacked
        """
        return target_coordinate in self.attack_history
    
    def record_attack(self, attack_coordinate: str) -> None:
        """Record an attack in the player's history.
        
        Args:
            attack_coordinate: Coordinate that was attacked
        """
        if attack_coordinate not in self.attack_history:
            self.attack_history.append(attack_coordinate)


class HumanPlayer(Player):
    """Implementation of a human player.
    
    This player relies on external input handling rather than generating
    moves autonomously like the AI player.
    """
    
    def __init__(self, game_board: GameBoard):
        """Initialize human player.
        
        Args:
            game_board: The game board this player will attack
        """
        super().__init__(HUMAN_PLAYER_NAME, game_board)
    
    def generate_attack_coordinate(self) -> str:
        """Human players don't generate coordinates autonomously.
        
        Raises:
            NotImplementedError: Human input should be handled by InputHandler
        """
        raise NotImplementedError("Human player input should be handled by InputHandler")


class CPUPlayer(Player):
    """Implementation of a CPU player with intelligent targeting.
    
    This CPU player uses a two-mode strategy:
    - Hunt mode: Random searching for ships
    - Target mode: Systematic targeting of adjacent cells after a hit
    """
    
    def __init__(self, game_board: GameBoard):
        """Initialize CPU player.
        
        Args:        
            game_board: The game board this player will attack
        """
        super().__init__(CPU_PLAYER_NAME, game_board)
        self.current_cpu_mode = CPUMode.HUNT
        self.priority_target_queue: List[str] = []
    
    def generate_attack_coordinate(self) -> str:
        """Generate next attack coordinate using CPU strategy.
        
        Returns:
            String coordinate for next attack
        """
        if self._should_use_targeted_attack():
            return self._get_next_priority_target()
        
        return self._generate_random_attack()
    
    def _should_use_targeted_attack(self) -> bool:
        """Determine if CPU should use targeted attack mode."""
        return (self.current_cpu_mode == CPUMode.TARGET and 
                len(self.priority_target_queue) > 0)
    
    def _get_next_priority_target(self) -> str:
        """Get the next high-priority target from the queue."""
        while self.priority_target_queue:
            next_target = self.priority_target_queue.pop(0)
            if not self.has_previously_attacked(next_target):
                return next_target
        
        # No valid priority targets, switch to hunt mode
        self.current_cpu_mode = CPUMode.HUNT
        return self._generate_random_attack()
    
    def _generate_random_attack(self) -> str:
        """Generate a random attack coordinate that hasn't been used."""
        while True:
            random_position = BoardPosition(
                random.randint(0, self.target_board.board_size - 1),
                random.randint(0, self.target_board.board_size - 1)
            )
            attack_coordinate = random_position.to_string_coordinate()
            
            if not self.has_previously_attacked(attack_coordinate):
                return attack_coordinate
    
    def process_attack_outcome(self, attack_coordinate: str, was_hit: bool, 
                             ship_destroyed: bool) -> None:
        """Update CPU state based on attack results.
        
        Args:
            attack_coordinate: Coordinate that was attacked
            was_hit: Whether the attack hit a ship
            ship_destroyed: Whether the hit destroyed a ship completely
        """
        if was_hit and not ship_destroyed:
            self._switch_to_target_mode(attack_coordinate)
        elif ship_destroyed:
            self._switch_to_hunt_mode()
    
    def _switch_to_target_mode(self, hit_coordinate: str) -> None:
        """Switch to target mode and queue adjacent positions."""
        self.current_cpu_mode = CPUMode.TARGET
        hit_position = BoardPosition.from_string_coordinate(hit_coordinate)
        
        adjacent_positions = hit_position.get_adjacent_positions()
        for position in adjacent_positions:
            if (self.target_board.is_position_within_bounds(position) and
                not self.has_previously_attacked(position.to_string_coordinate())):
                
                target_coordinate = position.to_string_coordinate()
                if target_coordinate not in self.priority_target_queue:
                    self.priority_target_queue.append(target_coordinate)
    
    def _switch_to_hunt_mode(self) -> None:
        """Switch back to hunt mode and clear priority targets."""
        self.current_cpu_mode = CPUMode.HUNT
        self.priority_target_queue.clear()


class UserInterfaceDisplay:
    """Handles all user interface display operations.
    
    This class is responsible for rendering the game state to the console,
    including board visualization and user messages.
    """
    
    # Display formatting constants
    BOARD_HEADER_OPPONENT = '   --- OPPONENT BOARD ---'
    BOARD_HEADER_PLAYER = '--- YOUR BOARD ---'
    BOARD_SEPARATOR = '     '
    
    @staticmethod
    def render_game_boards(player_game_board: GameBoard, opponent_game_board: GameBoard) -> None:
        """Render both game boards side by side for display.
        
        Args:
            player_game_board: The human player's board
            opponent_game_board: The opponent's board (with ships hidden)
        """
        print(f"\n{UserInterfaceDisplay.BOARD_HEADER_OPPONENT}          {UserInterfaceDisplay.BOARD_HEADER_PLAYER}")
        
        # Generate and display column headers
        column_header = UserInterfaceDisplay._generate_column_header(player_game_board.board_size)
        print(f"{column_header}{UserInterfaceDisplay.BOARD_SEPARATOR}{column_header}")
        
        # Display each row of both boards
        for row_index in range(player_game_board.board_size):
            row_display = UserInterfaceDisplay._format_board_row(
                row_index, player_game_board, opponent_game_board
            )
            print(row_display)
        
        print()  # Add spacing after boards
    
    @staticmethod
    def _generate_column_header(board_size: int) -> str:
        """Generate column header with numbered columns."""
        header = "  "
        for column_index in range(board_size):
            header += f"{column_index} "
        return header
    
    @staticmethod
    def _format_board_row(row_index: int, player_board: GameBoard, 
                         opponent_board: GameBoard) -> str:
        """Format a single row showing both boards side by side."""
        row_display = f"{row_index} "
        
        # Add opponent board cells (hide ships)
        for column_index in range(opponent_board.board_size):
            position = BoardPosition(row_index, column_index)
            cell_content = opponent_board.get_cell_content(position)
            display_content = cell_content if cell_content in [HIT_SYMBOL, MISS_SYMBOL] else WATER_SYMBOL
            row_display += f"{display_content} "
        
        row_display += f"{UserInterfaceDisplay.BOARD_SEPARATOR}{row_index} "
        
        # Add player board cells (show ships)
        for column_index in range(player_board.board_size):
            position = BoardPosition(row_index, column_index)
            cell_content = player_board.get_cell_content(position)
            row_display += f"{cell_content} "
        
        return row_display
    
    @staticmethod
    def display_message(message_text: str) -> None:
        """Display a message to the user.
        
        Args:
            message_text: Text message to display
        """
        print(message_text)
    
    @staticmethod
    def show_game_over_message(winning_player: str) -> None:
        """Display the appropriate game over message.
        
        Args:
            winning_player: Name of the winning player
        """
        if winning_player == HUMAN_PLAYER_NAME:
            print(MESSAGE_PLAYER_WINS)
        else:
            print(MESSAGE_CPU_WINS)


class UserInputProcessor:
    """Handles user input validation and processing.
    
    This class manages all user input operations, including validation
    and error handling for coordinate entry.
    """
    
    def __init__(self, maximum_board_coordinate: int):
        """Initialize input processor with board size constraints.
        
        Args:
            maximum_board_coordinate: Maximum valid coordinate value (board_size - 1)
        """
        self.max_coordinate_value = maximum_board_coordinate
    
    def request_player_move(self) -> Optional[str]:
        """Request and validate a move from the human player.
        
        Returns:
            Valid coordinate string, or None if input was invalid
        """
        try:
            user_input = input(INPUT_PROMPT).strip()
            return self._validate_coordinate_input(user_input)
        except (KeyboardInterrupt, EOFError):
            print(MESSAGE_EXIT_GAME)
            sys.exit(0)
    
    def _validate_coordinate_input(self, coordinate_input: str) -> Optional[str]:
        """Validate user coordinate input.
        
        Args:
            coordinate_input: Raw input from user
            
        Returns:
            Valid coordinate string, or None if invalid
        """
        if not self._is_valid_input_format(coordinate_input):
            return None
        
        if not self._are_coordinates_in_bounds(coordinate_input):
            return None
        
        return coordinate_input
    
    def _is_valid_input_format(self, input_string: str) -> bool:
        """Check if input has correct format (exactly 2 digits)."""
        if not input_string or len(input_string) != 2:
            print(ERROR_INVALID_INPUT_LENGTH)
            return False
        
        try:
            int(input_string[0])
            int(input_string[1])
            return True
        except ValueError:
            print(ERROR_INVALID_COORDINATES_TEMPLATE.format(max_coord=self.max_coordinate_value))
            return False
    
    def _are_coordinates_in_bounds(self, coordinate_string: str) -> bool:
        """Check if coordinates are within valid board boundaries."""
        try:
            row, column = int(coordinate_string[0]), int(coordinate_string[1])
            
            if (row < 0 or row > self.max_coordinate_value or 
                column < 0 or column > self.max_coordinate_value):
                print(ERROR_INVALID_COORDINATES_TEMPLATE.format(max_coord=self.max_coordinate_value))
                return False
            
            return True
        except ValueError:
            print(ERROR_INVALID_COORDINATES_TEMPLATE.format(max_coord=self.max_coordinate_value))
            return False


class GameRulesEngine:
    """Core game logic and rule enforcement.
    
    This class manages the fundamental game mechanics, including setup,
    turn processing, and win condition checking.
    """
    
    def __init__(self, board_dimensions: int = DEFAULT_BOARD_SIZE, 
                 fleet_size: int = DEFAULT_NUMBER_OF_SHIPS, 
                 vessel_length: int = DEFAULT_SHIP_LENGTH):
        """Initialize the game rules engine.
        
        Args:
            board_dimensions: Size of the game board
            fleet_size: Number of ships per player
            vessel_length: Length of each ship
        """
        self.board_dimensions = board_dimensions
        self.ships_per_player = fleet_size
        self.individual_ship_length = vessel_length
        
        # Initialize game boards
        self.human_player_board = GameBoard(board_dimensions)
        self.computer_player_board = GameBoard(board_dimensions)
        
        # Initialize players
        self.human_combatant = HumanPlayer(self.human_player_board)
        self.artificial_intelligence_opponent = CPUPlayer(self.computer_player_board)
    
    def initialize_game_state(self) -> None:
        """Set up the initial game state by deploying ships."""
        print(MESSAGE_BOARDS_CREATED)
        
        # Deploy human player's fleet
        self._deploy_player_fleet(
            self.human_player_board, 
            HUMAN_PLAYER_NAME, 
            make_ships_visible=True
        )
        
        # Deploy computer player's fleet
        self._deploy_player_fleet(
            self.computer_player_board, 
            CPU_PLAYER_NAME, 
            make_ships_visible=False
        )
    
    def _deploy_player_fleet(self, target_board: GameBoard, player_identifier: str, 
                           make_ships_visible: bool) -> None:
        """Deploy a complete fleet for a player.
        
        Args:
            target_board: Board to deploy ships on
            player_identifier: Name of the player for messaging
            make_ships_visible: Whether ships should be visible on the board
        """
        successful_deployments = 0
        
        while successful_deployments < self.ships_per_player:
            if target_board.place_ship_at_random_location(
                self.individual_ship_length, 
                make_ships_visible
            ):
                successful_deployments += 1
        
        print(MESSAGE_SHIPS_PLACED_TEMPLATE.format(
            count=self.ships_per_player, 
            player=player_identifier
        ))
    
    def execute_human_player_attack(self, target_coordinate: str) -> bool:
        """Process an attack by the human player.
        
        Args:
            target_coordinate: Coordinate string for the attack
            
        Returns:
            True if the attack was valid and processed
        """
        if self.human_combatant.has_previously_attacked(target_coordinate):
            print(MESSAGE_DUPLICATE_GUESS)
            return False
        
        self.human_combatant.record_attack(target_coordinate)
        attack_hit, target_destroyed = self.computer_player_board.process_incoming_attack(target_coordinate)
        
        if attack_hit:
            print(MESSAGE_PLAYER_HIT)
            if target_destroyed:
                print(MESSAGE_SHIP_SUNK_BY_PLAYER)
        else:
            print(MESSAGE_PLAYER_MISS)
        
        return True
    
    def execute_computer_player_attack(self) -> None:
        """Process an attack by the computer player."""
        print(MESSAGE_CPU_TURN_HEADER)
        
        attack_coordinate = self.artificial_intelligence_opponent.generate_attack_coordinate()
        
        if self.artificial_intelligence_opponent.current_cpu_mode == CPUMode.TARGET:
            print(MESSAGE_CPU_TARGETS_TEMPLATE.format(location=attack_coordinate))
        
        self.artificial_intelligence_opponent.record_attack(attack_coordinate)
        attack_successful, ship_eliminated = self.human_player_board.process_incoming_attack(attack_coordinate)
        
        if attack_successful:
            print(MESSAGE_CPU_HIT_TEMPLATE.format(location=attack_coordinate))
            if ship_eliminated:
                print(MESSAGE_SHIP_SUNK_BY_CPU)
        else:
            print(MESSAGE_CPU_MISS_TEMPLATE.format(location=attack_coordinate))
        
        self.artificial_intelligence_opponent.process_attack_outcome(
            attack_coordinate, attack_successful, ship_eliminated
        )
    
    def determine_game_winner(self) -> Optional[str]:
        """Check if the game has ended and determine the winner.
        
        Returns:
            Winner's name, or None if game continues
        """
        if self.computer_player_board.count_remaining_ships() == 0:
            return HUMAN_PLAYER_NAME
        elif self.human_player_board.count_remaining_ships() == 0:
            return CPU_PLAYER_NAME
        
        return None


class GameOrchestrator:
    """Main game controller that coordinates all game components.
    
    This class serves as the central coordinator, managing the flow between
    different game systems and handling the main game loop.
    """
    
    def __init__(self, board_dimensions: int = DEFAULT_BOARD_SIZE, 
                 fleet_size: int = DEFAULT_NUMBER_OF_SHIPS, 
                 vessel_length: int = DEFAULT_SHIP_LENGTH):
        """Initialize the game orchestrator with specified parameters.
        
        Args:
            board_dimensions: Size of the game board
            fleet_size: Number of ships per player  
            vessel_length: Length of each ship
        """
        self.game_rules = GameRulesEngine(board_dimensions, fleet_size, vessel_length)
        self.user_interface = UserInterfaceDisplay()
        self.input_processor = UserInputProcessor(board_dimensions - 1)
        
        # Store configuration for easy access
        self.total_enemy_ships = fleet_size
    
    def commence_game_session(self) -> None:
        """Start and manage the complete game session."""
        self.game_rules.initialize_game_state()
        
        welcome_message = MESSAGE_GAME_START_TEMPLATE.format(count=self.total_enemy_ships)
        print(welcome_message)
        
        self._execute_main_game_loop()
    
    def _execute_main_game_loop(self) -> None:
        """Execute the main game loop until completion."""
        while True:
            # Check for game completion
            game_winner = self.game_rules.determine_game_winner()
            if game_winner:
                self._handle_game_completion(game_winner)
                return
            
            # Display current game state
            self.user_interface.render_game_boards(
                self.game_rules.human_player_board,
                self.game_rules.computer_player_board
            )
            
            # Process human player turn
            self._process_human_player_turn()
            
            # Check if human player won
            if self.game_rules.determine_game_winner():
                continue
            
            # Process computer player turn
            self.game_rules.execute_computer_player_attack()
    
    def _process_human_player_turn(self) -> None:
        """Handle the human player's turn with input validation."""
        while True:
            player_move = self.input_processor.request_player_move()
            if player_move and self.game_rules.execute_human_player_attack(player_move):
                break
    
    def _handle_game_completion(self, winner_name: str) -> None:
        """Handle the end of the game.
        
        Args:
            winner_name: Name of the winning player
        """
        self.user_interface.show_game_over_message(winner_name)
        self.user_interface.render_game_boards(
            self.game_rules.human_player_board,
            self.game_rules.computer_player_board
        )


def initialize_and_run_game() -> None:
    """Initialize and run a complete game session.
    
    This is the main entry point for starting a new battleship game.
    """
    game_orchestrator = GameOrchestrator()
    game_orchestrator.commence_game_session()


if __name__ == "__main__":
    initialize_and_run_game() 