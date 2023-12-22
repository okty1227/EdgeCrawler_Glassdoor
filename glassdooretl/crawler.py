from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
# from bs4 import BeautifulSoup
import time
import json
import asyncio
import math

class CONFIG():
    '''pending'''
    def check_read_conf(conf_search_preference:str):
        
        with open(conf_search_preference, 'r') as file:
            conf = json.load(file)

        if 'easy_apply_only' not in conf or not isinstance(conf['easy_apply_only'], bool):
            raise ValueError("easy_apply_only does not fullfill expected format")

        if 'Salary_Range' not in conf or not isinstance(conf['Salary_Range'], list) or len(conf['Salary_Range']) != 2:
            raise ValueError("Salary_Range does not fullfill expected format")

        if 'Company_Rating_atleast' not in conf or not isinstance(conf['Company_Rating_atleast'], (int, float)):
            raise ValueError("Company_Rating_atleast does not fullfill expected format")

        if 'last_date_posted' not in conf or not conf['last_date_posted'] in ['one day','three days','week','month'] :
            raise ValueError("last_date_posted does not fullfill expected format")

        print("Config File Check Passed")
        return conf
    
class CONNECTION():
    exist_close_view = '/html/body/div[11]/div[2]/div[1]/button'
    exist_close_envitation = '/html/body/div[8]/div/div[2]/span/svg'
    show_more_job = '/html/body/div[2]/div[1]/div[3]/div[2]/div[1]/div[2]/div/button'           
        
    basicInfo_Xpath = '/html/body/div[2]/div[1]/div[3]/div[2]/div[2]/div[1]/header/div[1]'
    ifEasyApply_Xpath = '/html/body/div[2]/div[1]/div[3]/div[2]/div[2]/div[1]/header/div[3]/div[2]'
    
    company_all_sect = 'section.JobDetails_jobDetailsSection__PJz1h'
    # jd_selector = 'div > div:nth-child(1)'
    jd_selector = 'div'
    salary_selector = 'section:nth-child(2) > div > div > div:nth-child(1)'
    size_selector = 'section:nth-child(3) > div > div > div:nth-child(1) > div'
    found_year_selector = 'section:nth-child(3) > div > div > div:nth-child(2) > div'
    industry_selector = 'section:nth-child(3) > div > div > div:nth-child(4) > div'
    sector_selector = 'section:nth-child(3) > div > div > div:nth-child(5) > div'

    def __init__(self,url:str,search_limit:int = 10 ,driver_appear:bool = False) -> None:
        self.url = url
        self.search_limit = search_limit
        options = webdriver.EdgeOptions()
        # options.add_experimental_option("detach", True)
        # driver = webdriver.Edge(options=options)
        self.driver = webdriver.Edge()
        self.driver.headless = driver_appear
        self.search_limit = search_limit
        self.stor_data = list()
        self.ignored = 0 
    def get_positio_amount(self):
        
        amount_descript = self.driver.find_element('/html/body/div[2]/div[1]/div[3]/div[2]/div[1]/div[1]/h1').text
        self.search_limit = int(amount_descript.split(' ')[0]) if int(amount_descript.split(' ')[0]) > self.search_limit else self.search_limit
        
        return self.search_limit
    
    def connect_glassdoor(self): 

        self.driver.get(self.url)
    
    def validate_element(self,parent_section_xpath,selector,defaule_val='-1'):
        try:
    
            element = parent_section_xpath.find_element(By.CSS_SELECTOR,selector).get_attribute('innerText')      
            return element
        
        except NoSuchElementException as e:
        
            print(f'{e}, default value -1 is given')
            return defaule_val
        
    def retrieve_info(self):
        
        stor_xpathtxt = {}
        trial = 0

        while not self.driver.find_elements(By.CSS_SELECTOR,self.company_all_sect) and trial <5 :
            
            time.sleep(1)
            trial += 1

        if trial <5:
            ## only collect the company & position where location, position, rate, company name information are all provided
            if len(self.driver.find_element(By.XPATH,self.basicInfo_Xpath).text.split('\n'))==4:
                
                stor_xpathtxt['position_info'] = self.driver.find_element(By.XPATH,self.basicInfo_Xpath).text
                stor_xpathtxt['if_easy_apply'] = self.driver.find_element(By.XPATH,self.ifEasyApply_Xpath).text
            
                comp_all_element = self.driver.find_elements(By.CSS_SELECTOR, self.company_all_sect)
                all_section = comp_all_element[0]
                stor_xpathtxt['jd'] = self.validate_element(all_section,selector=self.jd_selector)
                stor_xpathtxt['avg_salary'] = self.validate_element(all_section,selector=self.salary_selector)         
                stor_xpathtxt['size'] = self.validate_element(all_section,selector=self.size_selector)       
                stor_xpathtxt['found_year'] = self.validate_element(all_section,selector=self.found_year_selector)       
                # stor_xpathtxt['industry'] = self.validate_element(all_section,selector=self.industry_selector)        
                stor_xpathtxt['sector'] = self.validate_element(all_section,selector=self.sector_selector)   
                      
                self.stor_data.append(stor_xpathtxt)
            else:
                self.ignored +=1
        else:
            
            pass
        
        
    async def load_positions(self):
        
        for idx in range(0,int(self.search_limit)):   
           # load each selection .click()      
            
            position_sect = self.driver.find_element(By.XPATH, f'/html/body/div[2]/div[1]/div[3]/div[2]/div[1]/div[2]/ul/li[{idx+1}]')
            self.driver.execute_script('arguments[0].click();',position_sect) 

            # close all possible pop up windows
            if self.driver.find_elements(By.XPATH,self.exist_close_view):
                print('successfully close pop up window')
                self.driver.find_element(By.XPATH,self.exist_close_view).click()
                
            if self.driver.find_elements(By.XPATH,self.exist_close_envitation):
                print('successfully close pop up window')
                self.driver.find_element(By.XPATH,self.exist_close_envitation).click()
                
            self.retrieve_info()
     
    async def click_next_turn(self):
        # CONNECTION.get_positio_amount()
        for nb_turn in range(math.floor(self.search_limit/30)): #one fold explores 30 more position
            next_locator = self.driver.find_element(By.XPATH,self.show_more_job)
            
            self.driver.execute_script('arguments[0].click();',next_locator)
            print('successfully click next job page')

    async def main(self):
        self.connect_glassdoor()
        
        task1 = asyncio.create_task(self.click_next_turn())
        task2 = asyncio.create_task(self.load_positions())

        await task1
        await task2
        print(self.ignored)
        
        return self.stor_data
        
    def direct_to_search(self): ## currently replaced by url
        pass










