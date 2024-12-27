# -*- coding: utf-8 -*-

#
# Title: 对50个患者每列求和后汇总到一个文件
# Author:
# Refer:
# Repo:
# Date: 2024-06-06
#


import os
import pandas as pd
from workbase.dectpe.core.alpha import sum_columns


# 按行的方式创建Excel文件并保存
def run_perfusionsum_table():
    result_dirpath = r'E:\cjfh\dectpe\raw\allcases_result\allcases_resunet'
    # 指定需要累加的列名
    param_names = [
        'Right_Lung', 'Right_Normal', 'Right_Defect', 'Right_Reduced',
        'Left_Lung', 'Left_Normal', 'Left_Defect', 'Left_Reduced'
    ]
    table_header = [
        'case', 'Right_Lung', 'Right_Normal', 'Right_Defect', 'Right_Reduced',
        'Left_Lung', 'Left_Normal', 'Left_Defect', 'Left_Reduced'
    ]
    case_list = [f'case{i:03d}' for i in range(1, 245)]
    row_list = []
    for case in case_list:
        case_stat = [case]
        case_filepath = os.path.join(result_dirpath, case + ".xlsx")
        case_df = pd.read_excel(case_filepath)
        # 获取累加结果
        sum_result = sum_columns(case_df, param_names)
        # 打印累加结果
        '''
        print("Summed values for each column:")
        for column, total in sum_result.items():
            print(f"{column}: {total}")
        '''
        case_stat.extend(list(sum_result.values()))
        row_list.append(case_stat)

    # 创建 DataFrame
    df = pd.DataFrame(row_list, columns=table_header)

    # 指定输出的 Excel 文件路径
    stat_file_path = r'D:\download\allcases_stat.xlsx'
    # 将 DataFrame 写入 Excel 文件
    df.to_excel(stat_file_path, index=False)
    print(f"Excel file created at {stat_file_path}")


