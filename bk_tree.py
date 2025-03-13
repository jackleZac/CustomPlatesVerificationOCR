# This file contains the BK-Tree and Levenshtein Distance logic
def levenshtein_distance(s1, s2):
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]

class BKTree:
    def __init__(self, distance_func):
        self.distance_func = distance_func
        self.root = None

    def insert(self, word):
        if not self.root:
            self.root = (word, {})
            return
        node = self.root
        while True:
            dist = self.distance_func(word, node[0])
            if dist in node[1]:
                node = node[1][dist]
            else:
                node[1][dist] = (word, {})
                break

    def search(self, query, max_dist):
        if not self.root:
            return []
        results = []
        def _search(node, query, max_dist):
            if not node:
                return
            dist = self.distance_func(query, node[0])
            if dist <= max_dist:
                results.append((node[0], dist))
            for d, child in node[1].items():
                if dist - max_dist <= d <= dist + max_dist:
                    _search(child, query, max_dist)
        _search(self.root, query, max_dist)
        return results