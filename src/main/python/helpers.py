import os

def get_icon(file_name):
    path = os.path.dirname(os.path.abspath(__file__))

    icon_path = os.path.join(path, '..', 'icons', file_name)

    print('icon_path', icon_path)

    return icon_path
