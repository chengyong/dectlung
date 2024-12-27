# -*- coding: utf-8 -*-

#
# Title: 分割CT肺部并制作掩码
# Author:
# Refer:
# Repo:
# Date: 2024-05-09
#


import os
import glob
import numpy as np
import pandas as pd
import pydicom
from skimage import exposure
from scipy.ndimage import label
from skimage.filters import threshold_otsu
from skimage.measure import label, regionprops
from skimage.segmentation import clear_border
import matplotlib.pyplot as plt


# 读取DICOM文件
# https://blog.csdn.net/qq_42982824/article/details/135911016
def get_ct_mask(ct_file):
    dicom_data = pydicom.dcmread(ct_file)

    # 获取CT图像数据
    ct_image = dicom_data.pixel_array
    b = ct_image
    mask = b < 600
    #plt.figure(1)
    #plt.imshow(mask, cmap='gray')

    # 将图像中相连的区域打上相同的标签，将标签保持在两个最大的区域
    cleared = clear_border(mask)
    #plt.figure(2)
    #plt.imshow(mask, cmap='gray')

    label_image = label(cleared)
    #plt.figure(3)
    #plt.imshow(label_image, cmap='gray')
    #plt.imshow(cleared,cmap='gray')

    areas = [r.area for r in regionprops(label_image)]
    areas.sort()
    if len(areas) > 2:
        for region in regionprops(label_image):
            if region.area < areas[-2]:
                for coordinates in region.coords:
                    label_image[coordinates[0], coordinates[1]] = 0
    lung_mask = label_image > 0
    #plt.figure(4)
    #plt.imshow(mask, cmap=plt.cm.bone)
    # plt.show()

    # 左肺和右肺分开考虑
    left_lung_mask = np.zeros_like(lung_mask)
    right_lung_mask = np.zeros_like(lung_mask)

    for region in regionprops(label_image):
        if region.area == areas[-1]:    # 最大的区域为右肺
            for coordinates in region.coords:
                right_lung_mask[coordinates[0], coordinates[1]] = 1
        elif region.area == areas[-2]:  # 第二大的区域为左肺
            for coordinates in region.coords:
                left_lung_mask[coordinates[0], coordinates[1]] = 1
    return lung_mask, right_lung_mask, left_lung_mask


def run01_generate_ct_mask():
    ct_file = r'E:\cjfh\dectpe\raw\typical\case2\CT\IMG-0002-00137.dcm'
    lung_mask, right_lung_mask, left_lung_mask = get_ct_mask(ct_file)
    plt.figure()
    plt.imshow(lung_mask, cmap=plt.cm.bone)
    plt.show()


