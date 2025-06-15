<img src="enigma.png" alt="Enigma Machine" width="300"/>

# Enigma Machine CLI

enigma.js contains a simplified command-line Enigma machine implementation. The Enigma was a rotor-based cipher device used for secure communication in the early 20th century.

**Status:** ✅ Fully functional with comprehensive test coverage (85%+)

## Features

- **Historical accuracy**: Implements the Enigma I machine with rotors I, II, and III
- **Plugboard support**: Configurable letter swapping for enhanced security
- **Symmetric encryption**: Same settings encrypt and decrypt messages
- **Robust implementation**: Thoroughly tested with 19 test cases covering all functionality

## Usage

You can use the CLI to encrypt or decrypt messages using a configurable Enigma setup (rotors, plugboard, reflector).

## How to Run

1. **Ensure you have Node.js installed.**
2. **Navigate to the directory with enigma.js** in your terminal.
3. **Run the program** using:
   ```bash
   node enigma.js
   ```
4. **Follow the prompts** to enter your message and configuration.

## Running Tests

To verify the implementation and run the comprehensive test suite:

```bash
node test.js
```

The test suite includes:
- **19 comprehensive tests** covering all functionality
- **Plugboard mechanics** (3 tests)
- **Rotor operations** (5 tests) 
- **Core Enigma functionality** (11 tests)
- **Edge cases and error handling**
- **Historical accuracy verification**

## Detailed Instructions

When you run the program, you will be prompted for several configuration options:

### 1. Enter message
- Type the message you want to encrypt or decrypt. Only A-Z letters are processed; other characters are passed through unchanged.

### 2. Rotor positions (e.g. `0 0 0`)
- Enter three numbers (space-separated), each from 0 to 25, representing the initial position of each rotor (left to right). For example, `0 0 0` means all rotors start at 'A'.

### 3. Ring settings (e.g. `0 0 0`)
- Enter three numbers (space-separated), each from 0 to 25, representing the ring setting for each rotor. The ring setting shifts the internal wiring of the rotor. Historically, this was used to add another layer of security.

### 4. Plugboard pairs (e.g. `AB CD`)
- Enter pairs of letters (no separator between letters, space between pairs) to swap on the plugboard. For example, `AB CD` swaps A<->B and C<->D. You can leave this blank for no plugboard swaps.

## Example Sessions

### Basic encryption (no plugboard)
```
$ node enigma.js
Enter message: HELLO
Rotor positions (e.g. 0 0 0): 0 0 0
Ring settings (e.g. 0 0 0): 0 0 0
Plugboard pairs (e.g. AB CD): 
Output: VNACA
```

### Advanced encryption (with plugboard)
```
$ node enigma.js
Enter message: HELLOWORLD
Rotor positions (e.g. 0 0 0): 0 0 0
Ring settings (e.g. 0 0 0): 0 0 0
Plugboard pairs (e.g. AB CD): QW ER
Output: VDACACJJEA
```

### Decryption (same settings)
```
$ node enigma.js
Enter message: VDACACJJEA
Rotor positions (e.g. 0 0 0): 0 0 0
Ring settings (e.g. 0 0 0): 0 0 0
Plugboard pairs (e.g. AB CD): QW ER
Output: HELLOWORLD
```

## Technical Notes

- **Rotors**: Uses historical Enigma I rotors (I, II, III) with authentic wiring and notch positions
- **Reflector**: Implements the standard Enigma reflector for signal reflection
- **Stepping mechanism**: Accurate rotor advancement with proper double-stepping behavior
- **Character handling**: Only uppercase A-Z are encrypted; other characters pass through unchanged
- **Case insensitive**: Automatically converts lowercase input to uppercase
- **Symmetric operation**: The same settings encrypt and decrypt (Enigma's key property)

## Files in this Project

- **`enigma.js`** - Main Enigma machine implementation
- **`test.js`** - Comprehensive test suite (19 tests)
- **`test_report.txt`** - Detailed test coverage report  
- **`fix.md`** - Documentation of bug fixes applied
- **`README.md`** - This documentation file

## Important Security Properties

✅ **No letter encrypts to itself** - Historical Enigma property maintained  
✅ **Symmetric encryption/decryption** - Same settings work both ways  
✅ **Plugboard bidirectional** - Swaps work in both input and output stages  
✅ **Rotor stepping accurate** - Follows historical Enigma timing  

## Bug Fixes Applied

This implementation has been thoroughly debugged and tested. A critical plugboard bug was identified and fixed where the plugboard swapping was only applied at input but not at output, causing decryption failures. This has been resolved and verified through comprehensive testing.

## Requirements

- Node.js (any recent version)
- No additional dependencies required
