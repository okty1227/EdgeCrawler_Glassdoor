# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.common.exceptions import NoSuchElementException
# from bs4 import BeautifulSoup
# import time
import json
# import math
from crawler import CONNECTION
from preprocess import PREPROCESS
# from loadmongo import load_to_mongo_db


port_ = "mongodb://localhost:8585/"
jobs_catalog = {
    'data_scientist':'https://www.glassdoor.com/Job/united-states-data-scientist-jobs-SRCH_IL.0,13_IN1_KO14,28.htm',
    'bi_analyst': 'https://www.glassdoor.com/Job/united-states-business-intelligence-analyst-jobs-SRCH_IL.0,13_IN1_KO14,43.htm',
    'bi_engineer': 'https://www.glassdoor.com/Job/united-states-business-intelligence-engineer-jobs-SRCH_IL.0,13_IN1_KO14,44.htm',
    'dataspecialist':'https://www.glassdoor.com/Job/united-states-data-specialist-jobs-SRCH_IL.0,13_IN1_KO14,29.htm',
    'data_engineer':'https://www.glassdoor.com/Job/united-states-data-engineer-jobs-SRCH_IL.0,13_IN1_KO14,27.htm'
}

def run_main():
    for job_name, job_link in jobs_catalog.items():
        glassdoor_connect = CONNECTION(url=job_link,full_search=False,search_limit=100)
        result = glassdoor_connect.main()
        # print(result)
        processed = PREPROCESS.run_preprocess(crawed_raw_data=result)
        with open(f'{job_name}_glassdoor.json','w') as file:
            json.dump(obj=processed,fp=file) 
        # load_to_mongo_db(loaded_data=processed,port_link=port_)


if __name__ == '__main__':
    run_main()





