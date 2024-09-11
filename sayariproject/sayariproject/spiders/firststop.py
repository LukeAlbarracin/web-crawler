import scrapy
from pydispatch import dispatcher
from scrapy import signals
import json
import networkx as nx
import matplotlib.pyplot as plt

class FirststopSpider(scrapy.Spider):
    name = "firststop"
    allowed_domains = ["firststop.sos.nd.gov"]
    start_urls = ["https://firststop.sos.nd.gov/api/Records/businesssearch"]
    headers = {'Content-Type': 'application/json','authorization': 'undefined','Accept': 'application/json'}
    company_info = []

    def __init__(self):
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def start_requests(self):
        payload = json.dumps({
            "SEARCH_VALUE": "X",
            "STARTS_WITH_YN": "true",
            "ACTIVE_ONLY_YN": True
        })
        yield scrapy.Request(
            url=self.start_urls[0], # Business Search
            method='POST',
            body=payload,
            headers=self.headers
        )

    def parse(self, response):
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
        data = response.json()["DRAWER_DETAIL_LIST"]
        flattened_dict = {entry['LABEL']: entry['VALUE'] for entry in data}
        company_name = response.meta.get("Company")
        flattened_dict["COMPANY"] = company_name
        self.company_info.append(flattened_dict)
        # MUST USE ITEMS, see: https://www.geeksforgeeks.org/how-to-use-scrapy-items/
    
    def spider_closed(self, spider):
        with open('output.json', 'w') as f:
            json.dump(self.company_info, f, indent=4)