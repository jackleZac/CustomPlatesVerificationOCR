# Test the accuracy of the BK-Tree implementation by comparing the results of a set of test cases against the expected results
from bk_tree import BKTree, levenshtein_distance
from db import get_all_plates

# Initialize BK-Tree
tree = BKTree(levenshtein_distance)
plates = get_all_plates()
for plate in plates:
    tree.insert(plate)

# Define test cases: (input, expected match, max_distance)
test_cases = [
    ("ABC123", "ABC123", 2),  # Exact match
    ("ABCl23", "ABC123", 2),  # Small error (l vs 1)
    ("ABC12Z", "ABC123", 2),  # Small error (Z vs 3)
    ("ZZZ999", None, 2),      # No match
    ("XYZ78P", "XYZ789", 2),  # Small error (P vs 9)
]

def run_accuracy_tests():
    correct = 0
    total = len(test_cases)
    
    print("Running accuracy tests...")
    for input_plate, expected, max_dist in test_cases:
        matches = tree.search(input_plate, max_dist)
        found = matches[0][0] if matches else None
        is_correct = (found == expected)
        print(f"Input: {input_plate}, Expected: {expected}, Found: {found}, Correct: {is_correct}")
        if is_correct:
            correct += 1
    
    accuracy = (correct / total) * 100
    print(f"\nAccuracy: {accuracy:.2f}% ({correct}/{total} correct)")

if __name__ == "__main__":
    run_accuracy_tests()