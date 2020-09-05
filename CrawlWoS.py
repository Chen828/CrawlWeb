import pymysql
from selenium import webdriver
from selenium.common.exceptions import *
from time import sleep


class crawlWoS(object):
    def __init__(self, keyword):
        self.keyword = keyword
        self.driver = webdriver.Edge()
        print('正在加载主页...')
        self.driver.get('http://isiknowledge.com/')
        self.main_page()

    def main_page(self):
        self.driver.find_element_by_xpath('//input[@id="value(input1)"]').send_keys(self.keyword)  # 输入关键字
        self.driver.find_element_by_xpath('//button[@class="standard-button primary-button large-search-button"]').click()  # 点击查询
        self.WoS_content_page()

    # 通过xpath判断是否存在
    def WoS_xpath_exist(self, xpath):
        try:
            self.driver.find_element_by_xpath(xpath)
            return True
        except NoSuchElementException:
            return False
        pass

    def WoS_content_page(self):
        page_num = 1  # 页数
        print('第' + str(page_num) + '页')

        # 页码循环
        while True:  # 先for循环判当前页下一题目是否存在，再判断下一页是否存在

            sleep(3)    # 不能去，给页面反应的时间
            # 等待目录页；动态睡眠时间设置
            for time in range(1, 22):
                # 需要一个一定会加载出来的部分作为判断条件
                if self.WoS_xpath_exist('//div[@id="totalCount"]'):  # 目录页页脚搜索结果说明
                    break
                elif 6 < time < 20 and self.WoS_xpath_exist('//input[@value="' + str(page_num-1) + '"]'):     # 仍在上一页
                    self.driver.find_element_by_xpath('//a[@class="paginationNext"]/i').click()     # 单击下一页
                elif 6 < time < 20 and self.WoS_xpath_exist('//input[@id="value(input1)"]'):  # 仍在主页
                    # 再次点击
                    self.driver.find_element_by_xpath(
                        '//button[@class="standard-button primary-button large-search-button"]').click()  # 点击查询
                elif time > 20:
                    print('因网速或其他原因，导致加载错误！')
                    self.driver.close()
                    exit()  # 退出程序
                else:
                    sleep(1)  # 每次等待1秒

            for i in range(1, 11):  # 页面内循环
                """同一个个页面内跳转，需要等待加载，与cnki不同，cnki是加载新标签，目录页标签始终存在"""
                print('正在加载目录页...')

                # 详情页返回目录页等待；动态睡眠时间设置
                for time in range(1, 22):
                    # 需要一个一定会加载出来的部分作为判断条件,避免搜索结果不存在而以为是网速卡的情况
                    if self.WoS_xpath_exist('//div[@id="totalCount"]'):  # 目录页页脚搜索结果说明
                        break
                    elif 6 < time < 20 and self.WoS_xpath_exist('//div[@class="cited-ref-bottom-labels"]'):
                        # 仍在详情页，其页脚xpath页脚的页码说明
                        self.driver.back()
                    elif time > 20:
                        print('因网速或其他原因，导致加载错误！')
                        exit()  # 退出程序
                        # 或者self.driver.close()
                    else:
                        sleep(1)  # 每次等待1秒

                print('第' + str(i) + '次循环')
                if self.WoS_xpath_exist('//div[@class="search-results"]/div[' + str(i) + ']/div[3]/div[1]/div/a'):  # 判当前题目是否存在
                    print('第' + str(i) + '条目')

                    # 用于详情页出错查看
                    href = self.driver.find_element_by_xpath('//div[@class="search-results"]/div[' + str(i) + ']/div[3]/div[1]/div/a').get_attribute("href")
                    print(href)

                    # 点击题目链接
                    self.driver.find_element_by_xpath('//div[@class="search-results"]/div[' + str(i) + ']/div[3]/div[1]/div/a').click()

                    # 等待详情页；动态睡眠时间设置
                    for time in range(1, 22):
                        # 需要一个一定会加载出来的部分作为判断条件
                        if self.WoS_xpath_exist('//div[@class="cited-ref-bottom-labels"]'):  # 详情页页脚的页码说明
                            break
                        elif 6 < time < 20 and self.WoS_xpath_exist('//div[@id="totalCount"]'):  # 目录页页脚搜索结果说明
                            # 再次点击
                            self.driver.find_element_by_xpath(
                                '//div[@class="search-results"]/div[' + str(i) + ']/div[3]/div[1]/div/a').click()
                        elif time > 20:
                            print('因网速或其他原因，导致加载错误！')
                            exit()  # 退出程序
                            # 或者self.driver.close()
                        else:
                            sleep(1)  # 每次等待1秒

                    print('调用详情页...')
                    # 根据题目类型匹配各种详情页；此判断顺序按一般搜索各题目类型的数量由多到少，效率最高
                    self.WoS_default_page()
                else:
                    print('条目可能不存在或网络卡顿...')
                    break  # 用于退出for循环和while循环，当有多层循环时，退出break所在的循环体

            # 判下一页是否存在
            if self.WoS_xpath_exist('//a[@class="paginationNext"]'):  # 是否有下一页
                page_num = page_num + 1
                print('第' + str(page_num) + '页')
                # 单击下一页
                self.driver.find_element_by_xpath('//a[@class="paginationNext"]/i').click()
            else:
                print('退出浏览器...')
                self.driver.close()  # 关闭当前窗口，或最后打开的窗口
                break

    def WoS_default_page(self):
        """
        题名类型title_type 题名title 作者author 单位unit 发表时间data 关键词keyword DOI-doi
        期刊来源publisher_name 第几期publisher_term 期刊等级、类别publisher_class
        """
        print('default_page')
        title = self.driver.find_element_by_xpath('//div[@class="l-content"]/div[1]/value').text
        authors = self.driver.find_element_by_xpath('//div[@class="l-content"]/div[2]/p/a').text

        # publisher_name
        if self.WoS_xpath_exist('//div[@class="l-content"]/div[3]/p[@class="sourceTitle"]/value'):
            publisher_name = self.driver.find_element_by_xpath('//div[@class="l-content"]/div[3]/p[@class="sourceTitle"]/value').text
        else:
            publisher_name = ''

        # publisher_term
        if self.WoS_xpath_exist('//div[@class="l-content"]/div[3]/div/p'):
            publisher_term = self.driver.find_element_by_xpath('//div[@class="l-content"]/div[3]/div/p').text
        else:
            publisher_term = ''

        j = 4   # 位置
        # doi先
        if self.WoS_xpath_exist('//div[@class="l-content"]/div[3]/p[' + str(j) + ']/value'):
            doi = self.driver.find_element_by_xpath('//div[@class="l-content"]/div[3]/p[' + str(j) + ']/value').text
            j = j + 1
        else:
            doi = ''

        # data
        if self.WoS_xpath_exist('//div[@class="l-content"]/div[3]/p[' + str(j) + ']/value'):
            data = self.driver.find_element_by_xpath('//div[@class="l-content"]/div[3]/p[' + str(j) + ']/value').text
            j = j + 1
        else:
            data = ''

        # title_type
        if self.WoS_xpath_exist('//div[@class="l-content"]/div[3]/p[' + str(j) + ']'):
            title_type = self.driver.find_element_by_xpath('//div[@class="l-content"]/div[3]/p[' + str(j) + ']').text
            # j = j + 1
        else:
            title_type = ''

        # keywords
        if self.WoS_xpath_exist('//div[@class="l-content"]/div[5]/p/a'):
            keywords = self.driver.find_element_by_xpath('//div[@class="l-content"]/div[5]/p/a').text
        else:
            keywords = ''

        # units
        units = ''
        j = 1  # 两个unit_group
        while self.WoS_xpath_exist('//div[@class="l-content"]/div[6]/table[' + str(j) + ']'):
            i = 1
            while self.WoS_xpath_exist(
                    '//div[@class="l-content"]/div[6]/table[' + str(j) + ']/tbody/tr[' + str(i) + ']'):
                # /html/body/div[1]/div[25]/form[3]/div/div/div/div[1]/div/div[6]/table[1]/tbody/tr/td[2]
                unit = self.driver.find_element_by_xpath(
                    '//div[@class="l-content"]/div[6]/table[' + str(j) + ']/tbody/tr[' + str(i) + ']/td[2]').text
                units = units + unit
                i = i + 1
            j = j + 1

        # publisher_class
        publisher_class = self.driver.find_element_by_xpath('//div[@class="l-content"]/div[8]/p2').text

        # 数据库
        print("连接MYSQL")
        # 打开数据库连接
        db = pymysql.connect(host="localhost", user="root", password="123456", db="crawler", port=3306,
                             charset='utf8')
        # 使用cursor()方法获取操作游标
        cursor = db.cursor()

        mysql_select = "select * from crawler_data where title = %s"

        mysql_insert = "INSERT INTO crawler_data (Data,Title_type,Title,Authors,Units,Keywords,Doi,Publisher_name,Publisher_term,Publisher_class) VALUES ('%s', '%s','%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (
            pymysql.escape_string(data), title_type, pymysql.escape_string(title), authors,pymysql.escape_string(units),
            pymysql.escape_string(keywords), doi, publisher_name, publisher_term, publisher_class)

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

        self.driver.back()


if __name__ == "__main__":
    key = 'computer'
    c = crawlWoS(key)  # 初始化
