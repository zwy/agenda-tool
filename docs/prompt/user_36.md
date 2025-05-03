以下是我的一个需求描述：

1. 请你读取 `data/report.jsonl` 文件中的数据
2. 我们需要根据需求，输出json文件。
3. 编辑的代码是在 `tasks/307_post_report.py` 文件中
4. 输出的json文件是 `output/data/agenda/{agendaCode}.json` 文件，注意这里的 agendaCode 是文件名，我们从report.jsonl中读取出的是一个列表，
   这里的 agendaCode 是列表中的一个字段，我们需要根据这个字段来生成文件名，最后一条数据输出一个json文件
5. 输出的json文件是一个列表，请你根据json schema的要求，输出json文件， json schema文件在 `model/report.json` 文件中
6. 你可以参考 `300_post_session.py` `303_post_bibao.py` 这些文件来实现