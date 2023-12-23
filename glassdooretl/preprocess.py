import re
import json
from typing import List
import asyncio
class PREPROCESS():

    flexible_skills = ['SQL', 'Spark' ]
    independen_exist_skills = ['R','AI','ML','Tableau','Java','Scala','Python', 'machine learning']
    
    # with open('config.json') as f:
    with open('config.json') as f:
        conf = json.load(f)
    
    flexible_skills = conf['flexible_skills'] if conf['flexible_skills'] else flexible_skills
    independen_exist_skills = conf['independen_exist_skills'] if conf['independen_exist_skills'] else independen_exist_skills
        
    ##skill preprocess
    @staticmethod
    def replace_jd_skill(pos:str):
        print(pos)
        if_skill_exist_stor = {}
        for skill in PREPROCESS.flexible_skills:
            if re.search(skill, pos, re.IGNORECASE):
                if_skill_exist_stor[skill] = True
            else:
                if_skill_exist_stor[skill] = False
                
        for skill in PREPROCESS.independen_exist_skills:
            if re.search(rf'\b{skill}\b', pos, re.IGNORECASE):
                
                if_skill_exist_stor[skill] = True
            else:
                if_skill_exist_stor[skill] = False
        
        return if_skill_exist_stor
    
    @staticmethod
    def check_easy_apply(pos_easy_apply:str):
        
        return True if 'Easy Apply' in pos_easy_apply else False
            

    ##basic information
    @staticmethod
    def procees_basic_info(pos:str):
        
        ## len of position_info is assured to be 4 in crawler
        splited_jd = pos.split('\n')
        basic_info_store = {}
        basic_info_store['company_name'] = splited_jd[0]
        basic_info_store['company_rate'] = splited_jd[1]
        basic_info_store['position_name'] = splited_jd[2]
        location = splited_jd[3]
        # print(location)
        location_parts_space = location.split(' ')
        location_parts_comma = location.split(',')

        if len(location_parts_space) > 1 and len(location_parts_comma) > 0:
            state, city = location_parts_space[1], location_parts_comma[0]
        else:
            state, city = 'Not Applicable', 'Not Applicable'

        basic_info_store['company_location_state'] = state
        basic_info_store['company_location_city'] = city
        
        return basic_info_store
    
    ##process salary into yearly basis
    @staticmethod
    def process_salary(pos_salary:str):
        salary_info_store = {}
        
        pos_salary = re.sub(r"[$,\/]","",pos_salary)
        salary, unit = pos_salary.split('\n')
        salary_info_store['hourly_or_yearly_rate'] = unit
        
        if len(salary)<5: #if the digit is less than 5, it means the salary is hourly wage
            salary_info_store['salary'] = float(salary) * 2080 #generally hour to year salary rate
            
        else:
            salary_info_store['year_salary'] = float(salary) 
            
        return salary_info_store
    
    @staticmethod
    async def run_preprocess(crawed_raw_data:List) -> List:
        loop = asyncio.get_event_loop()

        for position in crawed_raw_data:
            position['jd'] = await loop.run_in_executor(None, PREPROCESS.replace_jd_skill, position['jd'])
            position['avg_salary'] = await loop.run_in_executor(None, PREPROCESS.process_salary, position['avg_salary'])
            position['position_info'] = await loop.run_in_executor(None, PREPROCESS.procees_basic_info, position['position_info'])
            position['if_easy_apply'] = await loop.run_in_executor(None, PREPROCESS.check_easy_apply, position['if_easy_apply'])
            
        return crawed_raw_data

# if __name__=='__main__':
    
#     processed = PREPROCESS.run_preprocess(crawed_raw_data = test_input)
#     print(processed)