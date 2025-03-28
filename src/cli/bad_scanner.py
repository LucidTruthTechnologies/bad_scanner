#!/usr/bin/env python3
import random
from pdf2image import convert_from_path
from PIL import Image, ImageFilter, ImageDraw, ImageEnhance
from pathlib import Path

# --------- Overlay Suite ---------

def generate_dust_spots(draw, width, height, dust_density, dust_min_radius, dust_max_radius, dust_alpha_min, dust_alpha_max):
    """
    Generate dark dust spots on the overlay.
    """
    num_dust_spots = int((width * height) // (200 * 200) * dust_density)
    for _ in range(num_dust_spots):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        radius = random.randint(dust_min_radius, dust_max_radius)
        alpha = random.randint(dust_alpha_min, dust_alpha_max)
        draw.ellipse((x, y, x + radius, y + radius), fill=(0, 0, 0, alpha))


def generate_curved_scratches(draw, width, height, scratch_count, scratch_line_width_min, scratch_line_width_max, scratch_alpha_min, scratch_alpha_max):
    """
    Generate curved scratches on the overlay.
    """
    for _ in range(scratch_count):
        start = (random.randint(0, width - 1), random.randint(0, height - 1))
        end = (random.randint(0, width - 1), random.randint(0, height - 1))
        num_points = random.randint(3, 6)  # total points including start and end
        points = [start]
        for i in range(1, num_points - 1):
            fraction = i / (num_points - 1)
            base_x = start[0] + fraction * (end[0] - start[0])
            base_y = start[1] + fraction * (end[1] - start[1])
            offset_range = 10  # controls the amplitude of the curve
            new_x = int(base_x + random.randint(-offset_range, offset_range))
            new_y = int(base_y + random.randint(-offset_range, offset_range))
            points.append((new_x, new_y))
        points.append(end)
        line_width = random.randint(scratch_line_width_min, scratch_line_width_max)
        alpha = random.randint(scratch_alpha_min, scratch_alpha_max)
        draw.line(points, fill=(0, 0, 0, alpha), width=line_width)


def generate_overlay(width, height,
                     dust_density=1.0, dust_min_radius=1, dust_max_radius=5,
                     dust_alpha_min=30, dust_alpha_max=100,
                     scratch_count=3, scratch_line_width_min=1, scratch_line_width_max=3,
                     scratch_alpha_min=50, scratch_alpha_max=150):
    """
    Generate an overlay image (RGBA) containing dark dust spots and curved scratches.
    """
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Generate dust spots
    generate_dust_spots(draw, width, height, dust_density, dust_min_radius, dust_max_radius, dust_alpha_min, dust_alpha_max)

    # Generate curved scratches
    generate_curved_scratches(draw, width, height, scratch_count, scratch_line_width_min, scratch_line_width_max, scratch_alpha_min, scratch_alpha_max)

    return overlay


# --------- Effects ---------

def apply_basic_enhancements(page, blur_radius, contrast, sharpness):
    """Apply basic image enhancements: blur, contrast, and sharpness."""
    processed = page.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    processed = ImageEnhance.Contrast(processed).enhance(contrast)
    processed = ImageEnhance.Sharpness(processed).enhance(sharpness)
    return processed


def add_paper_border(image, blur_radius):
    """Add a thin black border to simulate paper edge."""
    width, height = image.size
    border_overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw_border = ImageDraw.Draw(border_overlay)
    draw_border.rectangle((0, 0, width - 1, height - 1), outline=(0, 0, 0, 255), width=2)
    border_overlay_blurred = border_overlay.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    return Image.alpha_composite(image.convert("RGBA"), border_overlay_blurred)


def rotate_and_adjust_brightness(image, rotation_angle, brightness_factor):
    """Rotate the image and adjust its brightness."""
    rotated = image.rotate(rotation_angle, expand=True, fillcolor=(255, 255, 255))
    brightness_enhancer = ImageEnhance.Brightness(rotated)
    return brightness_enhancer.enhance(brightness_factor)


def apply_scanner_effects(image, blur_radius, dust_density, dust_min_radius, dust_max_radius, 
                          dust_alpha_min, dust_alpha_max, scratch_count, scratch_line_width_min, 
                          scratch_line_width_max, scratch_alpha_min, scratch_alpha_max):
    """Apply scanner effects (dust and scratches) to the image."""
    width, height = image.size
    overlay = generate_overlay(
        width, height,
        dust_density=dust_density,
        dust_min_radius=dust_min_radius,
        dust_max_radius=dust_max_radius,
        dust_alpha_min=dust_alpha_min,
        dust_alpha_max=dust_alpha_max,
        scratch_count=scratch_count,
        scratch_line_width_min=scratch_line_width_min,
        scratch_line_width_max=scratch_line_width_max,
        scratch_alpha_min=scratch_alpha_min,
        scratch_alpha_max=scratch_alpha_max
    )
    overlay_blurred = overlay.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    combined = Image.alpha_composite(image.convert("RGBA"), overlay_blurred)
    return combined.convert("RGB")


# --------- Utility Functions ---------

def set_random_seed(seed):
    """
    Set the random seed for reproducibility if a seed is provided.
    
    Args:
        seed: The random seed value or None
    """
    if seed is not None:
        random.seed(seed)
    

def convert_pdf_to_images(pdf_path):
    """Convert PDF pages to images and handle any errors."""
    print("Converting PDF pages to images...")
    try:
        pages = convert_from_path(pdf_path)
        if not pages:
            print("No pages found in the PDF.")
            return None
        return pages
    except Exception as e:
        print(f"Error converting PDF: {e}")
        return None


def save_pdf(images, output_path):
    """Save a list of images as a PDF file."""
    if not images:
        print("No pages were processed. Exiting.")
        return False
    
    print(f"Saving processed pages to {output_path}...")
    try:
        images[0].save(
            output_path,
            "PDF",
            resolution=100.0,
            save_all=True,
            append_images=images[1:]
        )
        print("PDF created successfully.")
        return True
    except Exception as e:
        print(f"Error saving output PDF: {e}")
        return False


def process_page(page, idx, total_pages, blur_radius, contrast, sharpness, rotate, brightness, 
                dust_density, dust_min_radius, dust_max_radius, dust_alpha_min, dust_alpha_max,
                scratch_count, scratch_line_width_min, scratch_line_width_max, scratch_alpha_min, 
                scratch_alpha_max):
    """Process a single page with all effects."""
    print(f"Processing page {idx+1}/{total_pages}...")
    
    # Apply basic enhancements
    processed = apply_basic_enhancements(page, blur_radius, contrast, sharpness)
    
    # Add paper border
    processed_with_border = add_paper_border(processed, blur_radius)
    
    # Rotate and adjust brightness
    rotated_bright = rotate_and_adjust_brightness(processed_with_border, rotate, brightness)
    
    # Apply scanner effects
    final_image = apply_scanner_effects(
        rotated_bright, blur_radius, dust_density, 
        dust_min_radius, dust_max_radius,
        dust_alpha_min, dust_alpha_max,
        scratch_count, scratch_line_width_min,
        scratch_line_width_max, scratch_alpha_min,
        scratch_alpha_max
    )
    
    return final_image


def process_dir(input_dir=r"data"):
    """
    Process all PDF files in the specified directory by applying random scanning effects.
    This function iterates through all PDF files in the input directory, applies various
    random effects (blur, dust, scratches, contrast adjustments, etc.) to simulate a
    scanned document appearance, and saves the processed files to an 'output' directory.
    Parameters
    ----------
    input_dir : Path, optional
        Directory containing PDF files to process. Defaults to 'data' directory.
    Notes
    -----
    - Random effects include: blur, dust particles, scratches, contrast, sharpness, 
      brightness, and slight rotation.
    - Processed files are saved with '_scan' appended to the original filename.
    - The output directory is created if it doesn't exist.
    """
    input_dir = Path(r'data') # convert to pathlib Path object for cross-platform compatibility

    blur = random.uniform(1.0, 3.0)
    dust_density = random.uniform(0.5, 2.0)
    dust_radius_min = random.randint(1, 3)
    dust_radius_max = random.randint(4, 8)
    dust_alpha_min = random.randint(20, 40)
    dust_alpha_max = random.randint(80, 120)
    scratch_count = random.randint(2, 5)
    contrast = random.uniform(0.8, 1.2)
    sharpness = random.uniform(0.8, 1.2)
    brightness = random.uniform(0.9, 1.1)
    rotate = random.uniform(-2.0, 2.0)

    if input_dir.is_dir():
        for file in input_dir.iterdir():
            if file.suffix.lower() == ".pdf":
                print(f"Processing file: {file.name}")
                output_dir = Path("output")
                output_dir.mkdir(exist_ok=True)
                output_file = output_dir / f"{file.stem}_scan{file.suffix}"
                
                # Apply random effects to each PDF file
                main(file, output_file, 
                     blur_radius=blur,
                     dust_density=dust_density,
                     dust_min_radius=dust_radius_min,
                     dust_max_radius=dust_radius_max,
                     dust_alpha_min=dust_alpha_min,
                     dust_alpha_max=dust_alpha_max,
                     scratch_count=scratch_count,
                     contrast=contrast,
                     sharpness=sharpness,
                     brightness=brightness,
                     rotate=rotate)
                
    else:
        print(f"{input_dir} is not a directory. Please provide a valid directory path.")


# --------- Main ----------

def main(input_pdf, output_pdf, 
         blur_radius=2.0, 
         dust_density=1.0,
         dust_min_radius=1,
         dust_max_radius=5,
         dust_alpha_min=30,
         dust_alpha_max=100,
         scratch_count=3,
         scratch_line_width_min=1,
         scratch_line_width_max=3,
         scratch_alpha_min=50,
         scratch_alpha_max=150,
         contrast=1.0,
         sharpness=1.0,
         brightness=1.0,
         rotate=0.0,
         seed=None):
    """
    Process a PDF file to simulate an out-of-focus scanner with dirty glass effect.
    
    Args:
        input_pdf (str): Path to the input PDF file
        output_pdf (str): Path to the output PDF file
        blur_radius (float): Gaussian blur radius
        dust_density (float): Multiplier for dust spot density
        dust_min_radius (int): Minimum radius for dust spots
        dust_max_radius (int): Maximum radius for dust spots
        dust_alpha_min (int): Minimum alpha for dust spots
        dust_alpha_max (int): Maximum alpha for dust spots
        scratch_count (int): Number of scratches
        scratch_line_width_min (int): Minimum scratch line width
        scratch_line_width_max (int): Maximum scratch line width
        scratch_alpha_min (int): Minimum alpha for scratches
        scratch_alpha_max (int): Maximum alpha for scratches
        contrast (float): Contrast factor for the final image
        sharpness (float): Sharpness factor for the final image
        brightness (float): Brightness factor for the final image
        rotate (float): Rotation angle in degrees for the final image
        seed (int): Random seed for consistent overlay generation
    """
    # Set random seed if provided (for reproducibility)
    set_random_seed(seed)

    # Convert PDF to images
    pages = convert_pdf_to_images(input_pdf)
    if not pages:
        return

    # Process each page
    processed_images = []
    print("Processing each page...")
    for idx, page in enumerate(pages):
        processed_images.append(process_page(
            page, idx, len(pages), 
            blur_radius, contrast, sharpness, rotate, brightness,
            dust_density, dust_min_radius, dust_max_radius, 
            dust_alpha_min, dust_alpha_max, scratch_count,
            scratch_line_width_min, scratch_line_width_max,
            scratch_alpha_min, scratch_alpha_max
        ))

    # Save all processed pages into a new PDF
    save_pdf(processed_images, output_pdf)

    print(f"{input_pdf} has been processed and saved to {output_pdf}.")


if __name__ == "__main__":
    # Examples:
    # One File (Replace input_file and output_file with your own paths)
    # input_file = r"data\PoliceReport.pdf"
    # output_file = r"output\PoliceReport_scan.pdf"
    # main(input_file, output_file)

    # Directory of PDFs:
    # randomly assigns effects to each file in the directory
    process_dir(input_dir=r"data") # rawstring (r"") recommended for input_dir