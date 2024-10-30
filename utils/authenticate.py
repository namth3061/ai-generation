from utils.client import Client
import os
from dotenv import load_dotenv

class Authenticate(Client):
    def __init__(self, ctx):
        super().__init__(ctx)
        self.token = ctx.get('token')


    def generate_token(self):
        load_dotenv()

        credentials = {
            "email": os.getenv("EMAIL"),
            "machineId": None,
            "password": os.getenv("PASSWORD") 
        }

        response = self.do(None, "POST", "login", credentials, False)
        
        if response.status_code == 200:
            token = response.json().get("token")  
            if token:
                with open("token.txt", "w") as file:
                    file.write(token)

                print("Token generated.")       

                return token
            else:
                print("Token not found in the response.")
        else:
            raise ValueError(f" {response.status_code} runway: Login failed")


