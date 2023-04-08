from bs4 import BeautifulSoup
import requests
from item import RequestItemUrl, BookResult, urls_to_scrape
from typing import Tuple, Union, Any, List
import re
import pandas as pd
from utils import timeit, resource_usage_decorator, parse_arguments
import itertools

def extract_data_http(parsed_doc : BeautifulSoup) -> List[BookResult]:
    
    # Find all 'shipping_prices'
    shipping_prices = parsed_doc.find_all('span', class_='item-shipping')
    shipping_prices = [float(re.findall(r'\d+\.\d+', price.get_text())[0])  for price in shipping_prices]

    # Find all 'titles'
    titles = parsed_doc.find_all('span', attrs={'data-cy': 'listing-title'})
    titles = [title.get_text() for title  in titles]
    
    # Find all "item_price"
    item_prices = parsed_doc.find_all('p', class_='item-price')
    item_prices = [float(re.findall(r'\d+\.\d+', price.get_text())[0])  for price in item_prices]
    
    # merge results
    books_found = [(BookResult(title=title,price=price,shipping=shipping)) for price,shipping,title in zip(item_prices,shipping_prices,titles)]
    
    return books_found

def send_request(session : requests.Session, url_data : RequestItemUrl) -> Tuple[int, requests.Response]:

    r = session.get(url_data.url)
    r.raise_for_status()
    
    return r.status_code, r

def parse_response(response : requests.Response, parse_method : str) -> Union[BeautifulSoup,dict[str, Any]]:

    if parse_method=="html.parser":
        parsed_doc = BeautifulSoup(response.text, "html.parser")
    else:
        raise ValueError(f'parse method: {parse_method} not supported')

    return parsed_doc


@resource_usage_decorator
# @timeit
def main(parse_method : str = "html.parser"):

    client = requests.Session()
    
    # get command_line args
    args = parse_arguments()

    n_runs = args.n_runs
    print_df = args.print_df

    print(f'Scraping... {n_runs} pages.')

    with client:
        
        overall_books_found = [] # tracking all results

        response_collection = [send_request(session=client,url_data=urls_to_scrape[idx]) for idx in range(n_runs)] 
        
        for status_code, response in response_collection:
            
            if status_code==200:
                
                parsed_doc = parse_response(response=response,parse_method=parse_method)
                    
                overall_books_found.append(extract_data_http(parsed_doc=parsed_doc))
        
        # list of list -> list
        overall_books_found = list(itertools.chain.from_iterable(overall_books_found))

        df = pd.DataFrame(overall_books_found)
        print(df.shape)
        if print_df:
            print(df)

main()
