import pymysql
from selenium import webdriver
from selenium.common.exceptions import *
from time import sleep


class crawlSD:
    def __init__(self, keyword):
        self.keyword = keyword
        self.driver = webdriver.Edge()
        print('正在加载主页...')
        self.driver.get('https://www.sciencedirect.com/')
        self.main_page()

    def main_page(self):
        self.driver.find_element_by_xpath('//input[@id="search-input"]').send_keys(self.keyword)  # 输入关键字
        self.driver.find_element_by_xpath('//input[@class="homesearch-quick-submit"]').click()  # 点击查询
        self.SD_content_page()

    # 通过xpath判断是否存在
    def SD_xpath_exist(self, xpath):
        try:
            self.driver.find_element_by_xpath(xpath)
            return True
        except NoSuchElementException:
            return False
        pass

    def SD_content_page(self):
        page_num = 1  # 页数
        print('第' + str(page_num) + '页')

        # 页码循环
        while True:  # 先for循环判当前页下一题目是否存在，再判断下一页是否存在
            """
            翻目录页时，页面覆盖一个小球表示正在加载，固定显示3秒。
            此时即使页面加载完成，若等待时间不够，便会报错：Message: Element is obscured元素覆盖
            所以设置固定等待3秒，以保证正常运行
            """
            sleep(3)    # 小球覆盖时间

            # 换页时，等待目录页；动态睡眠时间设置
            for time in range(1, 22):
                print(1)
                # 需要一个一定会加载出来的部分作为判断条件
                if self.SD_xpath_exist('//ol[@class="Pagination hor-separated-list"]'):  # 检索页码“Page 1 of 240”
                    print(2)
                    break
                elif 6 < time < 20 and self.SD_xpath_exist(
                        '//a[@href="/?qs=' + self.keyword +
                        '&authors=&pub=&volume=&issue=&page=&origin=home&zone=qSearch&offset=' +
                        str((page_num-1)*25) + '"]'):  # 仍在上一页
                    self.driver.find_element_by_xpath('//li[@class="pagination-link next-link"]/a').click()
                elif 6 < time < 20 and self.SD_xpath_exist('//input[@id="search-input"]'):
                    # 仍在主页，只主页有“search-input”
                    print(3)
                    # 再次点击
                    self.driver.find_element_by_xpath('//input[@class="homesearch-quick-submit"]').click()  # 点击查询
                elif time > 20:
                    print('因网速或其他原因，导致加载错误！')
                    exit()  # 退出程序
                    # 或者self.driver.close()
                else:
                    print(4)
                    sleep(1)  # 每次等待1秒

            for i in range(1, 26):  # 页面内循环
                """同一个个页面内跳转，需要等待加载，与cnki不同，cnki是加载新标签，目录页标签始终存在"""
                print('正在加载目录页...')

                # 每次由详情页返回目录页的等待加载；动态睡眠时间设置
                for time in range(1, 22):
                    print(11)
                    # 需要一个一定会加载出来的部分作为判断条件
                    if self.SD_xpath_exist('//ol[@class="Pagination hor-separated-list"]'):  # 检索页码“Page 1 of 240”
                        print(12)
                        break
                    elif 10 < time < 20 and self.SD_xpath_exist('//div[@class="Footer"]'):  # 详情页页脚
                        print(13)
                        # 再次返回目录页
                        self.driver.back()
                    elif time > 20:
                        print('因网速或其他原因，导致加载错误！')
                        exit()      # 退出程序
                        # 或者self.driver.close()
                    else:
                        print(14)
                        sleep(1)  # 每次等待1秒

                print('第' + str(i) + '次循环')
                if self.SD_xpath_exist('//div[@class="ResultList col-xs-24"]/ol/li[' + str(i) + ']'):  # 判当前题目是否存在
                    print('第' + str(i) + '条目')

                    # 目录页
                    title_type = self.driver.find_element_by_xpath('//div[@class="ResultList col-xs-24"]/ol/li[' + str(
                        i) + ']//span[@class="article-type u-clr-grey8"]').text  # 每个题目类型
                    # 发表日期,正数li可能是第二项(Book chapter)，可能是第三项，但肯定是倒数第二项，pages是最后一项，
                    data = self.driver.find_element_by_xpath(
                        '//div[@class="ResultList col-xs-24"]/ol/li[' + str(
                            i) + ']//ol[@class="SubType hor"]/li[last()-1]/span[1]').text

                    # 用于详情页出错查看
                    href = self.driver.find_element_by_xpath(
                        '//ol[@class="search-result-wrapper"]/li[' + str(
                            i) + ']//a[@class="result-list-title-link u-font-serif text-s"]').get_attribute("href")
                    print(href)

                    # 点击题目链接
                    self.driver.find_element_by_xpath(
                        '//div[@class="ResultList col-xs-24"]/ol/li['
                        + str(i) + ']//a[@class="result-list-title-link u-font-serif text-s"]').click()

                    # 等待详情页；动态睡眠时间设置
                    for time in range(1, 22):
                        print(21)
                        # 需要一个一定会加载出来，且每个详情页的路径均相同的部分作为判断条件
                        if self.SD_xpath_exist('//div[@class="Footer"]'):  # 详情页页脚
                            print(22)
                            break
                        elif 6 < time < 20 and self.SD_xpath_exist('//div[@class="ResultList col-xs-24"]/ol/li[' + str(i) + ']//a[@class="result-list-title-link u-font-serif text-s"]'):  # 仍在目录页
                            # (6 <time and <time < 12) simplify chained comparison 可简化连锁比较
                            print(23)
                            # 再次点击题目链接
                            self.driver.find_element_by_xpath(
                                '//div[@class="ResultList col-xs-24"]/ol/li['
                                + str(i) + ']//a[@class="result-list-title-link u-font-serif text-s"]').click()
                        elif time > 20:
                            print('因网速或其他原因，导致加载错误！')
                            exit()
                            # 或者self.driver.close()
                        else:
                            print(24)
                            sleep(1)  # 每次等待1秒

                    # 调用SD_default_page作为唯一一个爬取详情页的函数方法，内部判断各xpath，取有效的一个
                    print('调用详情页...')
                    self.SD_default_page(title_type, data)  # 将data传到default一起存储

                else:
                    print('条目不存在')
                    break  # 用于退出for循环和while循环，当有多层循环时，退出break所在的循环体

            # sleep(4)

            # 判下一页是否存在
            # 滚动到页脚，使的“next”按钮不被右下角“Facebook”弹框遮挡，否则报错“selenium.common.exceptions.WebDriverException: Message: Element is obscured”
            self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")     # 不报错，可进入if

            if self.SD_xpath_exist('//li[@class="pagination-link next-link"]/a'):  # 是否有下一页
                page_num = page_num + 1
                print('第' + str(page_num) + '页')
                # 单击下一页
                self.driver.find_element_by_xpath('//li[@class="pagination-link next-link"]/a').click()
            else:
                print('退出浏览器...')
                self.driver.close()  # 关闭当前窗口，或最后打开的窗口
                break

    def SD_default_page(self, title_type, current_data):
        """
         题名title 作者author 单位unit 发表时间data 关键词keywords DOI-doi
         期刊来源publisher_name 第几期publisher_term 题目类型title_type
         """
        print('default_page')

        # Xpath获取数据

        # publisher_name
        if self.SD_xpath_exist('//a[@class="publication-title-link"]'):
            publisher_name = self.driver.find_element_by_xpath('//a[@class="publication-title-link"]').text
        elif self.SD_xpath_exist('//div[@class="title"]/a/span'):
            publisher_name = self.driver.find_element_by_xpath('//div[@class="title"]/a/span').text
        else:
            publisher_name = ''
            print('publisher_name新路径')

        # publisher_term；a/span在前，a在后，否则就无span了
        if self.SD_xpath_exist('//a[@title="Go to table of contents for this volume/issue"]/span'):
            publisher_term = self.driver.find_element_by_xpath(
                '//a[@title="Go to table of contents for this volume/issue"]/span').text
        elif self.SD_xpath_exist('//a[@title="Go to table of contents for this volume/issue"]'):
            publisher_term = self.driver.find_element_by_xpath('//a[@title="Go to table of contents for this volume/issue"]').text
        elif self.SD_xpath_exist('//p[@class="specIssueTitle"]'):
            publisher_term = self.driver.find_element_by_xpath('//p[@class="specIssueTitle"]').text
        else:
            publisher_term = ''
            print('publisher_term新路径')

        # title
        if self.SD_xpath_exist('//span[@class="title-text"]'):
            title = self.driver.find_element_by_xpath('//span[@class="title-text"]').text
        elif self.SD_xpath_exist('//h1[@class="svTitle"]'):
            title = self.driver.find_element_by_xpath('//h1[@class="svTitle"]').text
        elif self.SD_xpath_exist('//span[@class="reference"]'):
            title = self.driver.find_element_by_xpath('//span[@class="reference"]').text
        else:
            title = ''      # 因为之前未定义，所以else重要加上赋值，否则未找到title时，item['title'] = title中的title不可用
            print('title新路径')

        # authors难点
        authors = ''
        i = 1
        if self.SD_xpath_exist('//div[@class="author-group"]/a[' + str(i) + ']'):
            while self.SD_xpath_exist('//div[@class="author-group"]/a[' + str(i) + ']'):
                given_name = self.driver.find_element_by_xpath(
                    '//div[@class="author-group"]/a[' + str(i) + ']//span[@class="text given-name"]').text
                surname = self.driver.find_element_by_xpath(
                    '//div[@class="author-group"]/a[' + str(i) + ']//span[@class="text surname"]').text
                authors = authors + given_name + ' ' + surname
                i = i + 1
        elif self.SD_xpath_exist('//ul[@class="authorGroup noCollab svAuthor"]/li[' + str(i) + ']'):
            while self.SD_xpath_exist('//ul[@class="authorGroup noCollab svAuthor"]/li[' + str(i) + ']'):
                author = self.driver.find_element_by_xpath(
                    '//ul[@class="authorGroup noCollab svAuthor"]/li[' + str(i) + ']/a').text
                authors = authors + author
                i = i + 1
        else:
            print('authors新路径')

        # 单击show more
        if self.SD_xpath_exist('//button[@class="show-hide-details"]'):
            show_more = self.driver.find_element_by_xpath('//button[@class="show-hide-details"]').text
            print(show_more + '1')
            self.driver.find_element_by_xpath('//button[@class="show-hide-details"]').click()
        elif self.SD_xpath_exist('//span[@class="showInfo expand"]'):       # Encyclopedia
            show_more = self.driver.find_element_by_xpath('//span[@class="showInfo expand"]').text
            print(show_more + '2')
            self.driver.find_element_by_xpath('//span[@class="showInfo expand"]').click()
        else:
            print('show_more新路径')

        # 等待show more加载完成退出循环；动态睡眠时间设置
        for time in range(1, 22):
            print(31)
            # 需要一个一定会加载出来，且每个详情页的路径均相同的部分作为判断条件
            # show more加载完后，作者详情部分标签属性两种变化
            if self.SD_xpath_exist('//div[@class="wrapper"]') or self.SD_xpath_exist('//div[@id="showMoreButtons"]/a[1]/span[@style="display: none;"]'):
                break
            elif 6 < time < 20 and self.SD_xpath_exist('//button[@class="show-hide-details"]'):  # 未more1成功
                # 再次点击题目链接
                self.driver.find_element_by_xpath('//button[@class="show-hide-details"]').click()
            elif 6 < time < 20 and self.SD_xpath_exist('//span[@class="showInfo expand"]'):       # Encyclopedia
                self.driver.find_element_by_xpath('//span[@class="showInfo expand"]').click()
            elif time > 20:
                print('因网速或其他原因，导致加载错误！')
                self.driver.close()
                exit()
            else:
                sleep(2)  # 每次等待1秒

        # unit隐藏在json中,问题点
        units = ''
        i = 1
        if self.SD_xpath_exist('//div[@class="AuthorGroups"]//dl[@class="affiliation"]'):
            # 每个author和对应unit共同包含在一个author_group里，分多个group
            # 第一层while对应多个作者
            while self.SD_xpath_exist('//div[@class="AuthorGroups"]/div[' + str(i) + ']'):
                # 第二层while对应一个作者的多个unit
                j = 1
                while self.SD_xpath_exist('//div[@class="AuthorGroups"]/div[' + str(i) + ']/dl[' + str(j) + ']'):
                    unit = self.driver.find_element_by_xpath('//div[@class="AuthorGroups"]/div[' + str(i) + ']/dl[' + str(j) + ']').text
                    units = units + unit
                    j = j + 1
                # unit = self.driver.find_element_by_xpath('//div[@class="AuthorGroups"]/div[' + str(i) + ']/dl').text     # 尝试直接获取一个作者的多个unit，作用抵消while
                i = i + 1
        elif self.SD_xpath_exist('//div[@class="page_fragment auth_frag"]/ul[@class ="affiliation authAffil smh"]'):    # Encyclopedia
            # 所有author和所有unit共同包含在一个group里，按位置对应，一个author一个unit一个author一个unit
            # 第一层while对应多个作者
            while self.SD_xpath_exist('//div[@class="page_fragment auth_frag"]/ul[' + str(i*2) + ']'):      # unit位于偶数位置
                # 第二层while对应一个作者的多个unit
                j = 1
                while self.SD_xpath_exist('//div[@class="page_fragment auth_frag"]/ul[' + str(i*2) + ']/li[' + str(j) + ']/span'):
                    unit = self.driver.find_element_by_xpath(
                        '//div[@class="page_fragment auth_frag"]/ul[' + str(i*2) + ']/li[' + str(j) + ']/span').text
                    units = units + unit
                    j = j + 1
                i = i + 1
        else:
            print('units新路径')

        # data有含在json中的，有在外边的，再就用目录页获取的data
        if self.SD_xpath_exist('//dd[@id="OrigDate"]'):
            # title_type为Book chapter的详情页，data隐藏在show more中
            data = self.driver.find_element_by_xpath('//dd[@id="OrigDate"]').text
        elif self.SD_xpath_exist('//div[@id="currtAsOf"]'):
            # title_type为Encyclopedia的详情页,data已知的路径为此
            data = self.driver.find_element_by_xpath('//div[@id="currtAsOf"]').text
        else:
            data = current_data

        # doi
        if self.SD_xpath_exist('//a[@class="doi"]'):        # article，book reviews
            doi_url = self.driver.find_element_by_xpath('//a[@class="doi"]').text
        # elif self.SD_xpath_exist('//a[@class="S_C_ddDoi"]'):       # 已知为Book chapter的路径
        elif self.SD_xpath_exist('//dd[@class="doi"]/a'):       # 已知为Book chapter的路径
            # doi_url = self.driver.find_element_by_xpath('//a[@class="S_C_ddDoi"]').text
            doi_url = self.driver.find_element_by_xpath('//dd[@class="doi"]/a').text
        elif self.SD_xpath_exist('//dd[@class="doi"]'):       # 已知为Encyclopedia的路径
            doi_url = self.driver.find_element_by_xpath('//dd[@class="doi"]').text
        else:
            doi_url = ''
            print('doi_url新路径')

        # keyword难点；含keyword的标签属性不唯一，所以用父标签的属性利用路径位置特点构造xpath
        keywords = ''
        if self.SD_xpath_exist('//div[@class="Keywords"]/div[last()]/div/span'):
            i = 1
            while self.SD_xpath_exist('//div[@class="Keywords"]/div[last()]/div[' + str(i) + ']/span'):
                keyword = self.driver.find_element_by_xpath('//div[@class="Keywords"]/div[last()]/div[' + str(i) + ']/span').text
                keywords = keywords + keyword
                i = i + 1
        elif self.SD_xpath_exist('//li[@class="svKeywords"]/span'):
            i = 1
            while self.SD_xpath_exist('//li[@class="svKeywords"]/span[' + str(i) + ']'):
                keyword = self.driver.find_element_by_xpath('//li[@class="svKeywords"]/span[' + str(i) + ']').text
                keywords = keywords + keyword
                i = i + 1
        else:
            keywords = ''
            print('keywords新路径')

        # 数据库
        print("连接MYSQL")
        # 打开数据库连接
        db = pymysql.connect(host="localhost", user="root", password="123456", db="crawler", port=3306,
                             charset='utf8')
        # 使用cursor()方法获取操作游标
        cursor = db.cursor()

        mysql_select = "select * from crawler_data where title = %s"

        mysql_insert = "INSERT INTO crawler_data (Data,Title,Authors,Units,Keywords,Doi,Publisher_name,Publisher_term) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (
            pymysql.escape_string(data), pymysql.escape_string(title), authors,pymysql.escape_string(units),
            pymysql.escape_string(keywords),pymysql.escape_string(doi_url),publisher_name,publisher_term)

        try:  # 执行sql语句
            if cursor.execute(mysql_select, title):  # 执行sql语句，返回sql查询成功的记录数目
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

        print('正在返回目录页...')
        self.driver.back()  # 返回目录页


if __name__ == "__main__":
    key = 'computer'
    c = crawlSD(key)  # 初始化
