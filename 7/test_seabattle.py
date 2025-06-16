#!/usr/bin/env python3
"""
Unit tests for the Sea Battle game using pytest.

This module contains comprehensive unit tests for all components of the
Sea Battle game, ensuring proper functionality and meaningful test coverage
of core logic modules.
"""

import pytest
from unittest.mock import patch, MagicMock
import sys
import random
from seabattle import (
    Ship, GameBoard, HumanPlayer, CPUPlayer, UserInterfaceDisplay, 
    UserInputProcessor, GameRulesEngine, GameOrchestrator,
    BoardPosition, ShipOrientation, CPUMode
)


# Test fixtures
@pytest.fixture
def board_position():
    """Fixture for creating a board position."""
    return BoardPosition(1, 2)

@pytest.fixture
def ship():
    """Fixture for creating a ship."""
    return Ship(['00', '01', '02'])

@pytest.fixture
def game_board():
    """Fixture for creating a game board."""
    return GameBoard(5)

@pytest.fixture
def human_player():
    """Fixture for creating a human player."""
    board = GameBoard(10)
    return HumanPlayer(board)

@pytest.fixture
def cpu_player():
    """Fixture for creating a CPU player."""
    board = GameBoard(10)
    return CPUPlayer(board)

@pytest.fixture
def ui_display():
    """Fixture for creating UI display."""
    return UserInterfaceDisplay()

@pytest.fixture
def input_processor():
    """Fixture for creating input processor."""
    return UserInputProcessor(9)  # max_coordinate_value = board_size - 1

@pytest.fixture
def game_rules():
    """Fixture for creating game rules engine."""
    return GameRulesEngine()

@pytest.fixture
def game_orchestrator():
    """Fixture for creating game orchestrator."""
    return GameOrchestrator()


# BoardPosition tests
def test_board_position_init(board_position):
    """Test BoardPosition initialization."""
    assert board_position.row == 1
    assert board_position.column == 2

def test_board_position_to_string_coordinate(board_position):
    """Test converting position to string coordinate."""
    assert board_position.to_string_coordinate() == '12'

def test_board_position_from_string_coordinate():
    """Test creating position from string coordinate."""
    pos = BoardPosition.from_string_coordinate('34')
    assert pos.row == 3
    assert pos.column == 4

def test_board_position_from_string_coordinate_invalid():
    """Test creating position from invalid string coordinate."""
    with pytest.raises(ValueError):
        BoardPosition.from_string_coordinate('1')
    
    with pytest.raises(ValueError):
        BoardPosition.from_string_coordinate('ab')

def test_board_position_get_adjacent_positions(board_position):
    """Test getting adjacent positions."""
    pos = BoardPosition(1, 1)
    adjacent = pos.get_adjacent_positions()
    
    expected = [
        BoardPosition(0, 1),  # Up
        BoardPosition(2, 1),  # Down
        BoardPosition(1, 0),  # Left
        BoardPosition(1, 2),  # Right
    ]
    
    assert len(adjacent) == 4
    for expected_pos in expected:
        assert expected_pos in adjacent

def test_board_position_equality():
    """Test position equality."""
    pos1 = BoardPosition(1, 2)
    pos2 = BoardPosition(1, 2)
    pos3 = BoardPosition(2, 1)
    
    assert pos1 == pos2
    assert pos1 != pos3
    assert pos1 != "not a position"

def test_board_position_hash():
    """Test position hashing."""
    pos1 = BoardPosition(1, 2)
    pos2 = BoardPosition(1, 2)
    pos3 = BoardPosition(2, 1)
    
    assert hash(pos1) == hash(pos2)
    assert hash(pos1) != hash(pos3)


# Ship tests - Core Logic Module
def test_ship_init(ship):
    """Test ship initialization."""
    assert ship.positions == ['00', '01', '02']
    assert len(ship.hit_status) == 3
    assert all(status == '' for status in ship.hit_status)

def test_ship_init_validation():
    """Test ship initialization validation."""
    with pytest.raises(ValueError):
        Ship([])  # Empty positions
    
    with pytest.raises(ValueError):
        Ship(['0'])  # Invalid position format
    
    with pytest.raises(ValueError):
        Ship(['ab'])  # Non-digit position

def test_ship_is_hit_at_position(ship):
    """Test checking if ship is hit at position."""
    assert not ship.is_hit_at_position('00')
    ship.attempt_hit('00')
    assert ship.is_hit_at_position('00')
    assert not ship.is_hit_at_position('01')

