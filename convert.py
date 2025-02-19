#!/usr/bin/env python3

import xml.etree.ElementTree as ET
from PIL import Image
import os

def createAnnotationPascalVocTree(folder, basename, path, width, height, unmasked_mode=False):
    annotation = ET.Element('annotation')
    ET.SubElement(annotation, 'folder').text = folder
    ET.SubElement(annotation, 'filename').text = basename
    ET.SubElement(annotation, 'path').text = path

    source = ET.SubElement(annotation, 'source')

    if not unmasked_mode:
        ET.SubElement(source, 'database').text = 'WIDER'
    else:
        ET.SubElement(source, 'database').text = 'WIDER_unmasked'

    size = ET.SubElement(annotation, 'size')
    ET.SubElement(size, 'width').text = width
    ET.SubElement(size, 'height').text = height
    ET.SubElement(size, 'depth').text = '3'

    ET.SubElement(annotation, 'segmented').text = '0'

    return ET.ElementTree(annotation)

def createObjectPascalVocTree(xmin, ymin, xmax, ymax, unmasked_mode=False):
    obj = ET.Element('object')
    if not unmasked_mode:
        ET.SubElement(obj, 'name').text = 'face'
    else:
        ET.SubElement(obj, 'name').text = 'unmasked_face'
    ET.SubElement(obj, 'pose').text = 'Unspecified'
    ET.SubElement(obj, 'truncated').text = '0'
    ET.SubElement(obj, 'difficult').text = '0'

    bndbox = ET.SubElement(obj, 'bndbox')
    ET.SubElement(bndbox, 'xmin').text = xmin
    ET.SubElement(bndbox, 'ymin').text = ymin
    ET.SubElement(bndbox, 'xmax').text = xmax
    ET.SubElement(bndbox, 'ymax').text = ymax

    return ET.ElementTree(obj)

def parseImFilename(imFilename, imPath):
    im = Image.open(os.path.join(imPath, imFilename))
            
    folder, basename = imFilename.split('/')
    width, height = im.size

    return folder, basename, imFilename, str(width), str(height)

def convertWFAnnotations(annotationsPath, targetPath, imPath, unmasked_mode=False, skip_Surgeons=False):
    ann = None
    basename = ''
    with open(annotationsPath) as f:
        while True:
            imFilename = f.readline().strip()
            if imFilename:
                folder, basename, path, width, height = parseImFilename(imFilename, imPath)
                ann = createAnnotationPascalVocTree(folder, basename, os.path.join(imPath, path), width, height, unmasked_mode)
                nbBndboxes = f.readline()
                
                i = 0
                while i < int(nbBndboxes):
                    i = i + 1
                    x1, y1, w, h, _, _, _, _, _, _ = [int(i) for i in f.readline().split()]

                    ann.getroot().append(createObjectPascalVocTree(str(x1), str(y1), str(x1 + w), str(y1 + h), unmasked_mode).getroot())
                
                if not os.path.exists(targetPath):
                     os.makedirs(targetPath)
                annFilename = os.path.join(targetPath, basename.replace('.jpg','.xml'))

                if unmasked_mode and folder == "30--Surgeons" and skip_Surgeons:
                    continue

                ann.write(annFilename)
                print('{} => {}'.format(basename, annFilename))
            else:
                break 
    f.close()


if __name__ == '__main__':
    """
    if skip_Surgeons == 1 than wider_val can be used as true validation, else wider_val used only for test face detection.
    """
    import argparse

    PARSER = argparse.ArgumentParser()
    PARSER.add_argument('-ap', '--annotations-path', help='the annotations file path. ie:"./wider_face_split/wider_face_train_bbx_gt.txt".')
    PARSER.add_argument('-tp', '--target-path', help='the target directory path where XML files will be copied.')
    PARSER.add_argument('-ip', '--images-path', help='the images directory path. ie:"./WIDER_train/images"')
    PARSER.add_argument('--unmasked_mode', help='create xmls for unmasked_mode', default=0, type=int)
    PARSER.add_argument('--skip_Surgeons', help='skip Surgeons class', default=0, type=int)

    ARGS = vars(PARSER.parse_args())
    
    convertWFAnnotations(ARGS['annotations_path'], ARGS['target_path'], ARGS['images_path'], bool(ARGS['unmasked_mode'])
                         , bool(ARGS['skip_Surgeons']))

