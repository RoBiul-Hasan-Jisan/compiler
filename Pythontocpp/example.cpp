int main() {
    int a = 5;
    int b = 10;
   

    // ---------- Unary operators ----------
    a++;    // 6
    b--;    // 9
    print(a);
    print(b);

 

    // ---------- Comparison operators ----------
    print(a < b);   // 1 (true)
    print(a <= b);  // 1
    print(a > b);   // 0
    print(a >= b);  // 0
    print(a == b);  // 0
    print(a != b);  // 1

    // ---------- Logical operators ----------
    print((a < b) && (b > 0));   // 1
    print((a > b) || (b > 0));   // 1

    // ---------- If-Else chains ----------
    if (a > b) {
        print("a > b");
    }
   
    else 
    {
        print("a < b");  // Expected output
    }

    return 0;
}