def test_ship_attempt_hit(ship):
    """Test attempting to hit ship."""
    # Valid hit
    assert ship.attempt_hit('00')
    assert ship.is_hit_at_position('00')
    
    # Duplicate hit
    assert not ship.attempt_hit('00')
    
    # Invalid position
    assert not ship.attempt_hit('99')

def test_ship_is_completely_destroyed(ship):
    """Test checking if ship is completely destroyed."""
    assert not ship.is_completely_destroyed()
    
    ship.attempt_hit('00')
    ship.attempt_hit('01')
    assert not ship.is_completely_destroyed()
    
    ship.attempt_hit('02')
    assert ship.is_completely_destroyed()

def test_ship_get_remaining_positions(ship):
    """Test getting remaining positions."""
    remaining = ship.get_remaining_positions()
    assert remaining == ['00', '01', '02']
    
    ship.attempt_hit('00')
    remaining = ship.get_remaining_positions()
    assert remaining == ['01', '02']


# GameBoard tests - Core Logic Module
def test_game_board_init(game_board):
    """Test board initialization."""
    assert game_board.board_size == 5
    assert len(game_board.game_grid) == 5
    assert len(game_board.game_grid[0]) == 5
    assert len(game_board.deployed_ships) == 0
    
    # Check all cells are water
    for row in game_board.game_grid:
        for cell in row:
            assert cell == '~'

def test_game_board_is_position_within_bounds(game_board):
    """Test coordinate validation."""
    assert game_board.is_position_within_bounds(BoardPosition(0, 0))
    assert game_board.is_position_within_bounds(BoardPosition(4, 4))
    assert not game_board.is_position_within_bounds(BoardPosition(-1, 0))
    assert not game_board.is_position_within_bounds(BoardPosition(0, -1))
    assert not game_board.is_position_within_bounds(BoardPosition(5, 0))
    assert not game_board.is_position_within_bounds(BoardPosition(0, 5))

def test_game_board_get_set_cell_content(game_board):
    """Test getting and setting cell content."""
    pos = BoardPosition(1, 1)
    assert game_board.get_cell_content(pos) == '~'
    
    game_board.update_cell_content(pos, 'X')
    assert game_board.get_cell_content(pos) == 'X'
    
    # Test invalid position
    invalid_pos = BoardPosition(-1, -1)
    assert game_board.get_cell_content(invalid_pos) == ''

def test_game_board_deploy_ship(game_board):
    """Test deploying ship."""
    ship = Ship(['11', '12'])
    game_board.deploy_ship(ship, make_visible=True)
    
    assert len(game_board.deployed_ships) == 1
    assert game_board.get_cell_content(BoardPosition(1, 1)) == 'S'
    assert game_board.get_cell_content(BoardPosition(1, 2)) == 'S'

def test_game_board_can_accommodate_ship(game_board):
    """Test checking if ship can be placed."""
    start_pos = BoardPosition(0, 0)
    
    # Valid placement
    assert game_board.can_accommodate_ship(start_pos, 3, ShipOrientation.HORIZONTAL)
    assert game_board.can_accommodate_ship(start_pos, 3, ShipOrientation.VERTICAL)
    
    # Invalid placement - out of bounds
    assert not game_board.can_accommodate_ship(BoardPosition(0, 3), 3, ShipOrientation.HORIZONTAL)
    assert not game_board.can_accommodate_ship(BoardPosition(3, 0), 3, ShipOrientation.VERTICAL)

def test_game_board_calculate_ship_positions(game_board):
    """Test calculating ship positions."""
    start_pos = BoardPosition(0, 0)
    
    # Horizontal placement
    positions = game_board._calculate_ship_positions(start_pos, 3, ShipOrientation.HORIZONTAL)
    expected = [BoardPosition(0, 0), BoardPosition(0, 1), BoardPosition(0, 2)]
    assert positions == expected
    
    # Vertical placement
    positions = game_board._calculate_ship_positions(start_pos, 3, ShipOrientation.VERTICAL)
    expected = [BoardPosition(0, 0), BoardPosition(1, 0), BoardPosition(2, 0)]
    assert positions == expected

def test_game_board_place_ship_at_random_location(game_board):
    """Test placing ship at random location."""
    success = game_board.place_ship_at_random_location(3, make_visible=True)
    assert success
    assert len(game_board.deployed_ships) == 1

