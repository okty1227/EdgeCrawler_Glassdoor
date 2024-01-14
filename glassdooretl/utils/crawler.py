from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

import time
import json
import math
import re
import logging
logging.basicConfig(filename='./log/crawlerLog.log',level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
# class CONFIG():
#     '''pending'''
#     def check_read_conf(conf_search_preference:str):
        
#         with open(conf_search_preference, 'r') as file:
#             conf = json.load(file)

#         if 'easy_apply_only' not in conf or not isinstance(conf['easy_apply_only'], bool):
#             raise ValueError("easy_apply_only does not fullfill expected format")

#         if 'Salary_Range' not in conf or not isinstance(conf['Salary_Range'], list) or len(conf['Salary_Range']) != 2:
#             raise ValueError("Salary_Range does not fullfill expected format")

#         if 'Company_Rating_atleast' not in conf or not isinstance(conf['Company_Rating_atleast'], (int, float)):
#             raise ValueError("Company_Rating_atleast does not fullfill expected format")

#         if 'last_date_posted' not in conf or not conf['last_date_posted'] in ['one day','three days','week','month'] :
#             raise ValueError("last_date_posted does not fullfill expected format")

#         print("Config File Check Passed")
#         return conf
    
class CONNECTION():
    
    with open('config-baseSetting.json', 'r') as file:
        conf = json.load(file)
        
    exist_close_view = conf["xpath"]["exist_close_view"] # locator for closing pop up window button
    exist_close_invitation = conf["xpath"]["exist_close_invitation"] # locator for closing invitation pop up window button
    show_more_job = conf["xpath"]["show_more_job"] # locator for clicking more job

    basicInfo_Xpath = conf["xpath"]["basic_info"] # locator for basic info
    ifEasyApply_Xpath = conf["xpath"]["if_easy_apply"] # locator for EasyApply data 

    company_all_sect = conf["xpath"]["company_all_section"] # locator for all company data(by company window) section, the following section should be affiliated by this locator

    jd_selector = conf["xpath"]["jd_selector"] # locator for job description content 
    salary_selector = conf["xpath"]["salary_selector"] # locator for salary info 

    size_selector = conf["xpath"]["size_selector"] # locator for company size info 
    found_year_selector = conf["xpath"]["found_year_selector"] # locator for company foundYear info 
    industry_selector = conf["xpath"]["industry_selector"] # locator for company industry info 
    sector_selector = conf["xpath"]["sector_selector"] # locator for company sector info (use this rather than industry selector)
    num_header_selector = conf["xpath"]["num_header_selector"] # locator for the number of positions available for each search
    click_dynamic_selector = conf["xpath"]["click_dynamic_selector"] # click javscript dynamics button
    
    validate_salary = conf["scrawlerKeyWord"]["validate_salary"] # validating the location of salary section 
    company_overview = conf["scrawlerKeyWord"]["company_overview"]  # validating the location of company info section     
         
    def __init__(self,url:str,full_search=True,search_limit:int = 10 ,driver_appear:bool = False, show_web=False,end_with_web=False) -> None:
        self.url = url
        
        options = webdriver.EdgeOptions()
        
        if end_with_web:
            # close browser or not when sessions end                     
            options.add_experimental_option("detach", True)
        
        if not show_web:
            ## hide web window showing up
            options.add_argument("--window-size=1920,1080")            
            options.add_argument("--headless=new") 
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            
            user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36' #prevent scraper detector
            options.add_argument(f'user-agent={user_agent}')

        self.driver = webdriver.Edge(options=options)
        self.driver.headless = driver_appear
        self.search_limit = search_limit # search limit by each job key word
        self.stor_data = list() # stor position data
        
        self.if_full_search = full_search # collect every position or search by certain amount( then should specify search_limit)
        

    def set_sec_validation_str(self,salary_str:str,company_str:str):
        '''as cralwer locators are dynamics, the key word is set to make sure the
            crawled section has the content we need'''
        self.validate_salary = salary_str if salary_str else self.validate_salary
        self.company_overview = company_str if company_str else self.company_overview

    
    def use_full_searched(self):
        '''this function must be used before loading the crawler function'''
        amount_descript = self.driver.find_element(By.XPATH,self.num_header_selector).text
        
        num_searched = int(re.search(r'(\d+)',re.sub(r',','',amount_descript)).group(1)) # the number of positions available
        
        self.search_limit = num_searched if num_searched > self.search_limit else self.search_limit
        
        return self.search_limit
    
    def connect_glassdoor(self): 
        '''connect to job searched page'''
        self.driver.get(self.url)
    
    def validate_element(self,selector,defaule_val='-1'):
        try:
    
            element = self.driver.find_element(By.CSS_SELECTOR,self.company_all_sect + selector).text
            return element
        
        except NoSuchElementException as e:
        
            logging.info(f'{e}, default value -1 is given')
            return defaule_val
        
    def validate_section_element(self,selector,val_str):
        
        validated_str_1 = self.driver.find_element(By.CSS_SELECTOR,self.company_all_sect + ' > section:nth-child(2)').text
        validated_str_2 = self.driver.find_element(By.CSS_SELECTOR,self.company_all_sect + ' > section:nth-child(3)').text
        val_bool = True
        
        if val_str in validated_str_1:
            val_bool = False
            return self.driver.find_element(By.CSS_SELECTOR,self.company_all_sect + ' > section:nth-child(2)'+selector).text
        
        if val_str in validated_str_2:
            val_bool = False
            return self.driver.find_element(By.CSS_SELECTOR,self.company_all_sect + ' > section:nth-child(3)'+selector).text
        
        if val_bool:
            return 'none'
        
    def retrieve_info(self):
        
        
        stor_xpathtxt = {}
        trial = 0

        while not self.driver.find_elements(By.CSS_SELECTOR,self.company_all_sect) and trial <5 :
            
            time.sleep(1)
            trial += 1      
            
        if trial <5:
            
            ## only collect the company & position whose location, position, rate, company name information are all provided
            if len(self.driver.find_element(By.XPATH,self.basicInfo_Xpath).text.split('\n'))==4:
                
                stor_xpathtxt['position_info'] = self.driver.find_element(By.XPATH,self.basicInfo_Xpath).text
                stor_xpathtxt['if_easy_apply'] = self.driver.find_element(By.XPATH,self.ifEasyApply_Xpath).text
                            
                stor_xpathtxt['jd'] = self.validate_element(selector=self.jd_selector)
                stor_xpathtxt['avg_salary'] = self.validate_section_element(selector=self.salary_selector,val_str=self.validate_salary)         
                stor_xpathtxt['size'] = self.validate_section_element(selector=self.size_selector,val_str=self.company_overview)       
                stor_xpathtxt['found_year'] = self.validate_section_element(selector=self.found_year_selector,val_str=self.company_overview)       
                stor_xpathtxt['sector'] = self.validate_section_element(selector=self.sector_selector,val_str=self.company_overview)                         
                self.stor_data.append(stor_xpathtxt)
                
            else:
                filt_out = self.driver.find_element(By.XPATH,self.basicInfo_Xpath).text.split('\n')
                
                logging.info(f'''The position {filt_out[0]},{filt_out[1]} is not collected because the basic information is not intact''')
        else:
            self.driver.get_screenshot_as_file("./log/retrieve_info_err.png")
            pass
        
        
    def load_positions(self):
        
        for idx in range(0,self.search_limit):   
           
            position_sect = self.driver.find_element(By.XPATH, f'/html/body/div[2]/div[1]/div[3]/div[2]/div[1]/div[2]/ul/li[{idx+1}]')
            self.driver.execute_script(self.click_dynamic_selector,position_sect) 

            # close all possible pop up windows
            if self.driver.find_elements(By.XPATH,self.exist_close_view):
                logging.debug('successfully close pop up window')
                self.driver.find_element(By.XPATH,self.exist_close_view).click()
                
            if self.driver.find_elements(By.XPATH,self.exist_close_invitation):
                logging.debug('successfully close pop up window')
                self.driver.find_element(By.XPATH,self.exist_close_invitation).click()
                
            self.retrieve_info()
     
    def click_next_turn(self):
        
        for _ in range(math.floor(self.search_limit/30)): #one fold explores 30 more position
            time.sleep(1)
            self.driver.get_screenshot_as_file("./log/click_next_pg.png")
            next_locator = self.driver.find_element(By.XPATH,self.show_more_job)
            self.driver.execute_script(self.click_dynamic_selector,next_locator)
            time.sleep(2)
            logging.debug('successfully click next job page')

    def main(self):

        self.connect_glassdoor()
        if self.if_full_search:
            self.use_full_searched()
            logging.debug('searched all position result')
            
        self.click_next_turn()
        self.load_positions()
        return self.stor_data









