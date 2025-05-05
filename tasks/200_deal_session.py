import json
import pathlib
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', encoding='utf-8')
logger = logging.getLogger(__name__)


def process_session_data():
    """后处理分会场数据，处理showName字段等"""
    # 读取session.jsonl文件
    input_file = pathlib.Path("data/session.jsonl")

    if not input_file.exists():
        logger.error(f"错误: 文件 {input_file} 不存在!")
        return

    sessions = []
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    session = json.loads(line)
                    sessions.append(session)
        logger.info(f"已读取{len(sessions)}条分会场数据")
    except Exception as e:
        logger.error(f"读取数据时出错: {str(e)}")
        return

    # 处理showName字段
    updated_count = 0
    for session in sessions:
        # 如果showName为空，则将sessionName赋值给showName
        if "showName" not in session or not session["showName"]:
            if "sessionName" in session and session["sessionName"]:
                session["showName"] = session["sessionName"]
                updated_count += 1

    logger.info(f"已更新{updated_count}条记录的showName字段")

    # 保存回文件
    try:
        with open(input_file, "w", encoding="utf-8") as f:
            for session in sessions:
                f.write(json.dumps(session, ensure_ascii=False) + "\n")
        logger.info(f"已将更新后的数据保存到 {input_file}")
    except Exception as e:
        logger.error(f"保存数据时出错: {str(e)}")


if __name__ == "__main__":
    process_session_data()
