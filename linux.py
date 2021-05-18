# -*- coding: UTF-8 -*-
import requests as req
import socket
import time
import os
import webbrowser
import re
import requests
import json
import base64
import aria2p



headers={
	'Authorization':"",
	'Content-Type':'application/json'
}
uploadfile_list=[]
client_id="352ce6ec-85b0-4b0b-b1e2-fe6cadc23c64"
client_secret="HLTSIBS5.9PK13m8pPs_gSk6_hN~4.oaNl"


def hum_convert(value):
	value=float(value)
	units = ["B", "KB", "MB", "GB", "TB", "PB"]
	size = 1024.0
	for i in range(len(units)):
		if (value / size) < 1:
			return "%.2f%s" % (value, units[i])
		value = value / size


#返回登录信息
def service_client(new_socket):
	"""为这个客户端返回数据"""

	#  1.接收浏览器发送过来的请求，即HTTP请求
	request=new_socket.recv(1024)
	request=request.decode("utf-8")  #  解码
	request_lines=request.splitlines()  #  按照行('\r', '\r\n', \n')分隔，返回一个包含各行作为元素的列表
	print(request_lines)
	#  准备发送的header
	response="HTTP/1.1 200 OK\r\n"
	response+="\r\n"  #  header与body之间必须隔一行
	response+="Login information obtained successfully"
	#  发送header
	new_socket.send(response.encode("utf-8"))
	#  发送HTML
	new_socket.close()

def callbaock_login():
	redirect_uri="http://localhost:53682"
	scope="offline_access user.read Files.Read Files.ReadWrite Files.Read.All Files.ReadWrite.All Sites.Read.All Sites.ReadWrite.All"

	login_url=f"https://login.microsoftonline.com/common/oauth2/v2.0/authorize?" \
			  f"client_id={client_id}" \
			  "&response_type=code" \
			  f"&redirect_uri={redirect_uri}" \
			  "&response_mode=query" \
			  f"&scope={scope}"

	webbrowser.open(url=login_url)

	encoding = 'utf-8'
	BUFSIZE = 1024
	port = 53682
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	sock.bind(("127.0.0.1", port))
	sock.listen(0)
	client, cltadd = sock.accept()
	#print(client, cltadd)
	while True:
		data = client.recv(BUFSIZE)
		#print(type(data))
		if(data):
			string = bytes.decode(data, encoding)
			#print(type(string))
			#print(string)
			code=re.findall(".*?code=(.*?)&", string, re.S)[0]
			print(code)
			break
	service_client(client)
	sock.close()
	print("获取code成功")
	data={
		"client_id":client_id,
		"grant_type":"authorization_code",
		"redirect_uri":redirect_uri,
		"scope":scope,
		"client_secret":client_secret,
		"code":code
	}

	test_url="https://login.microsoftonline.com/common/oauth2/v2.0/token"
	result=requests.post(url=test_url,data=data)

	if result.status_code==200:
		result_json=result.json()

		input("获取access_token成功,已写入json,任意键返回菜单")
		config_data={}
		config_data['access_token']=result_json['access_token']
		config_data['refresh_token']=result_json['refresh_token']

		with open("config.json", "w") as jsonFile:
			json.dump(config_data, jsonFile,indent=4,ensure_ascii=False)
			jsonFile.close()
		return

#浏览器登录
def autologin():


	redirect_uri="http://localhost:53682"
	scope="offline_access user.read Files.Read Files.ReadWrite Files.Read.All Files.ReadWrite.All Sites.Read.All Sites.ReadWrite.All"

	login_url=f"https://login.microsoftonline.com/common/oauth2/v2.0/authorize?" \
			  f"client_id={client_id}" \
			  "&response_type=code" \
			  f"&redirect_uri={redirect_uri}" \
			  "&response_mode=query" \
			  f"&scope={scope}"

	webbrowser.open(url=login_url)
	print(login_url)
	result=input("输入浏览器登录后跳转链接\n")

	code=re.findall(".*?code=(.*?)&", result, re.S)[0]


	data={
		"client_id":client_id,
		"grant_type":"authorization_code",
		"redirect_uri":redirect_uri,
		"scope":scope,
		"client_secret":client_secret,
		"code":code
	}

	test_url="https://login.microsoftonline.com/common/oauth2/v2.0/token"
	result=requests.post(url=test_url,data=data)

	if result.status_code==200:
		result_json=result.json()

		input("获取access_token成功,已写入json,任意键返回菜单")
		config_data={}
		config_data['access_token']=result_json['access_token']
		config_data['refresh_token']=result_json['refresh_token']

		with open("config.json", "w") as jsonFile:
			json.dump(config_data, jsonFile,indent=4,ensure_ascii=False)
			jsonFile.close()
		return


	else:
		print("获取access_token失败")
		print(result.text)
		return

