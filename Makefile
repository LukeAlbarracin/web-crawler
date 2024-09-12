help:
	@echo make install
	@echo make format
	@echo make lint
	@echo make crawl

install:
	pip install -r requirements.txt

format:
	black scrapy/sayariproject/

lint:
	flake8 --ignore=E121,E501,E265,F821 scrapy/sayariproject/ ./webcrawling.ipynb

crawl:
	(cd scrapy && scrapy crawl firststop)