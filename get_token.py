import requests
import hashlib
import sys

url = "https://global-robot-api.unitree.com/login/email"

def login(email, password):
    data = {
        'email': email,
        'password': password
    }

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.post(url, data=data, headers=headers)

    return response.json()

def generate_md5(string):
    md5_hash = hashlib.md5(string.encode())
    return md5_hash.hexdigest()

def main(email, password, sn):
    password_hash = generate_md5(password)
    
    login_response = login(email, password_hash)
    
    if login_response.get("code") == 100:
        data = login_response.get("data")
        accessToken = data.get("accessToken")
        refreshToken = data.get("refreshToken")
        user = data.get("user")
        uid = user.get("uid")
        
        special_password = generate_md5(sn + uid)[-6:]
        
        print("Login successful.")
        print(f"AccessToken: {accessToken}")
        print(f"Special Password: {special_password}")
    else:
        print("Login failed. Error message:", login_response.get("errorMsg"))

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: script.py <email> <password> <SN>")
        sys.exit(1)
    email = sys.argv[1]
    password = sys.argv[2]
    sn = sys.argv[3]
    main(email, password, sn)

