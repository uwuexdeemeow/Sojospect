import json

url_to_inject = []
with open('crawl.txt','r') as crawl_file:
    for i in (crawl_file.readlines()):
        data_dict = json.loads(i) #Data is now a dictionary from json loads
        #Examples to read data
        #To print all fields
        for key in data_dict.keys():
            if(key.startswith("Param_")):
                if data_dict[key]['type'] == 'text' and data_dict[key]['id'] != None : 
                    print(f"name : {data_dict[key]['name']}, id : {data_dict[key]['id']}, value : {data_dict[key]['value']}, URL : {data_dict['URL']}, Endpoint : {data_dict['Endpoint']}")
                    
                    # check if there is repeated url
                    #
                    url_to_inject.append(data_dict)

print(len(url_to_inject))

