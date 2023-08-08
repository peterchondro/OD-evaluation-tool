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

1. Navigate to the `./EvalTool_2DWeighted` directory using your terminal.

2. Launch the application:
   ```bash
   python3 UI.py

Follow these steps to evaluate your dataset:

- Click on "Select Class List" and locate your class list file for your dataset.
- Click on "Select Weights List" and locate your weight list file for your dataset.
- Click on "Insert RGB Images" and locate the RGB data files of your dataset.
- Click on "Insert GT Images" and locate the ground truth data files of your dataset.
- Click on "Insert PD Images" and locate the result prediction data files of your dataset.

## Single Image Analysis

Make sure you have completed the setup steps.

Perform a single image analysis:

- Locate your set of RGB, GT, and PD images by clicking on each of them.
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

- RGB IMAGES: x.PNG
- GT IMAGES: x.PNG
- PD IMAGES: x.PNG
  (Where x represents the same name for corresponding images.)

## Notes

This README provides instructions for using the Dataset Evaluation Tool. Follow the steps carefully to analyze and evaluate your dataset effectively.

---

This project is licensed under the MIT License.
