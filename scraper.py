from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import csv
import logging
import os
from datetime import datetime

def linkedin_login(email, password):
    try:
        logging.info('linkedin_login started')
        dr.get("https://linkedin.com/uas/login")#opening login page
        time.sleep(2)#waiting time to load the page

        # entering username
        username = dr.find_element(By.ID, "username")#finding email input box by ID

        username.send_keys(email)#sending email

        # entering password
        pword = dr.find_element(By.ID, "password")#finding password input box by ID

        # Enter Your Password
        pword.send_keys(password)#sending password

        # for clicking on the log in button
        dr.find_element(By.XPATH, "//button[@type='submit']").click()

        #for email verification
        try:
            dr.find_element(By.ID,"input__email_verification_pin")#if email verification found
            verification = dr.find_element(By.ID,"input__email_verification_pin")
            verification.send_keys(int(input("Input your email verification number")))#asking for email verification input
            dr.find_element(By.XPATH, "//button[@type='submit']").click()
        except: # if not found
            pass
        logging.info("linkedin_login successful")
        time.sleep(20) #for giving you enough time to solve verification puzzle
    except Exception as e:
        logging.info("Exception occured in linkedin_login", e)
        
def fetch_links(firstname, lastname):
    try:
        logging.info("fetch_links started")
        url = f"https://www.linkedin.com/search/results/people/?keywords={firstname}%20{lastname}&origin=SWITCH_SEARCH_VERTICAL&sid=ljK"
        dr.get(url)
        time.sleep(5)
        #finding the links of profiles
        elements = dr.find_elements(By.CSS_SELECTOR, 'span.entity-result__title-text.t-16 a.app-aware-link')
        # Looping through the elements and extracting the href attribute
        for element in elements:
            text = element.text.strip()
            if "LinkedIn Member" not in text: # excluding elements with "Member" text
                href = element.get_attribute("href")
                links.add(href)
        logging.info("fetch_links successful")        
    except Exception as e:
        logging.info('Exception occured in fetch_link', e)
        
def fetching_data(links):
    try:
        logging.info("fetching_data started")
        for link in links:
            dr.get(link)

            start = time.time()
            # will be used in the while loop
            initialScroll = 0
            finalScroll = 1000

            while True:
                dr.execute_script(f"window.scrollTo({initialScroll},{finalScroll})")
                # this command scrolls the window starting from
                # the pixel value stored in the initialScroll
                # variable to the pixel value stored at the
                # finalScroll variable
                initialScroll = finalScroll
                finalScroll += 1000

                # we will stop the script for 3 seconds so that
                # the data can load
                time.sleep(3)
                # You can change it as per your needs and internet speed

                end = time.time()
                # We will scroll for 5 seconds.
                # You can change it as per your needs and internet speed
                if round(end - start) > 5:
                    break
            src = dr.page_source

            # Now using beautiful soup
            soup = BeautifulSoup(src, 'lxml')
            # Extracting the HTML of the complete introduction box
            intro = soup.find('div', {'class': 'pv-text-details__left-panel'})

            # In case of an error, try changing the tags used here.

            name_loc = intro.find("h1")

            # Extracting the Name
            name = name_loc.get_text().strip()#strip for removing blank space
            #Extracting the bio
            works_at_loc = intro.find("div", {'class': 'text-body-medium'})
            bio = works_at_loc.get_text().strip()
            try:
                location_loc = soup.find_all("span", {'class': 'text-body-small inline t-black--light break-words'})
                # Extracting the text content which is location
                for loc in location_loc:
                    location = loc.get_text().strip()
            except:
                location = "Not_Found"
            #Extraction connections count
            try:    
                span1 = soup.find('li', class_='text-body-small').find('span', class_='t-bold')
                connections = span1.get_text().strip()
            except:
                connections = "Not_found"
            #extracting college and degree from the Education section   
            try:        
                span2 = soup.find('a', class_='optional-action-target-wrapper display-flex flex-column full-width')
                college1=span2.find('div', class_='display-flex align-items-center mr1 hoverable-link-text t-bold').find(attrs={'aria-hidden': 'true'})
                college = ''.join(college1.find_all(text=True, recursive=False)).strip()
                degree1 = span2.find('span',class_="t-14 t-normal").find(attrs={'aria-hidden': 'true'})
                degree = ''.join(degree1.find_all(text=True, recursive=False)).strip()
            except:
                college = "Not_found"
                degree = "Not_found"
            #extracting data from the experience section    
            try:
                span3 = soup.find('div', class_="display-flex flex-row justify-space-between")
                #extracting the job title
                job = span3.find('div',class_="display-flex align-items-center mr1 t-bold")
                job_title = job.find(attrs={'aria-hidden': 'true'}).get_text(strip=True)

                # Extracting company name
                company_name_span = span3.find('span', class_=("t-14 t-normal"))
                company_name = company_name_span.find(attrs={'aria-hidden': 'true'}).get_text(strip=True)

                # Extracting working duration
                working_duration_span = span3.find('span', class_='t-14 t-normal t-black--light')
                start_= working_duration_span.find(attrs={'aria-hidden': 'true'}).get_text(strip=True)[0:8]
                total_time = working_duration_span.find(attrs={'aria-hidden': 'true'}).get_text(strip=True)[20:]
            except:
                job_title = "Not_working"
                company_name = "Not_working"
                start_ = "Not_working"
                total_time = "Not_wroking"
            data = {
                    'Names': name,
                    'Bio': bio,
                    'Connections/Followers': connections,
                    'Location': location,
                    'Job_title': job_title,
                    'Degree': degree,
                    'College': college,
                    'Company': company_name,
                    'Start_date': start_,
                    'Employment_Duration': total_time,
                    'Profile_Link':link
                }

            # Appending the data to the data_list
            data_list.append(data)
            time.sleep(5)
        logging.info("fetching_data successful") 
    except Exception as e:
        logging.info("Exception occured in fetching_data", e)
        
def saving_data(csv_file_path):
    try:
        logging.info("saving_data started")
        linkedin_login(email, password)
        fetch_links(firstname, lastname)
        fetching_data(links)
        with open(csv_file_path, mode='w', newline='',encoding='utf-8-sig') as csv_file:
            fieldnames = [
                'Names', 'Bio', 'Connections/Followers', 'Location', 'Job_title',
                'Degree', 'College', 'Company', 'Start_date', 'Employment_Duration','Profile_Link'
            ]
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

            # Writing the header row
            writer.writeheader()

            # Writing the data rows
            for data in data_list:
                writer.writerow(data)
        logging.info(f"saving_data successful. File_name:{csv_file_path}")       
    except Exception as e:
        logging.info("Exception occured in saving_data", e)





       
#for logging        
LOG_FILE = f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log" 
logs_path = os.path.join(os.getcwd(), "logs", LOG_FILE)
os.makedirs(logs_path, exist_ok=True)
LOG_FILE_PATH = os.path.join(logs_path, LOG_FILE)
logging.basicConfig(
            filename=LOG_FILE_PATH,
            format="[%(asctime)s] %(lineno)d %(name)s - %(levelname)s - %(message)s",
            level=logging.INFO) 

                        
email = "singharijit191@gmail.com"        
password = "zebronics"        
links = set() #initializing a empty set for links
data_list = [] #initializing a empty list for data 
firstname = input("Input first name: ")
lastname = input("Input last name: ")
dr = webdriver.Chrome()#creating driver variable
csv_file_name = 'linkedin_data.csv'
csv_file_path = os.path.join(os.getcwd(), csv_file_name)
saving_data(csv_file_path)