def choose_login():

	print("选择登录方式")
	print("1-全自动化登录")
	print("2-手动登录(选项1不成功请尝试此项)")
	while True:
		keywords=input()
		try:
			keywords=int(keywords)
			if keywords==1:
				callbaock_login()
				break
			elif keywords==2:
				autologin()
				break
			else:
				print("选项不存在")
		except Exception as e:
			if "invalid literal for int()" in str(e):
				print("输入的不是数字，请再次输入")
	return


def gettoken(id,secret,refresh_token):
	headers={'Content-Type':'application/x-www-form-urlencoded'
			 }
	data={'grant_type': 'refresh_token',
		  'refresh_token': refresh_token,
		  'client_id':id,
		  'client_secret':secret,
		  'redirect_uri':'http://localhost:53682/'
		  }
	html = req.post('https://login.microsoftonline.com/common/oauth2/v2.0/token',data=data,headers=headers)
	jsontxt = json.loads(html.text)
	refresh_token = jsontxt['refresh_token']
	access_token = jsontxt['access_token']
	return access_token

def creat_folder(drive_id,parent_item_id,name):
	creat_url=f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{parent_item_id}/children"
	creat_body={
		"name": name,
		"folder": {}
	}
	html=requests.post(url=creat_url,headers=headers,json=creat_body)
	#print(html.json())
	return html.json()


def get_info(drive_id,item_id):
	info_url=f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{item_id}"

	html=requests.get(url=info_url,headers=headers)
	return html.json()

def small_copy(driveid,itemid,dir_drive,dir_item):
	try:
		copy_url=f"https://graph.microsoft.com/v1.0/drives/{driveid}/items/{itemid}/copy"
		copy_body={
			"parentReference": {
				"driveId": dir_drive,
				"id": dir_item
			}
		}
		try:
			html=requests.post(url=copy_url,headers=headers,json=copy_body)
		except :
			print("复制失败，跳过")
			return
		#大文件夹
		if html.status_code==413:
			print("文件超出大小,启用分步复制")

			#获取文件夹名称
			temp_json=get_info(driveid,itemid)
			new_folder_name=temp_json['name']
			print(new_folder_name)

			#新建文件夹
			temp_json=creat_folder(drive_id=dir_drive,parent_item_id=dir_item,name=new_folder_name)
			#获取新建文件夹信息
			temp_drive=temp_json['parentReference']['driveId']
			temp_item=temp_json['id']
			#获取分享内容文件夹内子文件列表信息
			share_list=get_folder_list(driveid=driveid,itemid=itemid)
			#print(share_list)
			#遍历分享文件夹内容
			for a in share_list:
				share_driveid=a['parentReference']['driveId']
				share_id=a['id']
				small_copy(driveid=share_driveid,itemid=share_id,dir_drive=temp_drive,dir_item=temp_item)

			return
		#print(f"{new_folder_name} 全部复制完成")

		else:

			status_url=html.headers["Location"]

			temp_json=get_info(driveid,itemid)
			folder_name=temp_json['name']
			print(f"\033[1;32m添加成功:{folder_name}\033[0m")
			temp_json=get_info(driveid,itemid)
			folder_name=temp_json['name']
			upload_info={"status_url":status_url,"folder_name":folder_name}
			uploadfile_list.append(upload_info)
			time.sleep(1)
			return
	except:
		print("复制失败，跳过")
		return


