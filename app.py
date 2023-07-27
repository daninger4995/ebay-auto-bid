from flask import Flask, render_template, request, redirect
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.logfile import LogFile
from selenium.common.exceptions import NoSuchElementException, WebDriverException
import time
import threading
from pyvirtualdisplay import Display
from datetime import datetime
import dateutil.relativedelta as rd

# Credentials
from credentials import ebay_username, ebay_password

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        item_url = request.form['item_url']
        max_bid = request.form['max_bid']
        bid_timing = int(request.form['bid_timing'])
        bid_frequency = int(request.form['bid_frequency'])

        # Start a new thread for bidding on the item
        threading.Thread(target=bid_on_item, args=(item_url, max_bid, bid_timing, bid_frequency), name='bid_on_item').start()

        return redirect('/')
    else:
        return render_template('index.html')

def bid_on_item(item_url, max_bid, bid_timing, bid_frequency):
    display = Display(visible=0, size=(800, 600))
    display.start()
    try:
        driver = webdriver.Firefox(service=Service(log_file=LogFile('geckodriver.log')))
        
        # Login to eBay
        driver.get('https://www.ebay.com')
        time.sleep(3)
        io = driver.find_element_by_link_text('Sign in')
        io.click()
        time.sleep(3)
        elements = driver.find_elements_by_class_name("fld")
        elements[2].send_keys(ebay_username)
        elements[3].send_keys(ebay_password)
        button = driver.find_element_by_id("sgnBt")
        button.click()
        time.sleep(2)
        
        # Navigate to item
        driver.get(item_url)
        time.sleep(2)

        end_time_str = driver.find_element_by_class_name('vi-tm-left').text  # Example: "Ends in 5h 3m"
        end_time = calculate_end_time(end_time_str)

        # Calculate the time to wait before the first bid
        bid_start_time = end_time - (bid_timing * 60)
        wait_time = bid_start_time - time.time()

        if wait_time > 0:
            time.sleep(wait_time)

        # Start bidding
        for i in range(bid_frequency):
            try:
                elements = driver.find_element_by_id("MaxBidId")
                elements.send_keys(max_bid)
                elements = driver.find_element_by_id("bidBtn_btn")
                elements.click()
                time.sleep(3)
                io = driver.find_element_by_css_selector("a[id*='reviewBidSec_btn']")
                io.click()
            except NoSuchElementException as e:
                print(f"No Such Element Exception: {str(e)}")
                break  # Exit the loop if we can't find the element (probably because the auction ended)

            # Wait for the time interval between bids, unless this is the last iteration of the loop
            if i < bid_frequency - 1:
                time.sleep(bid_timing * 60)

    except WebDriverException as e:
        print(f"WebDriverException occurred: {str(e)}")
    finally:
        driver.quit()
        display.stop()

def calculate_end_time(end_time_str):
    # The end time string is expected to be something like "Ends in 5h 3m"
    time_parts = end_time_str.replace('Ends in', '').split()
    rel_delta_args = {}
    for i in range(0, len(time_parts), 2):
        val = int(time_parts[i])
        unit = time_parts[i+1].lower()[0]  # The first character of 'h', 'm', 's', etc.
        if unit == 'h':
            rel_delta_args['hours'] = val
        elif unit == 'm':
            rel_delta_args['minutes'] = val
        elif unit == 's':
            rel_delta_args['seconds'] = val

    end_time = datetime.now() + rd.relativedelta(**rel_delta_args)
    return end_time.timestamp()

if __name__ == '__main__':
    app.run(debug=True)
