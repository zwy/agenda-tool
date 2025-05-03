以下是我的一个需求描述：
1. 从一个文件夹 `input/report` 中读取所有的Excel文件
2. 读取每个Excel文件中的数据
3. 将数据存储到一个列表中
4. 对列表中的数据进行处理，处理时需要参考这个 `model/report.json` 文件, 该json文件是一个json schema文件
5. 注意json schema 需要对类似 enum 做验证，对 时间等做格式验证。
6. 处理完成后，将数据存储到一个 新的jsonl文件中，
   文件名为 `data/report.jsonl`
7. 你可以参考 `105_pre_expert.py`  `100_pre_session.py` 这些文件来实现
8. 编辑的代码是在 `106_pre_report.py` 文件中