import random
import time
import requests, os
from utils.client import Client

class Generate(Client):
    def __init__(self, ctx):
        super().__init__(ctx)
        self.name = ctx.get('name')
        self.prompt = ctx.get('prompt')
        self.image = ctx.get('image_url')
        self.seconds = ctx.get('seconds')
        self.asset_group_id = ctx.get('asset_group_id')
        self.team_id = ctx.get('team_id')
        self.expiration = time.time() + 3600 
    
    def video(self, folder):
        seed = random.randint(0, 999999999) + 2000000000
        credentials = {
            "taskType": "gen3a_turbo",
            "internal": False,
            "options": {
                "name": self.name,
                "seconds": self.seconds,
                "text_prompt": self.prompt,
                "seed": seed,
                "exploreMode": True,
                "watermark": False,
                "enhance_prompt": True,
                "flip": True,
                "keyframes": [
                    {
                        "image": self.image,
                        "timestamp": 0
                    }
                ],
                "assetGroupId": self.asset_group_id
            },
            "asTeamId": self.team_id,
            "sessionId": self.session_id
        }

        task = self.do(None, "POST", 'tasks', credentials, False)

        if task.status_code == 200:
            task = task.json()
            task_id = task["task"]["id"]

            url = f"tasks/{task_id}?asTeamId={self.team_id}"

            while True:
                response = self.do(None, "GET", url, {"asTeamId": self.team_id}, False)
                
                if response.status_code == 200:
                    data = response.json()
                    task_status = data["task"]["status"]
                    
                    if task_status == "SUCCEEDED":
                        print("Task completed successfully!")

                        if self.debug:
                            print(data['task'])
    
                        self.download(data['task']['artifacts'][0]['id'], self.name, folder)
    
                        break
                    else:
                        print(f"Task status: {task_status}. Waiting for completion...")
                else:
                    print(f"Request failed with status {response.status_code}. Retrying...")
                time.sleep(10) 


        else:
            print("Generate failed:", response.status_code)

    def download(self, video_id, file_name, folder_name):

        download_path = f"/var/www/ai-generation/public/processed_images/{folder_name}"
        # Check if the folder exists; if not, create it
        if not os.path.exists(download_path):
            os.makedirs(download_path)
            print(f"Folder '{folder_name}' created at {download_path}.")
        else:
            print(f"Folder '{folder_name}' already exists, skipping creation.")
        
        if not file_name.endswith('.mp4'):
            file_name += '.mp4'

        file_path = os.path.join(download_path, file_name)
    

        url =  f"assets/{video_id}/generate_download_link"
        response = self.do(None, "POST", url, {"filename": file_name}, False)

        if response.status_code == 200:
            data = response.json()
            response = requests.get(data["url"], stream=True)

            with open(file_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            print(f"Video downloaded successfully as {file_name}")
        else:
            print(f"Request download failed with status {response.status_code}.")
