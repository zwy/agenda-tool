以下是我的一个需求描述：

1. 请你读取 `data/session.jsonl` 文件中的数据
2. 我们需要对部分字段的数据进行处理，例如
   - showName - 分会场名称展示，如果为空，则将sessionName赋值给showName
3. 编辑的代码是在 `tasks/deep_session.py` 文件中