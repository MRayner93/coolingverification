"""
Author: Leon van Stevendaal & Merlin Rayner & Stefan Moormann & Leon Deupmann & Yannik Helms & Sebastian Klockgether
Version: 1.0
"""

import pyodbc
from datetime import datetime, timedelta
import functions, decryptfucntion,weatherfunction


# Connection data
server = 'sc-db-server.database.windows.net'
database = 'supplychain' 
username = 'rse'
password = 'Pa$$w0rd'

# Define connection string
conn_str = (
f'DRIVER={{ODBC Driver 18 for SQL Server}};'
f'SERVER={server};'
f'DATABASE={database};'
f'UID={username};'
f'PWD={password}'
)


while True:
    # Establish connection
    conn = pyodbc.connect(conn_str)
    # Create cursor
    cursor = conn.cursor()
    
    
    # Initialize matrix for data
    all_data = []
    
    all_transport_id_list = []
    
    transport_id_list=[]
    
    company_data= []
    
    # Retrieve existing Transport IDs from the database
    cursor.execute('SELECT transportid FROM v_coolchain_crypt')
    for row in cursor:
        all_transport_id_list.append(row[0])
    
    for id in all_transport_id_list:
        if id not in transport_id_list:
            transport_id_list.append(id)
    

    # User input for selecting the Transport ID
    while True:
        for i, transport_id in enumerate(transport_id_list, start=1):
            print(f"{i}. {transport_id}")
        entry = int(input("Which entry do you want to check? (1-" + str(len(transport_id_list)) + ") "))
        if 1 <= entry <= len(transport_id_list):
            transport_id = transport_id_list[entry-1]
            break
        else:
            print("Invalid input. Please choose a number between 1 and", len(transport_id_list))
    
    # Execute SQL query, sorted by the previously selected Transport ID
            
    cursor.execute('SELECT * FROM v_coolchain WHERE transportid = ? ORDER BY datetime', transport_id )
    # Save results
    for row in cursor:
        all_data.append(row)
    # Close connection
    
    
    cursor.execute('SELECT * FROM company_crypt ')
    for data in cursor:
        company_data.append(data) 
           
    cursor.close()
    conn.close()
    
    # Transfer encrypted company data to decryptfunction
    decrypted_company_data = decryptfucntion.decryption(company_data)
    # Check the weather in case of time differenz problems
    temperature_during_day =weatherfunction.check_weather(decrypted_company_data)
    # Check for cold chain consistency
    consistency_result, consistency_error = functions.check_consistency(all_data)
    # Check time difference
    time_difference_result, time_difference_error = functions.check_time_difference(all_data)
    # Check transport duration
    transport_duration_result = functions.check_transport_duration(all_data)
    
   
    if consistency_result and time_difference_result and transport_duration_result:
        print("The ID", transport_id, "is \033[1;32;4mcorrect\033[0m.")
    else:
        # If an error occurred, print the corresponding error messages
        print("The ID", transport_id," has the following issues.")
        if not consistency_result:
            print(f"\033[1;31;4mWarning:\033[0m The cold chain has consistency errors: {consistency_error}")
        if not time_difference_result:
            print(f"\033[1;31;4mWarning:\033[0m {time_difference_error}")
            print("The temperatur during the day was", temperature_during_day)
        if not transport_duration_result:
            print("\033[1;31;4mWarning:\033[0m The transport duration exceeded 48 hours.")
            
            
    retry = input("If you want to try another ID? (yes/no)")
    if retry != "yes":
        break
    