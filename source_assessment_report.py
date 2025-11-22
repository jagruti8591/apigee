import xlsxwriter
import os
import shutil
import json
import re
import zipfile

def add_new_sheet(resources,resource_str):
	row=0
	col=0
	worksheet_resources = workbook.add_worksheet(resource_str)
	for resource in (resources):
		worksheet_resources.write(row, col, resource)
		#worksheet.write(row, col + 1, score)
		row += 1
				
with open("config/app_config.json") as json_data_file:
    data = json.load(json_data_file)
    json_data_file.close()

apigee_edge_env= data["apigee_edge_env"]
folder_name= data["folder_name"]

index_of_tuple=0
index_of_tuple_sf=0
if os.path.exists("reports/source_org_assesment_report.xlsx"):
  os.remove("reports/source_org_assesment_report.xlsx")

### Name of output file 
workbook = xlsxwriter.Workbook('reports/source_org_assesment_report.xlsx')

proxy_path=folder_name+"\\proxies"
proxy_names_arr = os.listdir(proxy_path)
proxy_names_arr_without_zip =[]
for filename in proxy_names_arr:
    file_name_without_zip = re.search(r'(.*?)\.zip', filename)
    if file_name_without_zip:
        file_name_without_zip = file_name_without_zip.group(1)
        proxy_names_arr_without_zip.append(file_name_without_zip)
add_new_sheet(proxy_names_arr_without_zip,"Proxies")

sf_path=folder_name+"\\sharedflows"
sf_names_arr = os.listdir(sf_path)
sf_names_arr_without_zip =[]
for filename in sf_names_arr:
    file_name_without_zip = re.search(r'(.*?)\.zip', filename)
    if file_name_without_zip:
        file_name_without_zip = file_name_without_zip.group(1)
        sf_names_arr_without_zip.append(file_name_without_zip)
add_new_sheet(sf_names_arr_without_zip,"SharedFlows")

kvm_encryption_tuples = ()
lst_of_tuple_kvm = list(kvm_encryption_tuples)
lst_of_tuple_kvm.insert(0,["KVM", "Encrypted"])


kmv_path=folder_name+"\\keyvaluemaps\\env\\"+apigee_edge_env
kvm_names_arr = os.listdir(kmv_path)
kvm_names = []
for kvm in kvm_names_arr:
	list_kvm_dependency_map=[]
	f = open(kmv_path+"\\"+kvm)
	data = json.load(f)
	is_encrypted = data['encrypted']
	list_kvm_dependency_map.append(kvm)
	list_kvm_dependency_map.append(is_encrypted)
	lst_of_tuple_kvm.insert(1,list_kvm_dependency_map)
final_kvm_dependency_map = tuple(lst_of_tuple_kvm)
worksheet = workbook.add_worksheet("KVMs")
row = 0
col = 0
for kvm,encrypted in (final_kvm_dependency_map):
    worksheet.write(row, col, kvm)
    worksheet.write(row, col + 1, encrypted)
    row += 1

#add_new_sheet(kvm_names_arr,"KVMs")

ts_path=folder_name+"\\targetservers\\env\\"+apigee_edge_env
ts_names_arr = os.listdir(ts_path)
add_new_sheet(ts_names_arr,"Target Servers")

product_path=folder_name+"\\apiproducts"
prod_names_arr = os.listdir(product_path)
prod_names = []
for prod in prod_names_arr:
	f = open(product_path+"\\"+prod)
	data = json.load(f)
	prod_attributes = data['attributes']
	no_of_custom_attributes = len(prod_attributes)
	if no_of_custom_attributes > 16:
		prod_names.append(" Product " +prod+" has more than 14 custom attributes")
	else:
		prod_names.append(prod)
add_new_sheet(prod_names,"Products")

apps_path=folder_name+"\\apps"
app_names_arr = os.listdir(apps_path)
app_names = []
for app in app_names_arr:
	f = open(apps_path+"\\"+app)
	data = json.load(f)
	app_name = data['name']
	app_attributes = data['attributes']
	no_of_custom_attributes = len(app_attributes)
	if no_of_custom_attributes > 16:
		app_names.append(" APP " +app_name+" has more than 14 custom attributes")
	else:
		app_names.append(app_name)
add_new_sheet(app_names,"APPs")

policies_to_refractor = ''
policies_oauth_v1 = ''

sf_dependency_map=''



