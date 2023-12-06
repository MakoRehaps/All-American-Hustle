import os
from PIL import Image

# Define the input and output folders
input_folder1 = "input1"
input_folder2 = "input2"
output_folder = "output"

# Function to resize and save an image
def resize_and_save(input_path, output_path, size):
    img = Image.open(input_path)
    img = img.resize(size, Image.LANCZOS)  # Use LANCZOS for resizing
    os.makedirs(os.path.dirname(output_path), exist_ok=True)  # Create subdirectories as needed
    img.save(output_path)

# Function to get image sizes from a directory
def get_image_sizes(input_dir):
    sizes = {}
    for root, _, files in os.walk(input_dir):
        for file in files:
            try:
                img = Image.open(os.path.join(root, file))
                sizes[file] = img.size  # Store size with filename as key
            except Exception as e:
                print(f"Skipping non-image file: {file}")
    return sizes

# Get sizes of images in input_folder1
sizes_input1 = get_image_sizes(input_folder1)

# Function to process and resize images in input_folder2 based on sizes from input_folder1
def process_and_resize(input_dir, output_dir, sizes):
    for root, _, files in os.walk(input_dir):
        for file in files:
            input_path = os.path.join(root, file)
            try:
                img = Image.open(input_path)
            except Exception as e:
                print(f"Skipping non-image file: {input_path}")
                continue

            # Resize based on size from input_folder1, if available
            size = sizes.get(file, img.size)
            
            relative_path = os.path.relpath(input_path, input_dir)
            output_path = os.path.join(output_dir, relative_path)

            resize_and_save(input_path, output_path, size)
            print(f"Resized {file} and saved: {output_path}")

# Resize images in input_folder2 based on sizes from input_folder1
process_and_resize(input_folder2, os.path.join(output_folder, input_folder2), sizes_input1)

print("Image resizing complete.")
