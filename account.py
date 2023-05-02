import os
import json

TORRENTS_DIR = "/home/stablebay/uploads/"
def get_user_torrents(username):
    torrents = []
    for dirname in os.listdir(TORRENTS_DIR):
        if not os.path.isdir(os.path.join(TORRENTS_DIR, dirname)):
            continue
        torrent_info_path = os.path.join(TORRENTS_DIR, dirname, "info.json")
        if not os.path.exists(torrent_info_path):
            continue
        with open(torrent_info_path) as f:
            info = json.load(f)
        if info.get("uploaded_by") == username:
            torrent = {
                "name": info.get("name", dirname),
                "description": info.get("description", ""),
                "file_path": os.path.join(TORRENTS_DIR, dirname, f"{dirname}.torrent"),
                "tags": info.get("tags", []),
                "uploaded_by": info.get("uploaded_by", ""),
                "upload_date": info.get("upload_date", ""),
            }
            torrents.append(torrent)
    return torrents