#复制思路，不依靠路径，直接复制文件夹，提示文件过大则后新建文件夹复制子文件夹和子文件
def start_copy(driveid,itemid):
	print("开始复制")
	with open("config.json", "r",encoding='utf-8') as jsonFile:
		data = json.load(jsonFile)
		jsonFile.close()
	try:
		root_driveid=data['root_driveid']
		root_itemid=data['root_itemid']
	except:
		print("请先设定保存文件夹")
		return
	copy_url=f"https://graph.microsoft.com/v1.0/drives/{driveid}/items/{itemid}/copy"
	copy_body={
		"parentReference": {
			"driveId": root_driveid,
			"id": root_itemid
		}
	}
	html=requests.post(url=copy_url,headers=headers,json=copy_body)

	#大文件夹
	if html.status_code==413:
		print("文件超出大小,启用分步复制")

		#获取文件夹名称
		temp_json=get_info(driveid,itemid)
		new_folder_name=temp_json['name']
		print(new_folder_name)

		#新建文件夹
		temp_json=creat_folder(drive_id=root_driveid,parent_item_id=root_itemid,name=new_folder_name)
		#获取新建文件夹信息
		temp_drive=temp_json['parentReference']['driveId']
		temp_item=temp_json['id']

		#获取分享内容文件夹内子文件列表信息
		share_list=get_folder_list(driveid=driveid,itemid=itemid)
		#print(share_list)

		#遍历分享文件夹内容
		for a in share_list:
			share_driveid=a['parentReference']['driveId']
			share_id=a['id']
			small_copy(driveid=share_driveid,itemid=share_id,dir_drive=temp_drive,dir_item=temp_item)

		print("添加云端复制完成")
		return
		#print(f"{new_folder_name} 全部复制完成")

	else:

		status_url=html.headers["Location"]
		temp_json=get_info(driveid,itemid)
		folder_name=temp_json['name']
		print(f"\033[1;32m添加成功:{folder_name}\033[0m")

		upload_info={"status_url":status_url,"folder_name":folder_name}
		uploadfile_list.append(upload_info)

		print("添加云端复制完成")
		return



def login():

	try:
		with open("config.json", "r",encoding='utf-8') as jsonFile:
			data = json.load(jsonFile)
			jsonFile.close()
	except Exception as e:
		print(f"读取config.json错误{e}")
		return

	try:


		refresh_token=data['refresh_token']
		print("获取配置成功")
		access_token=gettoken(client_id,client_secret,refresh_token)
		#print(access_token)
		print("刷新access_token成功")

	except Exception as e:
		print(f"读取配置失败{e}")
		return

	global headers
	try:
		headers={
			'Authorization':access_token,
			'Content-Type':'application/json'
		}
		html=requests.get(r'https://graph.microsoft.com/v1.0/me/drive',headers=headers)
		#print(html.json())
		print(f'----------刷新成功--------\n'
			  f'name:{html.json()["name"]}\n'
			  f'webUrl:{html.json()["webUrl"]}\n'
			  f'driveType:{html.json()["driveType"]}\n'
			  f'身份信息:{html.json()["owner"]}\n')
		input("任意键回到菜单")
		return
	except Exception as e:
		print(f"登录失败失败{e}")
		return

def get_folder_list(driveid,itemid):
	html=requests.get(f'https://graph.microsoft.com/v1.0/drives/{driveid}/items/{itemid}/children',headers=headers)

	print(f"获取子文件夹{itemid}")
	#print(html.json())
	copy_list=[]
	while True:
		for a in html.json()['value']:
			copy_list.append(a)
		if "@odata.nextLink" in html.json():
			print("该资源子文件超过200")
			new_url=html.json()['@odata.nextLink']
			html=requests.get(url=new_url,headers=headers)
		else:
			break
	#print(copy_list)
	print(f"子文件数为：{len(copy_list)}")
	return copy_list

def get_folder_info(driveid,itemid,foldername):

	html=requests.get(f'https://graph.microsoft.com/v1.0/drives/{driveid}/items/{itemid}/children',headers=headers)
	#print(html.json())
	print(f"获取子文件夹{itemid}")
	copy_list=[]
	for a in html.json()['value']:
		if "file" in a:
			print(foldername)
			print(a['parentReference']['path'])
			temp_foldername=str(foldername).replace("+","\+")

			copy_path=re.findall(f".*?({temp_foldername}.*)", str(a['parentReference']['path']), re.S)[0]

			copy_dict={"driveId": a["parentReference"]["driveId"], "id" : a["id"] ,"path":copy_path}
			print(a['name'],copy_path)
			copy_list.append(copy_dict)
		elif "folder" in a:
			temp_list=get_folder_info(a["parentReference"]["driveId"],a["id"],foldername=foldername)
			copy_list=copy_list+temp_list
	return copy_list

