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

## Installation
This section depends on [uv](https://docs.astral.sh/uv/), a new package manager written in Rust. Installing uv is easy, see the [uv installation guide](https://docs.astral.sh/uv/getting-started/installation/#installing-uv).

### 1. Clone repository:
```bash
git clone https://github.com/LucidTruthTechnologies/bad_scanner.git
```
```bash
cd bad_scanner
```
### 2. Create virtual environment and install dependencies in one command:
```bash
uv run bad-scanner --help
```

## [Optional] Installation for devs:
  ### 1. Create virtual environment:
  ```bash
  uv venv
  ```
  ### 2. Install dependencies specified in pyproject.toml:
  ```bash
  uv install
  ```
  Or install specific versions specified in uv.lock:
  ```bash
  uv sync
  ```
  ### 3. Install package in editable mode:
  ```bash
  uv pip install -e .
  ```
  ### 4. Confirm Functionality
  ```bash
  pytest
  ```
  
## Usage

### Basic Usage

```bash
bad-scanner input.pdf output.pdf
```

### Advanced Options

```bash
bad-scanner input.pdf output.pdf
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
bad-scanner PoliceReport.pdf Scanned_PoliceReport.pdf
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