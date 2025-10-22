int main() {
    int n;
    n = 5;
    int fact;
    fact = 1;
    for (int i = 1; i <= n; i = i + 1) {
        fact = fact * i;
    }
    print(fact);
    return 0;
}
