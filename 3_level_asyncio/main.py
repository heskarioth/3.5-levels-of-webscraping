import requests
from item import  BookResult, isbns_to_scrape
from typing import Tuple
import pandas as pd
from utils import timeit, resource_usage_decorator, parse_arguments
from aiohttp import ClientSession, ClientResponse
import asyncio
import aiohttp

async def send_request(session: ClientSession, payload: dict) -> Tuple[int, ClientResponse]:
    api_endpoint = "https://www.abebooks.com/servlet/DWRestService/pricingservice"
    async with session.request(method='POST', url = api_endpoint, data=payload) as result:
        status_code = result.status
        if status_code == 200: # Request successful.
            response : ClientResponse = await result.json(content_type=None)    
            return status_code, response
        
        # raise aiohttp.ClientError()

def extract_data_api(response : requests.Response) -> BookResult:
    
    book = BookResult(
        title=response['bibliographicDetail']['title'],
        price=response['pricingInfoForBestUsed']['bestPriceInPurchaseCurrencyValueOnly'],
        shipping=response['pricingInfoForBestUsed']['bestShippingToDestinationPriceInPurchaseCurrencyValueOnly']
              )
    return book

# @resource_usage_decorator
@resource_usage_decorator
async def main():

    # get command_line args
    args = parse_arguments()

    n_runs = args.n_runs
    print_df = args.print_df
    
    print(f'Scraping... {n_runs} pages.')

    response_collection = []
    async with ClientSession() as session:
            pending = [
                asyncio.create_task(send_request(session=session, payload=isbns_to_scrape[idx].payload)) 
                for idx in range(n_runs)
            ]
            
            while pending:
                done, pending = await asyncio.wait(
                    pending, return_when=asyncio.FIRST_EXCEPTION
                )
                
                response_collection = [await done_task for done_task in done if not done_task.exception()]
                
    
    overall_books_found = [] # tracking all results
    
    response_collection = [collection for collection in response_collection if collection is not None]
    for status_code, response in response_collection:
    
        if status_code==200:
                
            overall_books_found.append(extract_data_api(response=response))
        
    df = pd.DataFrame(overall_books_found)
    print(df.shape)
    if print_df:
        print(df)


asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
asyncio.run(main())

