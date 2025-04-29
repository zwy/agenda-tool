以下是我的一个需求描述：

1. 编辑的代码是在 `1000_sync_to_oss.py` 文件中
2. 你可以参考 `upload_oss_pdf.py` `ossutil.py` 文件中的代码，可以基于此优化
3. 主要逻辑是
   - 按照顺序执行 `output/data` 文件夹中的 文件上传到oss中
   - 需要上传到阿里云oss 上这个目录下，已在env中配置 OSS_DATA_DIR
4. 你可以使用任何你认为合适的库来实现这个功能