from util import process_excel, save_to_excel
import sys
import os
import traceback
import pandas as pd
import datetime

# 添加当前目录到系统路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def transform_data(data_list):
    """
    根据规则转换数据
    
    Args:
        data_list: 原始数据列表
    
    Returns:
        转换后的数据列表
    """
    transformed_data = []
    
    # 根据分会场+专家姓名来存储唯一数据
    unique_entries = {}
    
    for item in data_list:
        # 检查是否包含必要的字段
        venue_field = next((field for field in item.keys() if "分会场名称" in field), None)
        
        # 如果没有找到分会场字段，跳过该条记录
        if not venue_field:
            continue
        
        # 提取分会场名称
        venue_name = item[venue_field]
        
        # 从角色字段获取角色信息
        role_field = next((field for field in item.keys() if field == "角色（IT）" or field == "角色"), None)
        chair_type = ""
        host_type = ""
        
        if role_field and item[role_field]:
            role = item[role_field]
            if "主席" in role:
                chair_type = role
            elif role == "主持人":
                host_type = role
        
        # 处理数据 - 现在需要处理可能同时存在的两种情况
        
        # 情况1: 处理报告人信息
        if "报告人" in item and item["报告人"]:
            expert_name = item["报告人"]
            first_title = item.get("机构", "")
            
            # 构建唯一键
            unique_key = f"{venue_name}_{expert_name}"
            
            if unique_key in unique_entries:
                # 更新现有记录
                existing_entry = unique_entries[unique_key]
                
                if not existing_entry["第一Title"] and first_title:
                    existing_entry["第一Title"] = first_title
                    
                if not existing_entry["主席类型"] and chair_type:
                    existing_entry["主席类型"] = chair_type
                    
                if not existing_entry["主持人类型"] and host_type:
                    existing_entry["主持人类型"] = host_type
            else:
                # 创建新记录
                unique_entries[unique_key] = {
                    "分会场名称": venue_name,
                    "专家姓名": expert_name,
                    "第一Title": first_title,
                    "主席类型": chair_type,
                    "主持人类型": host_type
                }
        
        # 情况2: 处理团队PI信息，团队PI这个没有角色
        if "团队PI" in item and item["团队PI"]:
            expert_name = item["团队PI"]
            first_title = item.get("团队PI机构", "")
            
            # 构建唯一键
            unique_key = f"{venue_name}_{expert_name}"
            
            if unique_key in unique_entries:
                # 更新现有记录
                existing_entry = unique_entries[unique_key]
                
                if not existing_entry["第一Title"] and first_title:
                    existing_entry["第一Title"] = first_title
                    
            else:
                # 创建新记录
                unique_entries[unique_key] = {
                    "分会场名称": venue_name,
                    "专家姓名": expert_name,
                    "第一Title": first_title,
                    "主席类型": "",
                    "主持人类型": ""
                }
    
    # 将字典转换为列表
    transformed_data = list(unique_entries.values())
    
    return transformed_data

def main():
    """
    主函数，接收Excel文件路径作为参数，处理数据并保存到新文件
    """
    if len(sys.argv) != 2:
        print("用法: python op-expert.py <Excel文件绝对路径>")
        sys.exit(1)
    
    excel_path = sys.argv[1]
    
    # 检查文件是否存在
    if not os.path.isfile(excel_path):
        print(f"错误: 文件 '{excel_path}' 不存在")
        sys.exit(1)
    
    # 获取当前时间戳
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    
    # 输出文件路径 - 保存在输入Excel文件的同级目录下
    output_dir = os.path.dirname(excel_path)
    output_excel = os.path.join(output_dir, f"op-expert-{timestamp}.xlsx")

    print(f"输入Excel文件: {excel_path}")
    print(f"输出Excel文件: {output_excel}")
    
    # 处理Excel文件
    try:
        # 获取原始数据
        data = process_excel(excel_path)
        
        # 转换数据
        transformed_data = transform_data(data)
        
        # 保存转换后的数据
        save_to_excel(transformed_data, output_excel)
        
        print(f"成功处理文件，共 {len(transformed_data)} 条记录")
        
    except Exception as e:
        print(f"处理Excel文件时出错: {str(e)}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
