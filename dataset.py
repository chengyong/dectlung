# -*- coding: utf-8 -*-

#
# Title: 双能CT基本库
# Author:
# Refer:
# Repo:
# Date: 2024-05-08
#

import os
import pandas as pd
import pydicom
import matplotlib.pyplot as plt


dect_dataset_path = r"E:\cjfh\dectpe"
dect_raw_path = r"E:\cjfh\dectpe\raw"
dect_result_path = r"E:\cjfh\dectpe\result"


# 使用Matplotlib绘制CT图像
def plot_ct_image(ct_dirpath, index):
    '''
        ct_dirpath: path of ct image;
        index: number of the ct sequence;
    '''
    dicom_files = os.listdir(ct_dirpath)
    # 使用 pydicom 读取 DICOM 文件
    dicom_data = pydicom.dcmread(os.path.join(ct_dirpath, dicom_files[index]))
    # 获取图像数据
    image_array = dicom_data.pixel_array
    print(image_array.shape)

    # 使用 matplotlib 显示图像
    plt.imshow(image_array, cmap=plt.cm.bone)  # cmap=plt.cm.bone 为显示灰度图像的常用色彩映射
    plt.axis('off')  # 不显示坐标轴
    plt.show()


def run_plot_ct_image():
    dirpath = r'E:\cjfh\dectpe\raw\untypical\case4\CT'
    index = 27
    plot_ct_image(dirpath, index)


#
# 把DICOM图像文件转换为Excel文件，不同的分量使用不同的Sheet，方便查看
#
def convert_dicom_excel(dicom_file, excel_file):
    # 读取DICOM文件
    dicom_data = pydicom.dcmread(dicom_file)
    # 获取像素数据
    pixel_data = dicom_data.pixel_array
    print(pixel_data.shape)

    # 检查数据的shape
    if pixel_data.shape == (512, 513, 3):
        # 将数据拆分为三个sheet
        sheet1_data = pixel_data[:, :, 0]
        sheet2_data = pixel_data[:, :, 1]
        sheet3_data = pixel_data[:, :, 2]

        # 创建DataFrame对象
        df1 = pd.DataFrame(sheet1_data)
        df2 = pd.DataFrame(sheet2_data)
        df3 = pd.DataFrame(sheet3_data)

        # 创建ExcelWriter对象
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            # 将DataFrame写入不同的sheet
            df1.to_excel(writer, sheet_name='Sheet1', index=False, header=False)
            df2.to_excel(writer, sheet_name='Sheet2', index=False, header=False)
            df3.to_excel(writer, sheet_name='Sheet3', index=False, header=False)

        print(f"数据已成功保存到Excel文件: {excel_file}")
    else:
        # 将数据拆分为三个sheet
        sheet1_data = pixel_data[:, :]
        df1 = pd.DataFrame(sheet1_data)
        # 创建ExcelWriter对象
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            # 将DataFrame写入不同的sheet
            df1.to_excel(writer, sheet_name='Sheet1', index=False, header=False)
            print(f"数据已成功保存到Excel文件: {excel_file}")

#
def run_convert_dicom_excel():
    dirpath = r'E:\cjfh\dectpe\raw\untypical\case4\PBV-color'
    dicom_files = os.listdir(dirpath)
    # 使用 pydicom 读取 DICOM 文件
    dicom_file = os.path.join(dirpath, dicom_files[0])
    excel_file = dicom_files[0] + '.xlsx'
    convert_dicom_excel(dicom_file, excel_file)


# 返回含有perfusion图片的文件名
def perfusion_image_list(dir_path):
    # 初始化空列表存放文件名
    image_list = []
    # 遍历目录中的所有文件
    for filename in os.listdir(dir_path):
        # 检查文件是否为PNG文件且文件名中是否包含"perfusion"
        if filename.endswith('.png') and 'perfusion' in filename:
            # 将符合条件的文件名添加到列表中
            image_list.append(filename)
    return image_list




# 把df中指定的列累加起来返回
def sum_columns(df, columns):
    # 初始化一个字典来存储每一列的累加值
    column_sums = {column: 0 for column in columns}
    # 累加指定列的值
    for column in columns:
        if column in df.columns:
            column_sums[column] = df[column].sum()
        else:
            print(f"Column '{column}' not found in the file.")
    return column_sums


# 计算每个患者灌注百分比
def perfusion_percent(df):
    '''
        df: df for pixel count.
    '''
    df['Right_Lung_Percent'] = round(df['Right_Lung'] / df['Right_Lung'] * 100.00, 2)
    df['Right_Normal_Percent'] = round(df['Right_Normal'] / df['Right_Lung'] * 100.00, 2)
    df['Right_Defect_Percent'] = round(df['Right_Defect'] / df['Right_Lung'] * 100.00, 2)
    df['Right_Reduced_Percent'] = round(df['Right_Reduced'] / df['Right_Lung'] * 100.00, 2)
    df['Left_Lung_Percent'] = round(df['Left_Lung'] / df['Left_Lung'] * 100.00, 2)
    df['Left_Normal_Percent'] = round(df['Left_Normal'] / df['Left_Lung'] * 100.00, 2)
    df['Left_Defect_Percent'] = round(df['Left_Defect'] / df['Left_Lung'] * 100.00, 2)
    df['Left_Reduced_Percent'] = round(df['Left_Reduced'] / df['Left_Lung'] * 100.00, 2)
    return df


def run_perfusion_percent():
    df = pd.read_excel(r'E:\cjfh\dectpe\raw\allcases_result\allcases244_stat_resunet.xlsx')
    perfusion_percent(df)
    df.to_excel(r'E:\cjfh\dectpe\raw\allcases_result\allcases244_percent_resunet.xlsx.xlsx')


