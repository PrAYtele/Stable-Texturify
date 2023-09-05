import os
import glob

def delete_files(file_extensions):
    for file_ext in file_extensions:
        for file in glob.glob(f"./*.{file_ext}"):
            try:
                os.remove(file)
                print(f"成功删除文件：{file}")
            except Exception as e:
                print(f"删除文件时出错：{file}，错误：{e}")

if __name__ == "__main__":
    file_extensions = ["png", "jpg"]
    delete_files(file_extensions)