from util import process_excel, save_to_jsonl, filter_fields, rename_fields, save_to_excel
import sys
import os
import traceback
import glob

# 添加当前目录到系统路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """
    主函数，接收文件夹路径作为参数，处理该文件夹下所有Excel文件
    """
    if len(sys.argv) != 2:
        print("用法: python jinshuju.py <Excel文件夹路径>")
        print("注意: 会处理文件夹中所有Excel文件并合并结果")
        sys.exit(1)
    
    folder_path = sys.argv[1]
    
    # 检查文件夹是否存在
    if not os.path.isdir(folder_path):
        print(f"错误: 目录 '{folder_path}' 不存在")
        sys.exit(1)
    
    # 输出文件路径
    output_file = os.path.join(folder_path, "combined_e2e_jinshuju.jsonl")
    output_excel = os.path.join(folder_path, "combined_e2e_jinshuju.xlsx")

    print(f"输出JSONL文件路径: {output_file}")
    print(f"输出Excel文件路径: {output_excel}")
    
    # 查找文件夹中所有的Excel文件
    excel_files = glob.glob(os.path.join(folder_path, "*.xlsx"))
    
    if not excel_files:
        print(f"错误: 在 '{folder_path}' 中未找到任何Excel文件")
        sys.exit(1)
    
    print(f"找到 {len(excel_files)} 个Excel文件需要处理")
    
    # 存储所有处理后的数据
    all_data = []
    
    # 处理每个Excel文件
    try:
        for excel_path in excel_files:
            print(f"处理文件: {os.path.basename(excel_path)}")
            
            # 获取原始数据
            data = process_excel(excel_path)

            # 重命名字段
            field_map = {
                "中文题目": "报告题目",
                "英文题目": "报告英文题目",
                "中文摘要（500字内）": "简介",
                "英文摘要（300单词内）": "英文简介",
            }
            renamed_data = rename_fields(data, field_map)

            # 必填字段检查
            required_fields = ["报告题目"]

            # 只保留特定字段，field_map中的键
            fields_to_keep = list(field_map.values())
            # 过滤数据，只保留指定字段
            filtered_data = filter_fields(renamed_data, fields_to_keep)
            
            # 检查必填字段
            valid_data = []
            for item in filtered_data:
                valid_item = True
                for field in required_fields:
                    if field not in item or not item[field] or item[field].strip() == "":
                        print(f"错误: '{field}' 字段不能为空，跳过该条记录")
                        valid_item = False
                        break
                if valid_item:
                    valid_data.append(item)
            
            # 将有效的数据添加到总数据中
            all_data.extend(valid_data)
        # 去重 all_data
        all_data = [dict(t) for t in {tuple(d.items()) for d in all_data}]

        # 保存合并后的数据
        save_to_jsonl(all_data, output_file)
        save_to_excel(all_data, output_excel)
        
        print(f"成功处理所有文件，共 {len(all_data)} 条记录")
        
    except Exception as e:
        print(f"处理Excel文件时出错: {str(e)}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
