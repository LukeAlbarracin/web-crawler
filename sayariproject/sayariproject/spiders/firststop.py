import scrapy
import json

class FirststopSpider(scrapy.Spider):
    name = "firststop"
    allowed_domains = ["firststop.sos.nd.gov"]
    start_urls = ["https://firststop.sos.nd.gov/api/Records/businesssearch", "https://firststop.sos.nd.gov/api/WebUserAccess/GET_USER_IS_OWNER"]
    headers = {
            'Content-Type': 'application/json',
            'authorization': 'undefined',
    }

    def start_requests(self):
        payload = json.dumps({
            "SEARCH_VALUE": "X",
            "STARTS_WITH_YN": "true",
            "ACTIVE_ONLY_YN": True
        })
        
        
        self.log("Ack102")
        yield scrapy.Request(
            url=self.start_urls[0], # Business Search
            method='POST',
            body=payload,
            headers=self.headers,
        )

    def parse(self, response):
        headers = {
            'Content-Type': 'application/json',
            'authorization': 'undefined',
        }
        data = response.json()["rows"]
        for index, key in enumerate(data):
            company = data[key]
            # print(f"Company {index}: {company}")
            source_id = company["ID"]
            print(f"CompanyID: {source_id}")
            print("\n")
            payload = json.dumps({
                "SOURCE_TYPE_ID": 54, 
                "SOURCE_ID": 337397
            })
            yield scrapy.Request(
                url=self.start_urls[1], # Confirm if user is owner,
                method='POST',
                body=payload,
                headers=self.headers,
                callback=self.parse_company
            )
    
    def parse_company(self, response):
        pass
            




            