# 评估双肺的灌注情况并显示
def extract_lung_perfusion(pbv_file, lung_mask, right_lung_mask, left_lung_mask, adaptive=False):
    # 读取PVB图像
    pbv_data = pydicom.dcmread(pbv_file)
    pbv_image = pbv_data.pixel_array

    # 归一化PVB图像到0-1范围
    pvb_normalized = exposure.rescale_intensity(pbv_image, out_range=(0, 1))

    #对掩码进行统计
    lung_count = np.sum(lung_mask)
    right_lung_count = np.sum(right_lung_mask)
    left_lung_count = np.sum(left_lung_mask)

    # 应用肺掩码提取功能图像
    lung_perfusion = pvb_normalized * lung_mask
    right_lung_perfusion = pvb_normalized * right_lung_mask
    left_lung_perfusion = pvb_normalized * left_lung_mask

    # 定义灌注状态的阈值
    if adaptive:
        # 应用Otsu's方法确定最优阈值
        threshold = threshold_otsu(lung_perfusion)
        normal_threshold = threshold * 2.2   # 正常阈值为最优阈值的2.2倍
        defect_threshold = threshold * 1.85  # 缺损阈值为最优阈值的1.85倍
    else:
        normal_threshold = 0.55
        defect_threshold = 0.45
    print(normal_threshold)
    print(defect_threshold)

    # 创建彩色灌注图像
    lung_perfusion_color = np.zeros((pbv_image.shape[0], pbv_image.shape[1], 3))
    right_lung_perfusion_color = np.zeros((pbv_image.shape[0], pbv_image.shape[1], 3))
    left_lung_perfusion_color = np.zeros((pbv_image.shape[0], pbv_image.shape[1], 3))

    # 评估全肺每个像素的灌注状态
    lung_normal = lung_perfusion >= normal_threshold
    lung_reduced = (lung_perfusion >= defect_threshold) & (lung_perfusion < normal_threshold)
    lung_defect = (lung_perfusion < defect_threshold) & (lung_perfusion > 0.0001)
    lung_perfusion_color[lung_normal] = [0, 1, 0]   # 正常灌注为绿色
    lung_perfusion_color[lung_reduced] = [0, 0, 1]  # 灌注减低为蓝色
    lung_perfusion_color[lung_defect] = [1, 0, 0]   # 灌注缺损为红色

    # 评估右肺每个像素的灌注状态
    right_lung_normal = right_lung_perfusion >= normal_threshold
    right_normal_count = np.sum(right_lung_normal)
    right_lung_defect = (right_lung_perfusion < defect_threshold) & (right_lung_perfusion > 0.0001)
    right_defect_count = np.sum(right_lung_defect)
    right_lung_reduced = (right_lung_perfusion >= defect_threshold) & (right_lung_perfusion < normal_threshold)
    right_reduced_count = np.sum(right_lung_reduced)
    right_lung_perfusion_color[right_lung_normal] = [0, 1, 0]   # 正常灌注为绿色
    right_lung_perfusion_color[right_lung_defect] = [1, 0, 0]   # 灌注缺损为红色
    right_lung_perfusion_color[right_lung_reduced] = [0, 0, 1]  # 灌注减低为蓝色

    # 评估左肺每个像素的灌注状态
    left_lung_normal = left_lung_perfusion >= normal_threshold
    left_normal_count = np.sum(left_lung_normal)
    left_lung_defect = (left_lung_perfusion < defect_threshold) & (left_lung_perfusion > 0.0001)
    left_defect_count = np.sum(left_lung_defect)
    left_lung_reduced = (left_lung_perfusion >= defect_threshold) & (left_lung_perfusion < normal_threshold)
    left_reduced_count = np.sum(left_lung_reduced)
    left_lung_perfusion_color[left_lung_normal] = [0, 1, 0]   # 正常灌注为绿色
    left_lung_perfusion_color[left_lung_defect] = [1, 0, 0]   # 灌注缺损为红色
    left_lung_perfusion_color[left_lung_reduced] = [0, 0, 1]  # 灌注减低为蓝色
    return lung_perfusion, lung_perfusion_color, right_lung_perfusion, right_lung_perfusion_color, left_lung_perfusion, left_lung_perfusion_color,\
    right_lung_count, right_normal_count, right_defect_count, right_reduced_count, left_lung_count, left_normal_count, left_defect_count, left_reduced_count


def run02_lung_perfusion():
    ctname = "CT-0003-00055"
    pbvname = "PBV-0014-00055"
    ct_file = os.path.join(r'E:\cjfh\dectpe\threshold\verifythreshold2\healthy-case1', ctname + '.dcm')
    pbv_file = os.path.join(r'E:\cjfh\dectpe\threshold\verifythreshold2\healthy-case1', pbvname + '.dcm')
    # 分割肺部区域并绘制轮廓线
    lung_mask, right_lung_mask, left_lung_mask = get_ct_mask(ct_file)

    adaptive = True
    lung_perfusion, lung_perfusion_color, right_lung_perfusion, right_lung_perfusion_color, left_lung_perfusion, left_lung_perfusion_color, \
        right_lung_count, right_normal_count, right_defect_count, right_reduced_count, left_lung_count, left_normal_count, left_defect_count, left_reduced_count = extract_lung_perfusion(
        pbv_file, lung_mask, right_lung_mask, left_lung_mask, adaptive)

    # 显示结果
    plt.subplot(1, 3, 1)
    plt.imshow(lung_perfusion_color)
    plt.axis('off')
    plt.title('lung')
    plt.subplot(1, 3, 2)
    plt.imshow(right_lung_perfusion_color)
    plt.axis('off')
    plt.title('right lung')
    plt.subplot(1, 3, 3)
    plt.imshow(left_lung_perfusion_color)
    plt.axis('off')
    plt.title('left lung')
    #plt.savefig(pbvname + '.png')
    plt.show()