proxy_dependency_tuples = ()
lst_of_tuple_proxy = list(proxy_dependency_tuples)
lst_of_tuple_proxy.insert(0,["Proxy Name", "Dependant Shared Flow", "Dependent KVM","Encrypted","Dependent TS","OAuth v2 Policy","IP Whitelisting"])


sf_dependency_tuples = ()
lst_of_tuple_sf = list(sf_dependency_tuples)
lst_of_tuple_sf.insert(0,["Shared Flow Name", "Dependant Shared Flow", "Dependent KVM","Encrypted","OAuth v2 Policy","IP Whitelisting"])

filenames = os.listdir(folder_name+"\\proxies")
############################## Unzips Proxies ################################################
for filename in filenames:
	check_whether_zip_file = re.search(r'\.(.*)', filename)
	if check_whether_zip_file:
		name_sc = check_whether_zip_file.group(1).strip()
		is_edge_micro_proxy = False
		filename = filename.strip()
		is_edge_micro_proxy_check = re.findall('(?i)edgemicro_', filename)
		is_edge_micro_proxy_check = str(is_edge_micro_proxy_check)
		if is_edge_micro_proxy_check != "[]":
			is_edge_micro_proxy = True
			filename = filename.replace(".zip",'')
			policies_oauth_v1=policies_oauth_v1+("Name of Edge Micro Proxy : "+filename+" |")+","
		
		filename = filename.replace(".zip",'')
		test=os.path.exists(folder_name+"\\proxies"+"\\"+filename)
		if test == False:
			filename = filename+".zip"
			with zipfile.ZipFile(folder_name+"\\proxies"+"\\"+filename, 'r') as zip_ref:
				filename = filename.replace(".zip",'')
				zip_ref.extractall(folder_name+"\\proxies"+"\\"+filename)

filenames = os.listdir(folder_name+"\\sharedflows")
############################## Unzips Shared Flows ################################################
for filename in filenames:
	check_whether_zip_file = re.search(r'\.(.*)', filename)
	if check_whether_zip_file:
		name_sc = check_whether_zip_file.group(1).strip()
		filename = filename.replace(".zip",'')
		test=os.path.exists(folder_name+"\\sharedflows"+"\\"+filename)
		if test == False:
			filename = filename+".zip"
			with zipfile.ZipFile(folder_name+"\\sharedflows"+"\\"+filename, 'r') as zip_ref:
				filename = filename.replace(".zip",'')
				zip_ref.extractall(folder_name+"\\sharedflows"+"\\"+filename)				

