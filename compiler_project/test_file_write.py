#!/usr/bin/env python3
"""
Test script to verify file writing works
"""

def test_file_write():
    try:
        with open('compiler_output.txt', 'w', encoding='utf-8') as f:
            f.write("TEST COMPILER OUTPUT\n")
            f.write("=" * 50 + "\n")
            f.write("This is a test file to verify writing works.\n")
            f.write("If you see this, file writing is working!\n")
        print("✅ Test file written successfully: compiler_output.txt")
    except Exception as e:
        print(f"❌ Error writing test file: {e}")

if __name__ == "__main__":
    test_file_write()