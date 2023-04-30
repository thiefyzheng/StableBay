import os
import json
import sys
import bencodepy
import hashlib
import base64
import random
import time

uploads_path = '/home/stablebay/uploads'

# List of jokes about magnet links
jokes = [
    "Why did the magnet link break up with the torrent? Because it was attracted to a different peer!",
    "Why did the pirate download a magnet link? He wanted to steal some attraction!",
    "What do you call a magnet link that doesn't work? A broken torrent relationship!",
    "Why do magnets prefer torrent files? Because they're always seeded!",
    "Why did the torrent marry the magnet link? Because they had great chemistry!",
    "Why don't magnets get along with BitTorrent? Because they have conflicting protocols!",
    "What did the magnet link say to the torrent file? Let's get together and download some content!",
]

while True:
    # Iterate through all subdirectories in uploads directory
    for model_name in os.listdir(uploads_path):
        model_dir = os.path.join(uploads_path, model_name)
        if not os.path.isdir(model_dir):
            continue

        # Check if model has a torrent file
        torrent_file = None
        for file_name in os.listdir(model_dir):
            if file_name.endswith('.torrent'):
                torrent_file = os.path.join(model_dir, file_name)
                break
        if not torrent_file:
            continue

        # Load model info from JSON file
        json_path = os.path.join(model_dir, 'info.json')
        with open(json_path, 'r') as f:
            model_info = json.load(f)

        # Extract magnet link from torrent file
        with open(torrent_file, 'rb') as f:
            metadata = bencodepy.decode(f.read())
            subj = metadata[b'info']
            hashcontents = bencodepy.encode(subj)
            digest = hashlib.sha1(hashcontents).digest()
            b32hash = base64.b32encode(digest).decode()
            magnet_link = 'magnet:?' \
                          + 'xt=urn:btih:' + b32hash \
                          + '&dn=' + metadata[b'info'][b'name'].decode() \
                          + '&tr=' + metadata[b'announce'].decode() \
                          + '&xl=' + str(metadata[b'info'][b'length'])

        # Update model info with magnet link and save to JSON file
        model_info['magnet_link'] = magnet_link
        with open(json_path, 'w') as f:
            json.dump(model_info, f)

    # Print a random joke about magnet links
    print(random.choice(jokes))
    # Wait for one minute before running again
    time.sleep(60)
