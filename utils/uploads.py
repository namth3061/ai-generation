import hashlib
import time
from contextlib import contextmanager
from pathlib import Path
from utils.client import Client

class Upload(Client):
    def __init__(self, ctx):
        super().__init__(ctx)
        self.image = ctx.get('image')
        self.wait = ctx.get('wait')
        self.debug = ctx.get('debug')
        self.proxy = ctx.get('proxy')
        self.folder = ctx.get('folder')
        self.team_id = ctx.get('team_id')
        self.expiration = time.time() + 3600 

    def main(self):
        if self.image:
            with open(self.image, "rb") as f:
                data = f.read()
            file_name = Path(self.image).name
            image_url, asset_id = self.upload(None, file_name, data)
            try:
                print(f"Uploaded Image {file_name} to S3.")
                return image_url
            finally:
                self.delete(None, asset_id)

        return

    def upload(self, ctx, name, data):
        ext = Path(name).suffix.lstrip('.')
        etag = hashlib.md5(data).hexdigest()

        types = ["DATASET", "DATASET_PREVIEW"]
        image_url = None
        upload_id, preview_upload_id = None, None

        for t in types:
            upload_req = {
                "filename": name,
                "numberOfParts": 1,
                "type": t,
            }
            upload_resp = super().do(ctx, "POST", "uploads", upload_req)

            if not upload_resp.get("uploadUrls"):
                raise ValueError("runway: no upload urls returned")
            
            upload_url = upload_resp["uploadUrls"][0]

            # Upload file
            headers = {"Content-Type": f"image/{ext}"}
            self.session.put(upload_url, data=data, headers=headers)

            # Complete upload
            complete_url = f"uploads/{upload_resp['id']}/complete"
            complete_req = {
                "parts": [{"PartNumber": 1, "ETag": etag}]
            }
            complete_resp = self.do(ctx, "POST", complete_url, complete_req)

            if not complete_resp.get("url"):
                raise ValueError(f"runway: empty image url for type {t}")

            image_url = complete_resp["url"]
            if t == "DATASET":
                upload_id = upload_resp["id"]
            elif t == "DATASET_PREVIEW":
                preview_upload_id = upload_resp["id"]

        # Create dataset
        dataset_req = {
            "fileCount": 1,
            "name": name,
            "uploadId": upload_id,
            "previewUploadIds": [
                preview_upload_id
            ],
            "metadata": {
                "size": {
                    "width": 3200,
                    "height": 1800
                }
            },
            "type": {
                "name": "image",
                "type": "image",
                "isDirectory": False
            },
            "asTeamId": self.team_id
        }
        dataset_resp = self.do(ctx, "POST", "datasets", dataset_req)

        if not dataset_resp["dataset"].get("url") or not dataset_resp["dataset"].get("id"):
            raise ValueError("runway: empty dataset url or id")

        return image_url, dataset_resp["dataset"]["id"]

    def delete(self, ctx, asset_id):
        path = f"assets/{asset_id}"
        req = {"asTeamId": self.team_id}
        resp = self.do(ctx, "DELETE", path, req)
        if not resp.get("success"):
            raise ValueError(f"runway: couldn't delete asset {asset_id}")

    @contextmanager
    def lock(self):
        yield

