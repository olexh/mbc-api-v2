
# r = requests.head("https://ipfs.io/ipfs/QmbaMuNB4UsCj11sLTyydag8911uLGqWzarKi7wuAC6uEk")

# print(r.headers["Content-Type"])
# print(r.headers["X-Ipfs-DataSize"])


from server.sync import sync_ipfs_cache

sync_ipfs_cache()


# import requests

# def get_ipfs_data(ipfs):
#     ALLOWED_MIME = ["application/json"]
#     MAX_DATA_SIZE = 100000

#     try:
#         endpoint = f"https://ipfs.io/ipfs/{ipfs}"
#         content = None
#         mime = None

#         head = requests.head(endpoint, timeout=10)

#         if head.status_code == 200:
#             if head.headers["Content-Type"] in ALLOWED_MIME:
#                 if int(head.headers["X-Ipfs-DataSize"]) < MAX_DATA_SIZE:
#                     r = requests.get(endpoint, timeout=10)

#                     mime = head.headers["Content-Type"]
#                     content = r.text

#         return True, content, mime

#     except:
#         return False, None, None

# print(get_ipfs_data("QmbaMuNB4UsCj11sLTyydag8911uLGqWzarKi7wuAC6uEk"))
