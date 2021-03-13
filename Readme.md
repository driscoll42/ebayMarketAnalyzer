# eBay Marker Analyzer

#### Formerly eBay Sold Price Scraper

This code is free for use and I encourage others to use it for their projects. If you do I would love to see how you
used it, shoot me an email or message if you're willing to share. Further, feel free to open up new issues for defects
or new features. I can't promise to get to all of them, but I can try.

Warning: This works as of the last commit. It's very likely some change in eBay's website will break this at some point
after I stop maintaining.

This program is built to scrape all sold item data from eBay for any particular item. It will save the data to an excel
file and create a scatter plot of the sold prices by date along with the median plot line and trendline. Further if you
enter in the MSRP, it will plot a line for that and the break even prices of scalpers (particularly relevant when this
was written during the PS5, Zen 3, and Xbox Series X launch).

Note: If you need to do commercial research, make actual business decisions, etc... off of eBay data, I *highly*
encourage you to
use [eBay's TeraPeaks](https://pages.ebay.com/seller-center/listing-and-marketing/terapeak.html?mkevt=1&mkcid=1&mkrid=711-53200-19255-0&campid=5336728181&customid=&toolid=10001)
instead. It goes back further in time, has more detail, is faster, and is officially supported, plus only $12-$19/month
or free if you have a Basic, Premium, Anchor, or Enterprise eBay Store. This tool is not meant to compete with it, but
is an interesting side project for me that I make open source.

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
* Install packages in environment.yml or requirements.txt

# How to Run

* By default the program is setup to allow for easy scraping of CPUs, GPUs, Consoles, and Motherboards
* There are a number of examples in run.py, see below for details on the main class and functions

## ebay_search Parameters

* query: str - The query you want to search on eBay, e.g. 'RTX 3080'
* e_vars: EbayVariables - An instance of EbayVariables class that gets passed into the function.
* query_exceptions: List - A list of exclusions to add to the query (e.g. ['pics', 'photos', 'paper']), these all get
  appended when eBay is searched
* msrp: float - The MSRP of the item, useful when plotting to get an idea of what the price should be normally
* min_price: float - The minimum price of the query you want to search on eBay for
* max_price: float - The maximum price of the query you want to search on eBay for

## EbayVariables Class Parameters

#### General Parameters

* run_cached: bool - default=False: If True does not get new data from eBay, just runs the plots/analysis on the saved
  xlsx files. Most useful if want to get the data then run the plots using a different min date (e.g. for all time and
  then after post-launch only)
* sleep_len: float - default=5: How long to wait between url calls. This is to prevent DoSing eBay's servers and having
  your connection killed

#### plotting Parameters

* show_plots: bool - default=False: Whether to display plots as the code runs, always saves to a directory regardless
* main_plot: bool - default=False: Whether to show the Sales Plot as the code runs, always saves to a directory
  regardless. If show_plots is False this is False
* profit_plot: bool - default=False: Whether to show the Cumulative Profit plot as the code runs, always saves to a
  directory regardless. If show_plots is False this is False
* trend_type: str - default='linear': What kind of Trendline to plot on the Sales Plot. Allowed values are "linear", "
  poly", "roll", or "none"
  * linear - Creates a Linear Regression trendline
  * poly - Creates a polynomial best fit line
  * roll - Creates a rolling average of the best fit line
  * none - Does not plot any trendline
* trend_param: List[int] - default_factory=[14]
  * linear - This should be a list with a single value, e.g. [14], how many days in the future it should project the
    trendline. If 0 it will not project at all.
  * poly - This should be a list with two values, e.g. [2, 14]. The first parameter is the degree of the polynomial, the
    second how many days in the future to project. The degree should be >=1 and the days should be >=01
  * roll - This should be a list with a single value, e.g. [7]. This is how many days to use for the rolling average
  * none - Does not matter what is in this field.

#### Search Parameters

* sacat: int - default=0: Can filter down to a specific category on eBay (For example, video game consoles = 139971)

#### Rate Parameters

* tax_rate: float - default=0.0625 - The tax rate to use when calculating profits
* store_rate: float - default=0.04 - The rate to use for eBay stores when calculating profits
* non_store_rate: float - default=0.1 - The rate to use for non-stores when calculating profits

#### Data Scraping Parameters

* country: str - default='USA': Allows for searching of different countries, currently only supports 'USA' and 'UK'
* ccode: str - default='$': What currency code to use when making plots
* days_before: int - default=30: How far back in time to search listings. Ends the search at current date - days_before.
  Note: eBay only makes public data 90 days old so there's no point in making this greater than 90
* feedback: bool - default=False: Gets the seller feedback for each sold item. WARNING: This explodes run times as the
  code needs to call the url of every single item. In testing the 5950X extract with this false takes 8 seconds, with
  True it takes 40 minutes the first time. This is forced True if full_quantity is True as there is no extra work to get
  the feedback
* quantity_hist: bool - default=False: Gets the full sold history of a multi-item listing. WARNING: This explodes run
  times
* desc_ignore_list: List[str] - default_factory=List

#### Misc. Parameters

* extra_title_text: str - default='': Extra text to add to the file name and plot titles
* brand_list: List[str] - default_factory=List: If populated, will search for brands in the list in the title and
  populate a column with the brand found. This is case insensitive.
* model_list: List[str] - default_factory=List: If populated, will search for models in the list in the title and
  populate a column with the model found. This is case insensitive.

#### debugging parameters

* debug: bool - default=False: If True prints out values found as the program finds them
* verbose: bool - default=False: If True prints out a number of exception statements, useful for debugging code issues.
  If you encounter a problem with the code it is VERY helpful if you set this to True, rerun it, and attach the output

## median_plotting Parameters

TO DO

## ebay_seller_plot Parameters

TO DO

## brand_plot Parameters

TO DO

## Release History

* 0.1.0
    * The first proper release
* 0.5.0
    * Added a number of performance enhancements and ensuring correct data being scraped