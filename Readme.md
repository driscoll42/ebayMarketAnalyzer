# eBay Sold Price Scraper

This program is built to scrape all sold item data from eBay for any particular item. It will save the data to an excel file and create a scatter plot of the sold prices by date along with the median plot line and trendline. Further if you enter in the MSRP, it will plot a line for that and the break even prices of scalpers (particularly relevant when this was written during the PS5, Zen 3, and Xbox Series X launch). 

Examples:

![PS5 Example](https://github.com/driscoll42/ebayScraper/blob/master/Images/PS5.png)
![RTX 3080 Example](https://github.com/driscoll42/ebayScraper/blob/master/Images/RTX%203080.png)

# Install Instructions

* Create an Anaconda 3.8 python environment
* Run "pip install matplotlib==3.2.2, numpy, pandas==1.1.0, beautifulsoup==4.9.1, lxml==4.6.2, openpyxl==3.0.5, requests==2.25.0, scipy==1.5.4, xlrd==1.2.0"
* Note: This code requires matplotlib 3.2.2, newer versions break the trend line

# How to Run
* In main.py update update the ebay_search() parameters for whatever product you are searching for as described below 
* Run main.py

# ebaysearch Parameters

* query - Search you wish to perform on eBay, can include spaces and "-" (Example: PS5 Digital -disc)
* msrp - The MSRP of the product to estimate scalper profits, if not entered it will not display those lines
* min_price - Default: 0 - The minimum price to search for
* max_price - Default: 10000 - The maximum price to search for
* min_date - Default: datetime.datetime(2020, 1, 1) - The earliest date to consider prices, useful if you want to split on preorders vs post-go live. Note that if you only have one day of data it errors out if you also have an msrp
* verbose - Default: False - If true prints out a number of debugging statements
* run_cached - Default: False - If true does not get new data from eBay, just runs the plots/analysis on the saved xlsx files. Most useful if want to get the data then run the plots using a different min date (e.g. for all time and then after post-launch only)

Extra Variables:

* feedback - Default: False - Gets the seller feedback for each sold item. WARNING: This explodes run times as the code needs to call the url of every single item. In testing the 5950X extract with this false takes 8 seconds, with True it takes 40 minutes. This is forced True if full_quantity is True as there is no extra work to get the feedback
* quantity_hist - Default: False - Gets the full sold history of a multi-item listing. WARNING: This explodes run times 

When running for the 5950X on 12/10/20:
* Both False - 5 URL calls - 00:07 - 434 listings 
* Only Feedback - 755 URL calls - 14:11 - 434 listings (470 total sold)
* Quantity_hist - 

## Release History

* 0.1.0
    * The first proper release
