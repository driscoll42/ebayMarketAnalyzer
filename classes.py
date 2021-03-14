"""
classes.py

Stores all classes used by the program.

Current Classes:
 - EbayVariables: Stores variables that are frequently reused between different searches
"""
from dataclasses import dataclass, field
from typing import List


# pylint: disable=too-many-instance-attributes
# pylint: disable=line-too-long

@dataclass
class EbayVariables:
    """
    A class used to store frequently reused variables for different runs of the program

    Attributes
    ---------
    run_cached : bool - default=False
        If True does not get new data from eBay, just runs the plots/analysis on the saved xlsx files. Most useful if
        want to get the data then run the plots using a different min date (e.g. for all time and then after post-launch
        only)
    sleep_len : float - default=5
        How long to wait between url calls. This is to prevent DoSing eBay's servers and having your connection killed

    show_plots : bool - default=False
        Whether to display plots as the code runs, always saves to a directory regardless
    main_plot : bool - default=False
        Whether to show the Sales Plot as the code runs, always saves to a directory regardless. If show_plots is False
        this is False
    profit_plot: bool - default=False
        Whether to show the Cumulative Profit plot as the code runs, always saves to a directory regardless. If
        show_plots is False this is False
    trend_type: str - default='linear'
        What kind of Trendline to plot on the Sales Plot. Allowed values are "linear", " poly", "roll", or "none"
            linear - Creates a Linear Regression trendline
            poly - Creates a polynomial best fit line
            roll - Creates a rolling average of the best fit line
            none - Does not plot any trendline
    trend_param: List[int] - Default=[14]
        linear - This should be a list with a single value, e.g. [14], how many days in the future it should project the
            trendline. If 0 it will not project at all.
        poly - This should be a list with two values, e.g. [2, 14]. The first parameter is the degree of the polynomial,
            the second how many days in the future to project. The degree should be >=1 and the days should be >=01
        roll - This should be a list with a single value, e.g. [7]. This is how many days to use for the rolling average
        none - Does not matter what is in this field.

    sacat: int - default=0: Can filter down to a specific category on eBay (For example, video game consoles = 139971)

    tax_rate: float - default=0.0625
        The tax rate to use when calculating profits
    store_rate: float - default=0.04
        The rate to use for eBay stores when calculating profits
    non_store_rate: float - default=0.1
        The rate to use for non-stores when calculating profits

    country: str - default='USA'
        Allows for searching of different countries, currently only supports 'USA' and 'UK'
    ccode: str - default='$'
        What currency code to use when making plots
    days_before: int - default=30
        How far back in time to search listings. Ends the search at current date - days_before. Note: eBay only makes
        public data 90 days old so there's no point in making this greater than 90
    feedback: bool - default=False
        Gets the seller feedback for each sold item. WARNING: This explodes run times as the code needs to call the url
        of every single item. In testing the 5950X extract with this false takes 8 seconds, with True it takes
        40 minutes the first time. This is forced True if full_quantity is True as there is no extra work to get the
        feedback
    quantity_hist: bool - default=False
        Gets the full sold history of a multi-item listing. WARNING: This explodes run times
    desc_ignore_list: List[str] - default=List
        If populated, will check the sub_description field on eBay for keywords and if they exist, set ignore=1.

    extra_title_text: str - default=''
        Extra text to add to the file name and plot titles
    brand_list: List[str] - default_factory=List
        If populated, will search for brands in the list in the title and populate a column with the brand found. This
        is case insensitive.
    model_list: List[str] - default_factory=List
        If populated, will search for models in the list in the title and populate a column with the model found. This
        is case insensitive.

    debug: bool - default=False
        If True prints out values found as the program finds them
    verbose: bool - default=False
        If True prints out a number of exception statements, useful for debugging code issues. If you encounter a
        problem with the code it is VERY helpful if you set this to True, rerun it, and attach the output
    """

    # General Parameters
    run_cached: bool = field(default=False)
    sleep_len: float = field(default=5)

    # plotting parameters
    show_plots: bool = field(default=False)
    profit_plot: bool = field(default=False)
    main_plot: bool = field(default=False)
    trend_type: str = field(default='linear')
    trend_param: List[int] = field(default_factory=List)

    # search_params
    sacat: int = field(default=0)

    # rates
    tax_rate: float = field(default=0.0625)
    store_rate: float = field(default=0.04)
    non_store_rate: float = field(default=0.1)

    # Data Scraping parameters
    country: str = field(default='USA')
    ccode: str = field(default='$')
    days_before: int = field(default=30)
    feedback: bool = field(default=False)
    quantity_hist: bool = field(default=False)
    domestic_only: bool = field(default=False)
    desc_ignore_list: List[str] = field(default_factory=List)

    # Misc.
    extra_title_text: str = field(default='')
    brand_list: List[str] = field(default_factory=List)
    model_list: List[str] = field(default_factory=List)

    # debugging parameters
    debug: bool = field(default=False)
    verbose: bool = field(default=False)
