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
- `--contrast`: Contrast factor for the final image (default: 1.0)
- `--sharpness`: Sharpness factor for the final image (default: 1.0)
- `--brightness`: Brightness factor for the final image (default: 1.0)
- `--rotate`: Rotation angle in degrees (default: 0.0)
- `--seed`: Random seed for consistent overlay generation (default: None)

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

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests. 