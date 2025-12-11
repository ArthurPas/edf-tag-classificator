from crop_tag import crop_folder
from reader_ocr import do_ocr
def end_to_end_process(model_path, input_folder, cropped_output_dir='cropped_output'):
    crop_folder(model_path, input_folder, output_dir=cropped_output_dir)
    print("Cropping completed. Cropped images are saved in:", cropped_output_dir)
    total_images, tags_found, found_tags_list = do_ocr(cropped_output_dir)

model_path = './best.pt'
input_folder = '../data/end_to_end'
end_to_end_process(model_path, input_folder)

    