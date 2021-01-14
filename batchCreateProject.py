#!/usr/bin/env python3

"""
这个脚本 用来 快速创建项目，并填充部分 测试数据, 需保证python环境中 pymongo 已安装
"""

import pymongo
import random 
import time

print('begin ...')

#client = pymongo.MongoClient('mongodb://root:root@114.67.113.229:8004/') # production
client = pymongo.MongoClient('mongodb://root:root@localhost:27017/')

mydb  = client['KWM']
# 1 创建项目
projectName = '项目'+ str(random.randint(1,10000))
tstamp =  time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())
projectInfo = {'projectName':projectName,'creater':'whsasf@qq.com',"timestamp" :tstamp}
result1 = mydb['Project'].insert_one(projectInfo)
pid = str(result1.inserted_id)


#2- 给项目 创建 分类

mydb2  = client['KWM' + '-' + pid]

categories= [
    {'categoryName': '视频'},
    {'categoryName': '音频'},
    {'categoryName': '美食' },
    {'categoryName': '潮流' },
    {'categoryName': '文学' },
    {'categoryName': '化学' },
    {'categoryName': '神学' },
    {'categoryName': '玄学' },
    {'categoryName': '物理学' },
    {'categoryName': '计算机科学' },
    {'categoryName': '自动化' }
    ]

result2 = mydb2['Categories'].insert_many(categories)


# 3- 给项目 添加URL 管理
print('url')
Urls = [
    {"modifiedTime" : "2020/09/22 13:28:14", "rootUrl" : "https://www.baidu.com", "category" : [ "视频", "物理学", "玄学" ], "status" : "未开始", "urlExcludePath" : [ { "path" : "https://www.baidu.com/name-1", "type" : "regex" }, { "path" : "http://www.baidu.com/include1", "type" : "包含" } ], "urlIncludePath" : [ { "path" : "https://www.baidu.com/exclude1", "type" : "regex" }, { "path" : "https://www.baidu.com/exclude2", "type" : "regex" }]},
    {"modifiedTime" : "2020/09/21 14:28:14", "rootUrl" : "https://www.stockhey.com", "category" : [ "自动化", "计算机科学", "潮流" ], "status" : "未开始", "urlExcludePath" : [ { "path" : "https://www.stockhey.com/name-1", "type" : "regex" }, { "path" : "http://www.stockhey.com/exclude1", "type" : "包含" } ], "urlIncludePath" : [ { "path" : "https://www.stockhey.com/include1", "type" : "regex" }, { "path" : "https://www.stockhey.com/include2", "type" : "包含" }]},
    {"modifiedTime" : "2020/09/20 16:28:14", "rootUrl" : "https://www.qq.com", "category" : [ "美食", "物理学", "化学" ], "status" : "未开始", "urlExcludePath" : [ { "path" : "https://www.qq.com/name-1", "type" : "regex" }, { "path" : "http://www.qq.com/exclude1", "type" : "包含" } ], "urlIncludePath" : [ { "path" : "https://www.qq.com/include1", "type" : "regex" }, { "path" : "https://www.qq.com/include2", "type" : "regex" }]},
    {"modifiedTime" : "2020/09/23 06:28:14", "rootUrl" : "http://www.dianbaobao.com", "category" : [ "音频", "文学", "视频" ], "status" : "未开始", "urlExcludePath" : [ { "path" : "https://www.dianbaobao.com/name-1", "type" : "regex" }, { "path" : "http://www.dianbaobao.com/exclude1", "type" : "包含" } ], "urlIncludePath" : [ { "path" : "https://www.dianbaobao.com/exclude1", "type" : "regex" }, { "path" : "https://www.dianbaobao.com/include2", "type" : "regex" }]},
    {"modifiedTime" : "2020/09/24 03:28:14", "rootUrl" : "https://www.88.com", "category" : [ "计算机科学", "物理学", "玄学" ], "status" : "未开始", "urlExcludePath" : [ { "path" : "https://www.88.com/name-1", "type" : "regex" }, { "path" : "http://www.88.com/exclude1", "type" : "包含" } ], "urlIncludePath" : [ { "path" : "https://www.88.com/include1", "type" : "regex" }, { "path" : "https://www.88.com/include2", "type" : "regex" }]}
]

result3 = mydb2['Urls'].insert_many(Urls)

