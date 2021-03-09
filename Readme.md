# eBay Marker Analyzer

#### Formally eBay Sold Price Scraper

This code is free for use and I encourage others to use it for their projects. If you do I would love to see how you
used it, shoot me an email or message if you're willing to share. Further feel free to open up new issues for defects or
new features. I can't promise to get to all of them but I can try.

Note: This works as of the last commit. It's very likely some change in eBay's website will break this at some point
after I stop maintaining.

This program is built to scrape all sold item data from eBay for any particular item. It will save the data to an excel
file and create a scatter plot of the sold prices by date along with the median plot line and trendline. Further if you
enter in the MSRP, it will plot a line for that and the break even prices of scalpers (particularly relevant when this
was written during the PS5, Zen 3, and Xbox Series X launch).

The code was used in a series of articles I wrote in late 2020 to early 2021:

* [An analysis of the $82 million eBay Scalping Market for Xbox, PS5, AMD, and NVIDIA](https://dev.to/driscoll42/an-analysis-of-the-80-million-ebay-scalping-market-for-xbox-ps5-amd-and-nvidia-f35)
* [An analysis of the $6 million Zen 3 Scalping Market](https://dev.to/driscoll42/zen-3-scalping-market-analysis-4hhf)
* [An analysis of the $62 million RTX 30 Series Scalping Market](https://dev.to/driscoll42/nvidia-ampere-rtx-30-series-scalping-market-analysis-4gad)
* [An analysis of the $4 million Big Navi/RDNA2 Scalping Market](https://dev.to/driscoll42/big-navi-rdna2-series-scalping-market-analysis-2c3k)
* [An analysis of the $80 million Xbox Series S/X Scalping Market](https://dev.to/driscoll42/xbox-series-s-x-scalping-market-analysis-l3m)
* [An analysis of the $143 million PS5 Scalping Market](https://dev.to/driscoll42/an-analysis-of-the-143-million-ps5-scalping-market-414d)
* [An analysis of the UK £54 million PS5/Xbox and computer hardware Scalping Market](https://dev.to/driscoll42/an-analysis-of-the-uk-54-million-ps5-xbox-and-computer-hardware-scalping-market-4i79)


Examples:

![PS5 Example](https://github.com/driscoll42/ebayScraper/blob/master/2101-Update/PS5%20-digital%20-image%20-jpeg%20-img%20-picture%20-pic%20-jpg.png?raw=true)
![PS5 Rolling Average Example](https://github.com/driscoll42/ebayScraper/blob/master/2101-Update/PS5%20Median%20Pricing%207%20Rolling%20Average_.png?raw=true)

# Install Instructions

* Create an Anaconda 3.8 python environment
* Run "pip install matplotlib==3.3.4, numpy, pandas==1.1.0, beautifulsoup4==4.9.1, lxml==4.6.2, openpyxl==3.0.5, requests==2.25.0, scipy==1.5.4, xlrd==1.2.0, lxml, requests_cache

# How to Run
* In main.py update update the ebay_search() parameters for whatever product you are searching for as described below 
* Run main.py

# ebaysearch Parameters
- Search Parameters
  * query - Search you wish to perform on eBay, can include the following symbols ",", "(", ")", "-", and " " (Example: (AMD, Ryzen) 3100 -combo)
  * msrp - The MSRP of the product to estimate scalper profits, if not entered it will not display those lines
  * min_price - Default: 0 - The minimum price to search for
  * max_price - Default: 10000 - The maximum price to search for
  * sacat - Default: 0 - Can filter down to a specific category on eBay (For example, video game consoles = 139971) 
  * country - Default: USA - Allows for searching of different countries, currently only supports 'USA' and 'UK'
  * feedback - Default: False - Gets the seller feedback for each sold item. WARNING: This explodes run times as the code needs to call the url of every single item. In testing the 5950X extract with this false takes 8 seconds, with True it takes 40 minutes the first time. This is forced True if full_quantity is True as there is no extra work to get the feedback
  * quantity_hist - Default: False - Gets the full sold history of a multi-item listing. WARNING: This explodes run times
  * run_cached - Default: False - If True does not get new data from eBay, just runs the plots/analysis on the saved xlsx files. Most useful if want to get the data then run the plots using a different min date (e.g. for all time and then after post-launch only)
  * sleep_len - Default: 0.4 - How long to wait between url calls. This is to prevent DoSing eBay's servers and having your connection killed

* Filtering Parameters (Mostly to improve performance)
  * days_before - Default: 999 - How far back in time to search listings. Ends the search at current date - days_before. 


* Plotting/file Parameters
  * brand_list - Default: [] - If populated, will search for brands in the list in the title and populate a column with the brand found. This is case insensitive.
  * model_list - Default: [] - If populated, will search for brands in the list in the title and populate a column with the brand found. This is case insensitive.
  * min_date - Default: datetime.datetime(2020, 1, 1) - The earliest date to consider prices when plotting, useful if you want to split on preorders vs post-go live. Note that if you only have one day of data it errors out if you also have a msrp
  * extra_title_text - Default: '' - Extra text to add to the file name and plot titles 


* Debugging parameters
   * debug - Default: False - If True prints out exceptions. If verbose=True this is effectively True
   * verbose - Default: False - If True prints out all the data as soon as its pulled



## Release History

* 0.1.0
    * The first proper release
* 0.5.0
    * Added a number of performance enhancements and ensuring correct data being scraped