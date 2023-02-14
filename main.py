import json
import os
import random
import drivefunctions as drive

if os.path.exists("yha/saved.jpg"): os.remove("yha/saved.jpg")

drive.init_auth()

print(json.dumps(drive.get_file_list(trashed=True), indent=4))