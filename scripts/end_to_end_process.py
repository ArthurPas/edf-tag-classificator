from crop_tag import crop_folder
from reader_ocr import do_ocr
from storage import initialize_db, store_tag,convert_db_to_js
import os
import re

def end_to_end_process(model_path, input_folder, cropped_output_dir='../data/cropped_output'):
    crop_folder(model_path, input_folder, output_dir=cropped_output_dir)
    print("Cropping completed. Cropped images are saved in:", cropped_output_dir)
    total_images, tags_found, found_tags_list = do_ocr(cropped_output_dir)
    print(f"Total images processed: {total_images}")
    print(f"Total tags found: {tags_found}")
    print(f"---- ")
    print("Storing tags in database...")
    for matches in found_tags_list:
        initialize_db()
        filename = matches[0]
        name, ext = os.path.splitext(filename)
        new_name = re.sub(r'_\d+$', '', name) + ext
        store_tag(new_name, matches[1])
    print("Tags stored successfully.")
    print("Converting database to JavaScript file...")
    convert_db_to_js()

if __name__ == "__main__":
    model_path = './scripts/best.pt'
    input_folder = './data/images'
    end_to_end_process(model_path, input_folder)

