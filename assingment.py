import sys


if len(sys.argv) != 3:
   
    sys.exit(1)

input_file, output_file = sys.argv[1], sys.argv[2]


keywords = {
    "auto","break","case","char",
    "double","float",
    "int","long"

}


def is_identifier(word):
    if not word:  
        return False
    if word in keywords: 
        return False
    
    if not (word[0].isalpha() or word[0] == '_'):
        return False
 
    for ch in word[1:]:
        if not (ch.isalnum() or ch == '_'):
            return False
    return True

# File handling
with open(input_file, "r") as infile, open(output_file, "w") as outfile:
    for line in infile:
        parts = line.strip().split()  
        for word in parts:
            if word in keywords:
                outfile.write(f"Keyword: {word}\n")
            elif is_identifier(word):
                outfile.write(f"Identifier: {word}\n")
            else:
                outfile.write(f"Error: {word}\n")
