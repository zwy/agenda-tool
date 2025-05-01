import json
import pathlib


def process_bibao_data():
    """处理壁报数据，根据aliyunVid补充视频相关信息"""
    # 读取bibao.jsonl文件
    bibao_file = pathlib.Path("data/bibao.jsonl")
    video_file = pathlib.Path("data/video.jsonl")

    if not bibao_file.exists():
        print(f"错误: 文件 {bibao_file} 不存在!")
        return
    
    if not video_file.exists():
        print(f"错误: 文件 {video_file} 不存在!")
        return

    # 读取壁报数据
    bibao_list = []
    try:
        with open(bibao_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    bibao = json.loads(line)
                    bibao_list.append(bibao)
        print(f"已读取{len(bibao_list)}条壁报数据")
    except Exception as e:
        print(f"读取壁报数据时出错: {str(e)}")
        return

    # 读取视频数据并创建查找表
    video_dict = {}
    try:
        with open(video_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    video = json.loads(line)
                    if "aliyunVid" in video:
                        video_dict[video["aliyunVid"]] = {
                            "permission": video.get("permission", ""),
                            "duration": video.get("duration", ""),
                            "cover": video.get("cover", "")
                        }
        print(f"已读取{len(video_dict)}条视频数据")
    except Exception as e:
        print(f"读取视频数据时出错: {str(e)}")
        return

    # 更新壁报数据
    updated_count = 0
    error_count = 0
    for bibao in bibao_list:
        if "aliyunVid" in bibao and bibao["aliyunVid"]:
            aliyun_vid = bibao["aliyunVid"]
            if aliyun_vid in video_dict:
                # 更新视频相关信息
                bibao["permission"] = video_dict[aliyun_vid]["permission"]
                bibao["duration"] = video_dict[aliyun_vid]["duration"]
                bibao["cover"] = video_dict[aliyun_vid]["cover"]
                updated_count += 1
            else:
                # 如果有aliyunVid但在视频数据中找不到对应记录，报错
                print(f"错误: 壁报的aliyunVid={aliyun_vid}在视频数据中找不到对应记录")
                error_count += 1

    print(f"已更新{updated_count}条壁报的视频相关信息")
    if error_count > 0:
        print(f"有{error_count}条壁报数据出现错误，请检查")
        return

    # 验证更新后的数据
    for bibao in bibao_list:
        if "aliyunVid" in bibao and bibao["aliyunVid"]:
            if "permission" not in bibao or "duration" not in bibao:
                print(f"错误: 壁报数据aliyunVid={bibao['aliyunVid']}没有完整的视频信息")
                return

    # 保存回文件
    try:
        with open(bibao_file, "w", encoding="utf-8") as f:
            for bibao in bibao_list:
                f.write(json.dumps(bibao, ensure_ascii=False) + "\n")
        print(f"已将更新后的数据保存到 {bibao_file}")
    except Exception as e:
        print(f"保存数据时出错: {str(e)}")


if __name__ == "__main__":
    process_bibao_data()
