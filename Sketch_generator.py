import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import numpy as np

class ImageConverterApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Sketch Converter")
        self.master.configure(background='#f0f0f0')

        # Initialize variables
        self.filepath = None
        self.processed_image = None
        

        # Header Label
        self.header_label = tk.Label(master, text="Image to Sketch Converter", font=("Helvetica", 20), bg='#f0f0f0', fg='#333333')
        self.header_label.pack(pady=10)

        # Frame for Upload Section
        self.upload_frame = tk.Frame(master, bg='#f0f0f0')
        self.upload_frame.pack(pady=10)

        self.upload_label = tk.Label(self.upload_frame, text="Select Image", font=("Helvetica", 12), bg='#f0f0f0', fg='#333333')
        self.upload_label.grid(row=0, column=0, padx=5)

        self.upload_button = tk.Button(self.upload_frame, text="Upload Image", font=("Helvetica", 12), bg='#4287f5', fg='white', command=self.upload_image)
        self.upload_button.grid(row=0, column=1, padx=5)

        # Frame for Sketch Settings
        self.sketch_frame = tk.Frame(master, bg='#f0f0f0')
        self.sketch_frame.pack(pady=10)

        self.sketch_label = tk.Label(self.sketch_frame, text="Sketch Settings", font=("Helvetica", 16), bg='#f0f0f0', fg='#333333')
        self.sketch_label.grid(row=0, columnspan=2, pady=5)

        self.contrast_label = tk.Label(self.sketch_frame, text="Contrast", font=("Helvetica", 12), bg='#f0f0f0', fg='#333333')
        self.contrast_label.grid(row=1, column=0, padx=5, pady=5)
        self.contrast_slider = tk.Scale(self.sketch_frame, from_=1, to=10, orient=tk.HORIZONTAL, bg='#f0f0f0', fg='#4287f5', command=self.update_contrast)
        self.contrast_slider.grid(row=1, column=1, padx=5, pady=5)

        self.brightness_label = tk.Label(self.sketch_frame, text="Brightness", font=("Helvetica", 12), bg='#f0f0f0', fg='#333333')
        self.brightness_label.grid(row=2, column=0, padx=5, pady=5)
        self.brightness_slider = tk.Scale(self.sketch_frame, from_=1, to=100, orient=tk.HORIZONTAL, bg='#f0f0f0', fg='#4287f5', command=self.update_brightness)
        self.brightness_slider.grid(row=2, column=1, padx=5, pady=5)

        # Frame for Output Format
        self.output_frame = tk.Frame(master, bg='#f0f0f0')
        self.output_frame.pack(pady=10)

        self.output_label = tk.Label(self.output_frame, text="Output Format", font=("Helvetica", 16), bg='#f0f0f0', fg='#333333')
        self.output_label.grid(row=0, columnspan=2, pady=5)

        self.output_var = tk.StringVar(master)
        self.output_var.set("Select format")
        self.output_dropdown = tk.OptionMenu(self.output_frame, self.output_var, "JPG", "PNG")
        self.output_dropdown.config(font=("Helvetica", 12), bg='#f0f0f0', fg='#4287f5', width=15)
        self.output_dropdown.grid(row=1, columnspan=2, pady=5)

        # Save Button
        self.save_button = tk.Button(master, text="Save Image", font=("Helvetica", 12), bg='#4287f5', fg='white', command=self.save_image)
        self.save_button.pack(pady=10)

        # Frame for Preview
        self.preview_frame = tk.Frame(master, bg='#f0f0f0')
        self.preview_frame.pack(pady=10)

        self.preview_label = tk.Label(self.preview_frame, bg='white', width=200, height=200)
        self.preview_label.grid(row=0, column=0, padx=10)

        self.update_preview()  # Update preview initially

    def upload_image(self):
        self.filepath = filedialog.askopenfilename(filetypes=[('PNG', '.png'), ('JPG', '.jpg'), ('JPEG', '.jpeg') , ('GIF', '.gif')])
        if self.filepath:
            self.process_image()

    def process_image(self):
        if not self.filepath:
            messagebox.showerror("Error", "Please upload an image first.")
            return
        
        try:
            img = Image.open(self.filepath)
            img_np = np.array(img)

            contrast_value = self.contrast_slider.get()
            brightness_value = self.brightness_slider.get()

            # Apply contrast adjustment
            contrast_img = cv2.convertScaleAbs(img_np, alpha=contrast_value/10)

            # Apply brightness adjustment
            brightness_img = cv2.add(contrast_img, np.array([brightness_value]))

            # Convert to grayscale
            grey_img = cv2.cvtColor(brightness_img, cv2.COLOR_BGR2GRAY)

            # Sketch transformation
            invert = cv2.bitwise_not(grey_img)
            blur = cv2.GaussianBlur(invert, (25, 25), 5)
            invertedblur = cv2.bitwise_not(blur)
            sketch = cv2.divide(grey_img, invertedblur, scale=250.0)

            # Update preview with processed image
            self.update_preview(Image.fromarray(sketch))
            self.processed_image = Image.fromarray(sketch)

        except Exception as e:
            messagebox.showerror("Error", f"Unsupported Picture Format: {e}")

    def save_image(self):
        # Ensure a file has been selected
        if not self.filepath:
            messagebox.showerror("Error", "Please upload an image first.")
            return

        # Prompt user to select output file format
        output_format = self.output_var.get()

        # Define supported formats and corresponding extensions
        supported_formats = {"JPG": ".jpg", "PNG": ".png"}

        # Ensure selected format is supported
        if output_format not in supported_formats:
            messagebox.showerror("Error", "Unsupported output format.")
            return

        # Prompt user for destination file path
        save_path = filedialog.asksaveasfilename(defaultextension=supported_formats[output_format])

        # Check if user canceled the save operation
        if save_path == "":
            return

        try:
            # Ensure processed image is available
            if self.processed_image is None:
                messagebox.showerror("Error", "No processed image available.")
                return

            # Save the processed image
            self.processed_image.save(save_path)
            messagebox.showinfo("Success", "Image saved successfully.")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save image: {e}")

    def update_preview(self, img=Image.open("icon.png")):
        # Resize the image to fit in the preview area
        img.thumbnail((200, 200))
        # Convert the image to ImageTk format for tkinter
        img_tk = ImageTk.PhotoImage(img)
        # Update the label with the new preview image
        self.preview_label.configure(image=img_tk)
        self.preview_label.image = img_tk

    def update_contrast(self, event):
        self.process_image()

    def update_brightness(self, event):
        self.process_image()

def main():
    root = tk.Tk()
    app = ImageConverterApp(root)
    root.geometry("500x700")
    root.mainloop()

if __name__ == "__main__":
    main()
