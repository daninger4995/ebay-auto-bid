from flask import Flask, render_template, request
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import threading
from dateutil.parser import parse
from datetime import datetime
from credentials import ebay_username, ebay_password

app = Flask(__name__)

def bid_on_item(item_url, max_bid, bid_frequency):
    driver = webdriver.Firefox()  # Make sure you have Firefox and the related driver installed
    driver.get('https://www.ebay.com')
    time.sleep(3)
    
    # Login
    driver.find_element_by_link_text('Sign in').click()
    time.sleep(3)
    driver.find_element_by_id('userid').send_keys(ebay_username)
    driver.find_element_by_id('pass').send_keys(ebay_password)
    driver.find_element_by_id('sgnBt').click()
    time.sleep(2)
    
    # Go to item page
    driver.get(item_url)
    time.sleep(3)
    
    # Fetch auction end time
    auction_end_time = driver.find_element_by_class_name('vi-tm-left').text
    auction_end_time = parse(auction_end_time)  # Convert to datetime object
    current_time = datetime.now()
    time_diff = auction_end_time - current_time
    time_to_start_bidding = time_diff.total_seconds() - (bid_frequency * 60)
    
    # Schedule the bids
    if time_to_start_bidding > 0:
        for i in range(int(time_to_start_bidding), 0, -bid_frequency*60):
            threading.Timer(i, place_bid, args=[driver, max_bid]).start()
    else:
        print('Not enough time to start bidding')

def place_bid(driver, max_bid):
    # Refresh page and place bid
    driver.refresh()
    time.sleep(3)
    driver.find_element_by_id('MaxBidId').send_keys(max_bid)
    driver.find_element_by_id('bidBtn_btn').click()
    time.sleep(3)
    driver.find_element_by_css_selector("a[id*='reviewBidSec_btn']").click()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        item_url = request.form['item_url']
        max_price = request.form['max_price']
        bid_frequency = int(request.form['bid_frequency']) # in minutes
        
        # Schedule the bid
        threading.Thread(target=bid_on_item, args=[item_url, max_price, bid_frequency]).start()

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
