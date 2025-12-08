//Test 1 pass one  which  is comments  allow  cpp and  python 


// This is a single-line comment
/* This is a
   multi-line comment */

//  dhfjkdsf

//test 2 pass still  some  issue like  #define MAX 10  
#include <stdio.h>
const expr int MAX = 10;
#ifdef DEBUG 
#include "stl_library.py"
#include <vector>


//test 3  identifiers string char  all pass 
//one  issue if i didnot close "  (")  than  all  are 

string a  = "Hello, World!"
string b  = "Line1\nLine2"
string c  =  "Quotes: \"C++\""
/*string x = "Hello \
World";*/
string y = "dfdf   hare  is it  error" 

char a = 'a'
char b = '\n'
char d = '\''
char c = '\\'

print("Hello EDU !")


//test 4 Number int 4.4  example  i  want  to  show only  4  but 4.4 show basic  done 

int  a = 4;
int b = 4.4  
float b=-5.5
b =  0x1A3F



//test 5 keyword all ok  type oparator  condition <= >= || && all ok  shifting working 

if
else
while
do  while


int a = 5;
float b = 3.14;
bool flag = true;
char c = 'A';

if (a >= 5 && flag) {
    a++;
    b += 2.0;
    c = 'B';
}

int* ptr = nullptr;
MyClass obj;
obj.method();
ptr->member;
x <<= 2;
y >>= 3;

if (a == b && c != d) {
    x <= 10 || y >= 5;
} else if (flag) {
    doSomething();
}

int x = 10;
float y = 20.5;
if (x < y) {
x += 1;
}



//test combo
#include <iostream>
#include "stl_library.py"   // Allowed custom STL library

#define MAX_SIZE 10          // Constant macro (can show a suggestion)

int main() {
    int arr[MAX_SIZE] = {5, 2, 9, 1, 5, 6, 3, 8, 7, 4};
    float pi = 3.14;
    bool flag = true;
    char c = 'A';

    // Create STL library object
    STLLibrary stl;

    // Using custom STL functions
    arr[0] = stl.find(arr, 5);   // Find element
    arr[0] = stl.sort(arr)[0];   // Sort array and get first element
    arr[0] = stl.swap(arr[0], arr[1]).first; // Swap two elements
    arr[0] = stl.reverse(arr)[0];            // Reverse array

    stl.malloc(10);             // Memory allocation simulation
    stl.free(arr);              // Free memory simulation
    std::cout << stl.printf("Pi is %1", pi) << std::endl;

    // Conditional statements
    if (flag && arr[0] >= 5) {
        arr[0]++;
        pi += 2.0;
        c = 'B';
    }

    // pointer example
    int* ptr = nullptr;
    ptr = &arr[0];

    return 0;
}



//func

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

void slove ()
{

    int i = 0;
    for(int i = 0 ;  i < n ; i++)
    i++;  //  not  work i=i+1  
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
