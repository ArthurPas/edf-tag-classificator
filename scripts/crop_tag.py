
import cv2
from ultralytics import YOLO
import os
import pytesseract
import cv2
import re
model_path = '/home/arthur-pascal/Perso/edf-tag-classificator/scripts/best.pt'
folder_path = 'test_original'
def crop_tag(image_path, model_path, output_dir, file_name):
    model = YOLO(model_path)
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("Image not found")
    results = model(image)
    os.makedirs(output_dir, exist_ok=True)
    i=0
    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())  # Get coordinates
            padding = 20  # Define padding
            x1 = max(0, x1 - padding)
            y1 = max(0, y1 - padding)
            x2 = min(image.shape[1], x2 + padding)
            y2 = min(image.shape[0], y2 + padding)
            cropped_image = image[y1:y2, x1:x2]  # Crop the image
            output_path = os.path.join(output_dir, f"{file_name}_{i}.png")
            cv2.imwrite(f"{output_path}.png", cropped_image) # Save the cropped image
            print(f"Cropped image saved to {output_path}")
            i += 1

def crop_folder(model_path, folder_path, output_dir='output'):
    image_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(('.png', '.jpg', '.jpeg'))]
    for img_path in image_files:
        try:
            crop_tag(img_path, model_path, output_dir=output_dir, file_name=os.path.splitext(os.path.basename(img_path))[0])
        except ValueError as e:
            print(e)

def do_ocr(matched_tags, regex_pattern, folder_path):
    image_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(('.png', '.jpg', '.jpeg'))]
    for img_path in image_files:
        text = pytesseract.image_to_string(img_path)
        clean_text = re.sub(r'[^a-zA-Z0-9_]', '', text).upper()
        match = re.search(regex_pattern, clean_text)
        if match:
            matched_tags.append((match.group(), img_path))
        else:
            not_matched_tags.append((clean_text, img_path))
def report(matched_tags, not_matched_tags):
    print("Report:")
    total_tags = len(matched_tags) + len(not_matched_tags)
    if total_tags > 0:
        success_rate = (len(matched_tags) / total_tags) * 100
        failure_rate = (len(not_matched_tags) / total_tags) * 100
        print(f"Success Rate: {success_rate:.2f}%")
        print(f"Failure Rate: {failure_rate:.2f}%")
    else:
        print("No tags processed.")

    print("\nExamples of Matched Tags:")
    for tag, path in matched_tags[:5]:
        print(f"Tag: {tag}, Image Path: {path}")

    print("\nExamples of Failed Tags:")
    for text, path in not_matched_tags:
        print(f"Extracted Text: {text}, Image Path: {path}")
def enlarge_image(input_path, output_path, scale=2):
    image = cv2.imread(input_path)
    if image is None:
        raise ValueError("Image not found")
    width = int(image.shape[1] * scale)
    height = int(image.shape[0] * scale)
    enlarged_image = cv2.resize(image, (width, height), interpolation=cv2.INTER_CUBIC)
    cv2.imwrite(output_path, enlarged_image)
    print(f"Enlarged image saved to {output_path}")

def enlarge_folder(input_dir, output_dir, scale=5):
    os.makedirs(output_dir, exist_ok=True)
    image_files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]
    for img_path in image_files:
        file_name = os.path.basename(img_path)
        output_path = os.path.join(output_dir, file_name)
        try:
            enlarge_image(img_path, output_path, scale)
        except ValueError as e:
            print(e)

matched_tags = []
not_matched_tags = []
folder_path = 'test_original_cropped/enlarged'
regex_pattern = r"([A-Z0-9]{9})"
# do_ocr(matched_tags, regex_pattern, folder_path)
# report(matched_tags, not_matched_tags)
