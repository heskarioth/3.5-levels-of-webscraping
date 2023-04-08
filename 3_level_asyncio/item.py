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
class ISBN:
    value: str
    payload : dict = None

    def __post_init__(self):
        if self.payload is None:
            self.payload = {
            "action": "getPricingDataByISBN",
            "isbn": self.value,
            "container": f"pricingService-{self.value}",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.52 Safari/536.5",
            "country": "GBP",
            }


input_isbns = [
    '9780553293425',
    '9780385313315',
    '9780813332918',
]

redundancy = 10


isbns_to_scrape  = [ISBN(value=isbn) for isbn in input_isbns for x in range(redundancy)]

