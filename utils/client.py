import requests
import time
from contextlib import contextmanager
from pathlib import Path
import uuid


class Client:
    def __init__(self, ctx):
        self.token = ctx.get('token')
        self.debug = ctx.get('debug')
        self.team_id = 0
        self.session = requests.Session()
        self.session_id = ctx.get('session_id')
        self.expiration = time.time() + 3600 

    def load_team_id(self, ctx, token=None):
        if token:
            self.token = token
        resp = self.get_profile(ctx)
        if resp is None:
            raise ValueError("runway: couldn't get profile")

        return resp["user"]["id"]

    def get_profile(self, ctx):
        return self.do(ctx, "GET", "profile", {})
      
    def create_assest_folder(self, name):
        asset_group_id = str(uuid.uuid4())
        asset = {
            "id": asset_group_id,
            "name": name,
            "favorite": False,
            "asTeamId": self.load_team_id(None),
            "privateInTeam": False
        }

        resp = self.do(None, "POST", "asset_groups", asset)
        
        print(f"Created Folder {name}.")

        return resp['assetGroup']['id']
      
    def do(self, ctx, method, path, in_data, is_json = True):
        url = f"https://api.runwayml.com/v1/{path}"
 
        headers = {
            "accept": "application/json",
            "accept-language": "en-US,en;q=0.9",
            "authorization": f"Bearer {self.token}",
            "content-type": "application/json",
            "origin": "https://app.runwayml.com",
            "priority": "u=1, i",
            "referer": "https://app.runwayml.com/",
            "sec-ch-ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        }

        resp = self.session.request(method, url, headers=headers, json=in_data)

        if self.debug:
            print(f"----------------------------------")
            print(f"url: {url}")
            print(f"Response: {resp.json()}")
            print(f"----------------------------------")

        resp.raise_for_status()
        if is_json:
            return resp.json()
        return resp
    