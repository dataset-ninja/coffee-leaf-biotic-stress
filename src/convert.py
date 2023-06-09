import zipfile, os, sys, random, csv
import supervisely as sly
import numpy as np
import gdown
from supervisely.io.fs import get_file_name, get_file_name_with_ext
from cv2 import connectedComponents
from typing import Literal
from pathlib import Path


root_source_dir = str(Path(sys.argv[0]).parents[1])
sly.logger.info(f"Root source directory: {root_source_dir}")
sys.path.append(root_source_dir)

datasets = ["Train", "Val", "Test"]

sample_img_count = {"Train": 400, "Val": 50, "Test": 50}

# project_name = "Coffee Leaf Biotic Stress"
work_dir = "coffee_data"
coffee_url = "https://docs.google.com/uc?id=15YHebAGrx1Vhv8-naave-R5o3Uo70jsm"

arch_name = "coffee-datasets.zip"
images_folder = "segmentation/images"
anns_folder = "segmentation/annotations"
symptom_tag_file = "leaf/dataset.csv"
ann_ext = "_mask.png"

batch_size = 30

obj_classes_names = ["symptom", "leaf"]
symptom_idx = 0
leaf_idx = 1
obj_class_color_idxs = [255, 176]
symptom_color = [255, 0, 0]
leaf_color = [0, 176, 0]

obj_class_leaf = sly.ObjClass(obj_classes_names[1], sly.Bitmap, color=leaf_color)
obj_class_symptom = sly.ObjClass(obj_classes_names[0], sly.Bitmap, color=symptom_color)

obj_classes = [obj_class_symptom, obj_class_leaf]
obj_class_collection = sly.ObjClassCollection(obj_classes)

tags_data = {}
tag_names = ["predominant_stress", "miner", "rust", "phoma", "cercospora", "severity"]
tag_metas = []
for tag_name in tag_names:
    tag_meta = sly.TagMeta(tag_name, sly.TagValueType.ANY_NUMBER)
    tag_metas.append(tag_meta)

tag_meta_collection = sly.TagMetaCollection(tag_metas)

meta = sly.ProjectMeta(obj_classes=obj_class_collection, tag_metas=tag_meta_collection)

sly.fs.mkdir(work_dir)
archive_path = os.path.join(work_dir, arch_name)


def convert_and_upload_supervisely_project(
    api: sly.Api, workspace_id: int, project_name: str
) -> sly.ProjectInfo:
    download_and_extract()

    coffee_data_path = os.path.join(work_dir, sly.fs.get_file_name(arch_name))
    tags_file = os.path.join(coffee_data_path, symptom_tag_file)
    read_csv(tags_file)

    new_project = api.project.create(workspace_id, project_name, change_name_if_conflict=True)
    api.project.update_meta(new_project.id, meta.to_json())

    for ds in datasets:
        new_dataset = api.dataset.create(new_project.id, ds, change_name_if_conflict=True)

        curr_img_path = os.path.join(coffee_data_path, images_folder, ds.lower())
        curr_ann_path = os.path.join(coffee_data_path, anns_folder, ds.lower())

        curr_img_cnt = sample_img_count[ds]
        sample_img_path = random.sample(os.listdir(curr_img_path), curr_img_cnt)

        progress = sly.Progress("Create dataset {}".format(ds), curr_img_cnt, sly.logger)
        for img_batch in sly.batched(sample_img_path, batch_size=batch_size):
            img_pathes = [os.path.join(curr_img_path, name) for name in img_batch]
            ann_pathes = [
                os.path.join(curr_ann_path, get_file_name(name) + ann_ext) for name in img_batch
            ]

            anns = [create_annotation(ann_path) for ann_path in ann_pathes]

            img_infos = api.image.upload_paths(new_dataset.id, img_batch, img_pathes)
            img_ids = [im_info.id for im_info in img_infos]
            api.annotation.upload_anns(img_ids, anns)
            progress.iters_done_report(len(img_batch))

    return new_project


