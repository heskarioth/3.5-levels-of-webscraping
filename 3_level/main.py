import requests
from item import  BookResult, isbns_to_scrape
from typing import Tuple
import pandas as pd
from utils import timeit, resource_usage_decorator, parse_arguments


def send_request(session : requests.Session, payload : dict) -> Tuple[int, requests.Response]:

    api_endpoint = "https://www.abebooks.com/servlet/DWRestService/pricingservice"
    r = session.post(api_endpoint,data=payload)
    r.raise_for_status()
    
    return r.status_code, r

def extract_data_api(response : requests.Response) -> BookResult:
    
    book = BookResult(
        title=response['bibliographicDetail']['title'],
        price=response['pricingInfoForBestUsed']['bestPriceInPurchaseCurrencyValueOnly'],
        shipping=response['pricingInfoForBestUsed']['bestShippingToDestinationPriceInPurchaseCurrencyValueOnly']
              )
    return book

# @resource_usage_decorator
@resource_usage_decorator
def main():

    # get command_line args
    args = parse_arguments()

    n_runs = args.n_runs
    print_df = args.print_df
    
    client = requests.Session()
    
    print(f'Scraping... {n_runs} pages.')

    with client:
        
        overall_books_found = [] # tracking all results

        response_collection = [send_request(session=client,payload=isbns_to_scrape[idx].payload) for idx in range(n_runs)] 
        
        for status_code, response in response_collection:
            
            if status_code==200:
                
                overall_books_found.append(extract_data_api(response=response.json()))
        
        df = pd.DataFrame(overall_books_found)
        print(df.shape)
        if print_df:
            print(df)


main()
