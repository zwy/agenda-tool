请你帮我把下班那个设计的表格转换成json schema的json文件。

表头	表头含义	输入	输出	系统生成	必填	介绍	类型	可选值	默认值	参考
sessionName	分会场名称	✅	✅		✅	唯一	string			例如，宏基因组有上午和下午，如果需要分开，这里可以填宏基因组1、宏基因组2
showName	分会场名称展示	✅	✅			不唯一	string			例如，宏基因组有上午和下午，这里可以填宏基因组
type	分会场类型	✅	✅		✅		enum	开幕式、培训班、学术分会场、产业分会场、卫星会		
theme	主题	✅	✅			多个字符串，英文逗号分隔	string			技术方法,营养与食品
desc	分会场介绍	✅	✅				string			7小时干货培训就是让你大涨知识哦！
venueName	场馆名称	✅	✅				string			311AB
teyao	特邀报告数量	✅	✅				string		0	
tougao	投稿报告数量	✅	✅				string		0	
haiwai	海外报告数量	✅	✅				string		0	
sessionCode	分会场编码		✅	基于（分会场名称+meeting）生成base64编码，如果分会场名称变了，这个也变了			string			
startTime	开始时间	✅	✅				string			2025-01-01 08:00:00
endTime	结束时间	✅	✅				string			2025-01-01 08:00:00
day	日期		✅	基于时间生成			string			05月23日
week	星期		✅	基于时间生成			string	星期日、星期六、星期五、星期四、星期三、星期二、星期一		星期一
eeee	时间段		✅	基于时间生成			enum	上午、中午、下午		上午
meeting	会议编码		✅	？？？			string			chinagut2025