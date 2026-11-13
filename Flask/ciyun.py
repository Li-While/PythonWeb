import jieba  # jieba分词
from IPython.display import Image
import stylecloud
article = """心血管疾病是全球导致死亡的主要原因，研究其
发病相关的危险因素成为重要任务。据国家心血管中心统计，中
国心血管疾病现患病人数约3.3亿，其中脑卒中1300万、冠心病11
39万。面对如此高发高危的疾病，只有找到它的弱点才能与之抗衡。
将医疗系统与计算机系统有机结合，对个体心血管进行发病风险预
测评价，客观评价发病风险，提前预估，做好预防工作，这是对心
血管疾病进行预防的重要方法。通过这个方法，可以让患有心血管
病人群更加集中，极大地促进了卫生资源的合理使用。与此同时，
这也极大地降低了心血管病的发生率和死亡率。如今，国内也建立
了很多心血管评估模型，但是推广效果不甚明显。国外也有很好的
预测模型，但是由于文化、经济、人文差异性，在我国并不适用。
所以，在我国，心血管疾病预测评估模型的研究和开发有看广阔的应用前景。
本文基于心血管患者诊断数据，从患者生理指标、医疗检测指标和
患者提供的主观信息出发，使用机器学习中的集成方法对人们是否患心血管疾病进行预测。"""

# 切割
wordlist = jieba.lcut_for_search(''.join(article))
result = ' '.join(wordlist)
# print(result)

# 停用
stop_words = ['的', '进行', '也', '由于', '通过']
ciyun_words = ''

# 过滤后的词
for word in result:
    if word not in stop_words:
        ciyun_words += word
stylecloud.gen_stylecloud(text=ciyun_words,
                          icon_name='fas fa-heart',
                          collocations=False,
                          font_path=r"C:/Windows/Fonts/simfang.ttf",
                          size=400,
                          max_font_size=90,  # stylecloud 中的最大字号
                          max_words=500,  # stylecloud 可包含的最大单词数
                          gradient=None,
                          output_name='./static/image/ciyun.png')
# 可视化词云
Image(filename='./static/image/ciyun.png')
