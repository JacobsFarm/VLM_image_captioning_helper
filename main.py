import os
import sys
import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from PIL import Image, ImageTk
import shutil
from pathlib import Path
import json

# Configuration - adjust these paths to match your project structure
input_folder = "annotate"  # Folder containing images to be annotated
output_folder_labels = "annotated_labels"  # Folder for JSON files
output_folder_images = "annotated_images"  # Folder for annotated images
delete_folder = "Delete"  # Folder for storing deleted/transferred images
enable_delete_mode = True  # Set to either False or True to enable image deletion functionality from start-up

# Predefined text blocks configuration
PREDEFINED_QUESTIONS = [
    "your question1",
    "your question2.",
    "your question3"
]

PREDEFINED_VIEWPOINTS = {
    "1": "mainline1",
    "2": "mainline2", 
    "3": "mainline3",
    "4": "mainline4"
}

PREDEFINED_DETAILS = {
    "1": "Extra line",
    "2": "Extra line",
    "3": "Extra line",
    "4": "Extra line",
    "5": "Extra line",
    "6": "Extra line",
    "7": "Extra line",
    "8": "Extra line"
}

class VLMAnnotationApp:
    def __init__(self, root, input_folder, output_folder_labels, output_folder_images, delete_folder, enable_delete_mode):
        self.root = root
        self.root.title("VLM Annotation Helper")
        self.root.geometry("1400x800")
        
        # Set up folders
        self.input_folder = input_folder
        self.output_folder_labels = output_folder_labels
        self.output_folder_images = output_folder_images
        self.delete_folder = delete_folder
        self.delete_mode_enabled = enable_delete_mode
        
        # Create output folders if they don't exist
        os.makedirs(self.output_folder_labels, exist_ok=True)
        os.makedirs(self.output_folder_images, exist_ok=True)
        os.makedirs(self.delete_folder, exist_ok=True)
        
        # Get all images
        self.image_files = [f for f in os.listdir(self.input_folder) 
                            if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        self.current_index = 0
        
        # Variables for annotation
        self.current_question = PREDEFINED_QUESTIONS[0]
        self.selected_viewpoint = ""
        self.selected_details = []
        self.current_img = None
        self.current_image_info = {}
        
        # UI setup
        self.setup_ui()
        
        # Load the first image
        if self.image_files:
            self.root.update_idletasks()
            self.root.after(100, self.load_current_image)
    
    def setup_ui(self):
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left side: Image display
        image_frame = ttk.LabelFrame(main_frame, text="Image")
        image_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.image_canvas = tk.Canvas(image_frame, highlightthickness=0, bg='white')
        self.image_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Right side: Annotation panel
        annotation_frame = ttk.LabelFrame(main_frame, text="Annotation")
        annotation_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        annotation_frame.config(width=500)
        
        # Question selection
        question_frame = ttk.LabelFrame(annotation_frame, text="Question Selection")
        question_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.question_var = tk.StringVar(value=self.current_question)
        for i, question in enumerate(PREDEFINED_QUESTIONS):
            ttk.Radiobutton(question_frame, text=f"{i+1}. {question}", 
                           variable=self.question_var, value=question,
                           command=self.update_question).pack(anchor=tk.W, padx=5, pady=2)
        
        # Custom question entry
        ttk.Label(question_frame, text="Or custom question:").pack(anchor=tk.W, padx=5)
        self.custom_question_entry = ttk.Entry(question_frame, width=50)
        self.custom_question_entry.pack(fill=tk.X, padx=5, pady=2)
        self.custom_question_entry.bind('<KeyRelease>', self.update_custom_question)
        
        # Viewpoint selection
        viewpoint_frame = ttk.LabelFrame(annotation_frame, text="Viewpoint (press number)")
        viewpoint_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.viewpoint_var = tk.StringVar()
        for key, value in PREDEFINED_VIEWPOINTS.items():
            ttk.Radiobutton(viewpoint_frame, text=f"{key}. {value}", 
                           variable=self.viewpoint_var, value=value,
                           command=self.update_viewpoint).pack(anchor=tk.W, padx=5, pady=2)
        
        # Details selection
        details_frame = ttk.LabelFrame(annotation_frame, text="Details (press number for selection)")
        details_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.detail_vars = {}
        for key, value in PREDEFINED_DETAILS.items():
            var = tk.BooleanVar()
            self.detail_vars[key] = var
            ttk.Checkbutton(details_frame, text=f"{key}. {value}", 
                           variable=var, command=self.update_details).pack(anchor=tk.W, padx=5, pady=2)
        
        # Preview of generated answer
        preview_frame = ttk.LabelFrame(annotation_frame, text="Answer Preview")
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.preview_text = scrolledtext.ScrolledText(preview_frame, height=8, wrap=tk.WORD)
        self.preview_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Control buttons
        button_frame = ttk.Frame(annotation_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Delete mode toggle checkbox
        self.delete_mode_var = tk.BooleanVar(value=self.delete_mode_enabled)
        self.delete_mode_checkbox = ttk.Checkbutton(
            button_frame, 
            text="Delete Mode", 
            variable=self.delete_mode_var,
            command=self.toggle_delete_mode
        )
        self.delete_mode_checkbox.pack(pady=5)
        
        # Navigation buttons
        nav_frame = ttk.Frame(button_frame)
        nav_frame.pack(fill=tk.X)
        
        ttk.Button(nav_frame, text="Previous (A)", command=self.prev_image).pack(side=tk.LEFT, padx=2)
        ttk.Button(nav_frame, text="Next (D)", command=self.next_image).pack(side=tk.LEFT, padx=2)
        ttk.Button(nav_frame, text="Save (S)", command=self.save_annotation).pack(side=tk.LEFT, padx=2)
        ttk.Button(nav_frame, text="Skip (O)", command=self.skip_current).pack(side=tk.LEFT, padx=2)
        
        # Status bar
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_label = ttk.Label(self.status_frame, text="")
        self.status_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Keyboard shortcuts
        self.setup_keyboard_shortcuts()
        
        # Initial preview update
        self.update_preview()
    
    def setup_keyboard_shortcuts(self):
        # Navigation
        self.root.bind("<a>", lambda event: self.prev_image())
        self.root.bind("<A>", lambda event: self.prev_image())
        self.root.bind("<Left>", lambda event: self.prev_image())
        
        self.root.bind("<d>", lambda event: self.next_image())
        self.root.bind("<D>", lambda event: self.next_image())
        self.root.bind("<Right>", lambda event: self.next_image())
        
        self.root.bind("<s>", lambda event: self.save_annotation())
        self.root.bind("<S>", lambda event: self.save_annotation())
        
        self.root.bind("<o>", lambda event: self.skip_current())
        self.root.bind("<O>", lambda event: self.skip_current())
        
        # Viewpoint selection
        for key in PREDEFINED_VIEWPOINTS.keys():
            self.root.bind(f"<{key}>", lambda event, k=key: self.select_viewpoint_by_key(k))
        
        # Details selection (Shift + number)
        for key in PREDEFINED_DETAILS.keys():
            self.root.bind(f"<Shift-{key}>", lambda event, k=key: self.toggle_detail_by_key(k))
        
        self.root.bind("<Q>", lambda event: self.root.quit())
        self.root.bind("<q>", lambda event: self.root.quit())
        self.root.bind("<Escape>", lambda event: self.root.quit())
    
    def select_viewpoint_by_key(self, key):
        if key in PREDEFINED_VIEWPOINTS:
            self.viewpoint_var.set(PREDEFINED_VIEWPOINTS[key])
            self.update_viewpoint()
    
    def toggle_detail_by_key(self, key):
        if key in self.detail_vars:
            current_value = self.detail_vars[key].get()
            self.detail_vars[key].set(not current_value)
            self.update_details()
    
    def toggle_delete_mode(self):
        """Toggle delete mode on/off"""
        self.delete_mode_enabled = self.delete_mode_var.get()
        
        # Update the current status display
        if self.image_files:
            status_text = f"Image {self.current_index + 1} of {len(self.image_files)}: {self.image_files[self.current_index]}"
            if self.delete_mode_enabled:
                status_text += " | Delete mode: ON - processed images will be moved"
            self.status_label.config(text=status_text)
    
    def move_to_delete_if_enabled(self, img_filename):
        """Move image to DELETE folder if delete mode is enabled"""
        if not self.delete_mode_enabled:
            return False
            
        source_path = os.path.join(self.input_folder, img_filename)
        dest_path = os.path.join(self.delete_folder, img_filename)
        
        try:
            # Move the image to the DELETE folder
            shutil.move(source_path, dest_path)
            print(f"Image moved to DELETE: {img_filename}")
            return True
        except Exception as e:
            print(f"Error moving to DELETE: {e}")
            return False
    
    def copy_image_to_annotated(self, img_filename):
        """Copy image to annotated_images folder"""
        source_path = os.path.join(self.input_folder, img_filename)
        dest_path = os.path.join(self.output_folder_images, img_filename)
        
        try:
            # Copy the image to the annotated_images folder
            shutil.copy2(source_path, dest_path)
            print(f"Image copied to annotated_images: {img_filename}")
            return True
        except Exception as e:
            print(f"Error copying to annotated_images: {e}")
            return False
    
    def load_current_image(self):
        if not self.image_files:
            self.status_label.config(text="No images found!")
            return
        
        # Update status
        status_text = f"Image {self.current_index + 1} of {len(self.image_files)}: {self.image_files[self.current_index]}"
        if self.delete_mode_enabled:
            status_text += " | Delete mode: ON - processed images will be moved"
        self.status_label.config(text=status_text)
        
        # Load image
        img_path = os.path.join(self.input_folder, self.image_files[self.current_index])
        self.current_img_path = img_path
        
        # Load and display image
        original_img = cv2.imread(img_path)
        original_img = cv2.cvtColor(original_img, cv2.COLOR_BGR2RGB)
        self.current_img = original_img
        
        self.display_image(original_img, self.image_canvas)
        
        # Reset selections for new image
        self.reset_selections()
    
    def display_image(self, cv_img, canvas):
        """Displays an image centered on the canvas"""
        canvas_width = canvas.winfo_width() or 600
        canvas_height = canvas.winfo_height() or 600
        
        height, width = cv_img.shape[:2]
        
        # Calculate scale factor
        scale = min(canvas_width / width, canvas_height / height) * 0.9
        
        new_width = int(width * scale)
        new_height = int(height * scale)
        
        if scale != 1.0:
            cv_img = cv2.resize(cv_img, (new_width, new_height))
        
        # Convert to PIL and then to Tkinter format
        pil_img = Image.fromarray(cv_img)
        tk_img = ImageTk.PhotoImage(pil_img)
        
        # Clear canvas and add image
        canvas.delete("all")
        
        x_offset = (canvas_width - new_width) // 2
        y_offset = (canvas_height - new_height) // 2
        
        canvas.create_image(x_offset, y_offset, anchor=tk.NW, image=tk_img)
        canvas.image = tk_img
    
    def reset_selections(self):
        """Reset all selections for a new image"""
        self.viewpoint_var.set("")
        for var in self.detail_vars.values():
            var.set(False)
        self.custom_question_entry.delete(0, tk.END)
        self.question_var.set(PREDEFINED_QUESTIONS[0])
        self.current_question = PREDEFINED_QUESTIONS[0]
        self.update_preview()
    
    def update_question(self):
        self.current_question = self.question_var.get()
        self.custom_question_entry.delete(0, tk.END)
        self.update_preview()
    
    def update_custom_question(self, event=None):
        custom_text = self.custom_question_entry.get().strip()
        if custom_text:
            self.current_question = custom_text
            self.question_var.set("")  # Deselect radio buttons
        self.update_preview()
    
    def update_viewpoint(self):
        self.selected_viewpoint = self.viewpoint_var.get()
        self.update_preview()
    
    def update_details(self):
        self.selected_details = []
        for key, var in self.detail_vars.items():
            if var.get():
                self.selected_details.append(PREDEFINED_DETAILS[key])
        self.update_preview()
    
    def update_preview(self):
        """Update the preview of the generated answer"""
        answer_parts = []
        
        if self.selected_viewpoint:
            answer_parts.append(self.selected_viewpoint)
        
        if self.selected_details:
            detail_text = ", ".join(self.selected_details)
            if answer_parts:
                answer_parts.append(f", {detail_text}")
            else:
                answer_parts.append(detail_text.capitalize())
        
        if answer_parts:
            full_answer = "".join(answer_parts) + "."
        else:
            full_answer = "No details selected yet."
        
        self.preview_text.delete(1.0, tk.END)
        self.preview_text.insert(1.0, full_answer)
    
    def generate_json_data(self):
        """Generate the JSON data structure for the current annotation"""
        img_filename = self.image_files[self.current_index]
        base_name = os.path.splitext(img_filename)[0]
        
        # Get the current answer from preview
        answer = self.preview_text.get(1.0, tk.END).strip()
        
        # Create the JSON structure with relative path to annotated_images
        json_data = {
            "id": base_name,
            "image": os.path.join(self.output_folder_images, img_filename),
            "conversations": [
                {
                    "from": "human", 
                    "value": f"<image>\n{self.current_question}"
                },
                {
                    "from": "gpt",
                    "value": answer
                }
            ]
        }
        
        return json_data
    
    def save_annotation(self):
        """Save the current annotation as a JSON file and copy image to annotated_images"""
        if not self.image_files:
            return
        
        # Check if we have any content to save
        answer = self.preview_text.get(1.0, tk.END).strip()
        if not answer or answer == "No details selected yet.":
            messagebox.showwarning("Warning", "Please select some details before saving.")
            return
        
        # Generate JSON data
        json_data = self.generate_json_data()
        
        # Get filenames
        img_filename = self.image_files[self.current_index]
        base_name = os.path.splitext(img_filename)[0]
        json_filename = f"{base_name}.json"
        json_path = os.path.join(self.output_folder_labels, json_filename)
        
        try:
            # Save JSON file to annotated_label folder
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            
            # Copy image to annotated_images folder
            self.copy_image_to_annotated(img_filename)
            
            # Move to DELETE folder if delete mode is enabled
            self.move_to_delete_if_enabled(img_filename)
            
            self.status_label.config(text=f"Annotation saved: {json_filename} | Image copied to annotated_images")
            self.next_image()
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not save annotation: {str(e)}")
    
    def skip_current(self):
        """Skip the current image"""
        img_filename = self.image_files[self.current_index]
        
        # Move to DELETE folder if delete mode is enabled
        self.move_to_delete_if_enabled(img_filename)
        
        self.status_label.config(text=f"Image skipped: {img_filename}")
        self.next_image()
    
    def next_image(self):
        if self.current_index < len(self.image_files) - 1:
            self.current_index += 1
            self.load_current_image()
        else:
            messagebox.showinfo("Complete", "All images have been processed!")
    
    def prev_image(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.load_current_image()

def main():
    # Start the application
    root = tk.Tk()
    app = VLMAnnotationApp(root, input_folder, output_folder_labels, output_folder_images, delete_folder, enable_delete_mode)
    root.mainloop()

if __name__ == "__main__":
    main()
