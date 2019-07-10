import requests
import json

# Mattermost server
url = "http://3.81.100.169:8065"
login_url = url+"/api/v4/users/login"
team_name = "demoteam"
channel_name = "testexport"

# Mattermost target server
mm_url = "http://52.90.9.20:8065"
mm_login_url = mm_url+"/api/v4/users/login"
mm_team_name = "demoteam"
mm_channel_name = "putest02"

files = []
message = ""

def login(login_url):
    # Mattermost user/password to import with
    payload = { "login_id": "admin@mattermost.com",
                "password": "MattermostDemo,1"}
    headers = {"content-type": "application/json"}
    s = requests.Session()
    r = s.post(login_url, data=json.dumps(payload), headers=headers)
    auth_token = r.headers.get("Token")
    global hed
    hed = {'Authorization': 'Bearer ' + auth_token}

def get_team_id(url, team_name):
    team_url = url+"/api/v4/teams/search"
    payload = { "term": team_name}
    response = requests.post(team_url, headers=hed, json=payload)
    info = response.json()
    global team_id
    team_id = info[0]["id"]

def get_channel_id(url, team_id, channel_name):
    team_url = url+"/api/v4/teams/"+team_id+"/channels/search"
    payload = { "term": channel_name}
    response = requests.post(team_url, headers=hed, json=payload)
    info = response.json()
    global channel_id
    channel_id = info[0]["id"]

def get_posts(channel_id):
    team_url = url+"/api/v4/channels/"+channel_id+"/posts"
    response = requests.get(team_url, headers=hed)
    info = response.json()
    print(info)
    for i in info['posts'].items():
        parse_post(i)

def get_username(user_id):
    login(login_url)
    team_url = url+"/api/v4/users/"+user_id
    response = requests.get(team_url, headers=hed)
    info = response.json()
    global user_name
    user_name = info['username']

def parse_post(p):
    post = (p[1])
    for k, v in post.items():
        if k == "user_id":
            get_username(v)
        if k == "file_ids":
            for fileid in v:
                print("fileId: "+fileid)
                get_uploads(fileid)
        if k == "message":
            message = v
    create_post(mm_url, message, user_name)

def create_post(mm_url, message, user_name):
    print("Creating a new post...")
    login(mm_login_url)
    get_team_id(mm_url, mm_team_name)
    get_channel_id(mm_url, team_id, mm_channel_name)
    post_url = mm_url+"/api/v4/posts"
    for i in files:
        print("File ID in neuem Post: "+i)
    payload = {
        "channel_id":channel_id,
        "message":message,
        "file_ids":
            files
            ,
        "props": {
            "from_webhook":"true",
            "override_username":user_name
            }
        }
    print(payload)
    response = requests.post(post_url, headers=hed, json=payload)
    info = response.json()

def get_uploads(fileid):
    login(login_url)
    print("Getting uploads...")
    info_url = url+"/api/v4/files/" + fileid + '/info'
    response = requests.get(info_url, headers=hed)
    info = response.json()
    print("Filename: "+info['name'])
    global filename
    filename = info['name']
    # Download the file
    file_url = url+"/api/v4/files/" + fileid
    response = requests.get(file_url, headers=hed)
    open(filename, 'wb').write(response.content)
    print(filename)
    post_uploads(filename)

def post_uploads(filename):
    print("Uploading files...")
    login(mm_login_url)
    get_team_id(mm_url, mm_team_name)
    get_channel_id(mm_url, team_id, mm_channel_name)
    post_url = mm_url+"/api/v4/files?channel_id="+channel_id
    headers = {"content-type": "multipart/form-data"}
    file = {'upload_file': open(filename, 'rb')}
    response = requests.post(post_url, headers=hed, files=file)
    info = response.json()
    file_id = info['file_infos'][0]['id']
    str(file_id)
    files.append(file_id)
    print(info)

def main():
    login(login_url)
    get_team_id(url, team_name)
    get_channel_id(url, team_id, channel_name)
    get_posts(channel_id)

if __name__ == "__main__":
    main()
