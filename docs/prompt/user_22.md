以下是我的一个需求描述：

1. 请你读取 `data/bibao.jsonl` 文件中的数据
2. 请你读取 `data/video.jsonl` 文件中的数据
3. 我们需要对bibao.jsonl部分字段的数据进行处理，根据 aliyunVid 的值来获取视频的相关信息，在video.jsonl中
   - permission - 视频权限，根据 aliyunVid 值来查找对应的
   - duration - 视频时长，根据 aliyunVid 值来查找对应的
   - cover - 视频封面，根据 aliyunVid 值来查找对应的
4. 如果 bibao中有aliyunVid字段，最后缺没有 permission、duration 字段，则报错
5. 编辑的代码是在 `202_deep_bibao.py` 文件中
6. 你可以参考 `200_deal_session.py` 这个文件来实现