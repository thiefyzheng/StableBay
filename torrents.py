import os
import json

TORRENTS_DIR = "/home/stablebay/PycharmProjects/StableBay/uploads/"

def get_torrents():
    torrents = []
    for dirname in os.listdir(TORRENTS_DIR):
        if not os.path.isdir(os.path.join(TORRENTS_DIR, dirname)):
            continue
        torrent_info_path = os.path.join(TORRENTS_DIR, dirname, "info.json")
        if not os.path.exists(torrent_info_path):
            continue
        with open(torrent_info_path) as f:
            info = json.load(f)
        magnet_link = info.get("magnet_link", "")
        torrent = {
            "name": info.get("name", dirname),
            "description": info.get("description", ""),
            "file_path": os.path.join(TORRENTS_DIR, dirname, f"{dirname}.torrent"),
            "tags": info.get("tags", []),
            "uploaded_by": info.get("uploaded_by", ""),
            "upload_date": info.get("upload_date", ""),
            "magnet_link": magnet_link,
        }
        if magnet_link:
            torrent["magnet_button"] = f'<a href="{magnet_link}" target="_blank" class="btn btn-primary">Magnet</a>'
        else:
            torrent["magnet_button"] = ""
        torrents.append(torrent)
    return torrents
