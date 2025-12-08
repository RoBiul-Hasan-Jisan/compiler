#include <bits/stdc++.h>
using namespace std;

// Grammar type: map from Non-Terminal to list of productions
using Grammar = map<string, vector<string>>;

// Split a string by a delimiter
vector<string> split(const string &s, char delim) {
    vector<string> tokens;
    string temp;
    for (char c : s) {
        if (c == delim) {
            if (!temp.empty()) tokens.push_back(temp);
            temp = "";
        } else temp += c;
    }
    if (!temp.empty()) tokens.push_back(temp);
    return tokens;
}

// Find longest common prefix among at least 2 productions
string longestCommonPrefix(const vector<string> &prods) {
    string longest = "";
    for (size_t i = 0; i < prods.size(); i++) {
        for (size_t j = i + 1; j < prods.size(); j++) {
            string prefix = "";
            int len = min(prods[i].size(), prods[j].size());
            for (int k = 0; k < len; k++) {
                if (prods[i][k] == prods[j][k]) prefix += prods[i][k];
                else break;
            }
            // Count how many productions start with this prefix
            int count = 0;
            for (auto &p : prods)
                if (p.substr(0, prefix.size()) == prefix) count++;
            if (count >= 2 && prefix.size() > longest.size())
                longest = prefix;
        }
    }
    return longest;
}

// Recursive left factoring for a non-terminal
void factorNonTerminal(string A, Grammar &grammar, int &primeCount) {
    vector<string> prods = grammar[A];
    string prefix = longestCommonPrefix(prods);
    if (prefix.empty()) return;

    string newNT = A + string(primeCount, '\''); // e.g., A', A''
    primeCount++;

    vector<string> prodsA, prodsNew;
    for (auto &p : prods) {
        if (p.substr(0, prefix.size()) == prefix) {
            string suffix = p.substr(prefix.size());
            if (suffix.empty()) suffix = "epsilon"; // Use ε for empty suffix
            prodsNew.push_back(suffix);
        } else {
            prodsA.push_back(p);
        }
    }

    prodsA.push_back(prefix + newNT);
    grammar[A] = prodsA;
    grammar[newNT] = prodsNew;

    // Recursively factor the new non-terminal if needed
    if (prodsNew.size() > 1)
        factorNonTerminal(newNT, grammar, primeCount);
}

// Left factor the entire grammar
void leftFactorGrammar(Grammar &grammar) {
    int primeCount = 1;
    vector<string> nonTerminals;
    for (auto &it : grammar)
        nonTerminals.push_back(it.first);

    for (size_t i = 0; i < nonTerminals.size(); i++) {
        factorNonTerminal(nonTerminals[i], grammar, primeCount);
    }
}

// Display grammar
void printGrammar(const Grammar &grammar) {
    for (auto &it : grammar) {
        cout << it.first << " -> ";
        for (size_t i = 0; i < it.second.size(); i++) {
            cout << it.second[i];
            if (i != it.second.size() - 1) cout << " | ";
        }
        cout << endl;
    }
}

int main() {
    Grammar grammar;
    int n;
    cout << "Enter number of non-terminals: ";
    cin >> n;
    cin.ignore();

    cout << "Enter grammar productions (e.g., S -> aSSbS | aSaSb | abb | b):\n";
    for (int i = 0; i < n; i++) {
        string line;
        getline(cin, line);
        line.erase(remove(line.begin(), line.end(), ' '), line.end()); // remove spaces

        int pos = line.find("->");
        if (pos == string::npos) {
            cout << "Invalid format!\n";
            i--;
            continue;
        }

        string lhs = line.substr(0, pos);
        string rhs = line.substr(pos + 2);
        vector<string> prods = split(rhs, '|');

        // Convert "e" or "epsilon" to "ε"
        for (auto &p : prods)
            if (p == "e" || p == "epsilon") p = "epsilon";

        grammar[lhs] = prods;
    }

    cout << "\nOriginal Grammar:\n";
    printGrammar(grammar);

    leftFactorGrammar(grammar);

    cout << "\nGrammar After Left Factoring:\n";
    printGrammar(grammar);

    return 0;
}
