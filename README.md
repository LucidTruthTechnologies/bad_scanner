# Bad Scanner

A Python tool that simulates a poor-quality scanner by applying various visual effects to PDF documents. This tool can be useful for creating test data or simulating degraded document conditions.

## Features

- Converts PDF documents to images with simulated scanner artifacts
- Applies realistic effects including:
  - Dust spots and particles
  - Scratches and marks
  - Blur effects
  - Contrast, sharpness, and brightness adjustments
  - Paper rotation
  - Paper edge simulation
- Supports batch processing of PDF files
- Highly configurable parameters for fine-tuning the effects

## Prerequisites

- Python 3.x
- Poppler (required for PDF processing)
  - Windows: Download and install from [poppler releases](http://blog.alivate.com.au/poppler-windows/)
  - Linux: `sudo apt-get install poppler-utils`
  - macOS: `brew install poppler`
- `qpdf` (used to normalise the OCR output; `apt install qpdf`)
- `ocrmypdf` and `tesseract-ocr`, only if you use `--ocr`
  - Linux: `sudo apt-get install ocrmypdf tesseract-ocr`
  - macOS: `brew install ocrmypdf`

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd bad_scanner
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```bash
python bad_scanner.py input.pdf output.pdf
```

### Advanced Options

```bash
python bad_scanner.py input.pdf output.pdf \
    --blur-radius 2.0 \
    --dust-density 1.0 \
    --dust-min-radius 1 \
    --dust-max-radius 5 \
    --dust-alpha-min 30 \
    --dust-alpha-max 100 \
    --scratch-count 3 \
    --scratch-line-width-min 1 \
    --scratch-line-width-max 3 \
    --scratch-alpha-min 50 \
    --scratch-alpha-max 150 \
    --contrast 1.0 \
    --sharpness 1.0 \
    --brightness 1.0 \
    --rotate 0.0 \
    --seed 42
```

### Batch Processing

Use the `run_batch.sh` script to process multiple PDF files:

```bash
./run_batch.sh input_directory output_directory
```

## Parameters

- `--blur-radius`: Gaussian blur radius (default: 2.0)
- `--dust-density`: Multiplier for dust spot density (default: 1.0)
- `--dust-min-radius`: Minimum radius for dust spots (default: 1)
- `--dust-max-radius`: Maximum radius for dust spots (default: 5)
- `--dust-alpha-min`: Minimum alpha for dust spots (default: 30)
- `--dust-alpha-max`: Maximum alpha for dust spots (default: 100)
- `--scratch-count`: Number of scratches (default: 3)
- `--scratch-line-width-min`: Minimum scratch line width (default: 1)
- `--scratch-line-width-max`: Maximum scratch line width (default: 3)
- `--scratch-alpha-min`: Minimum alpha for scratches (default: 50)
- `--scratch-alpha-max`: Maximum alpha for scratches (default: 150)
- `--scratch-vertical`: Run scratches down the page, as glass and roller marks do. Optional; the
  default free-angle scratch models a crease or pre-existing damage and is unchanged
- `--contrast`: Contrast factor for the final image (default: 1.0)
- `--sharpness`: Sharpness factor for the final image (default: 1.0)
- `--brightness`: Brightness factor for the final image (default: 1.0)
- `--rotate`: Rotation angle in degrees, applied to every page (default: 0.0)
- `--rotate-jitter`: Per-page random skew in degrees, +/- this amount, added to `--rotate` (default: 0.0)
- `--dpi`: Rasterisation DPI, also written as the output resolution (default: 200)
- `--seed`: Random seed. If omitted, one is drawn and printed so the run stays reproducible
- `--no-pin-dates`: Keep real wall-clock timestamps instead of pinned ones
- `--ocr`: Run OCR over the degraded pages to add a text layer (requires `ocrmypdf`)
- `--ocr-lang`: Tesseract language for `--ocr` (default: eng)

## Examples

### Basic Example
```bash
python bad_scanner.py PoliceReport.pdf Scanned_PoliceReport.pdf
```

### Heavy Degradation Example
```bash
python bad_scanner.py input.pdf output.pdf \
    --blur-radius 3.0 \
    --dust-density 2.0 \
    --scratch-count 5 \
    --contrast 0.8 \
    --brightness 0.9
```

## The output has no text layer unless you ask for one

By default the output is page **images** wrapped in a PDF. `pdftotext` on it returns zero
characters. That is correct and often what you want: it is what a scan-to-PDF appliance with no OCR
produces, and it exercises a pipeline that has to look at pixels.

It is *not* what you want if you are testing how a system copes with **wrong text**. For that, pass
`--ocr`. The tool then runs `ocrmypdf --force-ocr` over the degraded pages, so the text layer is
what an OCR engine actually read off the damaged image, mistakes included. Those mistakes are the
artifact you are testing with, not a defect in it.

```bash
# images only, no text layer at all
python bad_scanner.py input.pdf output.pdf --seed 1234

# degraded pages plus the text OCR managed to read off them
python bad_scanner.py input.pdf output.pdf --seed 1234 --ocr
```

## Reproducibility

Test data you cannot regenerate is not test data, so a run is repeatable by default:

- **`--seed` is always in effect.** If you do not pass one, the tool draws a seed and prints it, so
  even an ad-hoc run can be reproduced afterwards.
- **Timestamps are pinned.** Pillow stamps `/CreationDate` and `/ModDate` from the wall clock and
  `ocrmypdf` adds XMP timestamps of its own, so two runs with the same seed used to produce
  identical-looking pages inside different files. Both are now rewritten to a fixed instant, using
  a length-preserving substitution so the xref table stays valid. Pass `--no-pin-dates` to keep the
  real times.

What that buys you, precisely:

| Mode | Same seed, same output path, twice |
|---|---|
| without `--ocr` | **byte-identical** |
| with `--ocr` | **identical extracted text**, and near-identical bytes |

The OCR path stops short of byte-identity on purpose. `ocrmypdf` names the text-layer XObject
randomly on every run (`/OCR-GlVv-WaArATXmDJTQ2E5Ig`), and that name lives in a compressed content
stream where it cannot be rewritten without breaking the reference it points at — an early attempt
to normalise it silently produced files whose text layer extracted **zero** characters. Since the
name affects nothing any consumer reads, the honest contract is the one above: assert the text and
the page images, not the bytes. `qpdf --deterministic-id` is still applied, so the document ID and
the timestamps are stable and the residual difference is confined to that one name.

## How bad is too bad: a calibration

A bad scanner really can produce unusable output, and the useful range is narrower than it looks.
Measured on `PoliceReport.pdf`, comparing the text `--ocr` recovers against the text of the
original PDF, as a character error rate:

| Settings | CER | What it is |
|---|---|---|
| defaults | **0.6%** | a decent office scanner; OCR reads it almost perfectly |
| `--blur-radius 3.0 --dust-density 2.0 --scratch-count 5 --contrast 0.8 --brightness 0.9` | **76%** | a bad photocopy: **a person reads it fine, OCR does not** |
| `--blur-radius 4.0` | 99% | past the cliff |
| `--blur-radius 5.0 --contrast 0.7` | 99% | past the cliff |
| `--dpi 100 --blur-radius 4.0 --rotate-jitter 1.5` | 100% | nothing extractable at all |

The middle row is the interesting one, and the jump from 0.6% to 76% with nothing in between is
worth knowing about before you go hunting for a dial. That row produces errors of exactly the kind
real discovery is full of:

| the document says | OCR reads |
|---|---|
| `Case Number: 2025-012` | `Case Number 2075-012` |
| `789 Oak Avenue, Riverside` | `789 Oss Avenue Riversadte` |
| `Ms. Karen Fields` | `Ma Laren Feids` |
| `29-year-old` | `279 year old` |

A misread digit in a case number and a witness whose surname has changed are the failures that
matter, and they only appear on a page a human would call perfectly legible.

### Tilt

Tilted pages are normal in real productions, and tilt is unusually expensive:

| Tilt | Characters recovered (of 679) |
|---|---|
| 0 deg | 641 |
| 0.7 deg | 643 |
| 1.5 deg | 276 |
| 3.0 deg | 70 |

Below about 1 degree OCR copes; past that it starts losing whole lines. **Keep `--rotate-jitter`
at or below 1.0** unless losing the page is the point.

`ocrmypdf --deskew` does not rescue this and is not wired in, because it was measured making
things worse: 3 degrees with deskew recovered **zero** characters against 70 without it. On a
noisy low-contrast page the deskew estimate is itself unreliable.

## A note on page size

Before this was fixed, pages were rasterised at pdf2image's default 200 DPI and then saved
declaring `resolution=100.0`. Every output therefore claimed to be **1224 x 1584 pt**, twice
US Letter and not a real paper size at all. `--dpi` now feeds both halves, so a letter page stays
612 x 792 pt while the embedded image scales with the DPI you asked for.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests. 