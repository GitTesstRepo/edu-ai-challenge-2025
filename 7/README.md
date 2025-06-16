# Sea Battle CLI Game

A Python implementation of the classic Sea Battle (Battleship) game with a focus on clean, maintainable code and professional software engineering practices.

## Features

- **Classic Battleship Gameplay**: 10x10 grid with 3 ships of length 3
- **Intelligent CPU Opponent**: Uses hunt/target strategy for challenging gameplay
- **Clean Architecture**: Professional-grade code structure following SOLID principles
- **Excellent Code Quality**: 94% test coverage with comprehensive pytest unit tests
- **Enhanced Readability**: Clear naming conventions and consistent code style
- **Maintainable Design**: Well-documented classes with single responsibilities

## Quick Start

### Prerequisites

- Python 3.7 or higher
- pytest (for running tests)
- pytest-cov (for coverage reports)

### Installation

1. Clone or download the project files
2. Install testing dependencies (optional):
```bash
pip install pytest pytest-cov
```

### Playing the Game

Run the game directly:
```bash
python seabattle.py
```

The game will:
1. Randomly place 3 ships (each of length 3) on both player and CPU boards
2. Display both boards side-by-side (your ships are visible as 'S', enemy ships are hidden)
3. Prompt you to enter coordinates (e.g., "23" for row 2, column 3)
4. Show hit results and continue until all ships are sunk

### Game Symbols

- `~` : Water (unexplored)
- `S` : Your ship
- `X` : Hit (ship part destroyed)
- `O` : Miss (water shot)

## Code Architecture

The codebase follows a clean, modular architecture with clear separation of concerns:

### Core Components

#### Model Layer (Game State & Logic)
- **`BoardPosition`**: Immutable coordinate representation with utilities
- **`Ship`**: Naval vessel with position tracking and damage state
- **`GameBoard`**: Game grid management with ship placement and attack processing
- **`Player` (Abstract)**: Base player interface ensuring consistent behavior
- **`HumanPlayer`**: Human player implementation
- **`CPUPlayer`**: Intelligent computer opponent with hunt/target CPU strategy

#### View Layer (User Interface)
- **`UserInterfaceDisplay`**: All console rendering and message display operations

#### Controller Layer (Input & Game Flow)
- **`UserInputProcessor`**: Input validation and error handling
- **`GameRulesEngine`**: Core game mechanics and rule enforcement
- **`GameOrchestrator`**: Main coordinator managing game flow and component interaction

### Enhanced Code Quality Features

#### Naming Conventions
- **Classes**: PascalCase with descriptive, professional names
- **Methods**: snake_case with clear action-oriented names
- **Variables**: Descriptive names avoiding abbreviations
- **Constants**: UPPERCASE with clear semantic meaning

#### Code Organization
- **Named Constants**: All magic numbers and strings replaced with meaningful constants
- **Enumerations**: Type-safe enums for ship orientations and CPU modes  
- **Comprehensive Documentation**: Detailed docstrings for all public methods
- **Input Validation**: Robust error handling with clear user feedback
- **Single Responsibility**: Each class has one clear, focused purpose

#### Professional Patterns
- **Dependency Injection**: Loose coupling between components
- **Abstract Base Classes**: Enforced contracts for extensibility
- **Immutable Objects**: BoardPosition and enum usage for reliability
- **Error Handling**: Graceful failure handling throughout

## Testing

### Running Tests

Run all tests:
```bash
python -m pytest test_seabattle.py -v
```

Run tests with coverage report:
```bash
python -m pytest test_seabattle.py --cov=seabattle --cov-report=term-missing
```

Generate HTML coverage report:
```bash
python -m pytest test_seabattle.py --cov=seabattle --cov-report=html
```

### Test Coverage

The test suite achieves **94% code coverage** with 55 comprehensive test cases covering:

