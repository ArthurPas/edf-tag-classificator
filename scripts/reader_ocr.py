from PIL import Image, ImageOps  # Importez ImageOps pour l'inversion
import re
import os
import torch
from transformers import TrOCRProcessor, VisionEncoderDecoderModel,AutoModel, AutoTokenizer





def do_ocr(folder_path):
    tag_pattern = re.compile(r'([0-9A-Z]?\s*[A-Z]{3}\s*\d{3}\s*[A-Z]{2}[0-9A-Z]?)', re.IGNORECASE)
    tokenizer = AutoTokenizer.from_pretrained('ucaslcl/GOT-OCR2_0', trust_remote_code=True)
    model = AutoModel.from_pretrained('ucaslcl/GOT-OCR2_0', trust_remote_code=True, low_cpu_mem_usage=True, device_map='cuda', use_safetensors=True, pad_token_id=tokenizer.eos_token_id)
    model = model.eval().cuda()
    total_images = 0
    tags_found = 0
    found_tags_list = []

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
                    found_tags_list.append((filename, found_tag))

                    
            except Exception as e:
                print(f"{filename}: Error during processing: {e}")

    build_report_file(found_tags_list, tags_found, total_images)
    return total_images, tags_found, found_tags_list


def build_report_file(found_list, tags_found, total_images):
    print("\nBuilding report file 'found_tags.txt'...")
    print(f"Total images processed: {total_images}")
    success_rate = (tags_found / total_images) * 100
    print(f"Success Rate: {success_rate:.2f}%")
    print(f"Total images with found tags: {len(found_list)}")
    print("Report file created.")
    with open("found_tags.txt", "w") as f:
        for img, tag in found_list:
            f.write(f"{img}: {tag}\n")

