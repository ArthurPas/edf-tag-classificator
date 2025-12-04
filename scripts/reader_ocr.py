from PIL import Image, ImageOps  # Importez ImageOps pour l'inversion
import re
import os
import torch
from transformers import TrOCRProcessor, VisionEncoderDecoderModel,AutoModel, AutoTokenizer
# --- Configuration ---
folder_path = '/home/arthur-pascal/Perso/edf-tag-classificator/cropped_output'

tag_pattern = re.compile(r'([0-9A-Z]?\s*[A-Z]{3}\s*\d{3}\s*[A-Z]{2}[0-9A-Z]?)', re.IGNORECASE)

total_images = 0
tags_found = 0
found_tags_list = []

tokenizer = AutoTokenizer.from_pretrained('ucaslcl/GOT-OCR2_0', trust_remote_code=True)
model = AutoModel.from_pretrained('ucaslcl/GOT-OCR2_0', trust_remote_code=True, low_cpu_mem_usage=True, device_map='cuda', use_safetensors=True, pad_token_id=tokenizer.eos_token_id)
model = model.eval().cuda()


for filename in os.listdir(folder_path):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        total_images += 1
        image_path = os.path.join(folder_path, filename)
        
        try:
            res = model.chat(tokenizer, image_path, ocr_type='ocr')
            res = res.replace('\n', ' ').replace('\r', ' ').replace('  ', ' ').replace(' ', '')
            match = tag_pattern.search(res)
            if match:
                found_tag = match.group(1)
                tags_found += 1
                print(f"{filename}: Found Tag: {found_tag}")
                found_tags_list.append((filename, found_tag))
            else:
                print(f"{filename}: No matching tag found.")
                
        except Exception as e:
            print(f"{filename}: Error during processing: {e}")

# --- Statistiques ---
if total_images > 0:
    print(f"\nProcessed {total_images} images.")
    print(f"Found tags in {tags_found} images.")
    print(f"Success rate: {tags_found/total_images*100:.2f}%")
    if tags_found > 0:
        print("\nFound tags and associated images:")
        for img, tag in found_tags_list:
            print(f"{img}: {tag}")
else:
    print("\nNo images found to process.")