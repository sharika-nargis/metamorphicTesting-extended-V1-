# Metamorphic Testing for AI Sentiment Analysis

An extended work of an automated metamorphic testing framework for validating AI-based sentiment analysis using Selenium and Python. This project implements **Metamorphic Testing (MT)** to validate the robustness of an AI-based sentiment analysis system using Selenium automation. It demonstrates how to test Machine Learning-based systems when traditional expected-output (oracle) testing is not feasible. It automatically verifies that the model’s sentiment predictions remain consistent under metamorphic transformations (like adding emphasis words).

## Project Objective
AI systems often suffer from the **Oracle Problem** — where the correct output is unknown or probabilistic.

To address this, this project applies:

### Metamorphic Relation 1 (MR1)
> Adding emphasis words (e.g., "very", "really") should not change the predicted sentiment classification.

Example:

| Original Text | Transformed Text |
|--------------|------------------|
| I love this movie | I really love this movie |

Expected: Sentiment prediction remains unchanged.

## Tech Stack

- Python 3
- Selenium WebDriver
- ChromeDriver (via webdriver-manager)
- Explicit Waits (WebDriverWait)
- CSV reporting
- Logging

## Test Workflow

1. Launch browser (headless supported)
2. Navigate to SUT
3. Submit original text
4. Capture prediction
5. Apply transformation (add emphasis)
6. Resubmit transformed text
7. Compare predictions
8. Generate CSV report
   
## Project Structure
metamorphic-testing-sentiment-analysis/
│
├── mr1_test.py
├── mr1_results.csv
├── requirements.txt
└── README.md

## Installation

### Clone Repository
git clone https://github.com/your-username/metamorphicTesting-extended-V1-.git
cd metamorphic-testing-sentiment-analysis

### Install Dependencies
pip install -r requirements.txt

Or manually:
pip install selenium webdriver-manager

## How to Run
python mr1_test.py

The script will:
- Run test cases
- Compare predictions
- Generate `mr1_results.csv`

Author

Sharika Nargis
Software Quality Assurance Engineer
Focused on advanced automation and AI system validation.

