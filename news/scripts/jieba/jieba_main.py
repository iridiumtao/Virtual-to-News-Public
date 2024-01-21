import jieba
import jieba.posseg
import jieba.analyse

news_text = """
《國際產業》郭明錤：蘋果最新版AirPods上季狂賣2700萬組
11:422022/01/04天風國際資產管理公司知名蘋果分析師郭明錤出具報告指出，蘋果在假日期間賣出2700萬組最新版AirPods，使整個2021年10～12月旺季期間其無線耳機總銷售量達到9000萬組，可望帶動其可穿戴設備業務營收較前一年同期成長20%。

去年底蘋果的可穿戴設備業務交出亮眼的成績單，今年更將是該部門重要的一年。除了郭明錤所指今年秋季將推出的新版AirPods Pro之外，蘋果可能還會推出傳聞已久的擴增實境（AR）頭戴裝置。

雖然iPhone手機仍是蘋果最重要、最賺錢的產品，但該公司以iPhone手機為核心已經發展出一個硬體配件的生態系，而且很受歡迎。



蘋果雖然沒有個別公布可穿戴裝置的銷售收入，但這項業務確實占該公司「其他產品」（Other Products）事業相當大的一部分。蘋果的「其他產品」事業包括iPhone手機殼和充電線等配件。

在2020年的10～12月季度，蘋果的「其他產品」事業營收達到近130億美元。蘋果在未來幾周公布上季財報時，該事業的表現將成為關注焦點之一。

郭明錤在報告中指出，蘋果將於今年秋季推出新版AirPods Pro 無線耳機，新產品將擁有新設計、一個在遺失時會發出嗶嗶聲的外殼，以及更好的串流音訊。他並看好這款新一代AirPods Pro耳機今年銷量可望達到2000萬組。

至於其他可穿戴裝置，彭博社周末報導蘋果的AR頭戴裝置最快可能於今年春天亮相，並於年底推出。同時臉書母司Meta今年擬發布更高階版的虛擬現實（VR）頭戴裝置。彭博並表示，蘋果今年也將推出新版Apple Watch，其中將包括更加耐用的「強固型」（ rugged）機款。

周一蘋果盤中股價一度升至182.88美元，創下歷史新高，並帶動市值站上3兆美元大關，反映出投資人相當看好蘋果仍將推出高利潤產品，而消費者也仍將願意買單。

"""


def jieba_test():
    text = """
    南韓第三季GDP數據和韓國企業巨擘的財報即將出爐，投資人態度保守，韓股在平盤上下震盪。恒大意外支付債息的消息，一度讓走勢勁揚，但是最終仍以小跌作收。週五(22日)KOSPI指數挫低0.04%(1.17點)、收3,006.16點。

過去五週來，KOSPI指數有四週收跌。

中國官媒《人民日報》旗下的《證券時報》報導，恒大集團週四支付了一筆逾期利息，總額達8,350萬美元。恒大意外付款，讓該集團避開了違約厄運。下午盤為止，香港掛牌的恒大股票上漲逾3%。

路透社報導，南韓第三季GDP下週二(26日)公布。經濟學家估計，經季節調整後，Q3 GDP季增0.6%，遜於前季的季增0.8%。和去年同期相比，Q3 GDP年增4.2%、也不及Q2的年增6.0%。主要原因是疫情肆虐導致內需萎靡，抵銷了出口暢旺的挹注。

藍籌股三星電子和SK海力士將在下週四、二公布財報。三星電子上漲0.28%、SK海力士上漲2.28%。

BusinessKorea報導，三星電子預期DRAM價格將跌，把南韓華城廠的部份DRAM產線，改為生產CMOS影像感測器。研調機構估計，全球CMOS感測器的市值，將從2020年的22兆韓圜、2024年升至29兆韓圜。

Sony和三星是CMOS的前兩大生產商，市佔分別為47.7%、19.6%。去年底為止，三星的CMOS產量為每月10萬組。

南韓電動車電池大廠Samsung SDI跟隨LG新能源腳步，週五宣布將和汽車巨擘Stellantis成立首家電池合資企業，地點設在美國。Samsung SDI攀升1.94%。

今日盤中為止，外資賣超韓股892億韓圜。


    """
    seg_list = jieba.cut(text)  # 默认是精确模式
    print(", ".join(seg_list))


def jieba_test2():
    print('=' * 40)
    print('3. 关键词提取')
    print('-' * 40)
    print(' TF-IDF')
    print('-' * 40)

    s = news_text
    for x, w in jieba.analyse.extract_tags(s, withWeight=True):
        print('%s %s' % (x, w))

    print('-' * 40)
    print(' TextRank')
    print('-' * 40)

    for x, w in jieba.analyse.textrank(s, withWeight=True):
        print('%s %s' % (x, w))

    print('=' * 40)
    print('4. 词性标注')
    print('-' * 40)

    words = jieba.posseg.cut("我爱北京天安门")
    for word, flag in words:
        print('%s %s' % (word, flag))

    print('=' * 40)
    print('6. Tokenize: 返回词语在原文的起止位置')
    print('-' * 40)
    print(' 默认模式')
    print('-' * 40)

    result = jieba.tokenize('永和服装饰品有限公司')
    for tk in result:
        print("word %s\t\t start: %d \t\t end:%d" % (tk[0], tk[1], tk[2]))

    print('-' * 40)
    print(' 搜索模式')
    print('-' * 40)

    result = jieba.tokenize('永和服装饰品有限公司', mode='search')
    for tk in result:
        print("word %s\t\t start: %d \t\t end:%d" % (tk[0], tk[1], tk[2]))


if __name__ == '__main__':
    print("hi")
    jieba_test2()
