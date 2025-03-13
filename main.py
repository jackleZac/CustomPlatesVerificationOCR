# Entry point, initializes Flask app
from flask import Flask
from bk_tree import BKTree, levenshtein_distance
from db import get_all_plates
from routes import init_routes

app = Flask(__name__)

# Initialize BK-Tree with database records
def initialize_bk_tree():
    tree = BKTree(levenshtein_distance)
    plates = get_all_plates()
    for plate in plates:
        tree.insert(plate)
    return tree

# Global BK-Tree instance
bk_tree = initialize_bk_tree()

# Register routes
init_routes(app, bk_tree)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)