import scrapy
import json
import networkx as nx
import matplotlib.pyplot as plt

class FirststopSpider(scrapy.Spider):
    name = "firststop"
    allowed_domains = ["firststop.sos.nd.gov"]
    start_urls = ["https://firststop.sos.nd.gov/api/Records/businesssearch", "https://firststop.sos.nd.gov/api/WebUserAccess/GET_USER_IS_OWNER"]
    headers = {'Content-Type': 'application/json','authorization': 'undefined','Accept': 'application/json'}
    G = nx.Graph() # Person or Company that is an agent / owner

    def start_requests(self):
        payload = json.dumps({
            "SEARCH_VALUE": "X",
            "STARTS_WITH_YN": "true",
            "ACTIVE_ONLY_YN": True
        })
        self.log("Begin requests...")
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
            print(f"CompanyID: {source_id}")
            print("\n")
            payload = json.dumps({
                "SOURCE_TYPE_ID": 54, 
                "SOURCE_ID": 337397
            })
            # yield scrapy.Request(
            #     url=self.start_urls[1], # Confirm if user is owner,
            #     method='POST',
            #     body=payload,
            #     headers=self.headers,
            #     callback=self.parse_company
            # )
            company_name = company["TITLE"][0]
            url = "https://firststop.sos.nd.gov/api/FilingDetail/business/103327/false"
            yield scrapy.Request(
                url=url,
                method='GET',
                headers=self.headers,
                callback=self.parse_company,
                meta={'Company': company_name}
            )
            ## Also include handle error
    
    def parse_company(self, response):
        self.log("Done here...")
        data = response.json()["DRAWER_DETAIL_LIST"]
        flattened_dict = {entry['LABEL']: entry['VALUE'] for entry in data}
        print(flattened_dict)
        # self.G.add_node("")
        company_name = response.meta.get("Company")
        self.G.add_node(company_name, type="Company")
        if "Commercial Registered Agent" in flattened_dict:
            cr_agent = flattened_dict["Commercial Registered Agent"].split("\n")[0]
            self.G.add_node(cr_agent, type="Person")
            self.G.add_edges_from([(company_name, cr_agent),])
        
        pos = nx.spring_layout(self.G)
        nx.draw_networkx_nodes(self.G, pos, node_size=3000)
        nx.draw_networkx_edges(self.G, pos, edgelist=self.G.edges(), arrows=True)
        nx.draw_networkx_labels(self.G, pos)
        plt.title('Company and Owner Network')
        plt.show()
        # MUST USE ITEMS, see: https://www.geeksforgeeks.org/how-to-use-scrapy-items/
        
            




            