def add_down(url,path):
	with open("config.json", "r", encoding='utf-8') as jsonFile:
		data = json.load(jsonFile)
		jsonFile.close()
	try:
		Aria2_host = data['Aria2_host']
		Aria2_port = data['Aria2_port']
		Aria2_secret = data['Aria2_secret']
		Aria2_path = data['Aria2_path']
	except:
		print("未配置Aria2")
		return
	try:
		aria2 = aria2p.API(
			aria2p.Client(
				host=Aria2_host,
				port=int(Aria2_port),
				secret=Aria2_secret
			)
		)
		aria2.add_uris([url],options={"dir": f"{Aria2_path}{path}"})

	except Exception as e:
		print(f"添加出错;{e}")

def small_down(driveid,itemid,pafolder_name):
	html = requests.get(f'https://graph.microsoft.com/v1.0/drives/{driveid}/items/{itemid}', headers=headers)

	fold_name = html.json()['name']
	html = requests.get(f'https://graph.microsoft.com/v1.0/drives/{driveid}/items/{itemid}/children', headers=headers)



	for a in html.json()['value']:
		path = f"{pafolder_name}/{fold_name}"
		if "file" in a:
			print(f"添加任务-文件:{a['name']}-路径:{path}")
			add_down(url=a['@microsoft.graph.downloadUrl'], path=path)
		elif "folder" in a:
			#print(f"文件夹:" + a['name'])
			small_down(driveid=a['parentReference']['driveId'], itemid=a['id'], pafolder_name=fold_name)

def start_down(driveid,itemid):
	html=requests.get(f'https://graph.microsoft.com/v1.0/drives/{driveid}/items/{itemid}',headers=headers)
	#print(html.json())
	fold_name=html.json()['name']
	html=requests.get(f'https://graph.microsoft.com/v1.0/drives/{driveid}/items/{itemid}/children',headers=headers)
	#print(html.json())
	print("开始获取文件夹文件")

	for a in html.json()['value']:
		path=f"/{fold_name}"
		if "file" in a:
			print(f"添加任务-文件:{a['name']}-路径:{path}")
			add_down(url=a['@microsoft.graph.downloadUrl'],path=path)
		elif "folder" in a:
			#print(f"文件夹:"+a['name'])
			small_down(driveid=a['parentReference']['driveId'],itemid=a['id'],pafolder_name=path)





def small_list(driveid,itemid):
	#print(driveid,itemid)
	html=requests.get(f'https://graph.microsoft.com/v1.0/drives/{driveid}/items/{itemid}/children',headers=headers)
	#print(html.json())
	re_dict = html.json()
	info_list=[]
	num=0
	if re_dict['value']==[]:
		print("该文件夹为空")
	for a in re_dict['value']:
		info_list.append(a)
		#print(a['name']+'   '+a['remoteItem']['id']+'   '+a['remoteItem']['sharepointIds']['siteId']+'   '+a['remoteItem']['parentReference']['driveId'])
		print(f"{num} --- {a['name']}")
		num=num+1
	print("请输入资源对应的数字,y or yes - 复制当前文件夹,d or down - 下载当前文件夹内容到Aria2,s or save - 设置当前文件夹为保存文件夹,exit or q or quit - 退出\n扩展例子：0-9 保存当前多个文件夹")

	while True:
		keywords=input()
		if "exit" in keywords or "q" in keywords or "quit" in keywords:
			return
		elif "y" in keywords or "yes" in keywords:
			start_copy(driveid=driveid,itemid=itemid)
			input("任意键回到主菜单")
			return
		elif "-" in keywords:
			hua_list=keywords.split("-")

			for a in range(int(hua_list[0]),int(hua_list[1])):
				temp_driveid = info_list[a]['parentReference']['driveId']
				temp_itemid = info_list[a]['id']
				start_copy(driveid=temp_driveid,itemid=temp_itemid)
			return
		elif "s" in keywords or "save" in keywords:
			with open("config.json", "r",encoding='utf-8') as jsonFile:
				data = json.load(jsonFile)
				jsonFile.close()
			data['root_driveid']=driveid
			data['root_itemid']=itemid
			with open("config.json", "w") as jsonFile:
				json.dump(data, jsonFile,indent=4,ensure_ascii=False)
				jsonFile.close()
			input("保存配置成功，任意键回到菜单")
			return

		elif "d" in keywords or "down" in keywords:

			start_down(driveid=driveid,itemid=itemid)
			input("任意键回到主菜单")
			return

		try:
			keywords=int(keywords)
			#print(info_list[keywords])
			temp_driveid=info_list[keywords]['parentReference']['driveId']
			temp_itemid=info_list[keywords]['id']
			small_list(driveid=temp_driveid,itemid=temp_itemid)

			return
		except Exception as e:
			if "invalid literal for int()" in str(e):
				print("输入的不是数字，请再次输入")