run02_lung_perfusion()


# 列出目录中的所有dcm文件名
def list_dcm_files(directory):
    # 使用 glob 模块列出当前目录中的所有.dcm 文件
    dcm_files = glob.glob(os.path.join(directory, 'CT', '*.dcm'))
    # 过滤出文件（排除子目录），并获取文件名
    dcm_file_names = [os.path.basename(file) for file in dcm_files if os.path.isfile(file)]
    return dcm_file_names


# 示例用法
def batch_lung_perfusion(case_dirpath, case_id):
    dcm_files = list_dcm_files(os.path.join(case_dirpath, case_id))
    dcm_file_list = []
    right_lung_list = []
    right_normal_list = []
    right_defect_list = []
    right_reduced_list = []
    left_lung_list = []
    left_normal_list = []
    left_defect_list = []
    left_reduced_list = []
    # 创建pandas量化表格
    for dcm_file in dcm_files:
        ct_file = os.path.join(case_dirpath, case_id, 'CT', dcm_file)
        pbv_file = os.path.join(case_dirpath, case_id, 'PBV', dcm_file)
        # 分割肺部区域并绘制轮廓线
        lung_mask, right_lung_mask, left_lung_mask = get_ct_mask(ct_file)
        adaptive = True
        lung_perfusion, lung_perfusion_color, right_lung_perfusion, right_lung_perfusion_color, left_lung_perfusion, left_lung_perfusion_color,\
            right_lung_count, right_normal_count, right_defect_count, right_reduced_count, left_lung_count, left_nornal_count, left_defect_count, left_reduced_count = extract_lung_perfusion(pbv_file, lung_mask, right_lung_mask, left_lung_mask, adaptive)
        # 添加一个患者数据
        dcm_file_list.append(dcm_file)
        right_lung_list.append(right_lung_count)
        right_normal_list.append(right_normal_count)
        right_defect_list.append(right_defect_count)
        right_reduced_list.append(right_reduced_count)
        left_lung_list.append(left_lung_count)
        left_normal_list.append(left_nornal_count)
        left_defect_list.append(left_defect_count)
        left_reduced_list.append(left_reduced_count)

        # 显示结果
        plt.subplot(1, 3, 1)
        plt.imshow(lung_perfusion_color)
        plt.axis('off')
        plt.title('lung')
        plt.subplot(1, 3, 2)
        plt.imshow(right_lung_perfusion_color)
        plt.axis('off')
        plt.title('right lung')
        plt.subplot(1, 3, 3)
        plt.imshow(left_lung_perfusion_color)
        plt.axis('off')
        plt.title('left lung')
        plt.savefig(os.path.join(case_dirpath, case_id, 'result', dcm_file.split()[0] + '.png'))
        plt.close()

    # 量化结果保存为Excel文件
    df = pd.DataFrame({
        'File_Name': dcm_file_list,
        'Right_Lung': right_lung_list,
        'Right_Normal': right_normal_list,
        'Right_Defect': right_defect_list,
        'Right_Reduced': right_reduced_list,
        'Left_Lung': left_lung_list,
        'Left_Normal': left_normal_list,
        'Left_Defect': left_defect_list,
        'Left_Reduced': left_reduced_list,
    })

    # 将DataFrame保存为Excel文件
    df.to_excel(os.path.join(case_dirpath, case_id + '.xlsx'), index=False)


def run03_batch_lung_perfusion():
    # 使用os.listdir 列出目录中的所有患者
    case_dirpath = r'E:\cjfh\dectpe\raw\case50'
    #cases = [f'case{i}' for i in range(36, 51)]
    cases = ['case18', 'case35']
    for case in cases:
        batch_lung_perfusion(case_dirpath, case)
