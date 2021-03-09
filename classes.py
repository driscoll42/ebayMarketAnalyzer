"""

"""
from dataclasses import dataclass, field
from typing import List


@dataclass
class EbayVariables:
    """

    """
    # General Parameters
    run_cached: bool = field(default=False)
    sleep_len: float = field(default=5)

    # plotting parameters
    show_plots: bool = field(default=False)
    profit_plot: bool = field(default=False)
    main_plot: bool = field(default=False)

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

    # Misc.
    extra_title_text: str = field(default='')
    brand_list: List[str] = field(default_factory=List)
    model_list: List[str] = field(default_factory=List)

    # debugging parameters
    debug: bool = field(default=False)
    verbose: bool = field(default=False)
