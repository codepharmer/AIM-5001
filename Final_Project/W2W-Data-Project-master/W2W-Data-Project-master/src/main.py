
import fields
import os
import pandas as pd
import re
import threading
from datetime import datetime
from scraper import *
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def login(driver):
    url = 'https://whentowork.com/logins.htm'
    driver.get(url)
    username = driver.find_element_by_css_selector('#username')
    username.send_keys(os.getenv('W2W_USERNAME'))
    password = driver.find_element_by_css_selector('#password')
    password.send_keys(os.getenv('W2W_PASSWORD'))
    driver.find_element_by_name('Submit1').click()

    sid_pattern = re.compile(r'.*SID=([0-9]*).*')
    sid = ''
    dll_link = ''
    if re.match(sid_pattern, driver.current_url):
        sid = sid_pattern.search(driver.current_url).group(1)
    else:
        print('Could not find SID in URL.  Login was likely unsuccessful.')
        exit(1)

    dll_link_pattern =  re.compile(r'w2w[^\W]+\.dll')
    if re.search(dll_link_pattern,driver.current_url):
        dll_link = re.search(dll_link_pattern,driver.current_url).group()
    else:
        print('Could not find dll in URL.  Login was likely unsuccessful.')
        exit(1)
    return sid, dll_link


def collect_prep_data(driver, sid, dll_link):
    print(dll_link)
    print(f'https://www8.whentowork.com/cgi-bin/{dll_link}/empemplist.htm?SID={sid}&lmi=')
    driver.get(f'https://www8.whentowork.com/cgi-bin/{dll_link}/empemplist.htm?SID={sid}&lmi=')
    employees_js = f'''
    var employees = document.querySelectorAll("[aria-label=\'employee name\']");
    return Object.values(employees).map(x => x.innerText);
    '''
    employees = driver.execute_script(employees_js)

    driver.get(f'https://www8.whentowork.com/cgi-bin/{dll_link}/empfullschedule?SID={sid}&lmi=&View=Month')
    positions_js =  f'''
    var positions = document.getElementsByName('EmpListSkill')[0].innerText
    .split('\\n');
    return positions.slice(4, positions.length);  //first four elements are filters and section breaks
    '''
    positions = driver.execute_script(positions_js)

    return employees, positions


def scrape_data(employees, positions, year, start_date, end_date, results):
    scraper = Scraper(employees, positions, year, start_date, end_date)
    scraper.scrape_year(login)
    scraper.analyze_results(results)


def format_df(results_data):
    df = pd.DataFrame(results_data)
    df.index.rename('Employee', inplace=True)
    df.sort_index(inplace=True)
    for name in ['A Place Holder', 'CANCELLED CANCELLED', 'NO CLASS SCHEDULED']:
        if name in df.index:
            df = df.drop([name])
    if len(df.columns) > 1:
        df.loc[:,'Total'] = df.sum(axis=1)
    df = df.round(2)
    df.loc['Total',:]= df.sum(axis=0)
    # return df
    df.to_csv(os.path.join(fields.OUTPUT_DIRECTORY, fields.FILE_NAME))


def main(start_date, end_date):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(executable_path='./chromedriver.exe', options=chrome_options)
    sid, dll_link = login(driver)
    employees, positions = collect_prep_data(driver, sid, dll_link)
    driver.close()

    num_threads = end_date.year - start_date.year + 1

    results = {start_date.year + i: dict() for i in range(num_threads)}

    threads = []
    for i in range(num_threads):
        thread = threading.Thread(target=scrape_data, args=(employees, positions, i, start_date, end_date, results))
        threads.append(thread)
        thread.start()
    for t in threads:
        t.join()

    format_df(results)


if __name__ == '__main__':
    def validate(date, var_name):
        try:
            datetime.strptime(date, r'%Y-%m-%d')
        except:
            print(f'ERROR: {var_name} is not a valid date')
            exit(1)
        return datetime.strptime(date, '%Y-%m-%d').date()

    start_date = validate(fields.START_DATE, 'START_DATE')
    end_date = validate(fields.END_DATE, 'START_DATE')
    if start_date > end_date:
        print('ERROR: START_DATE is after END_DATE')
        exit(1)
    if not os.path.isdir(fields.OUTPUT_DIRECTORY):
        print(f'ERROR: {fields.OUTPUT_DIRECTORY} does not exist')
        exit(1)
    main(start_date, end_date)

