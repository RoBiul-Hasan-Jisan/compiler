# Define keywords
KEYWORDS = ["int", "float", "char", "double"]

def is_keyword(word):
    return word in KEYWORDS


def scan_file(filename):
    try:
        with open(filename, "r") as file:
            content = file.read()
    except FileNotFoundError:
        print(f"Error: Cannot open file '{filename}'")
        return

    word = ""
    for ch in content:
        
        if ch.isalnum() or ch in ['_', '.', '-']:
            word += ch
        else:
          
            if word:
                classify_word(word)
                word = ""

    
    if word:
        classify_word(word)


def classify_word(word):
    
    if is_keyword(word):
        print(f"Keyword: {word}")
        return

    
    if word[0].isalpha() or word[0] == '_':
        if all(c.isalnum() or c == '_' for c in word[1:]):
            print(f"Identifier: {word}")
            return

  
    if word[0].isdigit() or word[0] in ['-', '.']:
        is_num = True
        dot_count = 0

        for i, c in enumerate(word):
            if c == '.':
                dot_count += 1
            elif not (c.isdigit() or (i == 0 and c == '-')):
                is_num = False
                break

        if is_num and dot_count == 0:
            print(f"IntNUM: {word}")
        elif is_num and dot_count == 1:
            print(f"FloatNUM: {word}")
        else:
            print(f"ERROR: {word}")
        return


    print(f"ERROR: {word}")


if __name__ == "__main__":
    scan_file("input.txt")
