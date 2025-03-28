# Bad Scanner

![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)

A Python module that simulates a poor-quality scanner by applying various visual effects to PDF documents. This module is useful for creating test data or simulating degraded document conditions. It offers both a cli version and customizable script. The cli can process one file, the script can process an entire directory or one file. 

## Table of Contents
- [Features](#features)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Parameters](#parameters)
- [Examples](#examples)
- [License](#license)
- [Contributing](#contributing)

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
- Reproducible results with seed option

## Project Structure
```bash
bad_scanner
│   .gitignore
│   .python-version
│   pyproject.toml
│   README.md
│   uv.lock
│   CONTRIBUTING.md
│   LICENSE
│
├───data
│    │    PoliceReport.pdf
│    │    PoliceReport_modified.pdf
│
├───src
│   │   __init__.py
│   │
│   └───cli
│       │   __init__.py
│       │   bad_scanner.py
│       │   bad_scanner_cli.py
│       
│
└───tests
    │   __init__.py
    │   test_cli.py
```

## Prerequisites
- Python 3.12 or higher
- [Poppler](https://poppler.freedesktop.org/) (required for PDF processing):
  - **Windows**: Download from [poppler releases](https://github.com/oschwartz10612/poppler-windows/releases/)
  - **Linux**: `sudo apt-get install poppler-utils`
  - **macOS**: `brew install poppler`
- [uv](https://docs.astral.sh/uv/) package manager for installation (see [installation guide](https://docs.astral.sh/uv/getting-started/installation/#installing-uv))

## Installation

### 1. Clone repository:
```bash
git clone https://github.com/LucidTruthTechnologies/bad_scanner.git
cd bad_scanner
```

### 2. Create virtual environment and install dependencies in one command:
```bash
uv run bad-scanner --help
```

## [Optional] Editable installation for devs:
  ### 1. Create virtual environment:
  ```bash
  uv venv
  ```
  
  ### 2. Install dependencies:
  Install specific versions specified in uv.lock:
  ```bash
  uv sync
  ```
  
  ### 3. Install package in editable mode:
  ```bash
  uv pip install -e .
  ```
  
  ### 4. Confirm Functionality
  ```bash
  pytest -v
  ```
  
## Usage

### CLI Usage

```bash
bad-scanner input.pdf output.pdf
```

### Script Usage
Open `src/cli/bad_scanner.py` with text editor (nano, code, etc):
```bash
code src/cli/bad_scanner.py
```
Uncomment desired function:
```python
if __name__ == "__main__":
    # Examples:
    # One File (Replace input_file and output_file with your own paths)
    # input_file = r"data\PoliceReport.pdf"
    # output_file = r"output\PoliceReport_scan.pdf"
    # main(input_file, output_file)

    # Directory of PDFs:
    # randomly assigns effects to each file in the directory
    process_dir(input_dir=r"data") # rawstring (r"") recommended for input_dir
```

## Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `--blur-radius` | Gaussian blur radius | 2.0 |
| `--dust-density` | Multiplier for dust spot density | 1.0 |
| `--dust-min-radius` | Minimum radius for dust spots | 1 |
| `--dust-max-radius` | Maximum radius for dust spots | 5 |
| `--dust-alpha-min` | Minimum alpha for dust spots | 30 |
| `--dust-alpha-max` | Maximum alpha for dust spots | 100 |
| `--scratch-count` | Number of scratches | 3 |
| `--scratch-line-width-min` | Minimum scratch line width | 1 |
| `--scratch-line-width-max` | Maximum scratch line width | 3 |
| `--scratch-alpha-min` | Minimum alpha for scratches | 50 |
| `--scratch-alpha-max` | Maximum alpha for scratches | 150 |
| `--contrast` | Contrast factor for the final image | 1.0 |
| `--sharpness` | Sharpness factor for the final image | 1.0 |
| `--brightness` | Brightness factor for the final image | 1.0 |
| `--rotate` | Rotation angle in degrees | 0.0 |
| `--seed` | Random seed for consistent overlay generation | None |

## Examples

### Basic Example
```bash
bad-scanner input.pdf output.pdf
```

### Heavy Degradation Example
```bash
bad-scanner input.pdf output.pdf
    --blur-radius 3.0
    --dust-density 2.0
    --scratch-count 5
    --contrast 0.8
    --brightness 0.9
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.