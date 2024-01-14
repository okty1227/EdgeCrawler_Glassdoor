import json
from utils.crawler import CONNECTION
from utils.preprocess import PREPROCESS


def read_position_conf(conf_file:str):

    with open(conf_file, 'r') as file:
        conf = json.load(file)
    return conf

def run_main():
    conf = read_position_conf('conf-positionKeyword.json')
    for job_name, job_link in conf["positions"].items():
        
        glassdoor_connect = CONNECTION(url=job_link,full_search=False,
                                       search_limit=conf["search_limit"])
        
        result = glassdoor_connect.main()
        
        processed = PREPROCESS.run_preprocess(crawed_raw_data=result)
        with open(f'./out_files/{job_name}_glassdoor.json','w') as file:
            json.dump(obj=processed,fp=file) 


if __name__ == '__main__':
    run_main()





