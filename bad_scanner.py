#!/usr/bin/env python3
import argparse
import random
from pdf2image import convert_from_path
from PIL import Image, ImageFilter, ImageDraw, ImageEnhance

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

    # --- Dust Spots ---
    num_dust_spots = int((width * height) // (200 * 200) * dust_density)
    for _ in range(num_dust_spots):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        radius = random.randint(dust_min_radius, dust_max_radius)
        alpha = random.randint(dust_alpha_min, dust_alpha_max)
        # Draw dark dust (black with variable opacity)
        draw.ellipse((x, y, x + radius, y + radius), fill=(0, 0, 0, alpha))

    # --- Curved Scratches ---
    for _ in range(scratch_count):
        start = (random.randint(0, width - 1), random.randint(0, height - 1))
        end = (random.randint(0, width - 1), random.randint(0, height - 1))
        # Generate a few intermediate points to simulate curvature.
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

    return overlay

def main():
    parser = argparse.ArgumentParser(
        description="Simulate an out-of-focus scanner with a dirty glass effect on a PDF document."
    )
    parser.add_argument("input_pdf", help="Path to the input PDF file")
    parser.add_argument("output_pdf", help="Path to the output PDF file")
    parser.add_argument("--blur-radius", type=float, default=2.0,
                        help="Gaussian blur radius (default: 2.0)")
    parser.add_argument("--dust-density", type=float, default=1.0,
                        help="Multiplier for dust spot density (default: 1.0)")
    parser.add_argument("--dust-min-radius", type=int, default=1,
                        help="Minimum radius for dust spots (default: 1)")
    parser.add_argument("--dust-max-radius", type=int, default=5,
                        help="Maximum radius for dust spots (default: 5)")
    parser.add_argument("--dust-alpha-min", type=int, default=30,
                        help="Minimum alpha for dust spots (default: 30)")
    parser.add_argument("--dust-alpha-max", type=int, default=100,
                        help="Maximum alpha for dust spots (default: 100)")
    parser.add_argument("--scratch-count", type=int, default=3,
                        help="Number of scratches (default: 3)")
    parser.add_argument("--scratch-line-width-min", type=int, default=1,
                        help="Minimum scratch line width (default: 1)")
    parser.add_argument("--scratch-line-width-max", type=int, default=3,
                        help="Maximum scratch line width (default: 3)")
    parser.add_argument("--scratch-alpha-min", type=int, default=50,
                        help="Minimum alpha for scratches (default: 50)")
    parser.add_argument("--scratch-alpha-max", type=int, default=150,
                        help="Maximum alpha for scratches (default: 150)")
    parser.add_argument("--contrast", type=float, default=1.0,
                        help="Contrast factor for the final image (default: 1.0)")
    parser.add_argument("--sharpness", type=float, default=1.0,
                        help="Sharpness factor for the final image (default: 1.0)")
    parser.add_argument("--brightness", type=float, default=1.0,
                        help="Brightness factor for the final image (default: 1.0)")
    parser.add_argument("--rotate", type=float, default=0.0,
                        help="Rotation angle in degrees for the final image (default: 0; e.g., 180 for upside down)")
    parser.add_argument("--seed", type=int, default=None,
                        help="Random seed for consistent overlay generation (default: None)")
    args = parser.parse_args()

    # Set random seed if provided (for reproducibility)
    if args.seed is not None:
        random.seed(args.seed)

    print("Converting PDF pages to images...")
    try:
        pages = convert_from_path(args.input_pdf)
    except Exception as e:
        print(f"Error converting PDF: {e}")
        return

    if not pages:
        print("No pages found in the PDF.")
        return

    processed_images = []
    print("Processing each page...")
    for idx, page in enumerate(pages):
        print(f"Processing page {idx+1}/{len(pages)}...")

        # --- Process the page image ---
        processed = page.filter(ImageFilter.GaussianBlur(radius=args.blur_radius))
        processed = ImageEnhance.Contrast(processed).enhance(args.contrast)
        processed = ImageEnhance.Sharpness(processed).enhance(args.sharpness)

        # --- Apply a thin black border (simulate paper edge) BEFORE rotation ---
        orig_width, orig_height = processed.size
        border_overlay = Image.new("RGBA", (orig_width, orig_height), (0, 0, 0, 0))
        draw_border = ImageDraw.Draw(border_overlay)
        draw_border.rectangle((0, 0, orig_width - 1, orig_height - 1), outline=(0, 0, 0, 255), width=2)
        border_overlay_blurred = border_overlay.filter(ImageFilter.GaussianBlur(radius=args.blur_radius))
        processed_with_border = Image.alpha_composite(processed.convert("RGBA"), border_overlay_blurred)

        # --- Rotate the paper (with border) ---
        rotated = processed_with_border.rotate(args.rotate, expand=True, fillcolor=(255, 255, 255))
        # --- Apply brightness enhancement to the rotated paper ---
        brightness_enhancer = ImageEnhance.Brightness(rotated)
        rotated_bright = brightness_enhancer.enhance(args.brightness)
        rot_width, rot_height = rotated_bright.size

        # --- Apply the scanner overlay (dust & scratches) AFTER rotation ---
        overlay = generate_overlay(
            rot_width, rot_height,
            dust_density=args.dust_density,
            dust_min_radius=args.dust_min_radius,
            dust_max_radius=args.dust_max_radius,
            dust_alpha_min=args.dust_alpha_min,
            dust_alpha_max=args.dust_alpha_max,
            scratch_count=args.scratch_count,
            scratch_line_width_min=args.scratch_line_width_min,
            scratch_line_width_max=args.scratch_line_width_max,
            scratch_alpha_min=args.scratch_alpha_min,
            scratch_alpha_max=args.scratch_alpha_max
        )
        overlay_blurred = overlay.filter(ImageFilter.GaussianBlur(radius=args.blur_radius))

        # Composite the dust & scratch overlay over the brightened rotated paper.
        combined = Image.alpha_composite(rotated_bright.convert("RGBA"), overlay_blurred)

        final_image = combined.convert("RGB")
        processed_images.append(final_image)

    # Save all processed pages into a new PDF.
    if processed_images:
        print(f"Saving processed pages to {args.output_pdf}...")
        try:
            processed_images[0].save(
                args.output_pdf,
                "PDF",
                resolution=100.0,
                save_all=True,
                append_images=processed_images[1:]
            )
            print("PDF created successfully.")
        except Exception as e:
            print(f"Error saving output PDF: {e}")
    else:
        print("No pages were processed. Exiting.")

if __name__ == "__main__":
    main()

