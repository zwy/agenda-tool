以下是我的一个需求描述：

1. 请你通过API接口获取数据，`{TOUGAO_API_HOST}/open/bibaos/all?uuid={TOUGAO_UUID}`，从环境变量env里读取。
2. API接口返回的数据，请你参考 `docs/api_all_bibaos.json` 文件中的数据格式，输出json文件。
3. 编辑的代码是在 `tasks/102_pre_bibao.py` 文件中
4. 对列表中的数据进行处理，处理时需要参考这个 `model/bibao.json` 文件, 该json文件是一个json schema文件
5. 处理完成后，将数据存储到一个 新的jsonl文件中，
   文件名为 `data/bibao.jsonl`
6. 你可以参考 `apiutil.py` 这个文件来实现 接口数据的获取