"""
Metamorphic Testing Script for Sentiment Analysis Tool

This script performs Metamorphic Relation 1 (MR1):
Adding emphasis words to a sentence should not change
the predicted sentiment classification.

Author: [Sharika Nargis]
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv
import logging
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

wdriver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))


# ------- Configuration -------
SUT_URL = "https://www.clientzen.io/sentiment-analysis-tool"
wdriver.get(SUT_URL)
INPUT_SELECTOR = (By.CSS_SELECTOR, "#Happiness-Score-Text-3")
ANALYZE_BUTTON = (By.CSS_SELECTOR, "#happiness-score-button")
RESULT_SELECTOR = (By.CSS_SELECTOR, ".aspect-based-sentiment-description")
IMPLICIT_WAIT = 20
OUTPUT_CSV = "mr1_results.csv"

# ------- Logging -------
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

# ------- MR transformer -------
EMPHASIZERS = ["really", "very", "absolutely", "definitely", "totally"]

def add_emphasis(text: str, emph_word: str =None, position="before_verb") -> str:
    """
    Adds an emphasis word into the input sentence.

    Metamorphic Relation:
        Inserting an emphasis word (e.g., 'very', 'really')
        should not change the predicted sentiment label.

    Args:
        text (str): Original input sentence.
        emph_word (str, optional): Specific emphasis word to insert.
                                   If None, a random one is chosen.

    Returns:
        str: Transformed sentence with emphasis added.
    """
    if not emph_word:
        import random
        emph_word = random.choice(EMPHASIZERS)

    words = text.split()
    if len(words) <= 1:
        return f"{text} {emph_word}"

    # naive heuristic: insert after first pronoun or subject (index 1)
    insert_idx = 1
    # Better: use POS tagging (spaCy) to find verb/adjective
    words.insert(insert_idx, emph_word)
    return " ".join(words)

# ------- Selenium helpers -------
def start_driver(headless: bool = True):
    """
       Initializes and returns a Chrome WebDriver instance.

       Args:
           headless (bool): If True, runs browser in headless mode.

       Returns:
           webdriver.Chrome: Configured WebDriver instance.
       """
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
    service = ChromeService()  # use default chromedriver in PATH
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.implicitly_wait(IMPLICIT_WAIT)
    return driver

def get_prediction_from_page(driver, input_text: str) -> str:
    """
       Submits text to the sentiment analysis tool and retrieves prediction.

       Args:
           driver (webdriver.Chrome): Active Selenium WebDriver.
           input_text (str): Text to analyze.

       Returns:
           str: Predicted sentiment label from the web page.

       Raises:
           TimeoutException: If required elements are not found.
       """
    driver.get(SUT_URL)

    # Wait for input to be present
    WebDriverWait(driver, IMPLICIT_WAIT).until(EC.presence_of_element_located(INPUT_SELECTOR))

    # Input the text
    input_box = driver.find_element(*INPUT_SELECTOR)
    input_box.clear()
    input_box.send_keys(input_text)

    # Click analyze / submit
    analyze_btn = driver.find_element(*ANALYZE_BUTTON)
    analyze_btn.click()

    # Wait for the result element to show prediction text
    WebDriverWait(driver, IMPLICIT_WAIT).until(EC.visibility_of_element_located(RESULT_SELECTOR))
    result_elem = driver.find_element(*RESULT_SELECTOR)
    result_text = result_elem.text.strip()
    return result_text

# ------- MR test runner -------
def run_mr1_test(driver, original_text: str) -> dict:
    """
       Executes MR1 test case.

       Steps:
           1. Get prediction for original text.
           2. Transform text by adding emphasis.
           3. Get prediction for transformed text.
           4. Compare predictions.

       Args:
           driver (webdriver.Chrome): Active Selenium driver.
           original_text (str): Input sentence.

       Returns:
           dict: Test result containing predictions and pass/fail status.
       """
    try:
        original_pred = get_prediction_from_page(driver, original_text)
    except Exception as e:
        logging.exception("Failed to get original prediction")
        return {"status": "error", "error": str(e)}

    transformed_text = add_emphasis(original_text)
    try:
        transformed_pred = get_prediction_from_page(driver, transformed_text)
    except Exception as e:
        logging.exception("Failed to get transformed prediction")
        return {"status": "error", "error": str(e)}

    # Basic comparison rule: exact label equality
    passed = (original_pred.lower() == transformed_pred.lower())

    return {
        "original_text": original_text,
        "original_pred": original_pred,
        "transformed_text": transformed_text,
        "transformed_pred": transformed_pred,
        "passed": passed
    }

# ------- Main / batch runner -------
def run_batch_test(input_texts: list, headless: bool = True) -> list:
    """
       Runs MR1 tests on multiple input sentences.

       Args:
           input_texts (list): List of sentences to test.
           headless (bool): Run browser in headless mode or not.

       Returns:
           list: List of result dictionaries.
       """
    driver = start_driver(headless=headless)
    results = []
    try:
        for txt in input_texts:
            logging.info("Testing input: %s", txt)
            res = run_mr1_test(driver, txt)
            results.append(res)
            # small delay to not overload SUT
            time.sleep(0.8)
    finally:
        driver.quit()

    # write CSV report
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["original_text","original_pred","transformed_text","transformed_pred","passed","status","error"])
        writer.writeheader()
        for r in results:
            # ensure keys exist
            row = {
                "original_text": r.get("original_text"),
                "original_pred": r.get("original_pred"),
                "transformed_text": r.get("transformed_text"),
                "transformed_pred": r.get("transformed_pred"),
                "passed": r.get("passed", False),
                "status": r.get("status", "ok"),
                "error": r.get("error", "")
            }
            writer.writerow(row)

    return results

# ------- Example usage -------
if __name__ == "__main__":
    sample_inputs = [
        "I love this movie",
        "The product was outstanding and exceeded expectations",
        "I do not like this restaurant",
        "The service was okay but the food was great"
    ]
    results = run_batch_test(sample_inputs, headless=True)
    for r in results:
        print(r)