def list():
	try:
		html=requests.get(r'https://graph.microsoft.com/v1.0/me/drive/sharedWithMe?allowexternal=true',headers=headers,timeout=5)

		#print(type(html.json()))
		re_dict = html.json()
	except Exception as e:
		print(f"获取列表失败,正在尝试重新登录:{e}")
		login()
		return
	#print(re_dict['value'])
	info_list=[]
	num=0
	if re_dict['value']==[]:
		print("文件列表为空")
	for a in re_dict['value']:
		info_list.append(a)
		#print(a['name']+'   '+a['remoteItem']['id']+'   '+a['remoteItem']['sharepointIds']['siteId']+'   '+a['remoteItem']['parentReference']['driveId'])
		print(f"{num} --- {a['name']}---siteid:{a['remoteItem']['sharepointIds']['siteId']} driveid:{a['remoteItem']['parentReference']['driveId']}")
		num=num+1
	print("请输入资源对应的数字,exit or q or quit - 退出")

	while True:
		keywords=input()
		if "exit" in keywords or "q" in keywords or "quit" in keywords:
			return

		try:
			keywords=int(keywords)
			#print(info_list[keywords])
			temp_driveid=info_list[keywords]['remoteItem']['parentReference']['driveId']
			temp_itemid=info_list[keywords]['id']
			#get_folder_list(driveid=temp_driveid,itemid=temp_itemid)
			small_list(driveid=temp_driveid,itemid=temp_itemid)
			return
		except Exception as e:
			if "invalid literal for int()" in str(e):
				print("输入的不是数字，请再次输入")

def my_file():
	html=requests.get(r'https://graph.microsoft.com/v1.0/me/drive/root/children',headers=headers)
	#print(html.json())
	file_list=[]
	num=0
	for a in html.json()['value']:
		file_list.append(a)
		#print(num+" - "+ a['name']+'   ItemID:'+a['id']+'   driveId:'+a['parentReference']['driveId'])
		print(f"{num} - {a['name']}")
		num=num+1
	print("请输入资源对应的数字,exit or q or quit - 退出")

	while True:
		keywords=input()
		if "exit" in keywords or "q" in keywords or "quit" in keywords:
			return

		try:
			keywords=int(keywords)
			#print(file_list[keywords])


			small_list(driveid=file_list[keywords]['parentReference']['driveId'],itemid=file_list[keywords]['id'])

			return
		except Exception as e:
			if "invalid literal for int()" in str(e):
				print("输入的不是数字，请再次输入")


def my_root_sharelist_file(site_id):
	html=requests.get(f'https://graph.microsoft.com/v1.0/sites/{site_id}/drive/root/children',headers=headers)
	#print(html.json())
	file_list=[]
	num=0
	for a in html.json()['value']:
		file_list.append(a)
		#print(num+" - "+ a['name']+'   ItemID:'+a['id']+'   driveId:'+a['parentReference']['driveId'])
		print(f"{num} - {a['name']}")
		num=num+1
	print("请输入资源对应的数字,exit or q or quit - 退出")

	while True:
		keywords=input()
		if "exit" in keywords or "q" in keywords or "quit" in keywords:
			return
		try:
			keywords=int(keywords)
			#print(file_list[keywords])
			small_list(driveid=file_list[keywords]['parentReference']['driveId'],itemid=file_list[keywords]['id'])
			return


		except Exception as e:
			if "invalid literal for int()" in str(e):
				print("输入的不是数字，请再次输入")

