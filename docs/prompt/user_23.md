以下是我的一个需求描述：

1. 请你读取 `data/expert.jsonl` 文件中的数据
2. 这个是一个专家列表，其中有一个字段是 `rbaseUrl`，这个字段是专家的Rbase页面的URL，例如 `https://rbase.chinagut.cn/base/authorBase/ae0f43e5b3cf4f89820ef2bcb2c7a912/1?authorName=Qunyi%20Li&authorUuid=157d40b5205d4ca787c8573ccc941c5a`
3. 我们希望通过这个URL获取专家的头像图片URL，这里可以使用下边类似的接口获取
   `https://rbasefront.chinagut.cn/f/author/detail2?name=Qunyi+Li&uuid=157d40b5205d4ca787c8573ccc941c5a` 这个接口中的name对应rbaseUrl中的authorName，uuid对应rbaseUrl中的authorUuid
4. API接口返回的数据，请你参考 `docs/api_author_detail.json` 文件中的数据格式，输出json文件。注意专家头像是data中的avatar字段，会获取到类似`/rbase_2408/author_detail/image/20250430/c7889a0990cf4efd8dc5faa963ced34c.png`这样的路径
5. 在这里这个avatar字段，我们可以在阿里云的oss上下载下来，注意下载的时候，开头去掉‘/’，下载到本地的存在路径是 `input/avatar/{sessionName}`，文件名为 `{expertName}.png`
6. 这里，如果图片不是png格式的，需要转换成png格式
7. 编辑的代码是在 `tasks/203_deal_expert.py` 文件中
8.  你可以参考 `1000_sync_to_oss.py` `ossutil.py` 这两个文件中的代码