# 4- 给项目添加 Articles
print('语料')
articles = [
    {"modifiedTime" : "2020/09/22 17:23:25",'Length': 34, "root" : "1.txt", "url" : "1-20203203023.txt", "title" : "店宝宝", "keywords" : [ "红色", "绿色", "蓝色" ], "desciption" : "这是一个电商培训网站", "rawContent" : "帮你开店免费的", "body" : "那是最美好的时代，那是最糟糕的时代；那是智慧的年头，那是愚昧的年头；那是信仰的时期，那是怀疑的时期；那是光明的季节，那是黑暗的季节；那是希望的春天，那是失望的冬天；我们全都在直奔天堂，我们全都在直奔相反的方向——简而言之，那时跟现在非常相象，某些最喧嚣的权威坚持要用形容词的最高级来形容它。说邮车它好，是最高级的；说它不好，也是最高级的。",   "category" : [ "视频", "物理学" ], "status" : "已添加"},
    {"modifiedTime" : "2020/09/21 20:23:25",'Length': 35, "root" : "https://www.baidu.com", "url" : "https://www.baidu.com/haha", "title" : "经典文案", "keywords" : [ "双城记", "狄更斯", "英国" ], "desciption" : "这是一个经典名著", "rawContent" : "好看的经典名著", "body" : "那是耶稣纪元一干七百七十五年。灵魂启示在那个受到欢迎的时期跟现在一样在英格兰风行一时。骚斯柯特太太刚满了她幸福的二十五岁，王室卫队一个先知的士兵已宣布这位太太早已作好安排，要使伦敦城和西敏寺陆沉，从而为她崇高形象的出现开辟道路。即使雄鸡巷的幽灵在咄咄逼人地发出它的预言之后销声匿迹整整十二年，去年的精灵们咄咄逼人发出的预言仍跟她差不多，只是少灵魂了几分超自然的独创性而已。前不久英国国王和英国百姓才得到一些人世间的消息。那是从远在美洲的英国臣民的国会传来的。说来奇怪，这些信息对于人类的影响竟然比雄鸡巷魔鬼的子孙们的预言还要巨大",  "category" : [ "计算机科学", "文学" ], "status" : "已添加"},
    {"modifiedTime" : "2020/09/21 20:23:25",'Length': 35, "root" : "https://www.baidu.com", "url" : "https://www.baidu.com/haha2", "title" : "经典文案", "keywords" : [ "双城记", "狄更斯", "英国" ], "desciption" : "这是一个经典名著", "rawContent" : "好看的经典名著", "body" : "耶稣纪元一干七百七十五年。灵魂启示在那个受到欢迎的时期跟现在一样在英格兰风行一时。骚斯柯特太太刚满了她幸福的二十五岁，王室卫队一个先知的士兵已宣布这位太太早已作好安排，要使伦敦城和西敏寺陆沉，从而为她崇高形象的出现开辟道路。即使雄鸡巷的幽灵在咄咄逼人地发出它的预言之后销声匿迹整整十二年，去年的精灵们咄咄逼人发出的预言仍跟她差不多，只是少灵魂了几分超自然的独创性而已。前不久英国国王和英国百姓才得到一些人世间的消息。那是从远在美洲的英国臣民的国会传来的。说来奇怪，这些信息对于人类的影响竟然比雄鸡巷魔鬼的子孙们的预言还要巨大",   "category" : [ "计算机科学", "文学" ], "status" : "已添加"},
    {"modifiedTime" : "2020/09/23 19:23:25",'Length': 32, "root" : "https://www.qq.com", "url" : "https://www.qq.com/wenxue", "title" : "q文学", "keywords" : [ "马化腾", "马云", "黑色" ], "desciption" : "这是一个名人网站", "rawContent" : "谁说不是呢", "body" : "法兰西的灵异事物大灵魂体不如她那以盾和三叉戟为标志的姐妹那么受宠。法兰西正在一个劲儿地往坡下滑，印制着钞票，使用着钞票。除此之外她也在教士们的指引下建立些仁慈的功勋，寻求点乐趣。比如判决一个青年斩去双手，用钳子拔掉舌头，然后活活烧死，因为他在一群和尚的肮脏仪仗队从五六十码之外他看得见的地方经过时，竟然没有跪倒在雨地里向它致敬。而在那人被处死时，生长在法兰西和挪威森林里的某些树木很可能已被“命运”这个樵夫看中，要砍倒它们，锯成木板，做成一种在历史上以恐怖著名的可以移动的架子，其中包含了一个口袋和一把铡刀。而在同一天，巴黎近郊板结的土地上某些农户的简陋的小披屋里也很可能有一些大车在那儿躲避风雨。那些车很粗糙，溅满了郊野的泥浆，猪群在它旁边嗅着，家禽在它上面栖息。这东西也极有可能已被“死亡”这个农民看中，要在革命时给它派上死囚囚车的用场。可是那“樵夫”和“农民”尽管忙个不停，却总是默不作声，蹑手蹑脚，不让人听见。因此若是有人猜想到他们已在行动，反倒会被看作是无神论和大逆不道",   "category" : [ "音频", "玄学" ], "status" : "已添加"},
    {"modifiedTime" : "2020/09/20 07:23:25",'Length': 56, "root" : "2.csv", "url" : "2-20203433203023.csv", "title" : "三国杀", "keywords" : [ "刘备", "张飞", "诸葛亮" ], "desciption" : "三国历史名人传", "rawContent" : "三国历史名人传", "body" : "诸如此类的现象，还加上一千桩类似的事件，就像这样在可爱的古老的一千七百七十五年相继发生，层出不穷。在这些事件包围之中，“樵夫”和“农民”仍然悄悄地干着活，而那两位大下巴和另外两张平常的和姣好的面孔却都威风凛凛，专横地运用着他们神授的君权。一干七百七十五年就是像这样表现出了它的伟大，也把成干上万的小人物带上了他们时代前面的路——我们这部历史中的几位也在其中", "category" : [ "潮流", "自动化" ], "status" : "已添加"},
    {"modifiedTime" : "2020/09/24 05:23:25",'Length': 78, "root" : "https://www.stockhey.com", "url" : "https://www.stockhey.com/sdsdsd/sdsds", "title" : "我的网站", "keywords" : [ "睡觉", "吃饭", "喝娃哈哈" ], "desciption" : "世界很奇妙", "rawContent" : "尽在无线掌控", "body" : "除了刚才那人之外，还有两个人也在邮车旁艰难地行进。三个人都一直裹到颧骨和耳朵，都穿着长过膝盖的高统靴，彼此都无法根据对方的外表辨明他们的容貌。三个人都用尽多的障碍包裹住自己，不让同路人心灵的眼睛和肉体的眼睛看出自己的形迹。那时的旅客都很警惕，从不轻易对人推心置腹，因为路上的人谁时代都可能是强盗或者跟强盗有勾结。后者的出现是非常可能的，因为当时每一个邮车站，每一家麦酒店都可能有人“拿了老大的钱”，这些人从老板到最糟糕的马厩里的莫名其妙的人都有，这类花样非常可能出现。一千七百七十五年十一月底的那个星期五晚上，多佛邮车的押车卫士心里就是这么想的。那时他正随着隆隆响着的邮车往射手山上爬。他站在邮件车厢后面自己的专用踏板上，跺着脚，眼睛不时瞧着面前的武器箱，手也搁在那箱上。箱里有一把子弹上膛的大口径短抢，下面是六或八支上好子弹的马枪，底层还有一把短剑。", "category" : [ "视频", "物理学" ], "status" : "已添加"}
]

