import pytesseract
from pytesseract import Output
from PIL import Image
import cv2
import re
import os

img_path2 = 'tag_cropper/image.png'
img_path3 = 'tag_cropper/image2.png'
img_path4 = 'tag_cropper/image3.png'

matched_tags = []
regex_pattern = r"^(\d[A-Z]{4}\d{2})"
folder_path = '/tag_cropper/data/train/images'
image_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(('.png', '.jpg', '.jpeg'))]
for img_path in image_files:
    text = pytesseract.image_to_string(img_path, lang='eng').replace(" ", "").upper()
    match = re.search(regex_pattern, text)
    if match:
        matched_tags.append(match.group())

print("Matched Tags List:", matched_tags)