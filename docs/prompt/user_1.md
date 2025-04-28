以下是我的一个需求描述：
1. 从一个文件夹 `input/session` 中读取所有的Excel文件
2. 读取每个Excel文件中的数据
3. 将数据存储到一个列表中
4. 对列表中的数据进行处理，处理时需要参考这个 `model/session.json` 文件, 该json文件是一个json schema文件
5. 处理完成后，将数据存储到一个 新的jsonl文件中，
   文件名为 `data/session.jsonl`