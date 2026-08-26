#!/usr/bin/env python3
import argparse
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile
from pdf2image import convert_from_path
from PIL import Image, ImageFilter, ImageDraw, ImageEnhance

# Timestamps are pinned to 2000-01-01T00:00:00 in every form these tools emit.
# SOURCE_DATE_EPOCH is the same instant, handed to ocrmypdf so it pins what it can
# at the source; the byte substitutions below catch what it does not.
PINNED_EPOCH = "946684800"

# Each pattern matches ONLY the date-time field and is replaced by a string of
# exactly the same byte length, so every xref offset keeps pointing at its object.
# Neither pattern swallows a trailing timezone ("Z", "+00:00", "-04'00'"): the
# offset is real information and is left alone.
DATE_SUBSTITUTIONS = (
    # Pillow and PDF /CreationDate, /ModDate: "D:YYYYMMDDHHMMSS" + optional zone
    (re.compile(rb"D:\d{14}"), b"D:20000101000000"),
    # ocrmypdf XMP: "YYYY-MM-DDTHH:MM:SS" + optional zone
    (re.compile(rb"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"), b"2000-01-01T00:00:00"),
)

# xmp:MetadataDate carries fractional seconds that SOURCE_DATE_EPOCH does NOT pin;
# the digit count varies, so zero the digits in place rather than substituting a
# fixed string.
FRACTIONAL_SECONDS_RE = re.compile(rb"(?<=T\d\d:\d\d:\d\d)\.(\d+)")


def _zero_digits(match):
    return b"." + b"0" * len(match.group(1))


def pin_pdf_dates(pdf_path):
    """
    Rewrite every embedded timestamp in place to a fixed value.

    Pillow stamps /CreationDate and /ModDate from the wall clock, and ocrmypdf
    adds XMP timestamps of its own, so two runs with the SAME --seed produce
    visually identical pages inside byte-DIFFERENT files. That defeats any build
    that wants to assert a byte-identical rebuild, which is the only way to prove
    a fixture was regenerated rather than edited.

    The substitution is length-preserving on purpose: patching the bytes leaves
    the xref table valid, where re-serialising the document would not.

    Known limit: this can only reach timestamps stored as plain bytes. A metadata
    stream that happens to be compressed is invisible here, which is why the OCR
    path runs qpdf with --object-streams=disable first.

    Returns the number of timestamps replaced.
    """
    with open(pdf_path, "rb") as fh:
        data = fh.read()
    total = 0
    for pattern, pinned in DATE_SUBSTITUTIONS:
        data, count = pattern.subn(pinned, data)
        total += count
    data, count = FRACTIONAL_SECONDS_RE.subn(_zero_digits, data)
    total += count
    if total:
        with open(pdf_path, "wb") as fh:
            fh.write(data)
    return total

