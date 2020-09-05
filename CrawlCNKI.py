import pymysql
from selenium import webdriver
from selenium.common.exceptions import *
from time import sleep


class crawlCNKI:
    def __init__(self, keyword):
        self.keyword = keyword
        self.driver = webdriver.Edge()
        print('正在加载主页...')
        self.driver.get('http://www.cnki.net/')
        # self.driver.minimize_window()
        self.main_page()

    def main_page(self):
        self.driver.find_element_by_xpath('//input[@name="txt_SearchText"]').send_keys(self.keyword)  # 输入关键字
        self.driver.find_element_by_xpath('//input[@class="search-btn"]').click()  # 点击查询
        self.CNKI_content_page()

    # 通过xpath判断是否存在
    def CNKI_xpath_exist(self, xpath):
        try:
            self.driver.find_element_by_xpath(xpath)
            return True
        except NoSuchElementException:
            return False
        pass

    # 通过text文本判断元素是否存在
    def CNKI_text_exist(self, text):
        try:
            # self.driver.find_element_by_link_text(text)        # 完整text内容,易判唯一，难定位
            self.driver.find_element_by_partial_link_text(text)  # text中部分独有内容，难判唯一，易定位
            return True
        except NoSuchElementException:
            return False
        pass

    def CNKI_content_page(self):
        page_num = 1  # 页数

        # 动态等待iframe加载
        for time in range(1, 22):
            # 需要一个一定会加载出来的部分作为判断条件
            if self.CNKI_xpath_exist(
                    '//iframe[@name="iframeResult"]'):  # 进入目录页，需要定位frame，否则找不到内部各xpath、元素<ifram name=iframeResult>
                break
            elif time > 20:
                print('因网速或其他原因，导致加载错误！')
                exit()  # 退出程序
            else:
                sleep(2)  # 每次等待2秒

        self.driver.switch_to.frame("iframeResult")  # 进入目录页，需要定位frame，否则找不到内部各xpath、元素<ifram name=iframeResult>

        # 动态等待检索目录结果
        for time in range(1, 22):
            # 需要一个一定会加载出来的部分作为判断条件
            if self.CNKI_xpath_exist('//table[@class="GridTableContent"]'):  # 检索目录结果
                break
            elif time > 20:
                print('因网速或其他原因，导致加载错误！')
                exit()  # 退出程序
            else:
                sleep(2)  # 每次等待2秒

        while self.CNKI_xpath_exist('//div[@class="TitleLeftCell"]/font'):  # 开始每页循环

            print('正在加载目录页...')
            # 换页时，等待目录页；动态睡眠时间设置
            for time in range(1, 22):
                # 需要一个一定会加载出来的部分作为判断条件
                if self.CNKI_xpath_exist('//table[@class="GridTableContent"]'):  # 检索目录结果
                    break
                elif 10 < time < 20 and self.CNKI_xpath_exist(
                        '//font[contains(text(),"' + str(page_num - 1) + '")]'):  # 仍在上一页
                    # 根据元素内容定位元素（非常实用）
                    # 单击下一页
                    self.driver.find_element_by_xpath('//div[@class="TitleLeftCell"]/a[last()]').click()
                elif 10 < time < 20 and self.CNKI_xpath_exist('//input[@class="search-btn"]'):  # 仍在主页
                    # 再次点击
                    self.driver.find_element_by_xpath('//input[@class="search-btn"]').click()  # 点击查询
                elif time > 20:
                    print('因网速或其他原因，导致加载错误！')
                    exit()  # 退出程序
                else:
                    sleep(2)  # 每次等待1秒

            # 页面内循环；第一个题目位于第二个tr，20个题目，第23次循环为了判断下一页
            for i in range(2, 22):

                print('第' + str(i - 1) + '次循环')

                if self.CNKI_xpath_exist('//table[@class="GridTableContent"]/tbody/tr[' + str(i) + ']'):  # 判当前题目是否存在
                    print('第' + str(i - 1) + '条目')

                    # 目录页
                    data = self.driver.find_element_by_xpath(
                        '//table[@class="GridTableContent"]/tbody/tr[' + str(i) + ']/td[5]').text  # 发表日期

                    self.driver.find_element_by_xpath(
                        '//table[@class="GridTableContent"]/tbody/tr[' + str(i) + ']/td[2]/a').click()  # 点击题目链接

                    self.driver.switch_to.window(
                        self.driver.window_handles[1])  # 标签页顺序（按照打开顺序）：1 2 3 4 5 对应的句柄：0 4 3 2 1

                    # 等待详情页；动态睡眠时间设置
                    for time in range(1, 22):
                        # 需要一个一定会加载出来的部分作为判断条件
                        if self.CNKI_xpath_exist('//h2[@class="title"]'):  # 详情页题目标签
                            break
                        elif 6 < time < 20 and self.CNKI_xpath_exist('//div[@class="newsh_mid"]'):  # 仍在目录页
                            # 再次点击
                            self.driver.find_element_by_xpath(
                                '//table[@class="GridTableContent"]/tbody/tr[' + str(i) + ']/td[2]/a').click()  # 点击题目链接
                        elif time > 20:
                            print('因网速或其他原因，导致加载错误！')
                            self.driver.close()
                            exit()  # 退出程序
                        else:
                            sleep(2)  # 每次等待1秒

                    # 详情页
                    print('调用详情页...')
                    self.CNKI_default_page(data)  # 将data传到default一起存储
                else:
                    print('爬虫完毕...')
                    self.driver.close()  # 关闭当前窗口，或最后打开的窗口
                    exit()
                    break  # 用于退出for循环和while循环，当有多层循环时，退出break所在的循环体

            if self.CNKI_text_exist("下一页"):  # 是否有下一页
                page_num = page_num + 1
                print('第' + str(page_num) + '页')  # 到此好使
                # 单击下一页
                self.driver.find_element_by_xpath('//div[@class="TitleLeftCell"]/a[last()]').click()
                """换页时，因为从详情页返回到目录页，已经定位iframe，next后，因为iframe不变，xpath仍有效"""
            else:
                print('爬虫完毕...')
                self.driver.close()  # 关闭当前窗口，或最后打开的窗口
                exit()
                break

    def CNKI_default_page(self, data):
        print('CNKI_default_page')  # 到此好使

        """
        题名tittle 作者author 单位unit 发表时间data 数据库sql（期刊、博士） 被引citation
        基金foundation 关键词keyword DOI-doi 导师teacher 分类号class_number
        期刊来源publisher_name 第几期publisher_term 期刊等级publisher_class ISSN issn
        下载download  (被引citation)
        """

        # sql
        sql_course = '无'
        if self.CNKI_xpath_exist('//span[@id="catalog_Ptitle"]'):
            sql_course = self.driver.find_element_by_xpath('//span[@id="catalog_Ptitle"]').text

        # title
        title = self.driver.find_element_by_xpath('//h2[@class="title"]').text

        # authors
        authors = ''
        if self.CNKI_xpath_exist('//div[@class="author"]/span'):
            i = 1
            while self.CNKI_xpath_exist('//div[@class="author"]/span[' + str(i) + ']/a'):
                author = self.driver.find_element_by_xpath('//div[@class="author"]/span[' + str(i) + ']/a').text
                authors = authors + '；' + author
                i = i + 1
        else:
            authors = '无'

        # units
        units = ''
        if self.CNKI_xpath_exist('//div[@class="orgn"]/span/a'):
            i = 1
            while self.CNKI_xpath_exist('//div[@class="orgn"]/span[' + str(i) + ']/a'):
                unit = self.driver.find_element_by_xpath('//div[@class="orgn"]/span[' + str(i) + ']/a').text
                units = units + '；' + unit
                i = i + 1
        else:
            units = '无'

        # 中
        j = 2  # 元素从第二项开始

        # foundations
        foundations = ''
        if self.CNKI_xpath_exist('//label[@id="catalog_FUND"]'):
            i = 1
            while self.CNKI_xpath_exist('//div[@class="wxBaseinfo"]/p[' + str(j) + ']/a[' + str(i) + ']'):
                # 判是否有基金,必须xpath判断，因为页面有“相关基金文献”一栏，所以text判“基金：”不唯一
                foundation = self.driver.find_element_by_xpath(
                    '//div[@class="wxBaseinfo"]/p[' + str(j) + ']/a[' + str(i) + ']').text
                foundations = foundations + foundation
                i = i + 1
            j = j + 1
        else:
            foundations = '无'

        # keywords
        keywords = ''
        if self.CNKI_xpath_exist('//label[@id="catalog_KEYWORD"]'):
            i = 1
            while self.CNKI_xpath_exist('//div[@class="wxBaseinfo"]/p[' + str(j) + ']/a[' + str(i) + ']'):
                keyword = self.driver.find_element_by_xpath(
                    '//div[@class="wxBaseinfo"]/p[' + str(j) + ']/a[' + str(i) + ']').text
                keywords = keywords + keyword
                i = i + 1
            j = j + 1
        else:
            keywords = '无'

        # doi
        doi = '无'
        if self.CNKI_xpath_exist('//label[@id="catalog_ZCDOI"]'):  # 判是否有DOI
            doi = self.driver.find_element_by_xpath('//div[@class="wxBaseinfo"]/p[' + str(j) + ']').text
            j = j + 1

        # teacher
        teacher = '无'
        if self.CNKI_xpath_exist('//label[@id="catalog_TUTOR"]'):
            # elif CNKI_xpath_exist('//label[@id="catalog_TUTOR"]'):
            teacher = self.driver.find_element_by_xpath('//div[@class="wxBaseinfo"]/p[' + str(j) + ']/a').text
            j = j + 1

        # class_number
        class_number = self.driver.find_element_by_xpath('//div[@class="wxBaseinfo"]/p[' + str(j) + ']').text

        # 右
        publisher_term = '无'
        issn = '无'
        publisher_class = '无'
        if self.CNKI_xpath_exist('//p[@class="title"]/a'):  # 判断是期刊还是学校
            publisher_name = self.driver.find_element_by_xpath('//div[@class="sourinfo"]/p[1]/a').text
            if self.CNKI_xpath_exist('//div[@class="sourinfo"]/p[3]/a'):
                publisher_term = self.driver.find_element_by_xpath('//div[@class="sourinfo"]/p[3]/a').text
            k = 4
            # if self.CNKI_xpath_exist('//div[@class="sourinfo"]/p[' + str(k) + ']'):
            if self.CNKI_text_exist('ISSN：'):  # 中文冒号
                issn = self.driver.find_element_by_xpath('//div[@class="sourinfo"]/p[' + str(k) + ']').text
                k = k + 1
            if self.CNKI_xpath_exist('//div[@class="sourinfo"]/p[' + str(k) + ']'):
                publisher_class = self.driver.find_element_by_xpath('//div[@class="sourinfo"]/p[' + str(k) + ']').text
        else:  # 学校
            publisher_name = self.driver.find_element_by_xpath('//div[@class="sourinfo"]/p[1]/a').text

            # 下
        download = '0'
        if self.CNKI_xpath_exist('//span[@class="a"]'):  # 下载
            download = self.driver.find_element_by_xpath('//span[@class="a"]/b').text

        print(data + '\n' + sql_course + '\n' + title + '\n' + authors + '\n' + units + '\n' + foundations + '\n'
              + keywords + '\n' + doi + '\n' + teacher + '\n' + class_number + '\n' + publisher_name + '\n'
              + publisher_term + '\n' + publisher_class + '\n' + issn + '\n' + download)

        # 数据库
        print("连接MYSQL")
        # 打开数据库连接
        db = pymysql.connect(host="localhost", user="root", password="123456", db="crawler", port=3306,
                             charset='utf8')
        # 使用cursor()方法获取操作游标
        cursor = db.cursor()

        mysql_select = "select * from crawler_data where title = %s"

        mysql_insert = "INSERT INTO crawler_data (Data,Sql_course,Title,Authors,Units,Foundations,Keywords,Doi,Teacher,Class_number,Publisher_name,Publisher_term,Publisher_class,Issn,Download) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s','%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (
            pymysql.escape_string(data), sql_course, pymysql.escape_string(title), authors,
            pymysql.escape_string(units), pymysql.escape_string(foundations), pymysql.escape_string(keywords),
            pymysql.escape_string(doi), teacher, pymysql.escape_string(class_number), publisher_name,
            publisher_term, publisher_class, pymysql.escape_string(issn), download)

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

        self.driver.close()  # 关闭当前窗口，或最后打开的窗口
        self.driver.switch_to.window(self.driver.window_handles[0])  # 切回目录窗口,才能进行下一行检索
        self.driver.switch_to.frame("iframeResult")  # 每次回到目录页，需要重新定位frame，否则找不到内部各xpath、元素


if __name__ == "__main__":
    key = '互联网普及'
    c = crawlCNKI(key)  # 初始化
