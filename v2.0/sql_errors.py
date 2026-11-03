from bs4 import BeautifulSoup
import os
import sys
import re

execution_path = os.path.dirname(sys.argv[0])

def sql_error_check(response_text, error_xml_path):
    with open(error_xml_path) as file:
        data = file.read()

    Bs_data = BeautifulSoup(data,"xml")
    for dbms in Bs_data.find_all("dbms"):
        # print(f"Performing {dbms['value']} check...")
        full_re = []
        for error in dbms.find_all("error"):
            full_re.append(error['regexp'])
        if(re.search(("(?i)"+"("+'|'.join(full_re)+")"),response_text)):
            return dbms['value']
    return -1
        