#include <iostream>
#include "stl_library.py"
#include <vector>  // This should trigger a problem

#define MAX_SIZE 100
#define MIN(a,b) ((a)<(b)?(a):(b))
#define PI 3.14159

using namespace std;

class MyClass {
public:
    static const int VALUE = 42;
    
    void printMessage() {
        std::cout << "Hello World!\n";  // std:: should trigger problem
        printf("This is a test\n");     // printf should trigger problem
        
        // Different number types
        int decimal = 42;
        int hex = 0x1A3F;
        int binary = 0b1010;
        int octal = 0777;
        float floating = 3.14e-10;
        double precise = .5;
        bool flag = true;
        
        if (flag && decimal > 0) {
            for (int i = 0; i < MAX_SIZE; i++) {
                // Memory operations - should trigger problems
                int* arr = (int*)malloc(100 * sizeof(int));
                free(arr);
            }
        }
    }
    
private:
    int private_var;
    float float_var = 2.5f;
};

struct Point {
    int x, y;
    Point(int x, int y) : x(x), y(y) {}
};

// Function with different constructs
void processData() {
    int numbers[] = {1, 2, 3, 4, 5};
    
    // Different loops
    for (int i = 0; i < 5; i++) {
        numbers[i] *= 2;
    }
    
    int j = 0;
    while (j < 5) {
        std::cout << numbers[j] << " ";
        j++;
    }
    
    do {
        std::cout << "Do-while loop";
    } while (false);
    
    // Switch statement
    int choice = 2;
    switch (choice) {
        case 1:
            std::cout << "Case 1";
            break;
        case 2:
            std::cout << "Case 2";
            break;
        default:
            std::cout << "Default";
    }
}

// Template function
template<typename T>
T add(T a, T b) {
    return a + b;
}

// Main function
int main() {
    MyClass obj;
    obj.printMessage();
    
    Point p(10, 20);
    
    // Using standard library - should trigger problems
    std::vector<int> vec;
    vec.push_back(1);
    
    // More problematic calls
    scanf("%d");
    calloc(10, sizeof(int));
    
    return 0;
}

/* 
   Multi-line comment
   spanning multiple lines
   to test comment detection
*/

// Single line comment

#if DEBUG
void debugFunction() {
    std::cout << "Debug mode";
}
#endif