import sslyze
import requests
import json
import sys
import configparser
import mysql
from os.path import dirname
sys.path.append(dirname(dirname(f'{__file__}')))
from v2.yaml_vuln import vuln_extract

if __name__ == "__main__":
    user_input = sys.argv[1] # this is the domain
    scan_id = int(sys.argv[2])

config = configparser.ConfigParser()
config.read("config.ini")

all_scan_requests = [sslyze.ServerScanRequest(sslyze.ServerNetworkLocation(user_input))]

scanner = sslyze.Scanner()

scanner.queue_scans(all_scan_requests)
accepted_ciphers = []
is_vulnerable_to_heartbleed = False
vulnerable_ssl = False
for server_scan_result in scanner.get_results():
    is_vulnerable_to_heartbleed= server_scan_result.scan_result.heartbleed.result.is_vulnerable_to_heartbleed
    if(server_scan_result.scan_result.ssl_2_0_cipher_suites.status == sslyze.ScanCommandAttemptStatusEnum.COMPLETED):
        #Process if completed
        #success
        for accepted in server_scan_result.scan_result.ssl_2_0_cipher_suites.result.accepted_cipher_suites:
            accepted_ciphers.append([accepted,"SSL2.0"])
    if(server_scan_result.scan_result.ssl_3_0_cipher_suites.status == sslyze.ScanCommandAttemptStatusEnum.COMPLETED):
        #Process if completed
        #success
        for accepted in server_scan_result.scan_result.ssl_3_0_cipher_suites.result.accepted_cipher_suites:
            accepted_ciphers.append([accepted,"SSL3.0"])
    if(server_scan_result.scan_result.tls_1_0_cipher_suites.status == sslyze.ScanCommandAttemptStatusEnum.COMPLETED):
        #Process if completed
        #success
        for accepted in server_scan_result.scan_result.tls_1_0_cipher_suites.result.accepted_cipher_suites:
            accepted_ciphers.append([accepted,"TLS1.0"])
    if(server_scan_result.scan_result.tls_1_1_cipher_suites.status == sslyze.ScanCommandAttemptStatusEnum.COMPLETED):
        #Process if completed
        #success
        for accepted in server_scan_result.scan_result.tls_1_1_cipher_suites.result.accepted_cipher_suites:
            accepted_ciphers.append([accepted,"TLS1.1"])
    if(server_scan_result.scan_result.tls_1_2_cipher_suites.status == sslyze.ScanCommandAttemptStatusEnum.COMPLETED):
        #Process if completed
        #success
        for accepted in server_scan_result.scan_result.tls_1_2_cipher_suites.result.accepted_cipher_suites:
            accepted_ciphers.append([accepted,"TLS1.2"])
    if(server_scan_result.scan_result.tls_1_3_cipher_suites.status == sslyze.ScanCommandAttemptStatusEnum.COMPLETED):
        #Process if completed
        #success
        for accepted in server_scan_result.scan_result.tls_1_3_cipher_suites.result.accepted_cipher_suites:
            accepted_ciphers.append([accepted,"TLS1.3"])

for row in accepted_ciphers:
    cipher = row[0].cipher_suite
    key_ex = row[0].ephemeral_key
    tls_ssl = row[1]
    resp = requests.get(f"https://ciphersuite.info/api/cs/{cipher.name}")
    print(f"{cipher.name}: {json.loads(resp.text)[cipher.name]['security']}")
    if("CBC" in cipher.name and key_ex != None and key_ex.type_name=='DH' and key_ex.size<=1024):
        #DHE key size <= 1024 : Vulnerable to Logjam
        print("Vulnerable to Logjam")
        vulnerable_ssl = True
    #<=TLS 1.1 is deprecated as stated by nuclei 
    if(tls_ssl not in ["TLS1.2","TLS1.3"]):
        print("Using deprecated TLS version")
        vulnerable_ssl = True
#Test for heartbleed
if(is_vulnerable_to_heartbleed):
    print("Vulnerable to heartbleed")
    vulnerable_ssl = True

# if vulnerable_ssl :
#     print("Weak ssl detected")
#     db_host = config.get('SQL Database', 'db_host')
#     db_user = config.get('SQL Database', 'db_user')
#     db_password = config.get('SQL Database', 'db_password')

#     db_connection = mysql.connector.connect(
#         host=db_host,
#         user=db_user,
#         password=db_password,
#         database="vulnerabilities"
#     )

#     db_cursor = db_connection.cursor()
#     cwe_id = "CUST-Weak-SSL"
#     # Insert a row into the MySQL table
#     vuln_yml = vuln_extract(cwe_id)
#     name = vuln_yml["name"]

#     insert_query = "INSERT INTO vulnerabilities (scan_id, vulnerability_name, vulnerability_id, url) VALUES (%s, %s, %s, %s)"
#     values = []
#     values.append([scan_id,name,cwe_id,user_input])
#     db_cursor.executemany(insert_query, values)# Insert multiple rows together
#     db_connection.commit()

#     db_cursor.close()
#     db_connection.close()