def test_game_board_process_incoming_attack(game_board):
    """Test processing incoming attacks."""
    # Deploy a ship
    ship = Ship(['11', '12'])
    game_board.deploy_ship(ship, make_visible=True)
    
    # Test hit
    hit, destroyed = game_board.process_incoming_attack('11')
    assert hit
    assert not destroyed  # Ship not completely destroyed yet
    assert game_board.get_cell_content(BoardPosition(1, 1)) == 'X'
    
    # Test miss
    hit, destroyed = game_board.process_incoming_attack('00')
    assert not hit
    assert not destroyed
    assert game_board.get_cell_content(BoardPosition(0, 0)) == 'O'
    
    # Destroy the ship
    hit, destroyed = game_board.process_incoming_attack('12')
    assert hit
    assert destroyed

def test_game_board_count_remaining_ships(game_board):
    """Test counting remaining ships."""
    # No ships initially
    assert game_board.count_remaining_ships() == 0
    
    # Add ships
    ship1 = Ship(['11', '12'])
    ship2 = Ship(['33', '34'])
    game_board.deploy_ship(ship1, make_visible=True)
    game_board.deploy_ship(ship2, make_visible=True)
    
    assert game_board.count_remaining_ships() == 2
    
    # Destroy one ship
    ship1.attempt_hit('11')
    ship1.attempt_hit('12')
    assert game_board.count_remaining_ships() == 1


# HumanPlayer tests
def test_human_player_init(human_player):
    """Test human player initialization."""
    assert human_player.display_name == "Player"
    assert human_player.target_board is not None
    assert human_player.attack_history == []

def test_human_player_generate_attack_coordinate_raises_error(human_player):
    """Test that human player throws error when trying to generate coordinate."""
    with pytest.raises(NotImplementedError):
        human_player.generate_attack_coordinate()

def test_human_player_has_previously_attacked(human_player):
    """Test checking if coordinate was previously attacked."""
    assert not human_player.has_previously_attacked('00')
    human_player.record_attack('00')
    assert human_player.has_previously_attacked('00')


# CPUPlayer tests - Core Logic Module
def test_cpu_player_init(cpu_player):
    """Test CPU player initialization."""
    assert cpu_player.display_name == "CPU"
    assert cpu_player.current_cpu_mode == CPUMode.HUNT
    assert len(cpu_player.priority_target_queue) == 0

def test_cpu_player_generate_attack_coordinate_hunt_mode(cpu_player):
    """Test CPU coordinate generation in hunt mode."""
    coord = cpu_player.generate_attack_coordinate()
    assert len(coord) == 2
    assert coord.isdigit()

def test_cpu_player_generate_attack_coordinate_target_mode(cpu_player):
    """Test CPU coordinate generation in target mode."""
    cpu_player.current_cpu_mode = CPUMode.TARGET
    cpu_player.priority_target_queue = ['54', '56', '45', '65']
    
    coord = cpu_player.generate_attack_coordinate()
    assert coord in ['54', '56', '45', '65']

def test_cpu_player_process_attack_outcome_hit_not_destroyed(cpu_player):
    """Test processing attack outcome when hit but not destroyed."""
    cpu_player.process_attack_outcome('55', True, False)
    
    assert cpu_player.current_cpu_mode == CPUMode.TARGET
    assert len(cpu_player.priority_target_queue) > 0

def test_cpu_player_process_attack_outcome_destroyed(cpu_player):
    """Test processing attack outcome when ship is destroyed."""
    cpu_player.current_cpu_mode = CPUMode.TARGET
    cpu_player.priority_target_queue = ['54', '56']
    
    cpu_player.process_attack_outcome('55', True, True)
    
    assert cpu_player.current_cpu_mode == CPUMode.HUNT
    assert len(cpu_player.priority_target_queue) == 0


# UserInterfaceDisplay tests
@patch('builtins.print')
def test_ui_display_render_game_boards(mock_print, ui_display):
    """Test rendering game boards."""
    board1 = GameBoard(3)
    board2 = GameBoard(3)
    ui_display.render_game_boards(board1, board2)
    assert mock_print.called

@patch('builtins.print')
def test_ui_display_display_message(mock_print, ui_display):
    """Test displaying message."""
    ui_display.display_message("Test message")
    mock_print.assert_called_with("Test message")