def download_and_extract():
    gdown.download(coffee_url, archive_path, quiet=False)
    if zipfile.is_zipfile(archive_path):
        with zipfile.ZipFile(archive_path, "r") as archive:
            archive.extractall(work_dir)
    else:
        sly.logger.warn("Archive cannot be unpacked {}".format(arch_name))


def read_csv(file_path):
    with open(file_path, newline="") as File:
        reader = csv.reader(File)
        for row in reader:
            tags_data[row[0]] = row[1:]


def get_tags(file_id):
    curr_tags = tags_data[file_id]
    tags = []
    for idx, curr_tag_val in enumerate(curr_tags):
        if int(curr_tag_val) == 0:
            continue

        tag = sly.Tag(tag_metas[idx], value=int(curr_tag_val))
        tags.append(tag)

    return sly.TagCollection(tags)


def create_annotation(ann_path):
    ann_np_leaf = sly.image.read(ann_path)[:, :, leaf_idx]
    mask_leaf = ann_np_leaf == obj_class_color_idxs[leaf_idx]
    bitmap = sly.Bitmap(mask_leaf)
    label = sly.Label(bitmap, obj_classes[leaf_idx])
    labels = [label]

    ann_np_symptom = sly.image.read(ann_path)[:, :, symptom_idx]
    mask_symptom = ann_np_symptom == obj_class_color_idxs[symptom_idx]
    if len(np.unique(mask_symptom)) != 1:
        ret, curr_mask = connectedComponents(mask_symptom.astype("uint8"), connectivity=8)
        for i in range(1, ret):
            obj_mask = curr_mask == i
            bitmap = sly.Bitmap(obj_mask)
            label = sly.Label(bitmap, obj_classes[symptom_idx])
            labels.append(label)

    file_id = get_file_name_with_ext(ann_path).split(ann_ext)[0]
    tags = get_tags(file_id)

    return sly.Annotation(
        img_size=(ann_np_leaf.shape[0], ann_np_leaf.shape[1]), labels=labels, img_tags=tags
    )


# def to_supervisely(api: sly.Api, workspace_id):
#     download_and_extract()

#     coffee_data_path = os.path.join(work_dir, sly.fs.get_file_name(arch_name))
#     tags_file = os.path.join(coffee_data_path, symptom_tag_file)
#     read_csv(tags_file)

#     new_project = api.project.create(workspace_id, project_name, change_name_if_conflict=True)
#     api.project.update_meta(new_project.id, meta.to_json())

#     for ds in datasets:
#         new_dataset = api.dataset.create(new_project.id, ds, change_name_if_conflict=True)

#         curr_img_path = os.path.join(coffee_data_path, images_folder, ds.lower())
#         curr_ann_path = os.path.join(coffee_data_path, anns_folder, ds.lower())

#         curr_img_cnt = sample_img_count[ds]
#         sample_img_path = random.sample(os.listdir(curr_img_path), curr_img_cnt)

#         progress = sly.Progress("Create dataset {}".format(ds), curr_img_cnt, sly.logger)
#         for img_batch in sly.batched(sample_img_path, batch_size=batch_size):
#             img_pathes = [os.path.join(curr_img_path, name) for name in img_batch]
#             ann_pathes = [
#                 os.path.join(curr_ann_path, get_file_name(name) + ann_ext) for name in img_batch
#             ]

#             anns = [create_annotation(ann_path) for ann_path in ann_pathes]

#             img_infos = api.image.upload_paths(new_dataset.id, img_batch, img_pathes)
#             img_ids = [im_info.id for im_info in img_infos]
#             api.annotation.upload_anns(img_ids, anns)
#             progress.iters_done_report(len(img_batch))

#     return new_project


def from_supervisely(
    input_path: str, output_path: str = None, to_format: Literal["dir", "tar", "both"] = "both"
) -> str:
    raise NotImplementedError("Converter will be implemented soon")
