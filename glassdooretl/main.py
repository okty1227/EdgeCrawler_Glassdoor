# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.common.exceptions import NoSuchElementException
# from bs4 import BeautifulSoup
# import time
# import json
import asyncio
# import math
from crawler import CONNECTION
from preprocess import PREPROCESS
from loadmongo import load_to_mongo_db

url_scientist = 'https://www.glassdoor.com/Job/united-states-data-scientist-jobs-SRCH_IL.0,13_IN1_KO14,28.htm'
url_bi_analyst = 'https://www.glassdoor.com/Job/united-states-business-intelligence-analyst-jobs-SRCH_IL.0,13_IN1_KO14,43.htm'
url_bi_engineer = 'https://www.glassdoor.com/Job/united-states-business-intelligence-engineer-jobs-SRCH_IL.0,13_IN1_KO14,44.htm'
url_dataspecialist = 'https://www.glassdoor.com/Job/united-states-data-specialist-jobs-SRCH_IL.0,13_IN1_KO14,29.htm'
url_data_engineer = 'https://www.glassdoor.com/Job/united-states-data-engineer-jobs-SRCH_IL.0,13_IN1_KO14,27.htm'

port_ = "mongodb://localhost:8585/"
jobs_catalog = [url_scientist,
                     url_bi_analyst,
                     url_bi_engineer,
                     url_dataspecialist,
                     url_data_engineer]

async def run_main():
    for job_link in jobs_catalog:
        glassdoor_connect = CONNECTION(url=job_link)
        result = await glassdoor_connect.main()
        print(result)
        processed = PREPROCESS.run_preprocess(crawed_raw_data=result)
       
        load_to_mongo_db(loaded_data=processed,port_link=port_)

asyncio.run(run_main())







