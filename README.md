# Truck Plate Recognition Backend
This is a Flask-based backend for a truck plate recognition system designed for customs use. It processes truck number plates (OCR is handled externally), stores truck records in a MySQL database, and searches for approximate matches using a Levenshtein Distance algorithm optimized with a BK-Tree. The backend exposes RESTful APIs for a separate frontend to interact with, enabling efficient matching of plate numbers despite potential OCR errors.

## Features

- **Efficient Search**: Uses a BK-Tree to perform approximate string matching with Levenshtein Distance, tolerating OCR errors (e.g., "ABCI23" matches "ABC123").
- **MySQL Integration**: Stores truck records (plate number, truck ID, owner) and retrieves details for matches.
- **Modular Architecture**: Separates routes, database utilities, and search logic for maintainability.
- **API Endpoints**: Provides endpoints to search for plates and add new truck records.

## Search Algorithm

The backend implements Levenshtein Distance with a BK-Tree for efficient approximate string matching:

### Levenshtein Distance

- Measures the minimum number of single-character edits (insertions, deletions, substitutions) to transform one string into another.
- Example: Distance between "ABCI23" and "ABC123" is 1 (substitute "I" with "1").
- Time complexity: O(m * n) for two strings of lengths m and n.

### BK-Tree

- **Metric Tree**: Organizes strings based on their Levenshtein Distance from a root node.
- **Search Efficiency**: Uses the triangle inequality to prune branches during search, reducing the time complexity from O(n * m * k) (naive comparison with all database entries) to O(log n) on average for a database of n plates.
- **Example**: Searching "ABCI23" with a max distance of 2 quickly returns "ABC123" (distance 1) by avoiding unnecessary comparisons.
- **Initialization**: The BK-Tree is initialized with all plate numbers from the database on startup and updated when new trucks are added.

## Project Structure

The project structure includes the following files and directories:

- `main.py` - Flask app entry point
- `routes.py` - API routes
- `bk_tree.py` - BK-Tree and Levenshtein Distance implementation
- `models` - Yolov8 trained with custom dataset
- `db.py` - MySQL database utilities
- `config.py` - Configuration (e.g., MySQL credentials)
- `requirements.txt` - Dependencies
- `README.md` - Documentation

## Setup Instructions

### Prerequisites

- `Python 3.8+`
- `MySQL 8.0+`
- `easyOCR`
- `flask`
- `ultralytics` (for YOLOv8)
- `easyocr`
- `opencv-python`
- `mysql-connector-python`
- `numpy`

1. **Clone the Repository**

   ```sh
   git clone <repository-url>
   cd truck_plate_backend

2. **Set Up Virtual Environment**
   
   Create a virtual environment to isolate dependencies:
   
   ```
   python -m venv venv
   ```
   
   Activate the virtual environment
   - On Windows:
   ```
   venv\Scripts\activate
   ```
   
   - On macOS/Linux:
   ```
   source venv/bin/activate
   ```
   
   After activation, your terminal prompt should change (e.g., ``(venv)``), indicating you're in the virtual environment
     
4. **Install Dependencies**

   ```sh
   pip install -r requirements.txt

5. ***Configure MySQL***

   ***Create Database***:
   ```sql
   CREATE DATABASE trucks_db;
   USE trucks_db;
      
   CREATE TABLE trucks (
     plate_number VARCHAR(20) PRIMARY KEY,
     truck_id VARCHAR(50) NOT NULL,
     owner VARCHAR(100)
   );
      
   -- Sample data
   INSERT INTO trucks (plate_number, truck_id, owner) VALUES
   ('5YDR119', 'T005', 'Meme Stark');
   ```

   **Start Xampp**
   - Start XAMPP, ensure MySQL is running.
   - Open http://localhost/phpmyadmin, and log in
   - Create trucks_db and run the above SQL in the “SQL” tab
   - Update config.py with your MySQL credentials:
     
   ```
      DB_CONFIG = {
        'host': '127.0.0.1',
        'user': 'root',
        'password': '',
        'database': 'trucks_db'
      }
   ```
   
6. **Run the Backend**

   ```sh
   python main.py

The server will start at ``http://localhost:5000`` in debug mode. Ensure XAMPP’s MySQL is running if using it

### API Endpoints
***POST /api/scan_plate***
- ***Description***: This route would receive an image, along with a max_distance of 2 sent by the frontend. It consists of several functionalities: 1) Detect a number plates, 2) extract texts from the number plates, 3) search for truck records matching the provided plate number within a specified Levenshtein Distance tolerance.

  The curl command:
  ```
  curl -X POST http://localhost:5000/api/scan_plate \
  -F "image=@vehicle_image.jpg" \
  -F "max_distance=2"
  ```

  The Postman command:

  ![Postman setup](images/img-1.png)

***Response (200 OK):***
  ```
  {
    "results": [
        {
            "detected_plate": "ABC123",
            "matches": [
                {
                    "plate_number": "ABC123",
                    "truck_id": "T001",
                    "owner": "John Doe",
                    "status": "active",
                    "distance": 0,
                    "detected_plate": "ABC123"
                }
            ],
            "status": "registered"
        }
    ],
    "execution_time_ms": 305.2,
    "debug_info": {
        "annotated_image": "debug_output/annotated_1691234567.jpg",
        "cropped_plates": [
            "debug_output/plate_1691234567_0.jpg"
        ]
    }
}
```
Result (200) OK:

![My Image](images/img-2.png)




