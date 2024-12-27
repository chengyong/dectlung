# -*- coding: utf-8 -*-

#
# Title:
# Author:
# Refer:
# Repo:
# Date: 2024-11-xx
#

import numpy as np
import pydicom
import matplotlib.pyplot as plt
from scipy.ndimage import distance_transform_edt
from skimage import color, morphology, filters, measure, exposure, segmentation

def watershed_segment_lungs(dicom_file):
    # 读取DICOM文件
    dicom_data = pydicom.dcmread(dicom_file)

    # 获取CT图像数据
    ct_image = dicom_data.pixel_array

    # 将图像转换为灰度图像
    gray = exposure.rescale_intensity(ct_image, out_range=(0, 1))
    # 应用高斯模糊以减少噪声
    blurred = filters.gaussian(gray, sigma=1.0)

    # 应用Otsu阈值分割
    thresh = filters.threshold_otsu(blurred)
    binary = blurred > thresh

    # 进行形态学操作以去除小的噪声区域
    opening = morphology.opening(binary, morphology.disk(3))
    # 确定肺部区域的背景区域
    sure_bg = morphology.dilation(opening, morphology.disk(3))

    # 寻找肺部区域的前景区域
    dist_transform = distance_transform_edt(opening)
    sure_fg = dist_transform > 0.7 * dist_transform.max()

    # 找到未知区域
    unknown = np.logical_xor(sure_bg, sure_fg)
    # 标记标签
    markers = measure.label(sure_fg)
    # 将所有未知区域标记为0
    markers[unknown] = 0

    # 应用分水岭算法
    labels = segmentation.watershed(gray, markers, mask=binary)

    # 创建一个掩码图像
    mask = np.zeros_like(gray, dtype=bool)
    mask[labels == 0] = True  # 边界标记为白色

    # 标识左肺和右肺
    lung_labels = measure.label(~mask, background=0)

    # 假设最大的两个连通区域是左肺和右肺
    properties = measure.regionprops(lung_labels)
    areas = [prop.area for prop in properties]
    sorted_areas = sorted(areas, reverse=True)

    left_lung_label = None
    right_lung_label = None

    for prop in properties:
        if prop.area == sorted_areas[0]:
            left_lung_label = prop.label
        elif prop.area == sorted_areas[1]:
            right_lung_label = prop.label
            break

    # 为左肺和右肺创建掩码
    left_lung_mask = lung_labels == left_lung_label
    right_lung_mask = lung_labels == right_lung_label

    # 在原始图像上绘制轮廓线
    contours_left = measure.find_contours(left_lung_mask, 0.5)
    contours_right = measure.find_contours(right_lung_mask, 0.5)

    image_with_contours = color.gray2rgb(gray)

    for contour in contours_left:
        rows, cols = contour.astype(int).T
        image_with_contours[rows, cols] = (0, 1, 0)  # 绿色轮廓线

    for contour in contours_right:
        rows, cols = contour.astype(int).T
        image_with_contours[rows, cols] = (1, 1, 0)  # 红色轮廓线

    return image_with_contours, left_lung_mask, right_lung_mask


# 指定DICOM文件路径
def run_watershed_segment_lungs():
    ct_file = r'E:\cjfh\dectpe\raw\typical\case2\CT\IMG-0002-00137.dcm'
    # 分割肺部区域并绘制轮廓线
    segmented_image, left_lung_mask, right_lung_mask = watershed_segment_lungs(ct_file)
    print(left_lung_mask)
    # 显示结果
    plt.imshow(segmented_image)
    plt.axis('off')
    plt.show()


# 评估双肺的灌注情况并显示
def extract_lung_perfusion(pbv_file, left_lung_mask, right_lung_mask):
    # 读取PVB图像
    pbv_data = pydicom.dcmread(pbv_file)
    pbv_image = pbv_data.pixel_array

    # 归一化PVB图像到0-1范围
    pvb_normalized = exposure.rescale_intensity(pbv_image, out_range=(0, 1))

    # 应用左肺和右肺掩码提取功能图像
    right_lung_perfusion = pvb_normalized * right_lung_mask
    left_lung_perfusion = pvb_normalized * left_lung_mask

    # 定义灌注状态的阈值
    normal_threshold = 0.6
    defect_threshold = 0.3

    # 评估左肺每个像素的灌注状态
    left_lung_status = np.zeros_like(left_lung_perfusion, dtype=int)
    left_lung_status[left_lung_perfusion >= normal_threshold] = 2  # 正常灌注
    left_lung_status[(left_lung_perfusion >= defect_threshold) & (left_lung_perfusion < normal_threshold)] = 1  # 灌注减低
    left_lung_status[left_lung_perfusion < defect_threshold] = 0  # 灌注缺损

    # 评估右肺每个像素的灌注状态
    right_lung_status = np.zeros_like(right_lung_perfusion, dtype=int)
    right_lung_status[right_lung_perfusion >= normal_threshold] = 2  # 正常灌注
    right_lung_status[
        (right_lung_perfusion >= defect_threshold) & (right_lung_perfusion < normal_threshold)] = 1  # 灌注减低
    right_lung_status[right_lung_perfusion < defect_threshold] = 0  # 灌注缺损
    return left_lung_perfusion, right_lung_perfusion, left_lung_status, right_lung_status


# 示例用法
def run_extract_lung_perfusion():
    ct_filepath = r'E:\cjfh\dectpe\raw\typical\case1\CT\IMG-0001-00097.dcm'
    pbv_filepath = r'E:\cjfh\dectpe\raw\typical\case1\PBV-blackwhite\IMG-0016-00097.dcm'
    # 分割肺部区域并绘制轮廓线
    segmented_image, left_lung_mask, right_lung_mask = watershed_segment_lungs(ct_filepath)
    left_perfusion, right_perfusion, left_status, right_status = extract_lung_perfusion(pbv_filepath, left_lung_mask,
                                                                                       right_lung_mask)
    # 显示结果
    plt.imshow(right_perfusion)
    plt.axis('off')
    plt.show()



