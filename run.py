import json
import requests
import yaml
from datetime import datetime
import apprise
import yaml
import shutil
import os
import schedule
import time
import re
from os import path
from loguru import logger
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import InvalidSessionIdException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

#Function to check if we have a number in the message that we get so we will
#know if we need to raise notification 
def contains_non_zero_number(string):
    for char in string:
        if char.isdigit() and int(char) != 0:
            return True
    return False

#Function to read the configuration file
def read_config(config_path):
  with open(config_path) as stream:
      try:
          return (yaml.safe_load(stream))
      except yaml.YAMLError as e:
          return False

#Main function for gettting kid information 
def get_kid_information(kid_name, kid_username, kid_password, out_message_delimiter, screenshot_file_name, debug):
  #Set private params. 
  main_ofek_url = "https://myofek.cet.ac.il/he"
  s_delay = 5
  ofek_user_field = '//*[@id="HIN_USERID"]' 
  ofek_password_field = '//*[@id="Ecom_Password"]'
  ofek_edu_login_btn = '//*[@id="loginButton2"]'

  #Create Drivre and set options :
  s_options = webdriver.ChromeOptions()
  s_options.add_argument("-incognito")
  s_options.add_argument("--window-size=1920,1080")
  s_options.add_argument("--headless")
  s_options.add_argument("disable-gpu")
  s_options.add_argument("--no-sandbox")
  s_options.add_argument('--start-maximized')
  s_options.add_argument("--disable-dev-shm-usage")

  s_browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=s_options)
  s_browser = maximize_window()

  #Start , opening the page ... 
  s_browser.get(main_ofek_url)
  
  #Moving to the right page
  WebDriverWait(s_browser, s_delay).until(EC.presence_of_element_located(("xpath",'/html/body/div/div/div/header/div[1]/div/button'))).click()
  WebDriverWait(s_browser, s_delay).until(EC.presence_of_element_located(("xpath",'/html/body/div/div/div/header/div[1]/div/div/div/dialog/div/section/div[2]/div/button'))).click()
  s_browser.get(s_browser.current_url.replace('EduCombinedAuthSms','EduCombinedAuthUidPwd'))  
  if debug:
    s_browser.save_screenshot("./output/1.png")
  # Enter Username
  WebDriverWait(s_browser, s_delay).until(EC.presence_of_element_located(("xpath", ofek_user_field))).send_keys(kid_username)
  if debug:
    s_browser.save_screenshot("./output/2.png")
  # Enter Password
  WebDriverWait(s_browser, s_delay).until(EC.presence_of_element_located(("xpath", ofek_password_field))).send_keys(kid_password)
  if debug:
    s_browser.save_screenshot("./output/3.png")
  # Click the login button
  s_browser.find_element("xpath",ofek_edu_login_btn).click()

  #Wait 10 seconds 
  time.sleep(10)
  if debug:
    s_browser.save_screenshot("./output/4.png")
  #Get the information from the site
  #Get the main screenshot !!! 
  # Use JavaScript to get the full width and height of the webpage
  width = s_browser.execute_script("return Math.max( document.body.scrollWidth, document.body.offsetWidth, document.documentElement.clientWidth, document.documentElement.scrollWidth, document.documentElement.offsetWidth );")
  height = s_browser.execute_script("return Math.max( document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight );")

  # Set the window size to match the entire webpage
  s_browser.set_window_size(width, height)

  # Find the full page element (usually 'body') and capture the screenshot
  full_page = s_browser.find_element(By.TAG_NAME, "body")
  full_page.screenshot("./output/"+screenshot_file_name)

  if debug:
    s_browser.save_screenshot("./output/5.png")
  todo_text = s_browser.execute_script('return document.getElementsByClassName("TasksTab_tabLabel__vyFev TasksTab_selected__ukrf3")[0].innerHTML;')
  time.sleep(2)
  if debug:
    s_browser.save_screenshot("./output/6.png")
  recheck_text = s_browser.execute_script('return document.getElementsByClassName("TasksTab_tabLabel__vyFev TasksTab_selected__ukrf3")[1].innerHTML;')
  time.sleep(2)
  if debug:
    s_browser.save_screenshot("./output/7.png")
  done_text = s_browser.execute_script('return document.getElementsByClassName("TasksTab_tabLabel__vyFev TasksTab_selected__ukrf3")[2].innerHTML;')
  time.sleep(2)
  if debug:
    s_browser.save_screenshot("./output/8.png")
  wait_text = s_browser.execute_script('return document.getElementsByClassName("TasksTab_tabLabel__vyFev TasksTab_selected__ukrf3")[3].innerHTML;')  

  #Create out message: 
  out_message=todo_text+out_message_delimiter+recheck_text+out_message_delimiter+done_text+out_message_delimiter+wait_text

#Function to send notification
def send_notification(message, ha_url):
  data = {'message': message}
  response = requests.post(ha_url, data=data)
  return response 
  
#Setting Global Params 
main_config_path = './config/config.yaml'

#Get the data from the config file 
data=read_config(main_config_path)
if data == False:
  quit() 

#Starting .. We will do this for each kid . 
for kid in data["kids"]:
  #Run the function : 
  try: 
    screenshot_name = "output.png"
    message_output = get_kid_information(kid["name"],kid["username"], kid["password"], data["out_message_delimiter"],screenshot_name,data["debug"])
    
    if contains_non_zero_number(message_output): 
      #We have something that needs to be done
      message_output="Notice !! "+message_output
    else: 
      #We dont need anything , lets send debug message 
      #quit()
      message_output = "Nothing to do"
  except Exception as e:
    message_output = kid["name"]+" | Unable to access Ofek | "+str(e)
    
  #Send notification 
  #send_notification(message_output, data["ha_url"])  
  #save message 
  with open("./output/message.txt", "w") as file:
    file.write(message_output)

# Example usage
#message = "This is a test message with an image."
#image_path = '/tmp/1.png
