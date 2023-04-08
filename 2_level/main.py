from contextlib import contextmanager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.chrome.options import Options
from item import RequestItemUrl, BookResult, urls_to_scrape
from collections.abc import Generator
from typing import Dict, Union, List
from selenium.webdriver.common.by import By
import itertools
import pandas as pd
from utils import resource_usage_decorator, parse_arguments
# In Python, Generator[WebDriver, None, None] is a type hint for a generator function that yields instances of WebDriver objects. 
# The first argument of the Generator type hint specifies the type of object that the generator yields. 
# The second and third arguments specify the types of values that can be sent to the generator using its send() method 
# and returned by its close() method respectively.In your example, it seems that you are using a generator function that yields 
# instances of WebDriver objects. The None values in the second and third arguments indicate that no values can be sent to the 
# generator using its send() method and no value will be returned by its close() method respectively.
# more info: https://stackoverflow.com/questions/43658999/what-is-the-return-type-hint-of-a-generator-function
@contextmanager
def selenium_client(**properties : Dict[str,Union[str,List[str]]]) -> Generator[WebDriver, None, None]:

    options = Options()
    
    for key, value in properties.items():
        if key=='load_strategy':
            options.page_load_strategy = value
        elif key=='headless':
            options.headless = value
        elif key == 'additional_options':
            # Set additional Chrome options e.g.
#             --disable-gpu: Disables the use of GPU acceleration in Chrome.
#             --disable-extensions: Disables all Chrome extensions during the session.
#             --disable-infobars: Disables the "infobars" that Chrome displays for certain notifications.
#             --start-maximized: Starts Chrome with the window maximized.
#             --headless: Runs Chrome in headless mode, i.e., without a visible UI.
#             --proxy-server: Specifies a proxy server to use for network requests.
#             --user-agent: Sets a custom User-Agent string for the browser.
#             --ignore-certificate-errors: Ignores SSL certificate errors.
#             --disable-web-security: Disables web security features, allowing cross-origin requests.
#             --disable-popup-blocking: Disables Chrome's built-in popup blocker.
            if isinstance(value, list):
                for option in value:
                    options.add_argument(option)

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=options)

    try:
        yield driver
    finally:
        driver.close()

# Function to extract data from webpage
def fetch_data(driver : WebDriver, url_data : RequestItemUrl):
    
    def find_element(driver : WebDriver, x_path : str) -> List[Union[str,float]]:
        elements = driver.find_elements(By.XPATH, x_path)
        elements_values = [element.text for element in elements]
        elements_values = [
            float(element.replace('£', '').replace(' Shipping', '')) if element.startswith('£') else element 
            for element in elements_values
            ]
        return elements_values

    # Navigate to the given URL
    driver.get(url_data.url)
    
    # get the data
    titles = find_element(driver=driver,x_path='//span[@data-cy="listing-title"]')
    item_prices = find_element(driver=driver,x_path='//p[@class="item-price" and @data-cy="listing-price"]')
    shipping_prices = find_element(driver=driver,x_path='//span[@class="item-shipping text-secondary text-500"]')
    
    # merge results
    books_found = [(BookResult(title=title,price=price,shipping=shipping)) for price,shipping,title in zip(item_prices,shipping_prices,titles)]
    
    return books_found
        
@resource_usage_decorator
def main():

    # get command_line args
    args = parse_arguments()

    n_runs = args.n_runs
    print_df = args.print_df
    
    print(f'Scraping... {n_runs} pages.')

    with selenium_client(load_strategy='eager',headless=True,additional_options=['--disable-gpu','--disable-extensions']) as driver:
        
        # fetch data
        response_collection : List[List[BookResult]] = [fetch_data(driver=driver,url_data=urls_to_scrape[idx]) for idx in range(n_runs)]
        
        # list of list -> list
        overall_books_found = list(itertools.chain.from_iterable(response_collection))

        df = pd.DataFrame(overall_books_found)
        print(df.shape)
        
        if print_df:
            print(df)


main()
# headless mode = False
# [640 rows x 4 columns]
# Function 'main' took 68.536379 seconds to execute.
# CPU usage: 8.70%
# Memory usage: -0.40%

## headless mode = True
#[640 rows x 4 columns]
# Function 'main' took 81.619946 seconds to execute.
# CPU usage: 6.50%
# Memory usage: -0.30%