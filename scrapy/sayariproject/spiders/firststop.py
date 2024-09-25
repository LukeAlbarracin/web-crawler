import scrapy
from scrapy import signals
from scrapy.utils.log import configure_logging
from pydispatch import dispatcher
import json
import logging


class FirststopSpider(scrapy.Spider):
    name = "firststop"
    allowed_domains = ["firststop.sos.nd.gov"]
    start_urls = ["https://firststop.sos.nd.gov/api/Records/businesssearch"]
    headers = {
        "Content-Type": "application/json",
        "authorization": "undefined",
        "Accept": "application/json",
    }
    company_info = []

    def __init__(self):
        dispatcher.connect(self.spider_closed, signals.spider_closed)
        configure_logging(install_root_handler=False)
        logging.basicConfig(
            filename="log.txt",
            format="%(levelname)s: %(message)s",
            level=logging.ERROR,
        )

    def start_requests(self):
        """
        Gathers all active businesses that start with 'X'

        Each business contains an ID that will be used in callback 'parse'
        """
        search_value = "X" ## TODO: Take in input, to know what to search if lambda / cronjob
        payload = json.dumps(
            {
                "SEARCH_VALUE": search_value,
                "STARTS_WITH_YN": "true",
                "ACTIVE_ONLY_YN": True,
            }
        )
        yield scrapy.Request(
            url=self.start_urls[0],
            method="POST",
            body=payload,
            headers=self.headers,
            errback=self.handle_error,
        )

    def parse(self, response):
        """
        Gathers info about business including owner, commercial registered/registered agent

        Passes over company_name from previous response from business search query to callback 'parse_company'
        """
        data = response.json().get("rows")
        for key in data:
            company = data.get(key)
            source_id = company.get("ID")
            self.log(f"CompanyID: {source_id}\n")
            company_name = company["TITLE"][0]
            url = f"https://firststop.sos.nd.gov/api/FilingDetail/business/{source_id}/false"
            # Normally would have a progress indicator for logging
            yield scrapy.Request(
                url=url,
                method="GET",
                headers=self.headers,
                callback=self.parse_company,
                errback=self.handle_error,
                meta={"Company": company_name},
            )

    def parse_company(self, response):
        """
        Flattens redundant "label" attribute in JSON response

        Adds the dictionary to a class-level list which will be used upon 'spider close'
        """
        data = response.json().get("DRAWER_DETAIL_LIST")
        flattened_dict = {entry["LABEL"]: entry["VALUE"] for entry in data}
        company_name = response.meta.get("Company")
        flattened_dict["Company"] = company_name
        self.company_info.append(flattened_dict)

    def spider_closed(self, spider):
        """
        Triggered when spider is done, writes out 'company_info' into a json file
        """
        with open("output.json", "w") as f:
            json.dump(self.company_info, f, indent=4)

    def handle_error(self, failure):
        """
        Log error on failure
        """
        self.logger.error(f"Request failed: {failure}")
