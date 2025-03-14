# Entry point, initializes Flask app
from flask import Flask
from threading import Thread
from bk_tree import BKTree, levenshtein_distance
from db import get_all_plates
from routes import init_routes
import gui

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

# Function to run Flask in a separate thread
def run_flask():
    app.run(debug=True, use_reloader=False)  # Prevents duplicate execution

if __name__ == "__main__":
    # Start Flask in a separate thread
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True  # Stops when the main program exits
    flask_thread.start()

    # ✅ Pass BK-Tree instance to the GUI correctly
    gui.run_gui(bk_tree)
