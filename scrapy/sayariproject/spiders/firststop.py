import scrapy
from scrapy import signals
from pydispatch import dispatcher
import json

class FirststopSpider(scrapy.Spider):
    name = "firststop"
    allowed_domains = ["firststop.sos.nd.gov"]
    start_urls = ["https://firststop.sos.nd.gov/api/Records/businesssearch"]
    headers = {
        'Content-Type': 'application/json',
        'authorization': 'undefined',
        'Accept': 'application/json'
    }
    company_info = []

    def __init__(self):
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def start_requests(self):
        """
        Gathers all active businesses that start with 'X'

        Each business contains an ID that will be used in callback 'parse'         
        """
        search_value = "X"
        payload = json.dumps({
            "SEARCH_VALUE": search_value,
            "STARTS_WITH_YN": "true",
            "ACTIVE_ONLY_YN": True
        })
        yield scrapy.Request(
            url=self.start_urls[0],
            method='POST',
            body=payload,
            headers=self.headers
        )

    def parse(self, response):
        """
        Gathers info about business including owner, commercial registered/registered agent

        Passes over company_name from previous response from business search query to callback 'parse_company'
        """
        data = response.json()["rows"]
        for key in data:
            company = data[key]
            source_id = company["ID"]
            self.log(f"CompanyID: {source_id}\n")
            company_name = company["TITLE"][0]
            url = f"https://firststop.sos.nd.gov/api/FilingDetail/business/{source_id}/false"
            yield scrapy.Request(
                url=url,
                method='GET',
                headers=self.headers,
                callback=self.parse_company,
                meta={'Company': company_name}
            )
    
    def parse_company(self, response):
        """
        Flattens redundant "label" attribute in JSON response

        Adds the dictionary to a class-level list which will be used upon 'spider close'
        """
        data = response.json()["DRAWER_DETAIL_LIST"]
        flattened_dict = {entry['LABEL']: entry['VALUE'] for entry in data}
        company_name = response.meta.get("Company")
        flattened_dict["COMPANY"] = company_name
        self.company_info.append(flattened_dict)
    
    def spider_closed(self, spider):
        """
        Triggered when spider is done, writes out 'company_info' into a json file
        """
        with open('output.json', 'w') as f:
            json.dump(self.company_info, f, indent=4)