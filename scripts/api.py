import requests
import os
import webbrowser
from dotenv import load_dotenv, set_key, find_dotenv
import json
from scripts.code_generator import get_new_code_verifier
from scripts.webserver import get_access_token_from_redirect

def generate_env():
  print("Welcome to Ozerune's Anime Randomizer!\n\nPlease go to:\n\nhttps://myanimelist.net -> Login -> <username dropdown> -> Preferences -> API -> Create ID\n\nApp Redirect URL: http://localhost/oauth\n\nSave then edit again\n\n")
  client_id = input("Client ID: ")
  client_secret = input("Client Secret: ")
  code = get_new_code_verifier()

  webbrowser.open(f"https://myanimelist.net/v1/oauth2/authorize?response_type=code&client_id={client_id}&code_challenge={code}")

  access_token = get_access_token_from_redirect()

  data = {
    'client_id': client_id,
    'client_secret': client_secret,
    'code': access_token,
    'code_verifier': code,
    'grant_type': 'authorization_code'
}

  response = requests.post("https://myanimelist.net/v1/oauth2/token", data=data)

  with open(".env", 'w') as f:
    f.write(f"client_id='{client_id}'\n")
    f.write(f"client_secret='{client_secret}'\n")
    f.write(f"api_key='{response.json()["access_token"]}'\n")
    f.write(f"refresh_token='{response.json()["refresh_token"]}'")

def check_api():
  print("Checking API key...")
  api_key = os.getenv("access_token")
  api_url = "https://api.myanimelist.net/v2/users/@me"
  headers = {
    "Authorization": f"Bearer {api_key}"
  }
  
  try:
    response = requests.get(api_url, headers=headers)
    response.raise_for_status()
    return True
  except requests.exceptions.RequestException:
    return False

def refresh_api():
  print("Refreshing API key...")
  dotenv_path = find_dotenv()
  refresh_token = os.getenv("refresh_token")
  client_id = os.getenv("client_id")
  client_secret = os.getenv("client_secret")
  api_url = "https://myanimelist.net/v1/oauth2/token"

  data = {
    "client_id": client_id,
    "grant_type": "refresh_token",
    "refresh_token": refresh_token,
    "client_secret": client_secret
  }

  response = requests.post(api_url, data=data)
  access_token = response.json().get('access_token')
  refresh_token = response.json().get('refresh_token')

  set_key(dotenv_path, "access_token", access_token)
  set_key(dotenv_path, "refresh_token", refresh_token)

  load_dotenv(dotenv_path, override=True)