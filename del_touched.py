import os
import shutil

for f in os.listdir("users"):
    try:
        os.remove("users/" + f + "/touched")
    except:
        pass
    for ff in os.listdir("users/" + f):
        if os.path.isdir("users/" + f + "/" + ff):
            shutil.rmtree("users/" + f + "/" + ff)

print("Done deleting touched files and mails")
