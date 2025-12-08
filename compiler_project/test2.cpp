#include "stdio.h"


// 1. Void function without parameters
void solve() {
    printf("Solving problem...\n");
    int x = 10;
    int y = 20;
    printf("x = %d, y = %d\n", x, y);
}

// 2. Void function with parameters
void processData(int a, float b) {
    printf("Processing data: %d, %.2f\n", a, b);
    if (a > b) {
        printf("a is greater\n");
    } else {
        printf("b is greater or equal\n");
    }
}

// 3. Integer function with parameters
int add(int a, int b) {
    int result = a + b;
    printf("Addition: %d + %d = %d\n", a, b, result);
    return result;
}

// 4. Float function with parameters
float calculateAverage(int arr[], int size) {
    float sum = 0;
    for (int i = 0; i < size; i++) {
        sum += arr[i];
    }
    float average = sum / size;
    printf("Average: %.2f\n", average);
    return average;
}

// 5. Function with return statement and braces
int multiply(int x, int y) {
    return x * y;
}

// 6. Function with empty body
int dummy() {}

// 7. Main function
int main() {
    printf("=== Testing Different Function Types ===\n");
    
    // Test void function without parameters
    solve();
    
    // Test void function with parameters
    processData(15, 25.5f);
    
    // Test integer function
    int sum = add(5, 7);
    printf("Sum result: %d\n", sum);
    
    // Test float function
    int numbers[] = {10, 20, 30, 40, 50};
    float avg = calculateAverage(numbers, 5);
    printf("Average result: %.2f\n", avg);
    
    // Test multiplication function
    int product = multiply(6, 8);
    printf("Product: %d\n", product);
    
    // Test dummy function
    int dummyResult = dummy();
    printf("Dummy result: %d\n", dummyResult);
    
    printf("=== Test Completed ===\n");
    return 0;
}