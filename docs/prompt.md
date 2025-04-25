请你帮我把下班那个设计的表格转换成json schema的json文件。

表头	表头含义	输入	输出	系统生成	必填	介绍	类型	可选值	默认值	参考
sessionName	分会场名称	✅			✅		string			
expertName	专家姓名	✅			✅	同一个分会场里唯一	string			
expertCode	专家编码			基于（分会场名称+专家姓名+meeting）生成base64编码，如果分会场名称、专家姓名变了，这个也变了			string			
avatar	头像			头像太多，这里按照规则合成，把头像文件按规则上传即可			string			
pinyin	专家姓名拼音			按照姓名自动生成			string			
title	第一Title	✅					string			南京医科大学第二附属医院
secondTitle	第二Title	✅					string			南京医科大学第二附属医院
academician	院士类型	✅					string	中国工程院院士｜中国科学院院士		
chairman	主席类型	✅					string	主席｜名誉主席｜执行主席		
presenter	主持人类型	✅					string	主持人		
rbaseUrl	Rbase页面URL	✅				专家在rbase上的个人详情页链接	string			