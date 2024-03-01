# LittleFieldLabsWebScraper

A web scraper script written in python to scrape the littlefield labs simulation for data and output it to excel sheet

I ran this on a crontab every hour to scrape new data when it came out.

You will need to set a couple of env vars in order for this script to auth to LittleField and do its work:

LF_PASSWORD
LF_USERNAME

Optionally, you can set the output file by setting env var:

OUTPUT_FILE