result4 = mydb2['Articles'].insert_many(articles)

# 5- 给项目 添加 basicWords
print('基础词')
mybasicWords = [
{"category" : [ "神学", "玄学" ], "source" : [ "1-20203203023.txt", "2-20203433203023.csv",'https://www.stockhey.com/sdsdsd/sdsds','手动添加' ], "word" : "时代",  "status" : "已添加", "weight" : 30,"timestamp" : "2020/09/24 19:18:12", 'Length': 100},
{"category" : [ "计算机科学", "自动化" ], "source" : [ "https://www.baidu.com/haha", "https://www.qq.com/wenxue",'手动添加'], "word" : "灵魂",  "status" : "已添加", "weight" : 20,"timestamp" : "2020/09/23 12:18:12", 'Length': 200},
{"category" : [ "美学", "视频",'音频' ], "source" : [ "1-20203203023.txt",'https://www.stockhey.com/sdsdsd/sdsds' ], "word" : "邮车",  "status" : "已添加", "weight" : 10,"timestamp" : "2020/09/21 16:18:12", 'Length': 300},
{"category" : [ "美学", "视频",'音频' ], "source" : [ '手动添加' ], "word" : "世界",  "status" : "已添加", "weight" : 8,"timestamp" : "2020/09/23 09:18:12", 'Length': 150},
{"category" : [ "音频", "神学"], "source" : [ '手动添加' ], "word" : "美丽",  "status" : "已添加", "weight" : 1,"timestamp" : "2020/09/23 09:16:12", 'Length': 50},
{"category" : [ "化学", "玄学"], "source" : [ '手动添加' ], "word" : "故乡",  "status" : "已添加", "weight" : 0,"timestamp" : "2020/08/23 09:16:12", 'Length': 30}
]