- **Unit Tests**: All individual components and their methods
- **Integration Tests**: Component interaction and game flow
- **Edge Cases**: Boundary conditions and error scenarios
- **CPU Behavior**: Intelligent opponent strategy verification
- **User Interface**: Display rendering and input processing
- **Core Logic**: Critical game mechanics and business rules

### Test Organization

Tests are organized using **pytest framework** with function-based tests and fixtures:
- **BoardPosition Tests**: Coordinate system validation and utilities
- **Ship Tests**: Naval vessel behavior and damage tracking
- **GameBoard Tests**: Grid management and attack processing  
- **Player Tests**: Human and CPU player behavior verification
- **UserInterface Tests**: Display rendering and input validation
- **GameRules Tests**: Core game mechanics and win conditions
- **Integration Tests**: Full game flow coordination
- **Edge Case Tests**: Boundary conditions and error handling

## Project Structure

```
sea-battle/
├── seabattle.py          # Main game implementation (933 lines)
├── test_seabattle.py     # Comprehensive pytest test suite (610 lines)
├── README.md             # Documentation (this file)
├── test_report.txt       # Latest test coverage report
├── refactoring.md        # Detailed refactoring documentation
├── seabattle.js          # Original JavaScript implementation
└── __pycache__/          # Python bytecode cache
    └── htmlcov/          # HTML coverage reports (when generated)
```

## Code Quality Metrics

- **Lines of Code**: 933 lines (main implementation)
- **Test Coverage**: 94% (357/381 statements covered)
- **Test Cases**: 55 comprehensive pytest unit tests
- **Classes**: 10 well-designed classes with clear responsibilities
- **Code Complexity**: Low complexity with focused, single-purpose methods
- **Documentation**: 100% of public methods documented
- **Testing Framework**: Pure pytest implementation with fixtures and function-based tests

## Development Philosophy

This implementation demonstrates professional software engineering practices:

1. **Clean Code**: Self-documenting code with meaningful names
2. **SOLID Principles**: Single responsibility, open/closed, dependency inversion
3. **Test-Driven Development**: Comprehensive test coverage ensuring reliability
4. **Maintainability**: Easy to understand, modify, and extend
5. **Readability**: Consistent style and clear documentation
6. **Robustness**: Graceful error handling and input validation

## Game Logic Details

### Ship Placement
- 3 ships per player, each 3 cells long
- Random placement with collision detection
- Horizontal or vertical orientation
- Ensures valid placement within board boundaries

### CPU Strategy
The computer opponent uses a sophisticated two-mode strategy:

1. **Hunt Mode**: Random coordinate selection to locate ships
2. **Target Mode**: Systematic targeting of adjacent cells after scoring a hit
3. **Smart Transitions**: Switches back to hunt mode when ships are destroyed

### Win Conditions
- Player wins: All enemy ships destroyed
- CPU wins: All player ships destroyed
- Game displays appropriate victory/defeat messages

## Technical Implementation

### Key Design Decisions

1. **Immutable Coordinates**: BoardPosition objects prevent coordinate mutation bugs
2. **Enum Usage**: Type-safe constants for orientations and CPU modes
3. **Abstract Base Classes**: Enforced contracts for extensible player types
4. **Separation of Concerns**: UI, logic, and input handling clearly separated
5. **Named Constants**: All magic values replaced with descriptive constants

### Error Handling

- Input validation with user-friendly error messages
- Graceful handling of invalid coordinates
- Keyboard interrupt handling for clean exit
- Comprehensive bounds checking

### Extensibility

The architecture supports easy extension:
- New player types (inherit from Player base class)
- Different board sizes (configurable dimensions)
- Varying ship configurations (adjustable fleet parameters)
- Alternative CPU strategies (modular opponent implementation)

## Contributing

When contributing to this codebase:

1. Follow the established naming conventions
2. Maintain comprehensive test coverage
3. Add detailed docstrings for new methods
4. Use type hints for better code clarity
5. Ensure all tests pass before submitting changes

## License

This implementation is provided as an educational example of clean, maintainable Python code following professional software engineering practices. 