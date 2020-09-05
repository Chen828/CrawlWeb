import urllib.parse
import urllib.request
# from time import sleep      # 无需睡眠，爬取速度主要与网络环境有关
import pymysql
from lxml import etree
"""
题目类型title_type 题目title 下载download 关键字keyword 作者author 单位unit DOI doi_url
出版名publisher_name 条目索引编号entries_num 丛书卷coverage(总共多少卷、期）
印刷ISBN：print_isbn 电子ISBN：online_isbn 印刷ISSN:print_issn 电子ISSN:online_issn
丛书印刷ISSN：series_print_issn 丛书电子ISSN：series_online_issn
"""


class crawlSpringer:

    def __init__(self, keyword):
        self.key_encode = urllib.parse.quote(keyword)  # 编码
        content_response = urllib.request.urlopen("https://link.springer.com/search?query=" + self.key_encode)
        # print(content_response)
        content_data = content_response.read().decode('utf-8')  # 读取反馈信息

        """
        当python爬虫遇到urlopen超时10060错误，分析
        单击连接，可以在浏览器正常打开，说明该站点是可以访问的。
        同样的脚本放在公司的体验网上运行OK，说明脚本本身没有问题。
        通过以上两个步骤，初步判断是公司对于外网的访问策略限制导致的。于是查找了下如何给urllib。request设置ProxyHandler代理 ，将代码修改为如下："""
        # The proxy address and port:
        proxy_info = {'host': 'web-proxy.oa.com', 'port': 8080}

        # We create a handler for the proxy
        proxy_support = urllib.request.ProxyHandler({"http": "http://%(host)s:%(port)d" % proxy_info})

        # We create an opener which uses this handler:
        opener = urllib.request.build_opener(proxy_support)

        # Then we install this opener as the default opener for urllib2:
        urllib.request.install_opener(opener)

        # print(content_data)
        self.content_page(content_data)

    # 打开网页链接
    """
    当用多线程爬取网站出现urlopen error [errno 10060]的错误，也就是连接失败。
    原因是多个线程爬去某个网站的数据，每次连接完需要sleep(1)一会，不然该网站服务端的防火墙会ban掉你的connect。
    睡眠等待机制会减少urlopen error [errno 10060]出现的概率，但访问次数多了还是会出现.
    之后看了网上说法是连接时网络不稳定造成的，于是写了个多次尝试连接的函数
    """

    @staticmethod
    def xpath_exist(page, xpath):
        try:
            select = etree.HTML(page)  # 将源码转化为能被XPath匹配的格式
            select.xpath(xpath)
            return True
        except ():
            return False
        pass

    def content_page(self, content_data):
        page_num = 1  # 页数
        print('第' + str(page_num) + '页')

        # 页码循环
        while True:  # 先获取列表按长度for循环，再判断下一页是否存在
            select = etree.HTML(content_data)  # 将源码转化为能被XPath匹配的格式
            try:
                href_list = select.xpath('//a[@class="title"]/@href')  # 每个题目的不完整专属链接,列表[0,20]
                type_list_original = select.xpath('//p[@class="content-type"]/text()')  # 每个题目的所属类型,列表
                # title_list = select.xpath('//a[@class="title"]/text()')   # 每个题目
            except():
                print('Sorry – we couldn’t find what you are looking for. Why not... ')
            print(href_list)

            """
                type_list_original含有空元素，影响按序、根据题目类型选择不同函数，所以需要去空元素
                方法： 删除列表空值或者准确获取text而不会使子层span成一个新的列表值
            """
            # 整理标题类型原始列表type_list_original
            type_list = []
            for i in range(len(type_list_original)):
                # 去除文本中空格和包含子标签所产生的\n
                element = type_list_original[i].replace('\n', '').replace(' ', '')
                if element != '':  # 去除列表中的空元素
                    type_list.append(element)
            # type_list = select.xpath('//p[@class="content-type"]/text()')  # 每个题目的所属类型,列表
            # title_type = type_list[i].xpath('string(.)').strip()
            print(type_list)

            # 列表内题目循环；
            """
            或者for循环，判断若有出版标题publication-title，则直接获取原文href，若无，则获取当前题目href；
            在此是先进入子标题，若为chapter或者refenceworkentry再进入publication-title，若为book则停留在当前详情页
           """
            for i in range(len(href_list)):
                print('第' + str(i + 1) + '条目')

                # 根据题目类型匹配各种详情页；此判断顺序按一般搜索各题目类型的数量由多到少，效率最高

                if type_list[i] == 'Chapter' or type_list[i] == 'ReferenceWorkEntry':  # 最多
                    default_url = 'https://link.springer.com' + href_list[i]  # 构造详情页url
                    print(default_url)
                    # 请求default_url

                    default_response = urllib.request.urlopen(default_url)

                    default_data = default_response.read().decode('utf-8')  # 读取反馈信息

                    self.middle_default_page(type_list[i], default_data)  # 定位、读取元数据

                elif type_list[i] == 'Article' \
                        or type_list[i] == 'ChapterandConferencePaper' \
                        or type_list[i] == 'Protocol' \
                        or type_list[i] == 'BookandConferenceProceedings' \
                        or type_list[i] == 'BookandReferenceWork' \
                        or type_list[i] == 'BookandLivingReferenceWork(Continuouslyupdatededition)' \
                        or type_list[i] == 'Journal' \
                        or type_list[i] == 'BookSeries':
                    default_url = 'https://link.springer.com' + href_list[i]  # 构造详情页url
                    print(default_url)

                    default_response = urllib.request.urlopen(default_url)

                    default_data = default_response.read().decode('utf-8')  # 读取反馈信息

                    self.default_page(type_list[i], default_data)  # 定位、读取元数据

                elif type_list[i] == 'Book':
                    default_url = 'https://link.springer.com' + href_list[i] + '#about'  # 构造详情页url
                    print(default_url)

                    default_response = urllib.request.urlopen(default_url)

                    default_data = default_response.read().decode('utf-8')  # 读取反馈信息

                    self.default_page(type_list[i], default_data)  # 定位、读取元数据

                else:
                    print('一种新的题目类型')

            # 目录页的下一页
            try:
                page_num = page_num + 1  # 页数+1
                print('第' + str(page_num) + '页')
                page_url = 'https://link.springer.com/search/page/' + str(page_num) + '?query=' + self.key_encode
                print('url:' + page_url)
                content_response = urllib.request.urlopen(page_url)
                content_data = content_response.read().decode('utf-8')  # 读取反馈信息
            except urllib.request.URLError:
                break

    # 若合并各相似的详情页方法，运行期间会多很多的判断，个人认为相对复杂、低效
    # 但是代码量少，规整

    # 中间链接
    def middle_default_page(self, type_list, default_data):
        # 在详情页获取引文链接，进入引文页面
        select = etree.HTML(default_data)  # 将源码转化为能被XPath匹配的格式

        # 引文链接
        cite_url = ''
        if self.xpath_exist(default_data, '//a[@class="gtm-book-link"]'):
            cite = select.xpath('//a[@class="gtm-book-link"]/@href')  # 获取引文fref链接
            print(cite[0])
            cite_url = 'https://link.springer.com' + cite[0] + '#about'  # 构造cite_url
        elif self.xpath_exist(default_data, '//a[@class="unified-header__link gtm-book-link"]'):
            cite = select.xpath('//a[@class="unified-header__link gtm-book-link"]/@href')  # 获取引文fref链接
            cite_url = 'https://link.springer.com' + cite[0]  # 构造cite_url
        print(cite_url)

        # 请求cite_url
        cite_response = urllib.request.urlopen(cite_url)

        # 读取反馈信息
        cite_data = cite_response.read().decode('utf-8')

        # 调用default_page
        self.default_page(type_list, cite_data)

    # 详情页
    def default_page(self, type_list, default_data):
        # title_type
        title_type = ''.join(type_list)

        # 将源码转化为能被XPath匹配的格式
        select = etree.HTML(default_data)

        # xpath获取数据

        if self.xpath_exist(default_data, '//h1[@class="ArticleTitle"]'):
            title = select.xpath('//h1[@class="ArticleTitle"]/text()')
            print(title)
        elif self.xpath_exist(default_data, '//h1[@class="ChapterTitle"]'):
            title = select.xpath('//h1[@class="ChapterTitle"]/text()')
            print(title)
        elif self.xpath_exist(default_data, '//div[@id="book-title"]/h1'):
            title = select.xpath('//div[@id="book-title"]/h1/text()')
            print(title)
        elif self.xpath_exist(default_data, '//a[@class="unified-header__link gtm-book-link"]'):
            title = select.xpath('//a[@class="unified-header__link gtm-book-link"]/text()')
            print(title)
        elif self.xpath_exist(default_data, '//h1[@id="title"]'):
            title = select.xpath('//h1[@id="title"]/text()')
            print(title)
        else:
            title = ['无']
        title = ''.join(title)
        print(title)

        # 作者    名字中间空格显示为'\xa0'问题
        """
        在网上可以查到，==>对应的UTF-8编码是\x3d\x3d\x3e，所以前面的那个神秘字符的编码就是\xc2\xa0，
        上网查到这是一个叫做Non-breaking space的东西，用于阻止在此处自动换行和阻止多个空格被压缩成一个。
        至于解决方法，先用subplace("\xc2\xa0", " ")把这个特殊的空格替换一下就行了。
        """
        if self.xpath_exist(default_data, '//span[@class="authors__name"]'):
            authors = select.xpath('//span[@class="authors__name"]/text()')  # 列表
        elif self.xpath_exist(default_data, '//span[@class="authors-affiliations__name"]/text()'):
            authors = select.xpath('//span[@class="authors-affiliations__name"]/text()')  # 列表
        else:
            authors = ['无']
        authors = ';'.join(authors)

        # unit可能不存在
        if self.xpath_exist(default_data, '//span[@class="affiliation__name"]'):  # 有无单位信息
            units = select.xpath('//span[@class="affiliation__name"]/text()')  # 列表
        else:
            units = ['There are no affiliations available']
        units = ';'.join(units)

        # download可能为0
        if self.xpath_exist(default_data, '//span[@class="article-metrics__views"]'):
            download = select.xpath('//span[@class="article-metrics__views"]/text()')
        elif self.xpath_exist(default_data, '//span[@id="chapterdownloads-count-number"]'):
            download = select.xpath('//span[@id="chapterdownloads-count-number"]/text()')
        elif self.xpath_exist(default_data, '//span[@id="bookdownloads-count-number"]'):  # 有无单位信息
            download = select.xpath('//span[@id="bookdownloads-count-number"]/text()')
        else:
            download = ['0']
        download = ''.join(download)

        # keywords可能不存在
        if self.xpath_exist(default_data, '//span[@class="Keyword"]'):
            keywords = select.xpath('//span[@class="Keyword"]/text()')  # 列表
            keywords = ';'.join(keywords)
        else:
            keywords = '无'

        # doi_url
        doi_url = select.xpath('//span[@id="doi-url"]/text()')
        doi_url = ''.join(doi_url)

        # publisher_name
        publisher_name = select.xpath('//span[@id="publisher-name"]/text()')
        print(publisher_name)
        publisher_name = ''.join(publisher_name)

        # print_isbn可能不存在
        if self.xpath_exist(default_data, '//span[@id="bibliographic-print-isbn"]'):  # 有无单位信息
            print_isbn = select.xpath('//span[@id="bibliographic-print-isbn"]/text()')
        elif self.xpath_exist(default_data, '//span[@id="print-isbn"]'):
            print_isbn = select.xpath('//span[@id="print-isbn"]/text()')
        else:
            print_isbn = ['无']
        print_isbn = ''.join(print_isbn)

        # online_isbn
        if self.xpath_exist(default_data, '//span[@id="bibliographic-electronic-isbn"]'):  # 有无单位信息
            online_isbn = select.xpath('//span[@id="bibliographic-electronic-isbn"]/text()')
        elif self.xpath_exist(default_data, '//span[@id="electronic-isbn"]/text()'):
            online_isbn = select.xpath('//span[@id="electronic-isbn"]/text()')
        else:
            online_isbn = ['无']
        online_isbn = ''.join(online_isbn)

        # entries_num
        if self.xpath_exist(default_data, '//span[@id="bibliographic-number-of-entries"]'):
            entries_num = select.xpath('//span[@id="bibliographic-number-of-entries"]/text()')
        else:
            entries_num = ['无']
        entries_num = ''.join(entries_num)

        # series_print_issn
        if self.xpath_exist(default_data, '//span[@id="print-issn"]/text()'):
            series_print_issn = select.xpath('//span[@id="print-issn"]/text()')
        else:
            series_print_issn = ['无']
        series_print_issn = ''.join(series_print_issn)

        # series_online_issn
        if self.xpath_exist(default_data, '//span[@id="electronic-issn"]'):
            series_online_issn = select.xpath('//span[@id="electronic-issn"]/text()')
        else:
            series_online_issn = ['无']
        series_online_issn = ''.join(series_online_issn)

        # coverage
        if self.xpath_exist(default_data, '//dd[@id = "abstract-about-journal-coverage"]'):
            coverage = select.xpath('//dd[@id = "abstract-about-journal-coverage"]/text()')  # 列表
        else:
            coverage = ['无']
        coverage = ''.join(coverage)

        # print_issn
        if self.xpath_exist(default_data, '//dd[@id = "abstract-about-journal-coverage"]'):
            print_issn = select.xpath('//dd[@id="abstract-about-journal-print-issn"]/text()')
        else:
            print_issn = ['无']
        print_issn = ''.join(print_issn)

        # online_issn
        if self.xpath_exist(default_data, '//dd[@id = "abstract-about-journal-coverage"]'):
            online_issn = select.xpath('//dd[@id="abstract-about-journal-online-issn"]/text()')
        else:
            online_issn = ['无']
        online_issn = ''.join(online_issn)

        print(title_type + '\n' + coverage + '\n' + title + '\n' + authors + '\n' + units + '\n' +
                           keywords + '\n' + doi_url + '\n' + print_issn + '\n' + online_issn + '\n' +
                           publisher_name + '\n' + print_isbn + '\n' + online_isbn + '\n' + series_print_issn + '\n' +
                           series_online_issn + '\n' + download + '\n' + entries_num)

        # 数据库
        print("连接MYSQL")
        # 打开数据库连接
        db = pymysql.connect(host="localhost", user="root", password="123456", db="crawler", port=3306,
                             charset='utf8')
        # 使用cursor()方法获取操作游标
        cursor = db.cursor()

        # mysql_select = "select * from crawler_data where title = %s"   单查题目
        mysql_select = "select * from crawler_data where title = %s and authors = %s"

        mysql_insert = "INSERT INTO crawler_data (Title_type,Coverage,Title,Authors,Units,Keywords,Doi,Print_issn," \
                       "Online_issn,Publisher_name,Print_isbn,Online_isbn,Series_print_issn,Series_online_issn," \
                       "Download,Entries_num) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s','%s', '%s'," \
                       " '%s', '%s', '%s', '%s', '%s', '%s')" % \
                       (title_type, coverage, pymysql.escape_string(title), authors, pymysql.escape_string(units),
                        pymysql.escape_string(keywords), pymysql.escape_string(doi_url),
                        pymysql.escape_string(print_issn), pymysql.escape_string(online_issn),
                        pymysql.escape_string(publisher_name), pymysql.escape_string(print_isbn),
                        pymysql.escape_string(online_isbn), pymysql.escape_string(series_print_issn),
                        pymysql.escape_string(series_online_issn), download, pymysql.escape_string(entries_num))

        try:  # 执行sql语句
            if cursor.execute(mysql_select, (title, authors)):  # 执行sql语句，返回sql查询成功的记录数目
                print('数据已存在\n')
                pass
            else:
                cursor.execute(mysql_insert)
                db.commit()  # 增、删、改需要提交表单，查询不需要
                print('数据插入成功\n')
        except():  # 发生错误时回滚
            db.rollback()

        #  关闭数据库连接
        cursor.close()
        db.close()


if __name__ == '__main__':
    key = 'computer'
    cs = crawlSpringer(key)