def generate_overlay(width, height,
                     dust_density=1.0, dust_min_radius=1, dust_max_radius=5,
                     dust_alpha_min=30, dust_alpha_max=100,
                     scratch_count=3, scratch_line_width_min=1, scratch_line_width_max=3,
                     scratch_alpha_min=50, scratch_alpha_max=150,
                     scratch_vertical=False):
    """
    Generate an overlay image (RGBA) containing dark dust spots and curved scratches.

    scratch_vertical constrains each scratch to run roughly down the page, which
    is how a mark from scanner glass or a feed roller lies. The default free-angle
    scratch models a different thing (a crease, or damage already on the paper) and
    is deliberately left as the default.
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
        if scratch_vertical:
            # Run down the page, drifting only a little sideways, and start and
            # stop at arbitrary points so the mark is a streak rather than a rule.
            x = random.randint(0, width - 1)
            y0, y1 = sorted((random.randint(0, height - 1), random.randint(0, height - 1)))
            drift = max(1, width // 200)
            start = (x, y0)
            end = (min(width - 1, max(0, x + random.randint(-drift, drift))), y1)
        else:
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
    parser.add_argument("--scratch-vertical", action="store_true",
                        help="Run scratches down the page rather than at free angles, which is "
                             "how a mark left by scanner glass or a feed roller lies. The default "
                             "free-angle scratch is the right shape for a crease or a mark already "
                             "on the paper, so this is an addition, not a correction.")
    parser.add_argument("--contrast", type=float, default=1.0,
                        help="Contrast factor for the final image (default: 1.0)")
    parser.add_argument("--sharpness", type=float, default=1.0,
                        help="Sharpness factor for the final image (default: 1.0)")
    parser.add_argument("--brightness", type=float, default=1.0,
                        help="Brightness factor for the final image (default: 1.0)")
    parser.add_argument("--rotate", type=float, default=0.0,
                        help="Rotation angle in degrees for the final image (default: 0; e.g., 180 for upside down)")
    parser.add_argument("--rotate-jitter", type=float, default=0.0,
                        help="Per-page random skew in degrees, added to --rotate as +/- this "
                             "amount (default: 0.0, every page skewed identically). A real "
                             "document fed through a sheet feeder skews a different way on "
                             "every page; a single fixed angle is the one thing a scanner "
                             "never does.")
    parser.add_argument("--dpi", type=int, default=200,
                        help="Rasterisation DPI, also written as the output resolution "
                             "(default: 200). Both halves matter: the rendering DPI and the "
                             "declared resolution must agree or the page lands at the wrong "
                             "physical size.")
    parser.add_argument("--seed", type=int, default=None,
                        help="Random seed for consistent overlay generation. Default is to draw "
                             "one and PRINT it, so an unseeded run is still reproducible after "
                             "the fact.")
    parser.add_argument("--no-pin-dates", action="store_true",
                        help="Leave the wall-clock /CreationDate and /ModDate in the output. "
                             "Dates are pinned by default so that two runs with the same seed "
                             "are byte-identical; pass this to keep real timestamps.")
    parser.add_argument("--ocr", action="store_true",
                        help="After degrading, run ocrmypdf over the result to lay down a text "
                             "layer read back off the degraded pixels. Without this the output "
                             "is images only and has NO text layer at all, which measures a "
                             "vision pipeline rather than a bad-OCR one.")
    parser.add_argument("--ocr-lang", default="eng",
                        help="Tesseract language passed through to ocrmypdf (default: eng)")
    args = parser.parse_args()

    # Seed BEFORE any draw. An unseeded run picks a seed and reports it rather
    # than being unreproducible: the point of the tool is repeatable test data,
    # and a scan you cannot regenerate is not test data.
    if args.seed is None:
        args.seed = random.SystemRandom().randrange(2**31)
        print(f"No --seed given; using {args.seed} (pass --seed {args.seed} to reproduce this run)")
    random.seed(args.seed)

    if args.ocr and shutil.which("ocrmypdf") is None:
        print("Error: --ocr requires ocrmypdf on PATH (apt install ocrmypdf).")
        return 5

    print("Converting PDF pages to images...")
    try:
        pages = convert_from_path(args.input_pdf, dpi=args.dpi)
    except Exception as e:
        print(f"Error converting PDF: {e}")
        return 2

    if not pages:
        print("No pages found in the PDF.")
        return 2

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
        # Only consume a random draw when jitter is actually requested. Drawing
        # unconditionally would shift the whole random stream and silently change
        # the dust and scratches every existing --seed produces.
        page_rotation = args.rotate
        if args.rotate_jitter:
            page_rotation += random.uniform(-args.rotate_jitter, args.rotate_jitter)
        rotated = processed_with_border.rotate(page_rotation, expand=True, fillcolor=(255, 255, 255))
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
            scratch_alpha_max=args.scratch_alpha_max,
            scratch_vertical=args.scratch_vertical
        )
        overlay_blurred = overlay.filter(ImageFilter.GaussianBlur(radius=args.blur_radius))

        # Composite the dust & scratch overlay over the brightened rotated paper.
        combined = Image.alpha_composite(rotated_bright.convert("RGBA"), overlay_blurred)

        final_image = combined.convert("RGB")
        processed_images.append(final_image)

    # Save all processed pages into a new PDF.
    if not processed_images:
        print("No pages were processed. Exiting.")
        return 1

    print(f"Saving processed pages to {args.output_pdf}...")
    try:
        processed_images[0].save(
            args.output_pdf,
            "PDF",
            resolution=float(args.dpi),
            save_all=True,
            append_images=processed_images[1:]
        )
        print("PDF created successfully.")
    except Exception as e:
        print(f"Error saving output PDF: {e}")
        return 1

    if args.ocr:
        rc = run_ocr(args.output_pdf, args.ocr_lang)
        if rc != 0:
            return rc

    if not args.no_pin_dates:
        replaced = pin_pdf_dates(args.output_pdf)
        print(f"Pinned {replaced} PDF date string(s) for reproducibility.")

    print(f"Done. Reproduce with --seed {args.seed}.")
    return 0


def run_ocr(pdf_path, lang):
    """
    Lay a text layer over the degraded pages with ocrmypdf.

    --force-ocr rather than --skip-text is required, not preferred: the pages
    coming out of this tool are images with no text layer at all, and the point
    is to capture what an OCR engine reads off DEGRADED pixels, errors included.
    That erroneous text is the artifact, not a defect in it.
    """
    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, "ocr.pdf")
        cmd = [
            "ocrmypdf", "--force-ocr", "--language", lang,
            "--output-type", "pdf", "--quiet",
            pdf_path, out,
        ]
        print(f"Running OCR ({lang}) over the degraded pages...")
        # ocrmypdf honours SOURCE_DATE_EPOCH for SOME of the timestamps it writes
        # and not others (measured: one of three). Set it anyway so the tool pins
        # what it can at the source, and let pin_pdf_dates() catch the remainder.
        env = dict(os.environ, SOURCE_DATE_EPOCH=PINNED_EPOCH)
        proc = subprocess.run(cmd, capture_output=True, text=True, env=env)
        if proc.returncode != 0:
            sys.stderr.write(proc.stderr or "")
            print(f"Error: ocrmypdf exited {proc.returncode}; output left un-OCRed.")
            return proc.returncode

        # ocrmypdf leaves three things a rerun changes, and byte-patching alone
        # reaches none of them: a random document /ID, and a /ModDate that lives
        # INSIDE a compressed object stream where no string substitution can see
        # it. qpdf fixes the first directly and exposes the second by writing the
        # object streams out plainly, so pin_pdf_dates() can then do its job.
        normalised = os.path.join(tmp, "norm.pdf")
        qpdf = subprocess.run(
            ["qpdf", "--deterministic-id", "--object-streams=disable", out, normalised],
            capture_output=True, text=True,
        )
        # qpdf exits 3 on warnings and still writes valid output; only a hard
        # failure should cost us the OCR we just paid for.
        if qpdf.returncode in (0, 3) and os.path.exists(normalised):
            shutil.move(normalised, pdf_path)
        else:
            sys.stderr.write(qpdf.stderr or "")
            print(f"Warning: qpdf normalisation failed ({qpdf.returncode}); "
                  "OCR kept but the output will NOT rebuild byte-identically.")
            shutil.move(out, pdf_path)
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)

