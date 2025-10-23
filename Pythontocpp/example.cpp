int main() {
    int a = 5;
    int b = 10;

    // Boolean expressions
    print(a < b);   // 1 (true)
    print(a > b);   // 0 (false)
    print(a != b);  // 1 (true)
    print(a == 5);  // 1 (true)

    // If-Else If-Else
    if (a < b) {
        print("a is less than b");
    } else if (a == b) {
        print("a is equal to b");
    } else {
        print("a is greater than b");
    }

    // Switch-case simulation
    int option = 2;
    switch (option) {
        case 1:
            print("Option is 1");
            break;
        case 2:
            print("Option is 2");
            break;
        case 3:
            print("Option is 3");
            break;
        default:
            print("Option is something else");
    }

    return 0;
}
