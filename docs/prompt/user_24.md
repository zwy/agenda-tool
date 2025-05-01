以下是我的一个需求描述：

1. 请你读取 `data/expert.jsonl` 文件中的数据
2. 在这里这个avatar字段，检测本地的存在路径是 `input/avatar/{sessionName}`，文件名为 `{expertName}.png` 是否存在，如果不存在报错
3. 如果头像存在则把 `avatar` 字段替换为 `{OSS_CDN_URL}/{OSS_DATA_DIR}/avatar/{sessionName}/{expertName}.png` ，这里的 `OSS_CDN_URL` 和 `OSS_DATA_DIR` 是在 `.env` 中定义，注意这个url，需要url编码
4. 在把处理好的数据，写入到 `data/expert.jsonl` 文件中
5. 在把 `input/avatar` 目录下的头像文件复制到 `output/data/avatar` 目录下
6. 编辑的代码是在 `tasks/204_deal_expert.py` 文件中
7.  你可以参考 `200_deal_session.py` 这文件中的代码