from PIL import Image
import os

image_path = r"g:\Dropbox\Backup Photographer Pics\1171 S Splash Drive\002_dsc02663_859.jpg"

try:
    if os.path.exists(image_path):
        with Image.open(image_path) as img:
            print(f"Image found!")
            print(f"Format: {img.format}")
            print(f"Mode: {img.mode}")
            print(f"Size: {img.size[0]} x {img.size[1]} pixels")
            print(f"File size: {os.path.getsize(image_path) / 1024 / 1024:.2f} MB")
            
            # Check if it meets ReimagineHome requirements
            width, height = img.size
            print("\nReimagineHome Requirements Check:")
            print(f"Minimum size (512x512): {'✓ PASS' if width >= 512 and height >= 512 else '✗ FAIL'}")
            print(f"Maximum size (2048x2048): {'✓ PASS' if width <= 2048 and height <= 2048 else '✗ FAIL'}")
            
            if width > 2048 or height > 2048:
                print(f"\nImage needs to be resized!")
                print(f"Current: {width}x{height}")
                
                # Calculate new size maintaining aspect ratio
                ratio = min(2048/width, 2048/height)
                new_width = int(width * ratio)
                new_height = int(height * ratio)
                print(f"Recommended resize: {new_width}x{new_height}")
    else:
        print(f"Image not found at: {image_path}")
        print("Please check the file path")
        
except Exception as e:
    print(f"Error: {e}")