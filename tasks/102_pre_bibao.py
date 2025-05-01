import os
import json
import asyncio
import aiohttp
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 从环境变量获取API地址和UUID
TOUGAO_API_HOST = os.getenv("TOUGAO_API_HOST")
TOUGAO_UUID = os.getenv("TOUGAO_UUID")

async def fetch_bibao_data():
    """从API获取壁报数据"""
    url = f"{TOUGAO_API_HOST}/open/bibaos/all?uuid={TOUGAO_UUID}"
    try:
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
        headers = {
            'User-Agent': ua,
            'Content-Type': "application/json"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    print(f"请求失败，状态码：{response.status}")
                    return None
                
                response_text = await response.text()
                response_json = json.loads(response_text)
                
                if response_json.get("code") != 200:
                    print(f"API返回错误：{response_json.get('msg')}")
                    return None
                
                return response_json
    except Exception as e:
        print(f"获取壁报数据失败: {e}")
        return None

def process_bibao_data(data):
    """处理壁报数据，确保符合schema要求"""
    if not data or "data" not in data:
        print("数据格式不正确")
        return []
    
    bibao_list = data.get("data", [])
    processed_data = []
    
    for bibao in bibao_list:
        # 将boardNum转为字符串以符合schema要求
        if "boardNum" in bibao:
            bibao["boardNum"] = str(bibao["boardNum"])
            
        # 确保所有必需字段都存在
        processed_item = {
            "boardNum": bibao.get("boardNum", ""),
            "bibaoPic": bibao.get("bibaoPic", ""),
            "reportTitle": bibao.get("reportTitle", ""),
            "theme": bibao.get("theme", ""),
            "name": bibao.get("name", ""),
            "employer": bibao.get("employer", ""),
            "position": bibao.get("position", ""),
            "background": bibao.get("background", ""),
            "methods": bibao.get("methods", ""),
            "results": bibao.get("results", ""),
            "conclusion": bibao.get("conclusion", ""),
            "images": bibao.get("images", ""),
            "keywords": bibao.get("keywords", ""),
            "aliyunVid": bibao.get("aliyunVid", ""),
            "duration": bibao.get("duration", ""),
            "permission": bibao.get("permission", ""),
            "cover": bibao.get("cover", "")
        }
        processed_data.append(processed_item)
    
    return processed_data

async def main():
    """主函数"""
    # 获取壁报数据
    print(f"正在从 {TOUGAO_API_HOST}/open/bibaos/all?uuid={TOUGAO_UUID} 获取壁报数据...")
    response = await fetch_bibao_data()
    
    if not response:
        print("获取壁报数据失败")
        return
    
    # 处理数据
    processed_data = process_bibao_data(response)
    
    if not processed_data:
        print("处理壁报数据失败")
        return
    
    # 创建data目录（如果不存在）
    os.makedirs("data", exist_ok=True)
    
    # 将数据保存为jsonl文件
    output_file = "data/bibao.jsonl"
    with open(output_file, "w", encoding="utf-8") as f:
        for item in processed_data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    
    print(f"壁报数据已保存到 {output_file}, 共 {len(processed_data)} 条记录")

if __name__ == "__main__":
    asyncio.run(main())
