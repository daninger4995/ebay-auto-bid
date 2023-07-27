from flask import Flask, render_template, request
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import threading
from credentials import ebay_username, ebay_password

app = Flask(__name__)

def bid_on_item(item_url, max_bid):
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
    
    # Go to item page and place bid
    driver.get(item_url)
    time.sleep(3)
    driver.find_element_by_id('MaxBidId').send_keys(max_bid)
    driver.find_element_by_id('bidBtn_btn').click()
    time.sleep(3)
    driver.find_element_by_css_selector("a[id*='reviewBidSec_btn']").click()
    time.sleep(20)
    driver.quit()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        item_url = request.form['item_url']
        max_price = request.form['max_price']
        bid_frequency = int(request.form['bid_frequency']) # in minutes
        bid_timing = int(request.form['bid_timing']) # in minutes before auction ends
        
        # Schedule the bid
        for i in range(bid_timing, 0, -bid_frequency):
            threading.Timer(i * 60, bid_on_item, args=[item_url, max_price]).start()

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
