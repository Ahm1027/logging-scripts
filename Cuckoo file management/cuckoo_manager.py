# Author: Ahmed Naveed Asif

from bs4 import BeautifulSoup
from selenium import webdriver
import numpy as np
import platform
import time
import re
import shutil
import os

from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service

cuckoo = 'https://cuckoo.cert.ee/'
urls = []

global log_file, log_position_file, json_log_file

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
binaries_directory = os.path.join('/dionaea/lib/dionaea/binaries/')
submitted_directory = os.path.join(BASE_DIR, 'submitted_done')
reports_directory = os.path.join(BASE_DIR, 'reports')
submitted_progress_file = os.path.join(BASE_DIR, 'submitted.npy')

log_file = "progress.log"

opts = ['export_files', 'export_shots', 'export_buffer', 'export_extracted', 'export_memory', 'export_curtain',
 'export_package_files', 'redsocks.log', 'export_logs', 'export_suricata', 'export_network', 'export_task.json',
 'export_binary', 'export_cuckoo.log', 'export_dump.pcap', 'export_analysis.log', 'export_files.json',
 'export_reboot.json', 'export_tlsmaster.txt', 'export_dump_sorted.pcap']

def loadUrls():
    try:
        urls = np.load(submitted_progress_file)
    except FileNotFoundError as e:
    # File not created yet
        pass

def saveUrls():
        np.save(submitted_progress_file, np.array(urls))

def checkForCompleted():
        for idx, x in enumerate(urls):
                options = webdriver.ChromeOptions()
                prefs = {
                        "download.default_directory": reports_directory,
                        "download.prompt_for_download": False,
                        "download.directory_upgrade": True
                }
                options.add_experimental_option('prefs', prefs)
                options.add_argument('--headless')
                options.add_argument('--no-sandbox')
                ser = Service('/usr/bin/chromedriver')
                driver = webdriver.Chrome(service=ser, options=options)
                driver.get(x)
                try:
                        completed = driver.find_element_by_xpath('//tr[@class="clickable finished"]')
                        if completed:
                                curr_url = 'https://cuckoo.cert.ee/analysis/'+completed.get_attribute('data-task-id')+'/export/'
                                driver.get(curr_url)
                                for y in opts:
                                        try:
                                                option = driver.find_element_by_xpath('//label[@for= "'+y+'"]')
                                                if option:
                                                        option.click()
                                        except NoSuchElementException:
                                                continue
                                content = driver.find_element_by_tag_name('form')
                                if content:
                                        download_btn = driver.find_element_by_xpath('//button[@class="btn btn-primary center-block"]')
                                        if (download_btn):
                                                download_btn.click()
                                                time.sleep(15)
                                                print(x+" downloaded successfully!")
                                urls.pop(idx)
                                saveUrls()
                        driver.close()
                except NoSuchElementException:
                        print(f"Report {x} could not be downloaded")
                        continue

def submit():
        loadUrls()
        for root, dirs, files in os.walk(binaries_directory):
            for file in files:
                file_path = os.path.join(binaries_directory, file)
                print("File path: ",file_path)
                ser = Service('/usr/bin/chromedriver')
                options = webdriver.ChromeOptions()
                options.add_argument('--headless')
                options.add_argument('--no-sandbox')
                driver = webdriver.Chrome(service=ser, options=options)
                driver.get(cuckoo)
                try:
                    inputs = driver.find_element_by_id('file')
                    if inputs:
                        inputs.send_keys(file_path)
                        time.sleep(20)
                        file_label = driver.find_element_by_xpath('//label[@for="filetree-1"]')
                        file_check = driver.find_element_by_xpath('//input[@id="filetree-1"]')
                        analysis = driver.find_element_by_id('start-analysis')
                        if not file_check.is_selected():
                                file_label.click()
                        if analysis:
                                analysis.click()

                        current_url = driver.current_url
                        current_url = current_url.replace('pre', 'post')
                        urls.append(current_url)
                        saveUrls()
                        destination = os.path.join(submitted_directory, file)
                        print(f"Moving {file_path} to {destination}")
                        shutil.move(file_path, destination)

                        print(f"[===INFO===] Submitted file to, {current_url} successfully")
                        print("Number of files submitted: ",len(urls))
                        driver.close()

                except NoSuchElementException:
                    driver.close()
                    continue
            return "Submitted all files"
        return "No Files not found"

submit()
checkForCompleted()