def my_sharelist_file():
	html=requests.get(r'https://graph.microsoft.com/v1.0/me/followedSites',headers=headers)
	print(html.json())
	file_list=[]
	num=0
	for a in html.json()['value']:
		file_list.append(a)
		#print(num+" - "+ a['name']+'   ItemID:'+a['id']+'   driveId:'+a['parentReference']['driveId'])
		print(f"{num} - {a['displayName']}")
		num=num+1
	print("请输入资源对应的数字,exit or q or quit - 退出")

	while True:
		keywords=input()
		if "exit" in keywords or "q" in keywords or "quit" in keywords:
			return
		try:
			keywords=int(keywords)

			my_root_sharelist_file(site_id=file_list[keywords]['id'])
			return


		except Exception as e:
			if "invalid literal for int()" in str(e):
				print("输入的不是数字，请再次输入")


def get_share_url(itemid):
	html=requests.get(f'https://graph.microsoft.com/v1.0/me/drive/items/{itemid}',headers=headers)
	#print(html.json())
	folder_name=html.json()['name']
	foder_size=hum_convert(html.json()['size'])
	print(f"{folder_name} {foder_size}")
	f = "shareurl.txt"


	data={
		"type": "view",
		"scope": "organization"
	}
	html=requests.post(f'https://graph.microsoft.com/v1.0/me/drive/items/{itemid}/createLink',headers=headers,json=data)
	#print(html.json())
	share_url=html.json()['link']['webUrl']
	with open(f,"a") as file:   #只需要将之前的”w"改为“a"即可，代表追加内容

		file.write(f"{folder_name}\n大小:{foder_size}\n链接地址:{share_url}\n\n")
		file.close()

def small_share(itemid):
	html=requests.get(f'https://graph.microsoft.com/v1.0/me/drive/items/{itemid}/children',headers=headers)
	file_list=[]
	num=0
	for a in html.json()['value']:
		file_list.append(a)
		#print(num+" - "+ a['name']+'   ItemID:'+a['id']+'   driveId:'+a['parentReference']['driveId'])
		print(f"{num} - {a['name']}")
		num=num+1
	print("请输入文件夹对应的数字进入文件夹,输入y or yes - 批量输出该文件夹分享链接，输入exit or q or quit - 退出")
	while True:
		keywords=input()
		if "exit" in keywords or "q" in keywords or "quit" in keywords:
			return
		elif "y" in keywords or "yes" in keywords:
			for a in file_list:
				temp_itemid=a['id']
				get_share_url(itemid=temp_itemid)
			input("导出分享链接成功，请检查程序目录下share.txt")
			return
		try:
			keywords=int(keywords)

			temp_itemid=file_list[keywords]['id']
			small_share(itemid=temp_itemid)
			return

		except Exception as e:
			if "invalid literal for int()" in str(e):
				print("输入的不是数字，请再次输入")


def share():
	html=requests.get(r'https://graph.microsoft.com/v1.0/me/drive/root/children',headers=headers)
	#print(html.json())
	file_list=[]
	num=0
	for a in html.json()['value']:
		file_list.append(a)
		#print(num+" - "+ a['name']+'   ItemID:'+a['id']+'   driveId:'+a['parentReference']['driveId'])
		print(f"{num} - {a['name']}")
		num=num+1
	print("请输入文件夹对应的数字进入文件夹,exit or q or quit - 退出")
	while True:
		keywords=input()
		if "exit" in keywords or "q" in keywords or "quit" in keywords:
			return
		try:
			keywords=int(keywords)
			temp_itemid=file_list[keywords]['id']
			small_share(itemid=temp_itemid)
			return

		except Exception as e:
			if "invalid literal for int()" in str(e):
				print("输入的不是数字，请再次输入")


