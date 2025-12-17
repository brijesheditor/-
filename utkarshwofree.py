import requests
import json
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad, pad
from base64 import b64decode, b64encode
import base64

# Configuration
API_URL = "https://application.utkarshapp.com/index.php/data_model"
COMMON_KEY = b"%!^F&^$)&^$&*$^&"
COMMON_IV = b"#*v$JvywJvyJDyvJ"
key_chars = "%!F*&^$)_*%3f&B+"
iv_chars = "#*$DJvyw2w%!_-$@"
HEADERS = {
    "Authorization": "Bearer 152#svf346t45ybrer34yredk76t",
    "Content-Type": "text/plain; charset=UTF-8",
    "devicetype": "1",
    "host": "application.utkarshapp.com",
    "lang": "1",
    "user-agent": "okhttp/4.9.0",
    "userid": "0",
    "version": "152"
}

# Encryption and Decryption Functions
def encrypt(data, use_common_key, key, iv):
    cipher_key, cipher_iv = (COMMON_KEY, COMMON_IV) if use_common_key else (key, iv)
    cipher = AES.new(cipher_key, AES.MODE_CBC, cipher_iv)
    padded_data = pad(json.dumps(data, separators=(",", ":")).encode(), AES.block_size)
    encrypted = cipher.encrypt(padded_data)
    return b64encode(encrypted).decode() + ":"

def decrypt(data, use_common_key, key, iv):
    cipher_key, cipher_iv = (COMMON_KEY, COMMON_IV) if use_common_key else (key, iv)
    cipher = AES.new(cipher_key, AES.MODE_CBC, cipher_iv)
    try:
        encrypted_data = b64decode(data.split(":")[0])
        decrypted_bytes = cipher.decrypt(encrypted_data)
        decrypted = unpad(decrypted_bytes, AES.block_size).decode()
        return decrypted
    except (ValueError, TypeError) as e:
        print(f"Decryption error: {e}")
        return None

def post_request(path, data=None, use_common_key=False, key=None, iv=None):
    encrypted_data = encrypt(data, use_common_key, key, iv) if data else data
    response = requests.post(f"{API_URL}{path}", headers=HEADERS, data=encrypted_data)
    decrypted_data = decrypt(response.text, use_common_key, key, iv)
    if decrypted_data:
        try:
            return json.loads(decrypted_data)
        except json.JSONDecodeError as e:
            print(f"JSON decoding error: {e}")
    return {}


def decrypt_stream(enc):
    try:
        enc = b64decode(enc)
        key = '%!$!%_$&!%F)&^!^'.encode('utf-8')
        iv = '#*y*#2yJ*#$wJv*v'.encode('utf-8')
        cipher = AES.new(key, AES.MODE_CBC, iv)

        decrypted_bytes = cipher.decrypt(enc)

        try:
            plaintext = unpad(decrypted_bytes, AES.block_size).decode('utf-8')
        except Exception:
            plaintext = decrypted_bytes.decode('utf-8', errors='ignore')
        cleaned_json = ''
        for i in range(len(plaintext)):
            try:
                json.loads(plaintext[:i+1])
                cleaned_json = plaintext[:i+1]  
            except json.JSONDecodeError:
                continue
        final_brace_index = cleaned_json.rfind('}')
        if final_brace_index != -1:
            cleaned_json = cleaned_json[:final_brace_index + 1]

        return cleaned_json

    except Exception as e:
        print(f"Decryption error: {e}")
        return None

def decrypt_and_load_json(enc):
    decrypted_data = decrypt_stream(enc)
    try:
        return json.loads(decrypted_data)
    except json.JSONDecodeError as e:
        print(f"JSON decoding error: {e}")
        return None

def encrypt_stream(plain_text):
    try:
        key = '%!$!%_$&!%F)&^!^'.encode('utf-8')
        iv = '#*y*#2yJ*#$wJv*v'.encode('utf-8')
        cipher = AES.new(key, AES.MODE_CBC, iv)

        padded_text = pad(plain_text.encode('utf-8'), AES.block_size)
        encrypted = cipher.encrypt(padded_text)

        return b64encode(encrypted).decode('utf-8')
    except Exception as e:
        print(f"Encryption error: {e}")
        return None

# Initialize session
session = requests.Session()

# Define URLs and headers
base_url = 'https://online.utkarsh.com/'
login_url = 'https://online.utkarsh.com/web/Auth/login'
tiles_data_url = 'https://online.utkarsh.com/web/Course/tiles_data'
layer_two_data_url = 'https://online.utkarsh.com/web/Course/get_layer_two_data'
meta_source_url = '/meta_distributer/on_request_meta_source'

# Define function to handle errors
def handle_error(message, exception=None):
    print(f"Error: {message}")
    if exception:
        print(f"Exception details: {exception}")

# Retrieve CSRF token
try:
    r1 = session.get(base_url)
    csrf_token = r1.cookies.get('csrf_name')
    if not csrf_token:
        raise ValueError("CSRF token not found.")
except Exception as e:
    handle_error("Failed to retrieve CSRF token", e)
    exit(1)

# Login
email = "email ya mob no dalo"
password = "yha pass dalo apna"
d1 = {'csrf_name': csrf_token, 'mobile': email, 'url': '0', 'password': password, 'submit': 'LogIn', 'device_token': 'null'}
h = {'Host': 'online.utkarsh.com', 'Sec-Ch-Ua': '"Chromium";v="119", "Not?A_Brand";v="24"', 'Accept': 'application/json, text/javascript, */*; q=0.01', 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8', 'X-Requested-With': 'XMLHttpRequest', 'Sec-Ch-Ua-Mobile': '?0', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.199 Safari/537.36'}