############################## Checks for SC policy Proxies ################################################
filenames = os.listdir(folder_name+"\\proxies")
for filename in filenames:
	
	check_whether_zip_file = re.search(r'\.(.*)', filename)
	dependent_sf=''
	dependent_kvm=''
	dependent_ts=''
	dependent_kvm_status=''
	policies_oauth_v2 = ''
	policies_access_control = ''
	is_enabled = ''


	if check_whether_zip_file:
		name_sc = check_whether_zip_file.group(1).strip()
	if name_sc == "zip":	
		isdir_target = os.path.isdir(folder_name+"\\proxies\\"+filename+"\\apiproxy\\targets\\")
		if isdir_target:
			################################## Target Endpoints #########################################		
			isdir_check_mutiple_endpoints = os.path.isdir(folder_name+"\\proxies\\"+filename+"\\apiproxy\\targets\\")
			if isdir_check_mutiple_endpoints:
				arr_proxy_endpoints = os.listdir(folder_name+"\\proxies\\"+filename+"\\apiproxy\\targets\\")
				for i in arr_proxy_endpoints:
					file2 = open(folder_name+"\\proxies\\"+filename+"\\apiproxy\\targets\\"+i, 'r')
					lines = file2.readlines()
					file2.close()
					for line in lines:
						result_check_ts = re.search(r'<Server.*name="(.*?)"', line)		
						if result_check_ts:
							name_ts = result_check_ts.group(1).strip()
							proxy_name_include_sc = filename.strip()
							dependent_ts=dependent_ts+name_ts+","
		
		isdir = os.path.isdir(folder_name+"\\proxies\\"+filename+"\\apiproxy\\policies\\")

		if isdir:
			################################## Proxy Endpoints #########################################
			isdir_check_mutiple_endpoints = os.path.isdir(folder_name+"\\proxies\\"+filename+"\\apiproxy\\proxies\\")
			if isdir_check_mutiple_endpoints:
				arr_proxy_endpoints = os.listdir(folder_name+"\\proxies\\"+filename+"\\apiproxy\\proxies\\")
				length_of_proxy_endpoints = len(arr_proxy_endpoints)
				if length_of_proxy_endpoints >5:
					policies_oauth_v1=policies_oauth_v1+("Name of Proxy with more than 5 proxy endpoints : "+filename+"|")+","


						
				length_of_target_endpoints = len(arr_proxy_endpoints)
				if length_of_target_endpoints >1000:
					policies_oauth_v1=policies_oauth_v1+("Name of Proxy with more than 5 target endpoints : "+filename+"|")+","

			arr = os.listdir(folder_name+"\\proxies\\"+filename+"\\apiproxy\\policies\\")
			for i in arr:
				
				list_proxy_dependency_map =[]
				file2 = open(folder_name+"\\proxies\\"+filename+"\\apiproxy\\policies\\"+i, 'r')
				lines = file2.readlines()
				file2.close()
				for line in lines:
					result_check_sc = re.search(r'<StatisticsCollector.*name="(.*?)"', line)
					result_check_oauth_v1_policy = re.search(r'<OAuthV1.*name="(.*?)"', line)
					result_check_extensions_policy = re.search(r'<ConnectorCallout.*name="(.*?)"', line)
					result_check_sf = re.search(r'<FlowCallout.*name="(.*?)"', line)
					result_check_kvm = re.search(r'<KeyValueMapOperations.*mapIdentifier="(.*?)"', line)
					result_check_oauth_v2_policy = re.search(r'<OAuthV2.*enabled="(.*?)".*name="(.*?)"', line)
					result_check_access_control_policy = re.search(r'<AccessControl.*enabled="(.*?)".*name="(.*?)"', line)
					#result_check_ts = re.search(r'<Server.*name="(.*?)"', line)
					
					if result_check_extensions_policy:
						name_extensions = result_check_extensions_policy.group(1).strip()
						proxy_name_include_sc = filename.strip()
						policies_oauth_v1=policies_oauth_v1+("Name of Extension Policy : "+name_extensions+" and Name of Proxy: "+proxy_name_include_sc+"|")+","

					if result_check_oauth_v1_policy:
						name_ov1=result_check_oauth_v1_policy.group(1).strip()
						proxy_name_include_sc = filename.strip()
						policies_oauth_v1=policies_oauth_v1+("Name of OAuth v1 Policy : "+name_ov1+" and Name of proxy : "+proxy_name_include_sc+"|")+","
						
					if result_check_sc:
						name_sc = result_check_sc.group(1).strip()
						proxy_name_include_sc = filename.strip()
						policies_to_refractor=policies_to_refractor+("Name of Statistic Collector Policy : "+name_sc+" and Name of proxy : "+proxy_name_include_sc+"|")+","

					if result_check_sf:
						name_sf = result_check_sf.group(1).strip()
						proxy_name_include_sc = filename.strip()
						dependent_sf=dependent_sf+name_sf+","
	
					if result_check_kvm:
						name_kvm = result_check_kvm.group(1).strip()
						proxy_name_include_sc = filename.strip()
						
						isfile=os.path.isfile(folder_name+"\\keyvaluemaps\\env\\"+apigee_edge_env+"\\"+name_kvm)
						if isfile:
							file2 = open(folder_name+"\\keyvaluemaps\\env\\"+apigee_edge_env+"\\"+name_kvm, 'r')
							data = json.load(file2)
							encrypted_status = data['encrypted']
							file2.close()
							dependent_kvm_status=dependent_kvm_status+str(encrypted_status)+","
						else:
							dependent_kvm_status=dependent_kvm_status+"KVM does not exists in data_edge folder"+","	
						dependent_kvm=dependent_kvm+name_kvm+","

					if result_check_oauth_v2_policy:
						is_enabled=result_check_oauth_v2_policy.group(1).strip()
						name_ov2=result_check_oauth_v2_policy.group(2).strip()
						proxy_name_include_sc = filename.strip()
						policies_oauth_v2=policies_oauth_v2+name_ov2+","
						#print(policies_oauth_v2)

					if result_check_access_control_policy:
						is_enabled=result_check_access_control_policy.group(1).strip()
						name_ac=result_check_access_control_policy.group(2).strip()
						proxy_name_include_sc = filename.strip()
						policies_access_control=policies_access_control+name_ac+","
						#print(policies_access_control)

						#print("Proxy Name"+filename+"dependant shared flow " +name_sf)
			if dependent_sf == '':
				dependent_sf = "No Dependant Shared Flow"			

			if dependent_kvm == '':
				dependent_kvm = "No Dependant KVM"
				dependent_kvm_status = "NA"

			if dependent_ts == '':
				dependent_ts = "No Dependant TS"
			
			if policies_oauth_v2 == '' or is_enabled != 'true':
				policies_oauth_v2 = 'No'

			if policies_access_control == '' or is_enabled != 'true':
				policies_access_control = 'No'

			dependent_sf=dependent_sf.strip(",")
			dependent_kvm=dependent_kvm.strip(",")
			dependent_ts=dependent_ts.strip(",")
			dependent_kvm_status=dependent_kvm_status.strip(",")
			policies_oauth_v2=policies_oauth_v2.strip(",")
			policies_access_control=policies_access_control.strip(",")

			list_proxy_dependency_map.append(filename)
			list_proxy_dependency_map.append(dependent_sf)
			list_proxy_dependency_map.append(dependent_kvm)
			#print(dependent_kvm_status)
			list_proxy_dependency_map.append(dependent_kvm_status)
			list_proxy_dependency_map.append(dependent_ts)
			list_proxy_dependency_map.append(policies_oauth_v2)
			list_proxy_dependency_map.append(policies_access_control)
			index_of_tuple=index_of_tuple+1
			lst_of_tuple_proxy.insert(index_of_tuple,list_proxy_dependency_map)
			
