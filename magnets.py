import bencodepy
import hashlib
import base64
from typing import BinaryIO

def get_magnet_link(file: BinaryIO) -> str:
    metadata = bencodepy.decode_from_file(file)
    subj = metadata[b'info']
    hashcontents = bencodepy.encode(subj)
    digest = hashlib.sha1(hashcontents).digest()
    b32hash = base64.b32encode(digest).decode()
    return 'magnet:?'\
             + 'xt=urn:btih:' + b32hash\
             + '&dn=' + metadata[b'info'][b'name'].decode()\
             + '&tr=' + metadata[b'announce'].decode()\
             + '&xl=' + str(metadata[b'info'][b'length'])

if __name__ == "__main__":
    with open(sys.argv[1], 'rb') as f:
        magnet = make_magnet_from_file(f)
    print(magnet)