def ownapi():
	try:
		newclient_id = str(input("请输入client_id\n"))
		newclient_secret =str(input("请输入client_secret\n"))
		data['client_id'] = newclient_id
		data['client_secret'] = newclient_secret
		with open("config.json", "w") as jsonFile:
			json.dump(data, jsonFile, indent=4, ensure_ascii=False)
			jsonFile.close()
		input("保存配置成功，任意键回到菜单,请重新登录")
		return
	except:
		print("写入失败")

def check_aria2():
	with open("config.json", "r", encoding='utf-8') as jsonFile:
		data = json.load(jsonFile)
		jsonFile.close()
	try:
		Aria2_host = data['Aria2_host']
		Aria2_port = data['Aria2_port']
		Aria2_secret = data['Aria2_secret']
	except:
		print("未配置Aria2")
		return
	try:
		aria2 = aria2p.API(
			aria2p.Client(
				host=Aria2_host,
				port=int(Aria2_port),
				secret=Aria2_secret
			)
		)
		sta=aria2.get_stats()
		input("连接成功,任意键回到菜单")
	except Exception as e:
		print(f"连接性出错;{e}")
		input()

def add_aria2():
	try:
		Aria2_host = str(input("请输入aria2的地址，格式为：http://IP\n"))
		Aria2_port =str(input("请输入aria2的端口号\n"))
		Aria2_secret = str(input("请输入aria2的secret\n"))
		Aria2_path = str(input("请输入aria2的下载路径，后面不加/\n"))
		data['Aria2_host'] = Aria2_host
		data['Aria2_port'] = Aria2_port
		data['Aria2_secret'] = Aria2_secret
		data['Aria2_path'] = Aria2_path
		with open("config.json", "w") as jsonFile:
			json.dump(data, jsonFile, indent=4, ensure_ascii=False)
			jsonFile.close()
		input("保存配置成功，任意键回到菜单,请测试连接性")
		return
	except:
		print("写入失败")

def menu():

	while True:
		os.system("clear")

		print("********** Onedrive同域转存分享内容工具 **********")
		print("工具作者:\033[1;32mhttps://t.me/Ben_chao\033[0m")
		print("欢迎访问Onedrive资源交流社区:\033[1;32mhttps://t.me/OneDrive_1oveClub\033[0m")
		print("1-浏览器登录")
		print("2-刷新状态")
		print("3-查看我的文件")
		print("4-查看sharepoint")
		print("5-查看与我分享")
		print("6-批量分享链接")
		print("7-使用自定义API")
		print("8-使用分享链接访问")
		print("9-添加Aria2")
		print("10-检查Aria2连接性")
		print("11-退出")
		print("输入选项")

		while True:
			keywords=input()
			try:
				keywords=int(keywords)

				if keywords==1:
					choose_login()
					break
				elif keywords==2:
					login()
					break
				elif keywords==3:
					my_file()
					break
				elif keywords == 4:
					my_sharelist_file()
					break
				elif keywords==5:
					list()
					break
				elif keywords==6:
					share()
					break
				elif keywords == 7:
					ownapi()
					break
				elif keywords == 8:
					visit_url()
					break
				elif keywords == 9:
					add_aria2()
					break
				elif keywords == 10:
					check_aria2()
					break
				elif keywords==11:
					return


			except Exception as e:
				if "invalid literal for int()" in str(e):
					print("输入的不是数字，请再次输入")


def my_sharepoint():
	html=requests.get(r'https://graph.microsoft.com/v1.0/me/followedSites',headers=headers)
	print(html.json())
	file_list=[]
	num=0
	for a in html.json()['value']:
		file_list.append(a)
		#print(num+" - "+ a['name']+'   ItemID:'+a['id']+'   driveId:'+a['parentReference']['driveId'])
		print(f"{num} - {a['displayName']} - {a['description']}")
		num=num+1
	print("请输入资源对应的数字,exit or q or quit - 退出")

def create_onedrive_directdownload (onedrive_link):
	data_bytes64 = base64.b64encode(bytes(onedrive_link, 'utf-8'))
	data_bytes64_String = data_bytes64.decode('utf-8').replace('/','_').replace('+','-').rstrip("=")
	data_bytes64_String="u!"+data_bytes64_String
	#print(data_bytes64_String)
	return data_bytes64_String

