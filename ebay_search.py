# Required functions/classes
from bs4 import BeautifulSoup
from time import time, sleep
from sys import exit
from math import ceil
from requests import get
from re import findall
from os.path import exists
from os import remove
from threading import Thread
import lxml, sqlite3
from LockableSqliteConnection import LockableSqliteConnection as lsc

## FILTER LISTS ##
# Database Filename
DB_FILTER_LIST = [' ', '/', '-', '.']
# Listing Title
TITLE_FILTER_LIST = ['"']
# Listing Shipping
SHIPPING_FILTER_LIST = ['Free 4 day shipping', 'Free 3 day shipping', 'Free', 'shipping',
                        ' ', '+', '$', 'Shippingnotspecified', 'Shipping not specified',
                        'estimate', 'day', 'Returns', 'returns', 'and', 'Accepted',
                        'Ships from United States']
# Listing Bids
BID_FILTER_LIST = ['·', ' ', 'bids', 'bid']
# Listing Time Left
TIME_LEFT_FILTER_LIST = [' ', 'left']
# Listing Price
PRICE_FILTER_LIST = ['$', 'estimate', ',']

# Declare browser headers for requests.
headers = {
    "User-Agent":
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582"
}

def ebay_page_parser(url, db, retry_attempts):
    """
    Scrape individual pages and save the results into the database.
    @params:
        url             -  url to scrape (Str)
        db              -  db class (LockableSqliteConnection)
        retry_attempts  -  number of retries before timout (Int)

    """

    try:
        # Attempt to get the search results
        attempt = 0
        for attempt in range(retry_attempts):
            try:
                page_info = get(url, headers=headers).text
                break
            except:
                sleep(.5)
                if (attempt+1) == retry_attempts:
                    raise
    except:
        print("\nERROR: Could not get the search results. Please try again.")
        exit()

    # Setup the info into a usable format.
    page_info = BeautifulSoup(page_info, 'lxml')

    # For listing on the page:
    for item in page_info.select('.s-item__wrapper.clearfix'):
        # Get the listing title.
        title = item.select_one('.s-item__title').text
        for filter_item in TITLE_FILTER_LIST:
            title = title.replace(filter_item, '')
        title = str(title)

        # Get the listing link.
        link = str(findall(r"^.*\?", item.select_one('.s-item__link')['href'])[0][:-1])

        # Get the listings condition.
        try:
            condition = str(item.select_one('.SECONDARY_INFO').text)
        except:
            condition = None

        # Get the listing shipping price.
        try:
            shipping = item.select_one('.s-item__logisticsCost').text
            for filter_item in SHIPPING_FILTER_LIST:
                shipping = shipping.replace(filter_item, '')
        except AttributeError:
            shipping = 0
        if shipping == '':
            shipping = 0
        shipping = round(float(shipping), 2)

        # Get the listing bid count.
        try:
            try:
                bid_count = item.select_one('.s-item__bidCount').text
                for filter_item in BID_FILTER_LIST:
                    bid_count = bid_count.replace(filter_item, '')
            except AttributeError:
                bid_count = 0
            bid_count = int(bid_count)
        except:
            bid_count = -1

        # Get the listing time left.
        try:
            bid_time_left = item.select_one('.s-item__time-left').text
            for filter_item in TIME_LEFT_FILTER_LIST:
                bid_time_left = bid_time_left.replace(filter_item, '')
            # Since the data point is in day hour minute form, turn it into number of hours.
            time_left = 0.00
            times = findall(r"\d+[mdh]", bid_time_left)
            for bid_time in times:
                if bid_time[-1] == 'd':
                    time_left += int(bid_time[:-1])*24
                if bid_time[-1] == 'h':
                    time_left += int(bid_time[:-1])
                if bid_time[-1] == 'm':
                    time_left += int(bid_time[:-1])/60
            bid_time_left = round(time_left, 2)
        except:
            bid_time_left = -1

        # Get the listing price.
        try:
            price = item.select_one('.s-item__price').text
            for filter_item in PRICE_FILTER_LIST:
                price = price.replace(filter_item, '')

            # Sometimes there will be multiple prices listed, therefore only get the highest price.
            prices = findall(r"\d+\.\d+", price)
            highest_price = 0.00
            for price in prices:
                if float(price) > highest_price:
                    highest_price = float(price)
            price = round(float(highest_price), 2)
        except:
            price = -1

        # Get rid of listing that don't exist.
        if title == "Shop on eBay":
            pass
        # Add the listing to the correct table in the database.
        elif (bid_count == 0) and (bid_time_left == -1):
            with db:
                db.cursor.execute('INSERT INTO buy_now VALUES ("{}", "{}", {}, "{}", {})'.format(title, link, price, condition, shipping))
        else:
            with db:
                db.cursor.execute('INSERT INTO auction VALUES ("{}", "{}", {}, "{}", {}, {}, "{}")'.format(title, link, price, condition, shipping, bid_count, bid_time_left))

