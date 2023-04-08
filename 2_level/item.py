from dataclasses import dataclass


@dataclass
class BookResult:
    title : str
    price : str
    shipping : str
    total_cost: float = None
    
    def __post_init__(self):
        # Calculate the total_cost as the sum of price and shipping
        if self.price is not None and self.shipping is not None:
            self.total_cost = float(self.price) + float(self.shipping)
            
@dataclass
class RequestItemUrl:
    url: str


input_urls = [
    'https://www.abebooks.co.uk/servlet/SearchResults?bi=0&bx=off&cm_sp=SearchF-_-Advtab1-_-Results&fe=off&ds=30&bi=s&isbn=9780553293425&sortby=17',
    'https://www.abebooks.co.uk/servlet/SearchResults?bi=0&bx=off&cm_sp=SearchF-_-Advtab1-_-Results&fe=off&ds=30&bi=s&isbn=9780385313315&sortby=17',
    'https://www.abebooks.co.uk/servlet/SearchResults?bi=0&bx=off&cm_sp=SearchF-_-Advtab1-_-Results&fe=off&ds=30&bi=s&isbn=9780813332918&sortby=17',
]

redundancy = 10


urls_to_scrape  = [RequestItemUrl(url=url) for url in input_urls for x in range(redundancy)]