#tttid="01LTX3PTSWETP2GUMITVCIBM74MZKTWFSF"
#login()
#get_share_url(itemid=tttid)
if os.path.isfile("config.json")==True:
	print("配置文件存在,直接读取")
	try:


		with open("config.json", "r",encoding='utf-8') as jsonFile:
			data = json.load(jsonFile)
			jsonFile.close()
		refresh_token=data['refresh_token']
		try:
			client_id = data['client_id']
			client_secret = data['client_secret']
		except:
			print("无自定义API，使用默认API")
		print("获取配置成功，开始刷新access_token")
		access_token=gettoken(client_id,client_secret,refresh_token)
		headers={
			'Authorization':access_token,
			'Content-Type':'application/json'
		}
	except Exception as e:
			input("无法读取access_token，请在菜单中登录")
else:
	input("未找到配置,请先登录，任意键到菜单登录")
	with open("config.json","a") as file:   #只需要将之前的”w"改为“a"即可，代表追加内容
		file.close()

def visit_url():

	print("\033[1;32m请注意，请预先用账号登录状态的浏览器打开分享链接\n\033[0m")
	link=input("请输入分享链接")
	shareIdOrEncodedSharingUrl=create_onedrive_directdownload(onedrive_link=link)


	html=requests.get(rf'https://graph.microsoft.com/v1.0/shares/{shareIdOrEncodedSharingUrl}/driveItem?$expand=children',headers=headers)
	#print(html.json())
	if "error" in str(html.json()):
		print(html.json())
		return
	if 'children' in html.json():

		file_list = []
		num = 0
		for a in html.json()['children']:
			file_list.append(a)
			# print(num+" - "+ a['name']+'   ItemID:'+a['id']+'   driveId:'+a['parentReference']['driveId'])
			print(f"{num} - {a['name']}")
			num = num + 1
		print("请输入资源对应的数字,y or yes - 复制当前文件夹,s or save - 设置当前文件夹为保存文件夹,exit or q or quit - 退出\n扩展例子：0-9 保存当前多个文件夹")
		driveid=html.json()['children'][0]['parentReference']['driveId']
		itemid=html.json()['id']
		while True:
			keywords=input()
			if "exit" in keywords or "q" in keywords or "quit" in keywords:
				return
			elif "y" in keywords or "yes" in keywords:
				start_copy(driveid=driveid,itemid=itemid)
				input("任意键回到主菜单")
				return
			elif "-" in keywords:
				hua_list=keywords.split("-")

				for a in range(int(hua_list[0]),int(hua_list[1])):
					temp_driveid = file_list[a]['parentReference']['driveId']
					temp_itemid = file_list[a]['id']
					start_copy(driveid=temp_driveid,itemid=temp_itemid)
				return
			elif "s" in keywords or "save" in keywords:
				with open("config.json", "r",encoding='utf-8') as jsonFile:
					data = json.load(jsonFile)
					jsonFile.close()
				data['root_driveid']=driveid
				data['root_itemid']=itemid
				with open("config.json", "w") as jsonFile:
					json.dump(data, jsonFile,indent=4,ensure_ascii=False)
					jsonFile.close()
				input("保存配置成功，任意键回到菜单")
				return

			try:
				keywords=int(keywords)
				#print(info_list[keywords])
				temp_driveid=file_list[keywords]['parentReference']['driveId']
				temp_itemid=file_list[keywords]['id']
				small_list(driveid=temp_driveid,itemid=temp_itemid)

				return
			except Exception as e:
				if "invalid literal for int()" in str(e):
					print("输入的不是数字，请再次输入")
	else:
		print(f"{html.json()['name']}")
		print("请输入资源对应的数字,y or yes - 复制当前文件,d or down - 下载当前文件夹内容到Aria2,exit or q or quit - 退出")
		driveid = html.json()['parentReference']['driveId']
		itemid = html.json()['id']
		while True:
			keywords = input()
			if "exit" in keywords or "q" in keywords or "quit" in keywords:
				return
			elif "y" in keywords or "yes" in keywords:
				start_copy(driveid=driveid, itemid=itemid)
				input("任意键回到主菜单")
				return

			elif "d" in keywords or "down" in keywords:

				start_down(driveid=driveid, itemid=itemid)
				input("任意键回到主菜单")
				return



menu()