try:
    u2 = session.post(login_url, data=d1, headers=h).json()
    r2 = u2.get("response")
    dr1 = decrypt_and_load_json(r2)
    t = dr1.get("token")
    jwt = dr1.get("data", {}).get("jwt")
    h["token"] = t
    h["jwt"] = jwt
    HEADERS["jwt"] = jwt
except Exception as e:
    handle_error("Failed to log in or retrieve tokens", e)
    exit(1)

# Retrieve User Profile
try:
    profile = post_request("/users/get_my_profile", use_common_key=True)
    user_id = profile["data"]["id"]
    HEADERS["userid"] = user_id

    key = "".join(key_chars[int(i)] for i in (user_id + "1524567456436545")[:16]).encode()
    iv = "".join(iv_chars[int(i)] for i in (user_id + "1524567456436545")[:16]).encode()

except Exception as e:
    handle_error("Failed to retrieve user profile", e)
    exit(1)

# Extract course information
ci = input("\033[1mHey I Am ➸ᴹᴿ°ɧąƈƙɛཞ ™࿐  .PLZ INPUT ANY BATCH ID TO EXTRACT THAT COURSE\033[0m : ")
d3 = {"course_id": ci, "revert_api": "1#0#0#1", "parent_id": 0, "tile_id": "15330", "layer": 1, "type": "course_combo"}
try:
    de1 = encrypt_stream(json.dumps(d3))
    d4 = {'tile_input': de1, 'csrf_name': csrf_token}
    u4 = session.post(tiles_data_url, headers=h, data=d4).json()
    r4 = u4.get("response")
    dr3 = decrypt_and_load_json(r4)
except Exception as e:
    handle_error("Failed to retrieve course data", e)
    exit(1)

# Process each item in the response
for i in dr3.get("data", []):
    try:
        fi = i.get("id")
        tn = i.get("title")
        binfo = i.get("segment_information")
        print(f"{fi} ♧ {tn} \n\n {binfo}")
        fn = f"{fi}_{tn.replace('/','_').replace(':','_').replace('|','_')}.txt"
        with open(fn, "w") as f:
            d5 = {"course_id": fi, "layer": 1, "page": 1, "parent_id": fi, "revert_api": "1#1#0#1", "tile_id": "0", "type": "content"}
            de2 = encrypt_stream(json.dumps(d5))
            d6 = {'tile_input': de2, 'csrf_name': csrf_token}
            u5 = session.post(tiles_data_url, headers=h, data=d6).json()
            r5 = u5.get("response")
            dr4 = decrypt_and_load_json(r5)
            for i in dr4["data"]["list"]:
                sfi = i.get("id")
                sfn = i.get("title")
                d7 = {"course_id": fi, "parent_id": fi, "layer": 2, "page": 1, "revert_api": "1#0#0#1", "subject_id": sfi, "tile_id": 0, "topic_id": sfi, "type": "content"}
                b641 = json.dumps(d7)
                de3 = base64.b64encode(b641.encode()).decode()
                d8 = {'layer_two_input_data': de3, 'csrf_name': csrf_token}
                u6 = session.post(layer_two_data_url, headers=h, data=d8).json()
                r6 = u6["response"]
                dr5 = decrypt_and_load_json(r6)
                for i in dr5["data"]["list"]:
                    ti = i.get("id")
                    tt = i.get("title")
                    d9 = {"course_id": fi, "parent_id": fi, "layer": 3, "page": 1, "revert_api": "1#0#0#1", "subject_id": sfi, "tile_id": 0, "topic_id": ti, "type": "content"}
                    b642 = json.dumps(d9)
                    de4 = base64.b64encode(b642.encode()).decode()
                    d10 = {'layer_two_input_data': de4, 'csrf_name': csrf_token}
                    u7 = session.post(layer_two_data_url, headers=h, data=d10).json()
                    r7 = u7["response"]
                    dr6 = decrypt_and_load_json(r7)
                    if "data" in dr6:
                        if "list" in dr6["data"]:
                            for i in dr6["data"]["list"]:
                                ji = i.get("id")
                                jt = i.get("title")
                                jti = i["payload"]["tile_id"]
                                j4 = {"course_id": fi, "device_id": "server_does_not_validate_it", "device_name": "server_does_not_validate_it", "download_click": "0", "name": ji + "_0_0", "tile_id": jti, "type": "video"}
                                j5 = post_request(meta_source_url, j4, key=key, iv=iv)
                                cj = j5.get("data", [])
                                if cj:
                                	qo = cj.get("bitrate_urls", [])
                                	if qo and isinstance(qo, list):
                                		vu1 = qo[3].get("url", "") if len(qo) > 3 else ""
                                		vu2 = qo[2].get("url", "") if len(qo) > 2 else ""
                                		vu3 = qo[1].get("url", "") if len(qo) > 1 else ""
                                		vu = qo[0].get("url", "") if len(qo) > 0 else ""
                                		selected_vu = vu1 or vu2 or vu3 or vu
                                		if selected_vu:
                                			pu = selected_vu.split("?Expires=")[0]
                                			print(f"{jt}:{pu}\n")
                                			f.write(f"{jt}:{pu}\n")
                                	else:
                                		vu = cj.get("link", "")
                                		if vu:
                                			if ".m3u8" in vu or ".pdf" in vu:
                                				pu = vu.split("?Expires=")[0]
                                				print(f"{jt}:{pu}\n")
                                				f.write(f"{jt}:{pu}\n")
                                			else:
                                				pu = f"https://www.youtube.com/embed/{vu}"
                                				print(f"{jt}:{pu}\n")
                                				f.write(f"{jt}:{pu}\n")


    except KeyError as e:
        handle_error(f"Missing key in response data: {e}")
    except Exception as e:
        handle_error("An error occurred while processing data", e)
