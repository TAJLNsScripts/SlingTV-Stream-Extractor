# SlingTV-Stream-Extractor
Extracts stream url and drm keys from chosen SlingTV live channel

Prerequisites:
  - SlingTV account
  - Non-blocked USA vpn
  - Pywidevine cdm file in .wvd format

Usage:
  - Login to SlingTV in your browser
  - Go to local storage and copy the value of variable "persist:root"
  - Make a file called "user.txt" next to slingtv.py and save the copied string into it
  - Set the path to your .wvd file at the top of the slingtv.py file
  - pip install -r requirements.txt
  - python slingtv.py
