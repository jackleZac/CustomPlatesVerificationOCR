import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk
import cv2
from routes import detect_plates, extract_text

# Global BKTree instance
bk_tree = None

def upload_image():
    """ Opens file dialog to select an image and processes it """
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.png;*.jpeg")])
    if not file_path:
        return
    
    # Load image with OpenCV
    image = cv2.imread(file_path)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image_pil = Image.fromarray(image_rgb)

    # Adjust image size dynamically while keeping the aspect ratio
    max_width, max_height = 600, 400  # Increase max preview size
    image_pil.thumbnail((max_width, max_height), Image.LANCZOS)  # Maintain aspect ratio

    # Convert image for Tkinter
    photo = ImageTk.PhotoImage(image_pil)
    
    # Update image preview
    image_label.config(image=photo, width=photo.width(), height=photo.height())
    image_label.image = photo

    status_label.config(text="🔄 Processing image...", foreground="#FFD700")  # Gold color status
    root.update_idletasks()

    progress_bar.start(10)  # Start progress animation
    root.after(500, lambda: process_image(file_path, image))  # Delay for effect


def process_image(file_path, image):
    """ Detects plates and extracts text, then updates GUI """
    global bk_tree  

    plates_detected = detect_plates(image)
    detected_texts = extract_text(plates_detected)

    results_text.delete(1.0, tk.END)  # Clear previous results
    progress_bar.stop()  # Stop progress animation
    
    if detected_texts:
        results_text.insert(tk.END, "🔍 PLATES DETECTED:\n\n", "bold")
        for text in detected_texts:
            results_text.insert(tk.END, f"📌 Plate: {text}\n", "plate")
            
            if bk_tree:
                matches = bk_tree.search(text, 2)
                if matches:
                    results_text.insert(tk.END, "✅ POSSIBLE MATCHES:\n", "match")
                    for match in matches:
                        results_text.insert(tk.END, f"   - {match[0]} (Distance: {match[1]})\n", "match_detail")
                else:
                    results_text.insert(tk.END, "⚠️ No close matches found in database.\n", "error")
            else:
                results_text.insert(tk.END, "⚠️ BK-Tree not initialized.\n", "error")
            results_text.insert(tk.END, "\n")  # Spacing
    else:
        results_text.insert(tk.END, "❌ No plates detected.", "error")

    status_label.config(text="✅ Processing complete!", foreground="#32CD32")  # Lime Green color

def run_gui(bk_tree_instance):
    """ Initializes and runs the GUI """
    global bk_tree, root
    bk_tree = bk_tree_instance  # Assign BKTree instance

    # 🏠 Main Window
    root = tk.Tk()
    root.title("🚗 Number Plate Recognition")
    root.geometry("700x850")
    root.configure(bg="#1E1E2E")  # Dark theme

    # 📌 Header Frame
    header_frame = tk.Frame(root, bg="#252542", pady=10, padx=20)
    header_frame.pack(fill="x")

    header_label = tk.Label(header_frame, text="🔎 Number Plate Recognition", 
                            font=("Arial", 20, "bold"), fg="white", bg="#252542")
    header_label.pack()

    # 🖼️ Image Frame (BIGGER)
    image_frame = tk.Frame(root, bg="#1E1E2E", pady=10)
    image_frame.pack()

    global image_label
    image_label = tk.Label(image_frame, bg="#2C2F33", width=75, height=30, relief=tk.SUNKEN)
    image_label.pack(pady=10)

    # 📂 Upload Button (Modern Style)
    upload_btn = tk.Button(root, text="📂 Upload Image", command=upload_image, 
                           font=("Arial", 14, "bold"), bg="#007BFF", fg="white", 
                           padx=30, pady=12, border=0, cursor="hand2", relief=tk.RAISED)
    upload_btn.pack(pady=10)

    # 🔄 Status Label
    global status_label
    status_label = tk.Label(root, text="Awaiting image...", font=("Arial", 12, "italic"), fg="lightgray", bg="#1E1E2E")
    status_label.pack()

    # ⏳ Progress Bar
    global progress_bar
    progress_bar = ttk.Progressbar(root, orient="horizontal", mode="indeterminate", length=400)
    progress_bar.pack(pady=5)

    # 📋 Results Section with GLASSMORPHISM Effect
    results_frame = tk.Frame(root, bg="#1E1E2E", pady=10)
    results_frame.pack(fill="both", expand=True, padx=20, pady=10)

    results_canvas = tk.Canvas(results_frame, bg="#252542", highlightthickness=0, relief="ridge")
    results_canvas.pack(fill="both", expand=True)

    results_text_frame = tk.Frame(results_canvas, bg="#3B3E45", bd=2, relief="ridge")
    results_text_frame.pack(fill="both", expand=True, padx=5, pady=5)

    global results_text
    results_text = tk.Text(results_text_frame, height=15, width=80, wrap="word", font=("Arial", 12), bd=0, bg="#3B3E45", fg="white")
    results_text.pack(pady=10, padx=10, fill="both", expand=True)

    # 🎨 Text Styling
    results_text.tag_configure("bold", font=("Arial", 12, "bold"))
    results_text.tag_configure("plate", foreground="cyan", font=("Arial", 12, "bold"))
    results_text.tag_configure("match", foreground="lightgreen", font=("Arial", 12, "bold"))
    results_text.tag_configure("match_detail", foreground="lightgreen")
    results_text.tag_configure("error", foreground="red", font=("Arial", 12, "bold"))

    root.mainloop()
