# routes.py - Defines the API endpoints
from flask import request, jsonify
import time
import os
from ultralytics import YOLO
import easyocr
import cv2
import numpy as np
from db import get_db_connection

# Initialize YOLOv8 with a custom-trained model
yolo_model = YOLO('models/best (1).pt')  # Path to the downloaded best.pt
reader = easyocr.Reader(['en'])  # EasyOCR for English

# Directory to save debug images
DEBUG_DIR = "debug_output"
if not os.path.exists(DEBUG_DIR):
    os.makedirs(DEBUG_DIR)

def detect_plates(image, image_id="unknown"):
    """Detect number plates in the image using YOLOv8 and save results with annotated image."""
    # Predict using YOLOv8
    results = yolo_model.predict(image, conf=0.25, iou=0.45)
    plates_detected = []

    # Create a copy of the image to draw bounding boxes
    annotated_image = image.copy()
    if annotated_image is None:
        print("Error: Failed to create annotated image copy")
        return plates_detected

    # Counter for detected plates
    plate_count = 0

    for result in results:
        boxes = result.boxes
        print(f"Number of detected boxes: {len(boxes)}")

        for box in boxes:
            class_id = int(box.cls)
            confidence = float(box.conf)
            print(f"Box: Class ID={class_id}, Confidence={confidence:.2f}")

            if class_id == 0:  # Assuming "number_plate" is class 0
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                print(f"Plate {plate_count} coordinates: ({x1}, {y1}, {x2}, {y2})")

                # Validate coordinates
                if x1 >= x2 or y1 >= y2 or x1 < 0 or y1 < 0 or x2 > image.shape[1] or y2 > image.shape[0]:
                    print(f"Warning: Invalid coordinates for plate {plate_count}: ({x1}, {y1}, {x2}, {y2})")
                    continue

                # Crop the plate image
                plate_img = image[y1:y2, x1:x2]
                if plate_img.size == 0:
                    print(f"Warning: Cropped plate {plate_count} is empty (size=0)")
                    continue

                # Save the cropped plate image
                plate_filename = os.path.join(DEBUG_DIR, f"plate_{image_id}_{plate_count}.jpg")
                cv2.imwrite(plate_filename, plate_img)
                print(f"Saved cropped plate: {plate_filename}")

                # Draw bounding box on the annotated image
                cv2.rectangle(annotated_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
                label = f"Plate {plate_count} ({confidence:.2f})"
                cv2.putText(annotated_image, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                print(f"Drew rectangle for plate {plate_count} at ({x1}, {y1}, {x2}, {y2})")

                plates_detected.append(plate_img)
                plate_count += 1

    # Ensure something was drawn before saving
    if plate_count == 0:
        print("No valid plates detected to annotate")
    else:
        # Save the annotated image with bounding boxes
        annotated_filename = os.path.join(DEBUG_DIR, f"annotated_{image_id}.jpg")
        cv2.imwrite(annotated_filename, annotated_image)
        print(f"Saved annotated image: {annotated_filename}")

    return plates_detected

def extract_text(plates_detected, image_id="unknown"):
    """Extract text from detected plates using EasyOCR."""
    detected_plates = []
    for i, plate_img in enumerate(plates_detected):
        try:
            if plate_img is None or plate_img.size == 0:
                print(f"Error: Plate image {i} (image_id={image_id}) is empty or None")
                continue

            plate_img = cv2.cvtColor(plate_img, cv2.COLOR_BGR2RGB)
            plate_img = cv2.convertScaleAbs(plate_img, alpha=1.5, beta=20)

            ocr_result = reader.readtext(plate_img)
            print(f"OCR result for plate {i} (image_id={image_id}): {ocr_result}")

            if ocr_result:
                best_result = max(ocr_result, key=lambda x: x[2])
                text = best_result[1].strip()
                confidence = best_result[2]
                print(f"Detected plate {i} (image_id={image_id}): '{text}' (confidence: {confidence:.2f})")
                detected_plates.append(text)
            else:
                print(f"No text detected for plate {i} (image_id={image_id})")

        except Exception as e:
            print(f"Error processing plate {i} (image_id={image_id}): {str(e)}")
            continue

    return detected_plates

def search_plate_info(plate_text, bk_tree, max_dist, cursor):
    """Search BK-Tree and database for plate information."""
    matches = bk_tree.search(plate_text, max_dist)
    plate_results = []

    for plate, distance in matches:
        cursor.execute(
            "SELECT plate_number, truck_id, owner FROM trucks WHERE plate_number = %s",
            (plate,)
        )
        truck_data = cursor.fetchone()
        if truck_data:
            truck_data['distance'] = distance
            truck_data['detected_plate'] = plate_text
            plate_results.append(truck_data)

    return {
        "detected_plate": plate_text,
        "matches": plate_results,
        "status": "registered" if plate_results else "unregistered"
    }

def process_image_file(image_file):
    """Convert uploaded image file to OpenCV format."""
    img_array = np.frombuffer(image_file.read(), np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Invalid image format")
    return img

def init_routes(app, bk_tree):
    @app.route('/api/scan_plate', methods=['POST'])
    def scan_plate():
        start_time = time.time()

        if 'image' not in request.files:
            return jsonify({"error": "No image file provided"}), 400

        image_file = request.files['image']
        max_dist = request.form.get('max_distance', 2, type=int)

        # Generate a unique image ID (e.g., timestamp) for debugging
        image_id = str(int(time.time()))

        try:
            img = process_image_file(image_file)

            # Detect plates with debugging
            plates_detected = detect_plates(img, image_id)
            if not plates_detected:
                return jsonify({"error": "No number plates detected"}), 404

            # Extract text with debugging
            detected_plates = extract_text(plates_detected, image_id)
            if not detected_plates:
                return jsonify({"error": "No text extracted from plates"}), 404

            # Database connection
            connection = get_db_connection()
            if not connection:
                return jsonify({"error": "Database connection failed"}), 500

            cursor = connection.cursor(dictionary=True)
            results = [search_plate_info(plate_text, bk_tree, max_dist, cursor)
                       for plate_text in detected_plates]

            cursor.close()
            connection.close()

            end_time = time.time()
            execution_time = end_time - start_time
            response = {
                "results": results,
                "execution_time_ms": execution_time * 1000,
                "debug_info": {
                    "annotated_image": f"debug_output/annotated_{image_id}.jpg",
                    "cropped_plates": [f"debug_output/plate_{image_id}_{i}.jpg" for i in range(len(plates_detected))]
                }
            }
            return jsonify(response), 200

        except ValueError as ve:
            return jsonify({"error": str(ve)}), 400
        except Exception as e:
            return jsonify({"error": f"Processing failed: {str(e)}"}), 500
