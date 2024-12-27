# -*- coding: utf-8 -*-

#
# Title: 把result里面的灌注影像都复制出来发给医生
# Author:
# Refer:
# Repo:
# Date: 2024-07-28
#


import os
import shutil
from workbase.dectpe.core.alpha import perfusion_image_list


# 批量复制灌注图像文件
def run_copy_perfusion_images():
    # 使用os.listdir 列出目录中的所有患者
    case_dirpath = r'E:\cjfh\dectpe\raw\allcases'
    case_list = [f'case{str(i).zfill(3)}' for i in range(101, 245)]
    for caseid in case_list:
        result_path = os.path.join(case_dirpath, caseid, "result_r231")
        names = perfusion_image_list(result_path)
        # 复制每一个文件
        for name in names:
            source_path = os.path.join(case_dirpath, caseid, "result_r231", name)
            destination_path = os.path.join(r"D:\download\allcases_perfusion", caseid)
            if not os.path.exists(destination_path):
                os.makedirs(destination_path)
            shutil.copy(source_path, destination_path)

