from collections import Counter

# Read all strings from a file (each line is one string)
with open("data.txt", "r") as f:
    words = [line.strip() for line in f if line.strip()]

# Count frequencies
freq = Counter(words)

# Show duplicates
duplicates = {k: v for k, v in freq.items() if v > 1}

if duplicates:
    print("Duplicate strings found:\n")
    for s, count in duplicates.items():
        print(f"{s} -> {count} times")
else:
    print(" No duplicates found.")
