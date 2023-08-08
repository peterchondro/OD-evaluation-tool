# Dataset Evaluation Tool

A tool for evaluating image dataset performance using weighted analysis.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
  - [Single Image Analysis](#single-image-analysis)
  - [Batch Image Analysis](#batch-image-analysis)
  - [3D Analysis](#3d-analysis)
- [Dataset Naming Rules](#dataset-naming-rules)
- [Notes](#notes)

## Installation

1. Install the required dependencies:
   - PyQt5
   - numpy
   - xlrd
   - xlwt
   - xlutils
   - matplotlib

2. **Important:** Do not delete the `./LUT/` directory.

## Usage

1. Navigate to the `./OD-evaluation-tool` directory using your terminal.

2. Launch the application:
   ```bash
   python3 UI.py

Follow these steps to evaluate your dataset:

- Click on "Select Class List" and locate your class list file for your dataset.
- Click on "Select Weights List" and locate your weight list file for your dataset.
- (Optional) Click on "Insert RGB Images" and locate the RGB data files of your dataset.
- (Optional) Click on "Insert GT Images" and locate the ground truth data files of your dataset.
- (Optional) Click on "Insert PD Images" and locate the result prediction data files of your dataset.

## Single Image Analysis

Make sure you have completed the setup steps.

Perform a single image analysis:

- Locate your set of RGB (optional), GT, and PD images by clicking on each of them.
- Click on "Analyze One" to view the evaluation data.
- Click on "Clear Data" before analyzing another image.
- Click on "Export Data" to save measurement data to an XLS file.

## Batch Image Analysis

Ensure you have completed the setup steps.

Perform batch image analysis:

- Click on "Analyze All" to evaluate all images in your dataset.
- Click on "Clear Data" before performing another evaluation.
- Click on "Export Data" to save measurement data to an XLS file.

## 3D Analysis

You can also perform similar steps for 3D data. Follow the instructions above, considering your dataset is in 3D format.

## Dataset Naming Rules

Ensure your dataset follows these naming rules:

- RGB IMAGES: x.YY
- GT IMAGES: x.ZZ
- PD IMAGES: x.ZZ
  (Where x represents the same name for corresponding images. YY is any image format, ZZ is TXT format)

## Notes

This README provides instructions for using the Dataset Evaluation Tool. Follow the steps carefully to analyze and evaluate your dataset effectively.
You can use sample data in drive-download-20230801T084518Z-001 for your test and to get to know the right format.

---

This project is licensed under the MIT License.