############################## Checks for SC policy in Shared Flow ################################################
filenames = os.listdir(folder_name+"\\sharedflows")
for filename in filenames:
	check_whether_zip_file = re.search(r'\.(.*)', filename)
	dependent_sf=''
	dependent_kvm=''
	dependent_kvm_status=''
	policies_oauth_v2 = ''
	policies_access_control = ''


	if check_whether_zip_file:
		name_sc = check_whether_zip_file.group(1).strip()
	if name_sc == "zip":
		isdir = os.path.isdir(folder_name+"\\sharedflows\\"+filename+"\\sharedflowbundle\\policies\\")
		if isdir:
			arr = os.listdir(folder_name+"\\sharedflows\\"+filename+"\\sharedflowbundle\\policies\\")
			for i in arr:
				list_sf_dependency_map = []
				file2 = open(folder_name+"\\sharedflows\\"+filename+"\\sharedflowbundle\\policies\\"+i, 'r')
				lines = file2.readlines()
				file2.close()
				for line in lines:
					result_check_sc = re.search(r'<StatisticsCollector.*name="(.*?)"', line)
					result_check_oauth_v1_policy = re.search(r'<OAuthV1.*name="(.*?)"', line)
					result_check_extensions_policy = re.search(r'<ConnectorCallout.*name="(.*?)"', line)
					result_check_sf = re.search(r'<FlowCallout.*name="(.*?)"', line)
					result_check_oauth_v2_policy = re.search(r'<OAuthV2.*enabled="(.*?)".*name="(.*?)"', line)
					result_check_access_control_policy = re.search(r'<AccessControl.*enabled="(.*?)".*name="(.*?)"', line)
					
					if result_check_extensions_policy:
						name_extensions = result_check_extensions_policy.group(1).strip()
						proxy_name_include_sc = filename.strip()
						policies_oauth_v1=policies_oauth_v1+("Name of Extension Policy : "+name_extensions+" and Name of Shared Flow: "+proxy_name_include_sc+"|")+","	
						
					if result_check_oauth_v1_policy:
						name_ov1=result_check_oauth_v1_policy.group(1).strip()
						proxy_name_include_sc = filename.strip()
						policies_oauth_v1=policies_oauth_v1+("Name of OAuth v1 Policy : "+name_ov1+" and Name of Shared Flow : "+proxy_name_include_sc+"|")+","					
					
					if result_check_sc:
						name_sc = result_check_sc.group(1).strip()
						proxy_name_include_sc = filename.strip()
						policies_to_refractor=policies_to_refractor+("Name of Statistic Collector Policy : "+name_sc+" and Name of Shared Flow : "+proxy_name_include_sc+"|")+","
					
					if result_check_sf:
						name_sf = result_check_sf.group(1).strip()
						proxy_name_include_sc = filename.strip()
						dependent_sf=dependent_sf+name_sf+","

					if result_check_kvm:
						name_kvm = result_check_kvm.group(1).strip()
						proxy_name_include_sc = filename.strip()
						
						isfile=os.path.isfile(folder_name+"\\keyvaluemaps\\env\\"+apigee_edge_env+"\\"+name_kvm)
						if isfile:
							file2 = open(folder_name+"\\keyvaluemaps\\env\\"+apigee_edge_env+"\\"+name_kvm, 'r')
							data = json.load(file2)
							encrypted_status = data['encrypted']
							#print(encrypted_status)
							file2.close()
							dependent_kvm_status=dependent_kvm_status+str(encrypted_status)+","
						else:
							dependent_kvm_status=dependent_kvm_status+"KVM does not exists in data_edge folder"+","	
												
						dependent_kvm=dependent_kvm+name_kvm+","

					if result_check_oauth_v2_policy:
						is_enabled=result_check_oauth_v2_policy.group(1).strip()
						name_ov2=result_check_oauth_v2_policy.group(2).strip()
						policies_oauth_v2=policies_oauth_v2+name_ov2+","
						# print(policies_oauth_v2)

					if result_check_access_control_policy:
						is_enabled=result_check_access_control_policy.group(1).strip()
						name_ac=result_check_access_control_policy.group(2).strip()
						proxy_name_include_sc = filename.strip()
						policies_access_control=policies_access_control+name_ac+","
						# print(policies_access_control)


			if dependent_sf == '':
				dependent_sf = "No Dependant Shared Flow"			

			if dependent_kvm == '':
				dependent_kvm = "No Dependant KVM"
				dependent_kvm_status = "NA"

			if policies_oauth_v2 == '' or is_enabled != 'true':
				policies_oauth_v2 = 'No'

			if policies_access_control == '' or is_enabled != 'true':
				policies_access_control = 'No'

			dependent_sf=dependent_sf.strip(",")
			dependent_kvm=dependent_kvm.strip(",")
			dependent_ts=dependent_ts.strip(",")
			policies_oauth_v2=policies_oauth_v2.strip(",")
			policies_access_control=policies_access_control.strip(",")
			sf_dependency_map = sf_dependency_map + "SF Name --> "+filename+" & Dependent SF --> " +dependent_sf+" & Dependent KVM --> " +dependent_kvm +" |"
			#print("SF Name --> "+filename+" Dependent SF --> " +dependent_sf+" Dependent KVM --> " +dependent_kvm)

			list_sf_dependency_map.append(filename)
			list_sf_dependency_map.append(dependent_sf)
			list_sf_dependency_map.append(dependent_kvm)
			list_sf_dependency_map.append(dependent_kvm_status)
			list_sf_dependency_map.append(policies_oauth_v2)
			list_sf_dependency_map.append(policies_access_control)
			index_of_tuple_sf=index_of_tuple_sf+1
			lst_of_tuple_sf.insert(index_of_tuple_sf,list_sf_dependency_map)

