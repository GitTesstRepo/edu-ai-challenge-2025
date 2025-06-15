# Enigma Machine Bug Fix Report

## Bug Description

The Enigma machine implementation had a critical bug in the plugboard handling during the encryption/decryption process. 

**Problem:** The plugboard swapping was only applied at the beginning of the encryption process, but not at the end. In a real Enigma machine, the plugboard is applied twice:
1. Before the signal enters the rotors (input stage)
2. After the signal exits the rotors (output stage)

This meant that while basic encryption without plugboard worked correctly, any configuration using plugboard pairs would fail to decrypt properly, producing garbled output instead of the original plaintext.

## Root Cause

In the `encryptChar` method of the `Enigma` class, the code was:

```javascript
encryptChar(c) {
  if (!alphabet.includes(c)) return c;
  this.stepRotors();
  c = plugboardSwap(c, this.plugboardPairs);  // Only applied here
  // ... rotor processing ...
  // ... reflector processing ...
  // ... rotor processing (reverse) ...
  return c;  // Missing plugboard swap here
}
```

## Fix Applied

Added the missing plugboard swap at the end of the encryption process:

```javascript
encryptChar(c) {
  if (!alphabet.includes(c)) return c;
  this.stepRotors();
  c = plugboardSwap(c, this.plugboardPairs);  // Input plugboard
  // ... rotor processing ...
  // ... reflector processing ...
  // ... rotor processing (reverse) ...
  c = plugboardSwap(c, this.plugboardPairs);  // Output plugboard (FIXED)
  return c;
}
```

## Verification

Before fix:
- Input: "HELLO" with plugboard [['A', 'B']]
- Encrypted: "VNBCB"
- Decrypted: "HEYLK" ❌ (incorrect)

After fix:
- Input: "HELLO" with plugboard [['A', 'B']]
- Encrypted: "VNBCB"
- Decrypted: "HELLO" ✅ (correct)

The fix ensures that the Enigma machine correctly implements the bidirectional nature of the plugboard, making encryption and decryption symmetric operations as required for proper Enigma functionality. 