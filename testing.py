from typing import List, Dict, Any

def create_dicts(x: List[int], y: List[Any], c: List[Any]) -> List[Dict[str, Any]]:
    # Get the unique values in x and c
    unique_x = sorted(set(x))  # Ensure unique x values are sorted for consistent dictionary keys
    unique_c = sorted(set(c))
    
    # Initialize the result list
    result = []
    new_result = []
    
    for ci in unique_c:
        # Create a dictionary for each unique value in c
        current_arr = [{"label": ci}]
        current_dict = {"label": ci}
        
        for xi in unique_x:
            # Find the corresponding y value for each unique x
            for xi_idx, x_val in enumerate(x):
                if x_val == xi and c[xi_idx] == ci:
                    current_arr.append({"var": y[xi_idx]})
                    current_dict[f"y_{xi}"] = y[xi_idx]
                    break  # Break to avoid redundant checks after finding the match
            else:
                # In case no matching y value is found for the specific (x=xi, c=ci) pair
                current_arr.append({"var": 0})
                current_dict[f"y_{xi}"] = None  # Or some other default value
        
        # Add the current dictionary to the result list
        result.append(current_dict)
        new_result.append(current_arr)
    
    print(new_result)
    return result

# Example usage
# x = [0, 1, 2, 0, 1, 2]
x = [0, 0, 0, 0, 0, 1, 1, 1]

# y = [10, 20, 30, 40, 50, 60]
y = [27,  9, 10,  3,  5, 38, 14,  7]

# c = ['red', 'red', 'red', 'blue', 'blue', 'blue']
c = [0, 1, 2, 3, 4, 0, 1, 2]

result = create_dicts(x, y, c)
print(result)
