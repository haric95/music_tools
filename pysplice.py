import os
import shutil as sh
import json
#point this to the root folder of the splice sample library
splice_root = f'{os.path.expanduser("~")}/Splice/sounds/packs'
#point this to a folder where the script will copy all the new files it finds
path_to_staging = ''
#point this to a json file inside of staging. If this is the first time running the script create a json file at this location that looks like the following
# {"files": [], "subdirs": {}}
# after the script has run once, this file will be updated so that only new files will be picked up on sucessive runs.
path_to_json = f'{path_to_staging}/map.json'

def describeFolder(path):
    folder_map = {}
    folder_map['files'] = []
    folder_map['subdirs'] = {}
    contents = os.listdir(path)
    for item in contents:
        if not os.path.isdir(f'{path}/{item}'):
            folder_map['files'].append(item)
        else:
            folder_map['subdirs'][item] = (describeFolder(f'{path}/{item}'))
    return folder_map

def getNewFiles(current_structure, new_structure):
    newFiles = []
    path = ""
    # path is just the json "path" so far.
    def compare(path, current_folder, new_folder):
        nonlocal newFiles
        print(new_folder['files'])
        for file in new_folder['files']:
            if file not in current_folder['files'] and file.split('.')[-1] == 'wav':
                newFiles.append(f'{path}/{file}')
        for folder in list(new_folder['subdirs'].keys()):
            if folder in current_folder['subdirs']:
                compare(f'{path}/{folder}', current_folder['subdirs'][folder], new_folder['subdirs'][folder])
            else:
                # probably a much cleaner way to do this than augmenting the current_folder object
                print(current_folder.keys())
                current_folder['subdirs'][folder] = {'files': [], 'subdirs': {}}
                print(current_folder)
                print(folder)
                compare(f'{path}/{folder}', current_folder['subdirs'][folder], new_folder['subdirs'][folder])
        print(newFiles)
    compare(path, current_structure, new_structure)
    return newFiles

def readJson(path):
    with open(path) as file:
        return json.load(file)

# Get folder layouts into dicts
current_folder = readJson(path_to_json)
new_folder = describeFolder(splice_root)

# find the new files and copy them to staging
new_files = getNewFiles(current_folder, new_folder)
for new_file in new_files:
    sh.copyfile(f'{splice_root}/{new_file}', f'{path_to_staging}/{new_file.split("/")[-1]}')

# update map file in staging
with open(path_to_json, 'w') as f:
    json.dump(new_folder, f)
