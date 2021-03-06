from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from google.cloud import bigquery
# from gcloud import storage
import csv
from concurrent.futures import ThreadPoolExecutor
import threading
import time
from google.cloud import storage

print("running script")

thread_local = threading.local()

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

# csv_folder = "/content/drive/MyDrive/Colab Notebooks/skw scraping/NYTaxes.csv"
csv_folder = "/NYTaxes.csv"

f = open(csv_folder, "w")

writer = csv.writer(f)

headers = ["borough", "block", "lot", "bbl", "accountBalanceErrors"]

writer.writerow(headers)

# project_id = "skw-test"
project_id = "data-project-1-350416"
client = bigquery.Client(project=project_id)

# query = "SELECT borough,block,lot,bbl FROM `skw-test.test_cloud_function.filteredPropertiesNY` LIMIT 30"
# query = "SELECT borough,block,lot,bbl FROM (SELECT borough,block,lot,bbl, ROW_NUMBER () OVER(ORDER BY bbl DESC) AS windex FROM `skw-test.test_cloud_function.filteredPropertiesNY`) WHERE windex BETWEEN 1 AND 100"
# query = "SELECT borough,block,lot,bbl FROM (SELECT borough,block,lot,bbl, ROW_NUMBER () OVER(ORDER BY bbl DESC) AS windex FROM `data-project-1-350416.assessor_results.properties_ny`) WHERE windex BETWEEN 200001 AND 273057"
query = "SELECT borough,block,lot,bbl FROM `data-project-1-350416.assessor_results.properties_ny`"

query_job = client.query(query)

def get_driver():
  if not hasattr(thread_local, "driver"):
    thread_local.driver = webdriver.Chrome('chromedriver',options=chrome_options)  
  return thread_local.driver

def get_client():
  if not hasattr(thread_local, "bigqueryClient"):
    thread_local.bigqueryClient = bigquery.Client(project=project_id)
  return thread_local.bigqueryClient

def save_on_csv(row, message):
  line = [row['borough'], row['block'], row['lot'], row['bbl'], message]
  writer.writerow(line)

def processRow(row):
  try:
    driver = get_driver()
    bq_client = get_client()
    
    driver.get("https://a836-pts-access.nyc.gov/care/Search/Disclaimer.aspx?FromUrl=../search/commonsearch.aspx?mode=persprop")
    driver.find_element(By.ID,"btAgree").click()

    Borough_select = Select(driver.find_element(By.ID,"inpParid"))
    Block_input = driver.find_element(By.ID,"inpTag")
    lot_input = driver.find_element(By.ID,"inpStat")

    # Borough = str(row['bbl'])[0] 
    Borough = row['bbl'][0]
    Block = row['block']
    Lot = row['lot']

    Block_input.send_keys(Block)
    lot_input.send_keys(Lot)
    Borough_select.select_by_value(Borough)

    driver.find_element(By.ID,"btSearch").click()

    driver.find_element(By.XPATH,'//*[@id="sidemenu"]/ul/li[2]/a').click()

    notes = driver.find_element(By.XPATH,'//*[@id="Notes"]/tbody/tr[1]/td')

    try:
      total_account_balance = driver.find_element(By.XPATH, '//*[@id="Account Balance Summary"]/tbody/tr[5]/td[6]').text
    except:
      total_account_balance = "0"

    total_account_balance = float(total_account_balance.replace(',', ''))

    """ safe on bq table """
    if total_account_balance >= 1000:
      rows_to_insert = [
        {'bbl': row['bbl'], 'distress_signal': 'Overdue Taxes', 'created_date': time.time(), 'account_balance': total_account_balance}
      ]
    #   rows_to_insert = [
    #     {'bbl': str(row['bbl']), 'distress_signal': 'Overdue Taxes', 'created_date': time.time()}
    #   ]
    #   errors = bq_client.insert_rows_json('skw-test.test_cloud_function.taxesNYpropertyDS', rows_to_insert)
      errors = bq_client.insert_rows_json('data-project-1-350416.assessor_results.distress_signal', rows_to_insert)
      if errors == []:
        # print("New rows have been added.")
        pass
      else:
        save_on_csv(row, "Encountered errors while inserting rows: {}".format(errors))
  except Exception as e:
    """ if error save on csv """
    save_on_csv(row, f"errors running scraping: {e}")

with ThreadPoolExecutor(max_workers=6) as executor:
  for row in query_job:
    executor.submit(processRow, row)

# driver.quit()
for thread in threading.enumerate():
  if hasattr(thread, "driver"): 
    print("closing driver for one thread")
    thread.driver.quit()

""" close errors file """
f.close()
print("closing csv file with errors")

""" Logic to save csv on cloud storage """
print("saving errors on cloud storage")
client_storage = storage.Client()
bucket = client_storage.get_bucket('skw-data-lake')
blob = bucket.blob('errorsScraping/NYTaxesErrosFile.csv')
blob.upload_from_filename(csv_folder)
print("script finish")