result5 = mydb2['basicWords'].insert_many(mybasicWords)

# 6- 给项目添加 拓展词
print('拓展词')
myextendedWords=[
 {"word" : "挣大钱", "category" : [ "化学","视频" ], "mword" : "灵魂", "baiduIndex" : 10, "searchCount" : 100, "bidPrice" : 100, "baiduIndexM" : 100, "searchCountM" : 100, "bidPriceM" : 100,  "baiduComment" : "很好啊", "usageTag" : [ "tag1", "tag2","tag3" ], "source" : "百度索引", "status" : "停止", "timestamp" : "2020/09/22 16:13:26", "Length" : 5},
 {"word" : "美好", "category" : [ "美学","物理学" ], "mword" : "时代", "baiduIndex" : 200, "searchCount" : 400, "bidPrice" : 200, "baiduIndexM" : 100, "searchCountM" : 100, "bidPriceM" : 100,"baiduComment" : "good", "usageTag" : [ "tag1", "tag2","tag4","tag5" ], "source" : "百度索引", "status" : "无效", "timestamp" : "2020/09/22 14:13:26", "Length" : 6},
 {"word" : "狐狸精", "category" : [ "计算机科学","视频" ], "mword" : "灵魂", "baiduIndex" : 30, "searchCount" : 600, "bidPrice" : 300,"baiduIndexM" : 100, "searchCountM" : 100, "bidPriceM" : 100, "baiduComment" : "bad", "usageTag" : [ "tag1", "tag2","tag5","tag8" ], "source" : "百度索引", "status" : "已添加", "timestamp" : "2020/09/22 17:13:26", "Length" : 7},
 {"word" : "公积金", "category" : [ "玄学","视频" ], "mword" : "时代", "baiduIndex" : 500, "searchCount" : 800, "bidPrice" : 400,"baiduIndexM" : 100, "searchCountM" : 100, "bidPriceM" : 100, "baiduComment" : "nice", "usageTag" : [ "tag1", "tag2" ,"tag9","tag3"], "source" : "百度索引", "status" : "已添加", "timestamp" : "2020/09/22 00:13:26", "Length" : 8},
 {"word" : "中国移动", "category" : [ "音频","视频" ], "mword" : "邮车", "baiduIndex" : 700, "searchCount" : 200, "bidPrice" : 500,"baiduIndexM" : 100, "searchCountM" : 100, "bidPriceM" : 100, "baiduComment" : "hello", "usageTag" : [ "tag1", "tag2" ,"tag7"], "source" : "百度索引", "status" : "已添加", "timestamp" : "2020/09/22 09:13:26", "Length" : 9},
 {"word" : "歌手", "category" : [ "化学","视频" ], "mword" : "灵魂", "baiduIndex" : 100, "searchCount" : 100, "bidPrice" : 100,"baiduIndexM" : 100, "searchCountM" : 100, "bidPriceM" : 100, "baiduComment" : "很好啊", "usageTag" : [ "tag1", "tag2","tag3" ], "source" : "百度索引", "status" : "停止", "timestamp" : "2020/09/22 16:13:26", "Length" : 5},
 {"word" : "能人", "category" : [ "美学","物理学" ], "mword" : "时代", "baiduIndex" : 200, "searchCount" : 400, "bidPrice" : 200,"baiduIndexM" : 100, "searchCountM" : 100, "bidPriceM" : 100, "baiduComment" : "good", "usageTag" : [ "tag1", "tag2","tag4","tag5" ], "source" : "百度索引", "status" : "无效", "timestamp" : "2020/09/22 14:13:26", "Length" : 6},
 {"word" : "战车", "category" : [ "计算机科学","视频" ], "mword" : "灵魂", "baiduIndex" : 300, "searchCount" : 400, "bidPrice" : 300,"baiduIndexM" : 100, "searchCountM" : 100, "bidPriceM" : 100, "baiduComment" : "bad", "usageTag" : [ "tag1", "tag2","tag5","tag8" ], "source" : "百度索引", "status" : "已添加", "timestamp" : "2020/09/22 17:13:26", "Length" : 7},
 {"word" : "败类", "category" : [ "玄学","视频" ], "mword" : "时代", "baiduIndex" : 500, "searchCount" : 800, "bidPrice" : 400,"baiduIndexM" : 100, "searchCountM" : 100, "bidPriceM" : 100, "baiduComment" : "nice", "usageTag" : [ "tag1", "tag2" ,"tag9","tag3"], "source" : "百度索引", "status" : "已添加", "timestamp" : "2020/09/22 00:13:26", "Length" : 8},
 {"word" : "电信", "category" : [ "音频","视频" ], "mword" : "邮车", "baiduIndex" : 700, "searchCount" : 200, "bidPrice" : 500,"baiduIndexM" : 100, "searchCountM" : 100, "bidPriceM" : 100, "baiduComment" : "hello", "usageTag" : [ "tag1", "tag2" ,"tag7"], "source" : "百度索引", "status" : "已添加", "timestamp" : "2020/09/22 09:13:26", "Length" : 9},
 {"word" : "烫头", "category" : [ "化学","视频" ], "mword" : "灵魂", "baiduIndex" : 100, "searchCount" : 100, "bidPrice" : 100, "baiduIndexM" : 100, "searchCountM" : 100, "bidPriceM" : 100,"baiduComment" : "很好啊", "usageTag" : [ "tag1", "tag2","tag3" ], "source" : "百度索引", "status" : "停止", "timestamp" : "2020/06/22 16:13:26", "Length" : 5},
 {"word" : "楷模", "category" : [ "美学","物理学" ], "mword" : "时代", "baiduIndex" : 200, "searchCount" : 400, "bidPrice" : 200, "baiduIndexM" : 100, "searchCountM" : 100, "bidPriceM" : 180,"baiduComment" : "good", "usageTag" : [ "tag1", "tag2","tag4","tag5" ], "source" : "百度索引", "status" : "无效", "timestamp" : "2020/07/22 14:13:26", "Length" : 6},
 {"word" : "大熊", "category" : [ "计算机科学","视频" ], "mword" : "灵魂", "baiduIndex" : 300, "searchCount" : 600, "bidPrice" : 300,"baiduIndexM" : 100, "searchCountM" : 100, "bidPriceM" : 100, "baiduComment" : "bad", "usageTag" : [ "tag1", "tag2","tag5","tag8" ], "source" : "百度索引", "status" : "已添加", "timestamp" : "2020/09/22 17:13:26", "Length" : 7},
 {"word" : "正义", "category" : [ "玄学","视频" ], "mword" : "时代", "baiduIndex" : 500, "searchCount" : 800, "bidPrice" : 400, "baiduIndexM" : 500, "searchCountM" : 100, "bidPriceM" : 100,"baiduComment" : "nice", "usageTag" : [ "tag1", "tag2" ,"tag9","tag3"], "source" : "百度索引", "status" : "已添加", "timestamp" : "2020/09/12 00:13:26", "Length" : 8},
 {"word" : "联通", "category" : [ "音频","视频" ], "mword" : "邮车", "baiduIndex" : 700, "searchCount" : 200, "bidPrice" : 500, "baiduIndexM" : 100, "searchCountM" : 100, "bidPriceM" : 100,"baiduComment" : "hello", "usageTag" : [ "tag1", "tag2" ,"tag7"], "source" : "百度索引", "status" : "已添加", "timestamp" : "2020/09/22 09:13:26", "Length" : 9},
 {"word" : "欺骗", "category" : [ "化学","视频" ], "mword" : "挣大钱", "baiduIndex" : 100, "searchCount" : 100, "bidPrice" : 100,"baiduIndexM" : 100, "searchCountM" : 100, "bidPriceM" : 100, "baiduComment" : "很好啊", "usageTag" : [ "tag1", "tag2","tag3" ], "source" : "百度索引", "status" : "停止", "timestamp" : "2020/09/22 16:13:26", "Length" : 5},
 {"word" : "报警", "category" : [ "美学","物理学" ], "mword" : "欺骗", "baiduIndex" : 200, "searchCount" : 400, "bidPrice" : 200,"baiduIndexM" : 100, "searchCountM" : 100, "bidPriceM" : 100, "baiduComment" : "good", "usageTag" : [ "tag1", "tag2","tag4","tag5" ], "source" : "百度索引", "status" : "无效", "timestamp" : "2020/09/22 14:13:26", "Length" : 6},
 {"word" : "打人", "category" : [ "计算机科学","视频" ], "mword" : "狐狸精", "baiduIndex" : 300, "searchCount" : 600, "bidPrice" : 300,"baiduIndexM" : 100, "searchCountM" : 100, "bidPriceM" : 100, "baiduComment" : "bad", "usageTag" : [ "tag1", "tag2","tag5","tag8" ], "source" : "百度索引", "status" : "已添加", "timestamp" : "2020/09/22 17:13:26", "Length" : 7},
 {"word" : "芒果卫视", "category" : [ "玄学","视频" ], "mword" : "歌手", "baiduIndex" : 500, "searchCount" : 800, "bidPrice" : 400,"baiduIndexM" : 100, "searchCountM" : 100, "bidPriceM" : 100, "baiduComment" : "nice", "usageTag" : [ "tag1", "tag2" ,"tag9","tag3"], "source" : "百度索引", "status" : "已添加", "timestamp" : "2020/09/22 00:13:26", "Length" : 8},
 {"word" : "周杰伦", "category" : [ "音频","视频" ], "mword" : "歌手", "baiduIndex" : 700, "searchCount" : 200, "bidPrice" : 500, "baiduIndexM" : 100, "searchCountM" : 100, "bidPriceM" : 100,"baiduComment" : "hello", "usageTag" : [ "tag1", "tag2" ,"tag7"], "source" : "百度索引", "status" : "已添加", "timestamp" : "2020/09/22 09:13:26", "Length" : 9},
 {"word" : "抓小偷", "category" : [ "化学","视频" ], "mword" : "正义", "baiduIndex" : 100, "searchCount" : 100, "bidPrice" : 100,"baiduIndexM" : 100, "searchCountM" : 100, "bidPriceM" : 100, "baiduComment" : "很好啊", "usageTag" : [ "tag1", "tag2","tag3" ], "source" : "百度索引", "status" : "停止", "timestamp" : "2020/09/22 16:13:26", "Length" : 5},
 {"word" : "于谦", "category" : [ "美学","物理学" ], "mword" : "烫头", "baiduIndex" : 2000, "searchCount" : 400, "bidPrice" : 200,"baiduIndexM" : 100, "searchCountM" : 100, "bidPriceM" : 100, "baiduComment" : "good", "usageTag" : [ "tag1", "tag2","tag4","tag5" ], "source" : "百度索引", "status" : "无效", "timestamp" : "2020/09/22 14:13:26", "Length" : 6},
 {"word" : "德云社", "category" : [ "计算机科学","视频" ], "mword" : "于谦", "baiduIndex" : 300, "searchCount" : 600, "bidPrice" : 300,"baiduIndexM" : 100, "searchCountM" : 100, "bidPriceM" : 100, "baiduComment" : "bad", "usageTag" : [ "tag1", "tag2","tag5","tag8" ], "source" : "百度索引", "status" : "已添加", "timestamp" : "2020/09/22 17:13:26", "Length" : 7},
 {"word" : "拓扑", "category" : [ "玄学","视频" ], "mword" : "联通", "baiduIndex" : 500, "searchCount" : 800, "bidPrice" : 400,"baiduIndexM" : 100, "searchCountM" : 100, "bidPriceM" : 100, "baiduComment" : "nice", "usageTag" : [ "tag1", "tag2" ,"tag9","tag3"], "source" : "百度索引", "status" : "已添加", "timestamp" : "2020/09/22 00:13:26", "Length" : 8},
 {"word" : "叮当猫", "category" : [ "音频","视频" ], "mword" : "大熊", "baiduIndex" : 700, "searchCount" : 200, "bidPrice" : 500,"baiduIndexM" : 100, "searchCountM" : 100, "bidPriceM" : 100, "baiduComment" : "hello", "usageTag" : [ "tag1", "tag2" ,"tag7"], "source" : "百度索引", "status" : "已添加", "timestamp" : "2020/09/22 09:13:26", "Length" : 9},
 {"word" : "打记者", "category" : [ "化学","视频" ], "mword" : "德云社", "baiduIndex" : 100, "searchCount" : 100, "bidPrice" : 100,"baiduIndexM" : 100, "searchCountM" : 100, "bidPriceM" : 100, "baiduComment" : "很好啊", "usageTag" : [ "tag1", "tag2","tag3" ], "source" : "百度索引", "status" : "停止", "timestamp" : "2020/09/22 16:13:26", "Length" : 5},
 {"word" : "莫吉托", "category" : [ "美学","物理学" ], "mword" : "周杰伦", "baiduIndex" : 200, "searchCount" : 400, "bidPrice" : 200,"baiduIndexM" : 10, "searchCountM" : 100, "bidPriceM" : 100, "baiduComment" : "good", "usageTag" : [ "tag1", "tag2","tag4","tag5" ], "source" : "百度索引", "status" : "无效", "timestamp" : "2020/09/22 14:13:26", "Length" : 6},
 {"word" : "伪君子", "category" : [ "计算机科学","视频" ], "mword" : "楷模", "baiduIndex" : 300, "searchCount" : 600, "bidPrice" : 300,"baiduIndexM" : 400, "searchCountM" : 100, "bidPriceM" : 100, "baiduComment" : "bad", "usageTag" : [ "tag1", "tag2","tag5","tag8" ], "source" : "百度索引", "status" : "已添加", "timestamp" : "2020/09/22 17:13:26", "Length" : 7},
 {"word" : "江疏影", "category" : [ "音频","视频" ], "mword" : "美丽", "baiduIndex" : 700, "searchCount" : 200, "bidPrice" : 500,"baiduIndexM" : 100, "searchCountM" : 100, "bidPriceM" : 100, "baiduComment" : "hello", "usageTag" : [ "tag1", "tag2" ,"tag7"], "source" : "百度索引", "status" : "已添加", "timestamp" : "2020/09/22 09:13:26", "Length" : 9},
 {"word" : "回家", "category" : [ "玄学","视频" ], "mword" : "流浪者", "baiduIndex" : 500, "searchCount" : 800, "bidPrice" : 400, "baiduIndexM" : 100, "searchCountM" : 100, "bidPriceM" : 100,"baiduComment" : "nice", "usageTag" : [ "tag1", "tag2" ,"tag9","tag3"], "source" : "百度索引", "status" : "已添加", "timestamp" : "2020/09/22 00:13:26", "Length" : 8},
 {"word" : "菊次郎", "category" : [ "音频","视频" ], "mword" : "故乡", "baiduIndex" : 700, "searchCount" : 200, "bidPrice" : 500, "baiduIndexM" : 100, "searchCountM" : 100, "bidPriceM" : 100,"baiduComment" : "hello", "usageTag" : [ "tag1", "tag2" ,"tag7"], "source" : "百度索引", "status" : "已添加", "timestamp" : "2020/09/22 09:13:26", "Length" : 9},
 {"word" : "宫崎骏", "category" : [ "玄学","视频" ], "mword" : "菊次郎", "baiduIndex" : 500, "searchCount" : 800, "bidPrice" : 400, "baiduIndexM" : 100, "searchCountM" : 100, "bidPriceM" : 100,"baiduComment" : "nice", "usageTag" : [ "tag1", "tag2" ,"tag9","tag3"], "source" : "百度索引", "status" : "已添加", "timestamp" : "2020/09/22 00:13:26", "Length" : 8},
 {"word" : "你奶奶", "category" : [ "音频","视频" ], "mword" : "美丽", "baiduIndex" : 700, "searchCount" : 200, "bidPrice" : 50, "baiduIndexM" : 100, "searchCountM" : 100, "bidPriceM" : 100,"baiduComment" : "hello", "usageTag" : [ "tag1", "tag2" ,"tag7"], "source" : "百度索引", "status" : "已添加", "timestamp" : "2020/09/22 09:13:26", "Length" : 9}
]
result6 = mydb2['extendedWords'].insert_many(myextendedWords)

print('end ...')

