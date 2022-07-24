# Required functions/classes
from bs4 import BeautifulSoup
from time import time
from sys import exit
from math import ceil
import requests, json, lxml, re, sqlite3

headers = {
    "User-Agent":
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582"
}

search_term = input("Please enter your search term:\n")
amount_per_page = 240

# Print iterations progress function
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total:
        print()

def get_organic_results():
    print("\nStarting Search...\n")
    start = time()

    try:
        search = requests.get('https://www.ebay.com/sch/i.html?_nkw='+search_term+'&_ipg='+str(amount_per_page), headers=headers)
    except:
        print("ERROR: Connection timed out. Please try again.")
        exit()

    parsed_search = BeautifulSoup(search.content, "html.parser")
    parsed_search = parsed_search.find_all("h1")
    results_amount = re.findall(r">[,?\d+]+", str(parsed_search))[0][1:].replace(",","")
    page_amount = ceil(int(results_amount)/int(amount_per_page))

    print("Search Term: {}\nSearch Results: {}\nAmount Shown Per Page: {}\nNumber of Pages: {}\n".format(search_term, results_amount, amount_per_page, page_amount))
    print("Finished in {} Seconds\n".format(time()-start))

    db = sqlite3.connect(search_term.replace(' ', '')+'buy.db')
    cursor = db.cursor()
    cursor.execute("CREATE TABLE buy_now (name TEXT, link TEXT, price FLOAT, condition TEXT, shipping FLOAT)")
    cursor.execute("CREATE TABLE bid (name TEXT, link TEXT, price FLOAT, condition TEXT, shipping FLOAT, bids INTEGER, time_left FLOAT)")

    current_item = 0
    print("Collecting Search Results...")
    printProgressBar(current_item, int(results_amount), "Progress: [", "]")
    start = time()

    for n in range(page_amount):
        try:
            html = requests.get('https://www.ebay.com/sch/i.html?_nkw='+search_term+'&_ipg='+str(amount_per_page)+'&_pgn='+str(n+1), headers=headers).text
        except:
            print("\nERROR: Connection timed out. Please try again.")
            exit()
        soup = BeautifulSoup(html, 'lxml')

        for item in soup.select('.s-item__wrapper.clearfix'):
            title = item.select_one('.s-item__title').text.replace('"', '')
            link = re.findall(r"^.*\?", item.select_one('.s-item__link')['href'])[0][:-1]

            try:
                condition = item.select_one('.SECONDARY_INFO').text
            except:
                condition = None

            try:
                shipping = item.select_one('.s-item__logisticsCost').text.replace('Free', '').replace('shipping', '').replace(' ', '').replace('+$', '').replace('Shippingnotspecified', '').replace('estimate', '')
                if shipping == '':
                    shipping = 0
            except:
                shipping = 0

            try:
                location = item.select_one('.s-item__itemLocation').text
            except:
                location = None

            try:
                bid_count = int(item.select_one('.s-item__bidCount').text.replace('·', '').replace(' ', '').replace('bids', ''))
            except:
                bid_count = 0

            try:
                bid_time_left = item.select_one('.s-item__time-left').text.replace(' left', '')
                time_left = 0.00
                times = re.findall(r"\d+[mdh]", bid_time_left)
                for bid_time in times:
                    if bid_time[-1] == 'd':
                        time_left += int(bid_time[:-1])*24
                    if bid_time[-1] == 'h':
                        time_left += int(bid_time[:-1])
                    if bid_time[-1] == 'm':
                        time_left += int(bid_time[:-1])/60
                bid_time_left = round(time_left, 2)
            except:
                bid_time_left = None

            try:
                price = item.select_one('.s-item__price').text.replace('$', '').replace('estimate', '')
                price = re.findall(r"\d+\.\d+", price)
                highest_price = 0.00
                for n in price:
                    if float(n) > highest_price:
                        highest_price = float(n)
                price = highest_price
            except:
                price = None

            if str(title) == "Shop on eBay":
                pass
            elif (bid_count == 0) and (bid_time_left == None):
                cursor.execute('INSERT INTO buy_now VALUES ("{}", "{}", {}, "{}", {})'.format(str(title), str(link), float(price), str(condition), float(shipping)))
            else:
                cursor.execute('INSERT INTO bid VALUES ("{}", "{}", {}, "{}", {}, {}, "{}")'.format(str(title), str(link), float(price), str(condition), float(shipping), int(bid_count), float(bid_time_left)))

            db.commit()
            current_item += 1

        printProgressBar(current_item, int(results_amount), "Progress: [", "]")
    print("\nFinished in {} Seconds\n".format(time()-start))
    print()

if __name__ == "__main__":
    get_organic_results()
