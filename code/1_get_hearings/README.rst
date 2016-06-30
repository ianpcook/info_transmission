Installation
============

This scraper is based on Scrapy framework (http://scrapy.org), so you'll need to install it and its dependencies. Some details are provided at http://doc.scrapy.org/en/0.24/intro/install.html

If installing manually, you typically have to install development versions of libxml2 and libssl libraries, then install virtualen or better virtuallenvwrapper, make a new virtual envrironment and install scrapy i.e.

# virtualenvwrapper scaping
# pip install -r requirements.txt

This is generally sufficient under linux, as long as scrapy's dependencies are in place.

Running spider
==============

From scraping directory, run:

# scrapy crawl gpo

This is enough to launch crawler. It has some extra arguments, specifically:

  * "destination": directory where results will be stored, default is "results"

  * "overwrite": if set to "1", will overwrite existing files. Default is no overwrite.

To add arguments to spider, use the following format:

# scrapy crawl gpo -a ARG=VALUE
