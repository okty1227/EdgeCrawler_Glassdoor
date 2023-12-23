# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.common.exceptions import NoSuchElementException
# from bs4 import BeautifulSoup
# import time 
# import json
# import math
import asyncio
import time
from typing import List
from crawler import CONNECTION
from preprocess import PREPROCESS
from loadmongo import load_to_mongo_db

url_scientist = 'https://www.glassdoor.com/Job/united-states-data-scientist-jobs-SRCH_IL.0,13_IN1_KO14,28.htm'
url_bi_analyst = 'https://www.glassdoor.com/Job/united-states-business-intelligence-analyst-jobs-SRCH_IL.0,13_IN1_KO14,43.htm'
url_bi_engineer = 'https://www.glassdoor.com/Job/united-states-business-intelligence-engineer-jobs-SRCH_IL.0,13_IN1_KO14,44.htm'
url_dataspecialist = 'https://www.glassdoor.com/Job/united-states-data-specialist-jobs-SRCH_IL.0,13_IN1_KO14,29.htm'
url_data_engineer = 'https://www.glassdoor.com/Job/united-states-data-engineer-jobs-SRCH_IL.0,13_IN1_KO14,27.htm'

port_ = "mongodb://localhost:8585/"
# jobs_catalog = [url_scientist,
#                      url_bi_analyst,
#                      url_bi_engineer,
#                      url_dataspecialist,
#                      url_data_engineer]
jobs_catalog = [url_bi_engineer,
                     url_dataspecialist,
                     url_data_engineer]
# async def run_main():
#     for job_link in jobs_catalog:
#         glassdoor_connect = CONNECTION(url=job_link)
#         result = await glassdoor_connect.main()
#         # print(result)
#         processed = PREPROCESS.run_preprocess(crawed_raw_data=result)
       
#         load_to_mongo_db(loaded_data=processed,port_link=port_)

# asyncio.run(run_main())



# async def process_job(job_link,port_endpoint:str):
    
#     glassdoor_connect = CONNECTION(url=job_link)
#     crawed_output = await glassdoor_connect.run_crawler()
#     processed = PREPROCESS.run_preprocess(crawed_raw_data=crawed_output)
    
#     load_to_mongo_db(loaded_data=processed,port_link=port_endpoint)


# async def run_craw_to_storage(jobs_catalog:List,port_endpoint:str):
#     tasks = [process_job(job_link=job,port_endpoint=port_endpoint) for job in jobs_catalog]
#     await asyncio.gather(*tasks)


# asyncio.run(run_craw_to_storage)

# class JobProcessor:
#     def __init__(self, job_link: str, port_endpoint: str, job_name: str):
#         self.job_link = job_link
#         self.port_endpoint = port_endpoint
#         self.job_name = job_name

#     async def process_job(self):
#         crawed_output = await CONNECTION(url=self.job_link).run_crawler()
#         # crawed_output = await glassdoor_connect
#         processed = await PREPROCESS.run_preprocess(crawed_raw_data=crawed_output)
#         load_to_mongo_db(loaded_data=processed, port_link=self.port_endpoint,collection_name=self.job_name)

# async def run_craw_to_storage(jobs_catalog: List, port_endpoint: str):
#     tasks = [JobProcessor(job_link=job_url, job_name=job_title, port_endpoint=port_endpoint).process_job() for job_title,job_url in jobs_catalog.items()]
#     await asyncio.gather(*tasks)


def crawl_process(job_link: str,job_name,port_endpoint):

    crawler = CONNECTION(url=job_link)
    crawler.connect_glassdoor()      
    crawed_result = crawler.load_positions()
    
    processed = PREPROCESS.run_preprocess(crawed_raw_data=crawed_result)
    load_to_mongo_db(loaded_data=processed, port_link=port_endpoint,collection_name=job_name)
    

async def run_async_crawling(job_link,job_name,port_endpoint):
    return await asyncio.to_thread(crawl_process(job_link,job_name,port_endpoint))

async def run_craw_to_storage(jobs_catalog: List, port_endpoint: str):
    tasks = []
    
    for job_title,job_url in jobs_catalog.items():
        task = (run_async_crawling(job_link=job_url, job_name=job_title, port_endpoint=port_endpoint))
        tasks.append(task)

    await asyncio.gather(*tasks)
    





jobs_catalog = {
    'data_scientist': 'https://www.glassdoor.com/Job/new-york-state-data-scientist-intern-jobs-SRCH_IL.0,14_IS428_KO15,36.htm'
    # 'bi_analyst': 'https://www.glassdoor.com/Job/united-states-business-intelligence-analyst-jobs-SRCH_IL.0,13_IN1_KO14,43.htm',
    # 'bi_engineer': 'https://www.glassdoor.com/Job/united-states-business-intelligence-engineer-jobs-SRCH_IL.0,13_IN1_KO14,44.htm',
    # 'data_specialist': 'https://www.glassdoor.com/Job/united-states-data-specialist-jobs-SRCH_IL.0,13_IN1_KO14,29.htm',
    # 'data_engineer': 'https://www.glassdoor.com/Job/united-states-data-engineer-jobs-SRCH_IL.0,13_IN1_KO14,27.htm'
}
endpoint = "mongodb://localhost:8585/"
start_t = time.perf_counter()
asyncio.run(run_craw_to_storage(jobs_catalog, endpoint))
end_t = time.perf_counter()

print(end_t-start_t)
