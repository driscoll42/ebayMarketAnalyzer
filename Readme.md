# eBay Sold Price Scraper

This program is built to scrape all sold item data from eBay for any particular item. It will save the data to an excel file and create a scatter plot of the sold prices by date along with the median plot line and trendline. Further if you enter in the MSRP, it will plot a line for that and the break even prices of scalpers (particularly relevant when this was written during the PS5, Zen 3, and Xbox Series X launch). 

Examples:

![PS5 Example](https://github.com/driscoll42/ebayScraper/blob/master/PS5%20-digital.png)
![RTX 3080 Example](https://github.com/driscoll42/ebayScraper/blob/master/RTX+3080.png?raw=true)

# Install Instructions

* Create an Anaconda 3.8 python environment
* Run "pip install matplotlib==3.2.2, numpy, pandas==1.1.0, beautifulsoup==4.9.1, lxml==4.6.2, openpyxl==3.0.5, requests==2.25.0, scipy==1.5.4"

# How to Run
* In main.py update update the ebay_search() parameters for whatever product you are searching for as described below 
* Run main.py

# ebaysearch Parameters

* query - Search you wish to perform on eBay, can include spaces and "-" (Example: PS5 Digital -disc)
* msrp - The MSRP of the product to estimate scalper profits, if not entered it will not display those lines
* min_price - Default: 0 - The minimum price to search for
* max_price - Default: 10000 - The maximum price to search for
* min_date - Default: datetime.datetime(2020, 1, 1) - The earliest date to consider prices, useful if you want to split on preorders vs post-go live
* verbose - Default: False - If true prints out a number of debugging statements

## Release History

* 0.1.0
    * The first proper release
