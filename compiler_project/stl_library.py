"""
Enhanced Custom STL Library with Real-world Algorithms (Pure Logic Version)
"""

class STLLibrary:
    def __init__(self):
        self.functions = {
            'sort': 'Custom quick sort implementation',
            'swap': 'Element swapping utility', 
            'reverse': 'Sequence reversal algorithm',
            'find': 'Linear search implementation',
            'copy': 'Deep copy functionality',
            'malloc': 'Memory allocation wrapper',
            'free': 'Memory deallocation wrapper',
            'printf': 'Formatted output implementation'
        }
    
    def sort(self, arr, ascending=True):
        """Custom QuickSort implementation"""
        if len(arr) <= 1:
            return arr
        
        pivot = arr[len(arr) // 2]
        left = [x for x in arr if x < pivot]
        middle = [x for x in arr if x == pivot]
        right = [x for x in arr if x > pivot]
        
        result = self.sort(left) + middle + self.sort(right)
        return result if ascending else result[::-1]
    
    def swap(self, a, b):
        """Swap two elements using tuple unpacking"""
        return b, a
    
    def reverse(self, arr):
        """Reverse array in-place using two pointers"""
        left, right = 0, len(arr) - 1
        while left < right:
            arr[left], arr[right] = arr[right], arr[left]
            left += 1
            right -= 1
        return arr
    
    def find(self, arr, target):
        """Find element in array with linear search"""
        for i, item in enumerate(arr):
            if item == target:
                return i
        return -1
    
    def copy(self, arr):
        """Deep copy array"""
        return [item for item in arr]
    
    def malloc(self, size):
        """Custom memory allocation simulation (returns zero-filled list)"""
        return [0] * size  # Simulate allocated memory
    
    def free(self, ptr):
        """Simulate freeing memory (no-op in Python)"""
        del ptr
    
    def printf(self, format_string, *args):
        """Custom formatted output implementation (returns formatted string)"""
        result = format_string
        for i, arg in enumerate(args):
            result = result.replace(f'%{i+1}', str(arg))
        return result
