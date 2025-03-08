import os
import requests
from dotenv import load_dotenv
import json
from tqdm import tqdm
import time
from PIL import Image
import io
import random
from scripts.api import check_api, refresh_api

load_dotenv()

def get_list(username, status, hentai, amount = 1000):
  access_token = os.getenv("access_token")
  headers = {
    f"Authorization": f"Bearer {access_token}"
  }

  if status != "all":
    status = f"status={status}&"
  else:
    status = ""

  def temp_list(offset):
    api_url = f'https://api.myanimelist.net/v2/users/{username}/animelist?{status}fields=list_status&limit=1000&offset={offset}&nsfw={hentai}'

    r = requests.get(api_url, headers=headers)

    if r.status_code != 200:
      return []

    try:
      response = r.json()
      id_list = []

      for entry in response.get('data', []):
        anime_id = entry['node']['id']
        id_list.append(anime_id)

      return id_list

    except json.JSONDecodeError:
      print(f"JSON Decode Error. Response text: {r.text}")
      return []


  id_list = []
  off = 0
  temp_id_list = temp_list(off)
  if not temp_id_list:
    return []
  id_list += temp_id_list
  off += 1000

  while len(temp_id_list) == 1000:
    temp_id_list = temp_list(off)
    if not temp_id_list:
      break
    off += 1000
    id_list += temp_id_list
  return id_list

def anime_info(anime_id):

  access_token = os.getenv("access_token")
  headers = {
    f"Authorization": f"Bearer {access_token}"
  }

  api_url = f'https://api.myanimelist.net/v2/anime/{anime_id}?fields=id,title,main_picture,alternative_titles,start_date,end_date,synopsis,mean,rank,popularity,num_list_users,num_scoring_users,nsfw,created_at,updated_at,media_type,status,genres,my_list_status,num_episodes,start_season,broadcast,source,average_episode_duration,rating,pictures,background,related_anime,related_manga,recommendations,studios,statistics'

  response = requests.get(api_url, headers=headers)

  try:
    response = response.json()
  except Exception as e:
    time.sleep(60)
    refresh_api()
    access_token = os.getenv("access_token")
    time.sleep(180)
    response = requests.get(api_url, headers=headers).json()

  return response

def build_cache(id_list):
  for i in tqdm(id_list):
    with open(f"cache/{i}.json", mode='w') as f:
      f.write(json.dumps(anime_info(i), indent=4))

def update_cache(id_list):
  cache = []
  for filename in os.listdir('cache'):
    if filename != "invalid.json":
      filepath = os.path.join('cache', filename)
      if os.path.isfile(filepath):
        base_name, extension = os.path.splitext(filename)
        cache.append(int(base_name))

  to_add = []

  for i in id_list:
    if i not in cache:
      to_add.append(i)

  build_cache(to_add)

  invalid = sanitize_cache()

  while len(invalid) > 0:
    print(f"Regenerating {len(invalid)} entries:")
    build_cache(invalid)
    invalid = sanitize_cache()

def sanitize_cache():

  with open("cache/invalid.json", 'r') as f:
    invalid = f.read()

  sanitize = []

  for filename in os.listdir("cache"):
    with open(f"cache/{filename}", 'r') as f:
      if filename != "invalid.json":
        data = f.read()
        if data == invalid or data == "":
          fsplit = filename.split('.')
          sanitize.append(int(fsplit[0]))
          os.remove(f"cache/{filename}")
  return sanitize

def get_image(id):
  with open(f"cache/{id}.json", 'r') as f:
    try:
      jstring = f.read()
      data = json.loads(jstring)
      response = requests.get(data["main_picture"]["medium"], stream=True)
      image_file = io.BytesIO(response.content)
      image = Image.open(image_file)
      return image
    except Exception as e:
      return e

def get_title(id):
    with open(f"cache/{id}.json", 'r') as f:
      try:
        jstring = f.read()
        data = json.loads(jstring)
        return data["title"]
      except Exception as e:
        return e

def get_random(name, list_type, media_type, score, year, episodes, include, exclude, amount, sequels):

  if not check_api():
    refresh_api()

  list_type = list_type.lower()
  list_type = list_type.replace(' ', '_')

  for i in range(len(media_type)):
    media_type[i] = media_type[i].lower()
    media_type[i] = media_type[i].replace(' ', '_')

  print(f"Grabbing {name}'s {list_type} list...")
  userlist = get_list(name, list_type, True if "hentai" in media_type else False)
  if not userlist:
    return []

  update_cache(userlist)

  posslist = []

  for i in tqdm(userlist):
    with open(f"cache/{i}.json", 'r') as f:
      jstring = f.read()
      data = json.loads(jstring)

      if (
          data["media_type"] in media_type
          and data.get("mean") is not None
          and data.get("mean", 0) >= score[0]
          and data.get("mean", 100) <= score[1]
          and "start_season" in data
          and data["start_season"] is not None
          and "year" in data["start_season"]
          and data["start_season"]["year"] >= year[0]
          and data["start_season"]["year"] <= year[1]
          and data["num_episodes"] >= episodes[0]
          and data["num_episodes"] <= episodes[1]
      ):

        sequel_check_passed = False
        if sequels == "Yes":
            sequel_check_passed = True
        elif sequels == "No":
            has_prequel = any(related["relation_type"] == "prequel" for related in data.get("related_anime", []))
            sequel_check_passed = not has_prequel
        elif sequels == "Exclusively":
            has_prequel = any(related["relation_type"] == "prequel" for related in data.get("related_anime", []))
            sequel_check_passed = has_prequel
        elif sequels is None or sequels == "":
            sequel_check_passed = True

        if sequel_check_passed:

          genre_check_passed = True

          if include:
            include_genres_present = set()
            if "genres" in data:
              for g in data["genres"]:
                if g["name"] in include:
                  include_genres_present.add(g["name"])
            if set(include) != include_genres_present:
              genre_check_passed = False

          if genre_check_passed and exclude:
            if "genres" in data:
              for g in data["genres"]:
                if g["name"] in exclude:
                  genre_check_passed = False
                  break 

          if genre_check_passed:
            posslist.append(data["id"])

  random.shuffle(posslist)
  posslist = posslist[:amount]

  random_list = []

  for i in tqdm(posslist):
    random_list.append((get_image(i), get_title(i)))

  print("List Randomized")

  return random_list