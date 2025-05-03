以下是我的一个需求描述：

1. 请你读取 `data/expert.jsonl` 文件中的数据
2. 我们需要根据需求，输出json文件。
3. 编辑的代码是在 `tasks/305_post_expert.py` 文件中
4. 输出的json文件是 `output/data/reporters.json` 文件
5. 输出的json文件是一个列表，请你根据json schema的要求，输出json文件， json schema文件在 `output/model/reporters.json` 文件中
6. 这里，还需要注意，需要从 `data/report.jsonl` 文件中读取数据，判断这个 expert.jsonl 中的专家是否是报告人，如果是`- reporterName - 报告人姓名` 或者 `piName - 团队PI姓名`，就输出到 reporters.json 文件中
7. 你可以参考 `304_post_expert.py` 这个文件来实现
8. 在添加一个逻辑，验证数据重复，如果重复则过滤一下，如果两条数据，expertName、title、secondTitle、rbaseUrl，一摸一样，则只保留一条