string_to_list_of_refractored=policies_to_refractor.split(",")
add_new_sheet(string_to_list_of_refractored,"Policies to Refractor")

string_to_list_of_oauth_v1=policies_oauth_v1.split(",")
add_new_sheet(string_to_list_of_oauth_v1,"Deprecated Policies")

##################### Dependency Map Proxy ######################
final_proxy_dependency_map = tuple(lst_of_tuple_proxy)
worksheet = workbook.add_worksheet("Proxy_Dependency_Map")
row = 0
col = 0
for proxy_name,shared_flow,kvm,encrypted,ts,ov2,ac in (final_proxy_dependency_map):
    worksheet.write(row, col, proxy_name)
    worksheet.write(row, col + 1, shared_flow)
    worksheet.write(row, col + 2, kvm)
    worksheet.write(row, col + 3, encrypted)
    worksheet.write(row, col + 4, ts)
    worksheet.write(row, col + 5, ov2)
    worksheet.write(row, col + 6, ac)
    row += 1


##################### Dependency Map SF ######################
final_sf_dependency_map = tuple(lst_of_tuple_sf)
worksheet = workbook.add_worksheet("SF_Dependency_Ma")
row = 0
col = 0
for shared_flow,dependent_sf,dependent_kvm,encrypted,ov2,ac in (final_sf_dependency_map):
    worksheet.write(row, col, shared_flow)
    worksheet.write(row, col + 1, dependent_sf)
    worksheet.write(row, col + 2, dependent_kvm)
    worksheet.write(row, col + 3, encrypted)
    worksheet.write(row, col + 4, ov2)
    worksheet.write(row, col + 5, ac)
    row += 1


#add_new_sheet(kvm_names_arr,"KVMs")
workbook.close()
