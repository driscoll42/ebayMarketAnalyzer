For various reasons I've had to write scripts to go back and fix missing data. Rather than delete them when done I figure it'd be useful to keep them in case I ever need to reuse them. 

Seeing as these were originally in the base directory they probably won't work immediately in this one, but should work if pulled into the base or just tweaked a little. This directory is more for future reference anyway.


### Multi_fix.py

If you hit eBay too often you'll get a captcha on the sold history of a listing with mutiple items. Running this will go through all the multilistings, check and update their history, make sure the total on the spreadsheet equals the total on the listing, and if it can't find a sale (often if the listing has >100 sold) it'll dump the rest of the sold quantity into one row with ignore=2

### feedback_update.py

Iterates through all the listings and updates the feedback to whatever the max is for each seller. Does not poll eBay, just goes through what we have as often sellers sell more than one item on different items

### get_location_data.py

When I added the city/state/country I had to go back through and repopulate all the listings, this automated that while trying to be smart and for a seller if the script already found the city/state/country would just pull from a dict.

### update_brand_model.py

Checks a listing's title for various keywords to populate the brand and model columns.