@patch('builtins.print')
def test_ui_display_show_game_over_message_player_wins(mock_print, ui_display):
    """Test showing game over message when player wins."""
    ui_display.show_game_over_message("Player")
    mock_print.assert_called_with('\n*** CONGRATULATIONS! You sunk all enemy battleships! ***')

@patch('builtins.print')
def test_ui_display_show_game_over_message_cpu_wins(mock_print, ui_display):
    """Test showing game over message when CPU wins."""
    ui_display.show_game_over_message("CPU")
    mock_print.assert_called_with('\n*** GAME OVER! The CPU sunk all your battleships! ***')


# UserInputProcessor tests
def test_input_processor_init(input_processor):
    """Test input processor initialization."""
    assert input_processor.max_coordinate_value == 9

@patch('builtins.input', return_value='12')
def test_input_processor_request_player_move_valid(mock_input, input_processor):
    """Test requesting valid player move."""
    move = input_processor.request_player_move()
    assert move == '12'

@patch('builtins.input', return_value='1')
@patch('builtins.print')
def test_input_processor_request_player_move_invalid_length(mock_print, mock_input, input_processor):
    """Test requesting player move with invalid length."""
    move = input_processor.request_player_move()
    assert move is None
    mock_print.assert_called()

@patch('builtins.input', return_value='ab')
@patch('builtins.print')
def test_input_processor_request_player_move_invalid_format(mock_print, mock_input, input_processor):
    """Test requesting player move with invalid format."""
    move = input_processor.request_player_move()
    assert move is None
    mock_print.assert_called()

@patch('builtins.input', return_value='aa')
@patch('builtins.print')
def test_input_processor_request_player_move_out_of_bounds(mock_print, mock_input, input_processor):
    """Test requesting player move out of bounds."""
    move = input_processor.request_player_move()
    assert move is None
    mock_print.assert_called()

@patch('builtins.input', side_effect=KeyboardInterrupt())
@patch('builtins.print')
@patch('sys.exit')
def test_input_processor_request_player_move_keyboard_interrupt(mock_exit, mock_print, mock_input, input_processor):
    """Test handling keyboard interrupt."""
    input_processor.request_player_move()
    mock_exit.assert_called_once_with(0)


# GameRulesEngine tests - Core Logic Module
def test_game_rules_engine_init(game_rules):
    """Test game rules engine initialization."""
    assert game_rules.human_player_board is not None
    assert game_rules.computer_player_board is not None
    assert game_rules.human_combatant is not None
    assert game_rules.artificial_intelligence_opponent is not None
    assert game_rules.board_dimensions == 10
    assert game_rules.ships_per_player == 3
    assert game_rules.individual_ship_length == 3

@patch('builtins.print')
def test_game_rules_engine_initialize_game_state(mock_print, game_rules):
    """Test initializing game state."""
    game_rules.initialize_game_state()
    
    # Check that ships are placed
    assert len(game_rules.human_player_board.deployed_ships) == 3
    assert len(game_rules.computer_player_board.deployed_ships) == 3

@patch('builtins.print')
def test_game_rules_engine_execute_human_player_attack_valid(mock_print, game_rules):
    """Test executing valid human player attack."""
    game_rules.initialize_game_state()
    
    # Test valid attack
    result = game_rules.execute_human_player_attack('00')
    assert result
    assert '00' in game_rules.human_combatant.attack_history

@patch('builtins.print')
def test_game_rules_engine_execute_human_player_attack_duplicate(mock_print, game_rules):
    """Test executing duplicate human player attack."""
    game_rules.initialize_game_state()
    
    # First attack
    game_rules.execute_human_player_attack('00')
    
    # Duplicate attack
    result = game_rules.execute_human_player_attack('00')
    assert not result

@patch('builtins.print')
def test_game_rules_engine_execute_computer_player_attack(mock_print, game_rules):
    """Test executing computer player attack."""
    game_rules.initialize_game_state()
    
    initial_history_length = len(game_rules.artificial_intelligence_opponent.attack_history)
    game_rules.execute_computer_player_attack()
    
    # Check that attack was recorded
    assert len(game_rules.artificial_intelligence_opponent.attack_history) == initial_history_length + 1