def get_organic_results(search_term, amount_per_page = 240, retry_attempts = 3, verbose = True):
    """
    Scrape ebay for search results.
    @params:
        search_term       - Required  : term to search on ebay (Str)
        amount_per_page   - Optional  : results per page on ebay (Int)
        retry_attempts    - Optional  : timeout retrys (Int)
        verbose           - Optional  : print progress (Bool)

    """

    ## SETUP THE DATABASE ##

    # Create database name
    db_name = search_term
    for filter_item in DB_FILTER_LIST:
        db_name = db_name.replace(filter_item, '')

    db_name += "_ebay_listings.db"

    # Connect to the database
    if exists(db_name):
        if verbose == True:
            print("\nFound database, deleting.")
        remove(db_name)

    try:
        # Attempt to connect to the database
        attempt = 0
        for attempt in range(retry_attempts):
            try:
                db = sqlite3.connect(db_name)
                if verbose == True:
                    print("\nConnected to Database.\n")
                break
            except:
                sleep(.5)
                if (attempt+1) == retry_attempts:
                    raise
    except:
        # If the databse cannot be connected to, stop the program.
        print("ERROR: Could not connect to database. Please try again.")
        exit()

    try:
        # Attempt to setup the database
        attempt = 0
        for attempt in range(retry_attempts):
            try:
                cursor = db.cursor()
                # Create two different tables, one to store buy it now listings, and another to store auctions.
                cursor.execute("CREATE TABLE buy_now (name TEXT, link TEXT, price FLOAT, condition TEXT, shipping FLOAT)")
                cursor.execute("CREATE TABLE auction (name TEXT, link TEXT, price FLOAT, condition TEXT, shipping FLOAT, bids INTEGER, time_left FLOAT)")
                cursor.close()
                if verbose == True:
                    print("Created the Database.\n")
                break
            except:
                sleep(.5)
                if (attempt+1) == retry_attempts:
                    raise
    except:
        # If the tables cannot be created, stop the program.
        print("ERROR: Could not create the database. Please try again.")
        exit()

    ## GATHER INFO ABOUT SEARCH QUERY ##

    # If verbose is tured off, nothing will output in the terminal.
    if verbose == True:
        print("Retreiving Page...\n")
        start = time()

    try:
        # Attempt to get the search query
        attempt = 0
        for attempt in range(retry_attempts):
            try:
                search = get('https://www.ebay.com/sch/i.html?_nkw='+search_term+'&_ipg='+str(amount_per_page), headers=headers)
                if verbose == True:
                    print("Finished in {:.2f} Seconds\n".format(time()-start))
                break
            except:
                sleep(.5)
                if (attempt+1) == retry_attempts:
                    raise
    except:
        # If the query times out, stop the program.
        print("ERROR: Retreival connection timed out. Please try again.")
        exit()

    if verbose == True:
        print("Collecting Results...\n")
        start = time()

    # Parse the result and find the headers (on the ebay search page there is only one h1 header, and it contains the information needed.)
    parsed_search = BeautifulSoup(search.content, "html.parser").find_all("h1")

    # Sort the info
    results_amount = findall(r">[,?\d+]+", str(parsed_search))[0][1:].replace(",","")
    page_amount = ceil(int(results_amount)/int(amount_per_page))

    if verbose == True:
        print("Search Term: {}\nDatabase Name: {}\nSearch Results: {}\nAmount Shown Per Page: {}\nNumber of Pages: {}\n".format(search_term, db_name, results_amount, amount_per_page, page_amount))
        print("Finished in {:.2f} Seconds\n".format(time()-start))

    ## COLLECT THE LISTINGS ##

    if verbose == True:
        print("Collecting Search Results...")
        start = time()

    # Declare the database.
    db = lsc(db_name)

    if verbose == True:
        percentage_done = 0
        print("\n\rProgress: {}%".format(percentage_done), end='\r')

    # Get the listings.
    for n in range(page_amount):
        ebay_page_parser('https://www.ebay.com/sch/i.html?_nkw='+search_term+'&_ipg='+str(amount_per_page)+'&_pgn='+str(n+1), db, retry_attempts)
        if verbose == True:
            percentage_done = round((n+1)/page_amount*100, 2)
            print("\rProgress: {}%".format(percentage_done), end='\r')

    if verbose == True:
        print("\n\nFinished in {} Seconds".format(time()-start))
    print()

if __name__ == "__main__":
    search = input("Please enter your search term:\n")
    get_organic_results(search)
