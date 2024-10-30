from utils.uploads import Upload
from utils.client import Client
from utils.generate import Generate
from utils.authenticate import Authenticate
import time
import uuid, os, random

def get_current_token():
    token_file_path = "token.txt"
    
    if not os.path.isfile(token_file_path):
        with open(token_file_path, "w") as file:
            file.write("") 
        
    with open(token_file_path, "r") as file:
        token = file.read().strip()   
        
    return token

def update_team_id_to_config(client):
    auth = Authenticate(cfg)

    try:
        cfg['team_id'] = client.load_team_id(None)
    except Exception as e:
        print(f"Error loading team ID: {e}")
        cfg['token'] = auth.generate_token()
        try:
            cfg['team_id'] = client.load_team_id(None, cfg['token'])  # Retry
        except Exception as e:
            print(f"Error loading team ID again: {e}")
            return cfg 

    return cfg

def main(cfg):
    seconds = 10
    session_id = str(uuid.uuid4())

    client = Client(cfg)

    cfg = update_team_id_to_config(client)

    generate = Generate(cfg)

    directory = '/var/www/ai-generation/public/images'
    folders = [name for name in os.listdir(directory) if os.path.isdir(os.path.join(directory, name))]
    image_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp', '.heif', '.svg', '.ico', '.jfif'}

    for folder in folders:
        asset_group_id = client.create_assest_folder(folder)    
        time.sleep(random.randint(5, 15))

        folder_path = os.path.join(directory, folder)
        images = [
            os.path.join(folder_path, file)  # Construct the full path
            for file in os.listdir(folder_path)
            if os.path.splitext(file)[1].lower() in image_extensions
        ]

        # Print the full image paths found in the folder
        if images:
            for image_path in images:
                print(f'File path:  - {image_path}')
                cfg['image'] = image_path

                upload = Upload(cfg)
                image_url = upload.main()
                time.sleep(random.randint(5, 15))

                config = {
                    "token": cfg['token'],
                    "session_id": session_id,
                    "name":  f"Gen-3 Alpha Turbo {time.time()}",
                    "prompt": '',
                    "image_url": image_url,
                    "seconds": seconds,
                    "asset_group_id": asset_group_id,
                    "team_id": cfg['team_id'],
                }

                generate = Generate(config)
                generate.video(folder)
                time.sleep(random.randint(10, 30))
        else:
            print('  No images found.')



if __name__ == "__main__":
    cfg = {
        "token": get_current_token(),
        "wait": True,
        "debug": False,
        "proxy": None,
        "folder": "",
    }


    main(cfg)