def test_game_rules_engine_determine_game_winner(game_rules):
    """Test determining game winner."""
    game_rules.initialize_game_state()
    
    # No winner initially
    winner = game_rules.determine_game_winner()
    assert winner is None
    
    # Simulate human player winning by destroying all computer ships
    for ship in game_rules.computer_player_board.deployed_ships:
        for pos in ship.positions:
            ship.attempt_hit(pos)
    
    winner = game_rules.determine_game_winner()
    assert winner == 'Player'
    
    # Reset and simulate CPU winning
    game_rules.initialize_game_state()
    for ship in game_rules.human_player_board.deployed_ships:
        for pos in ship.positions:
            ship.attempt_hit(pos)
    
    winner = game_rules.determine_game_winner()
    assert winner == 'CPU'


# GameOrchestrator tests
def test_game_orchestrator_init(game_orchestrator):
    """Test game orchestrator initialization."""
    assert game_orchestrator.game_rules is not None
    assert game_orchestrator.user_interface is not None
    assert game_orchestrator.input_processor is not None
    assert game_orchestrator.total_enemy_ships == 3

@patch('builtins.print')
def test_game_orchestrator_commence_game_session(mock_print, game_orchestrator):
    """Test commencing game session."""
    with patch.object(game_orchestrator, '_execute_main_game_loop'):
        game_orchestrator.commence_game_session()
        mock_print.assert_called()

@patch.object(UserInterfaceDisplay, 'render_game_boards')
@patch.object(UserInterfaceDisplay, 'show_game_over_message')
def test_game_orchestrator_main_game_loop_player_wins(mock_game_over, mock_boards, game_orchestrator):
    """Test main game loop when player wins."""
    game_orchestrator.game_rules.initialize_game_state()
    
    with patch.object(game_orchestrator.game_rules, 'determine_game_winner', return_value='Player'):
        game_orchestrator._execute_main_game_loop()
        mock_game_over.assert_called_with('Player')

@patch.object(UserInterfaceDisplay, 'render_game_boards')
@patch.object(UserInputProcessor, 'request_player_move', return_value='00')
@patch.object(GameRulesEngine, 'execute_human_player_attack', return_value=True)
@patch.object(GameRulesEngine, 'execute_computer_player_attack')
def test_game_orchestrator_main_game_loop_normal_turn(mock_cpu_attack, mock_player_attack, 
                                                    mock_get_move, mock_boards, game_orchestrator):
    """Test main game loop during normal turn."""
    game_orchestrator.game_rules.initialize_game_state()
    
    with patch.object(game_orchestrator.game_rules, 'determine_game_winner', side_effect=[None, 'Player']):
        with patch.object(game_orchestrator.input_processor, 'request_player_move', return_value='00'):
            game_orchestrator._process_human_player_turn()


# Main function test
@patch('seabattle.GameOrchestrator')
def test_initialize_and_run_game(mock_orchestrator_class):
    """Test the main game initialization and run function."""
    from seabattle import initialize_and_run_game
    
    mock_orchestrator = MagicMock()
    mock_orchestrator_class.return_value = mock_orchestrator
    
    initialize_and_run_game()
    
    mock_orchestrator_class.assert_called_once()
    mock_orchestrator.commence_game_session.assert_called_once()


# Additional core logic tests for comprehensive coverage
def test_ship_edge_cases():
    """Test ship edge cases."""
    ship = Ship(['00'])
    assert ship.attempt_hit('00')
    assert ship.is_completely_destroyed()
    
def test_board_edge_cases():
    """Test board edge cases."""
    board = GameBoard(1)
    assert board.board_size == 1
    assert board.is_position_within_bounds(BoardPosition(0, 0))
    assert not board.is_position_within_bounds(BoardPosition(1, 1))

def test_cpu_player_switch_modes():
    """Test CPU player mode switching."""
    board = GameBoard(10)
    cpu = CPUPlayer(board)
    
    # Test switch to target mode
    cpu._switch_to_target_mode('55')
    assert cpu.current_cpu_mode == CPUMode.TARGET
    assert len(cpu.priority_target_queue) > 0
    
    # Test switch to hunt mode
    cpu._switch_to_hunt_mode()
    assert cpu.current_cpu_mode == CPUMode.HUNT
    assert len(cpu.priority_target_queue) == 0

def test_player_attack_history():
    """Test player attack history functionality."""
    board = GameBoard(10)
    player = CPUPlayer(board)
    
    assert not player.has_previously_attacked('00')
    player.record_attack('00')
    assert player.has_previously_attacked('00')
    assert '00' in player.attack_history
    
    # Test duplicate recording
    initial_length = len(player.attack_history)
    player.record_attack('00')
    assert len(player.attack_history) == initial_length 