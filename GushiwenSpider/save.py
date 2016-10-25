# _*_ coding:utf8 _*_


import MySQLdb
import codecs
import redis
import os


class SaveGushiwen(object):
    """
    从数据库中读取内容，保存到本地
    """
    def __init__(self):
        # 数据库表结构见 数据库表结构.xlsx
        self.conn = MySQLdb.connect(
            host='192.168.154.135',
            port=3306,
            user='gushiwen',
            passwd='gushiwen',
            db='gushiwen',
            charset='utf8',
        )
        self.cur = self.conn.cursor()
        self.rds = redis.Redis(host='localhost', port=6379, db=0)

    def read_view(self):
        """
        从redis队列
            view_num 读取 view_num ,从表view中读取 view_num, view_name,,,,,
                  再根据view_num, fanyi_list, 分别从表 main_content, fanyi中读取相关内容
        依据作者名、朝代创建文件夹、文件，保存内容
        """
        while True:

            view_num = self.rds.lpop('view_num')
            if view_num:
                sqls_view = 'select * from view where view_num=%s'
                self.cur.execute(sqls_view, view_num)
                view_list = self.cur.fetchone()
                sqls_con = 'select content from main_content where view_num=%s'
                self.cur.execute(sqls_con, view_num)
                view_content = self.cur.fetchone()[0].decode('utf8')

                fy_list = view_list[6]
                if fy_list != '' and fy_list is not None:
                    #  有的作品没有翻译
                    fy_list = fy_list.split(',')
                    fanyi_content = ''
                    for fy_num in fy_list:
                        sqls_fy = 'select content from fanyi where fanyi_num=%s'
                        self.cur.execute(sqls_fy, fy_num)
                        """
                        fy_con = self.cur.fetchone()[0].decode('utf8')
                        TypeError: 'NoneType' object has no attribute '__getitem__'
                        http://so.gushiwen.org/view_64273.aspx
                        http://so.gushiwen.org/view_52227.aspx
                        http://so.gushiwen.org/view_48738.aspx
                        """
                        fy_con = self.cur.fetchone()[0].decode('utf8')
                        fanyi_content = fanyi_content + fy_con + '\n\n'
                else:
                    fanyi_content = ''

                self.write_view(view_list, view_content, fanyi_content)
            else:
                break

        print '作品部分处理完毕！'

    def write_view(self, view_list, view_content, fanyi_content):
        """"
        author_dir = dynasty + '\\' + author_name
        TypeError: coercing to Unicode: need string or buffer, NoneType found
        http://so.gushiwen.org/view_48749.aspx
        http://so.gushiwen.org/view_2073.aspx
        """

        if view_list[1]:
            author_name = view_list[1]
        else:
            author_name = u'佚名'
        view_link = view_list[2]
        dynasty = view_list[3]
        view_name = view_list[4]
        author_dir = dynasty + '\\' + author_name
        if not os.path.exists(author_dir):
            os.makedirs(author_dir)
        view_file_path = author_dir +  '\\' + view_name + '.txt'
        view_file = codecs.open(view_file_path, 'w', 'utf8')
        wrcont = view_name + '\n\n' + u'原文链接：' + view_link + '\n\n'\
                 + view_content + '\n\n' + fanyi_content
        view_file.write(wrcont)
        view_file.close()
        print '已经写入', view_name, '.txt'

    def read_author(self):
        """
        从redis队列
            author_num 读取 author_num, 从表author 中读取author_num, author_name, dynasty, main_content
                  再根据author_num, fanyi_list, 分别从表 main_content, fanyi中读取相关内容
        依据作者名、朝代创建文件夹、文件，保存内容
        """
        while True:
            author_num = self.rds.lpop('author_num')
            if author_num:
                sqls_author = 'select * from author where author_num=%s'
                self.cur.execute(sqls_author, author_num)
                author_list = self.cur.fetchone()
                sqls_con = 'select content from main_content where view_num=%s'
                self.cur.execute(sqls_con, author_num)
                author_content = self.cur.fetchone()[0].decode('utf8')
                fy_list = author_list[5]
                if fy_list != ''  and fy_list is not None:
                    #  如果有更多作者介绍的话
                    fy_list = fy_list.split(',')
                    fanyi_content = ''
                    for fy_num in fy_list:
                        sqls_fy = 'select content from fanyi where fanyi_num=%s'
                        self.cur.execute(sqls_fy, fy_num)
                        fy_con = self.cur.fetchone()[0].decode('utf8')
                        fanyi_content = fanyi_content + fy_con + '\n\n'
                else:
                    fanyi_content = ''
                self.write_author(author_list, author_content, fanyi_content)
            else:
                break

        print '作者介绍部分处理完毕！'

    def write_author(self, view_list, view_content, fanyi_content):
        author_name = view_list[1]
        author_link = view_list[2]
        dynasty = view_list[3]
        author_dir = dynasty + '\\' + author_name
        if not os.path.exists(author_dir):
            os.makedirs(author_dir)
        author_file_path = author_dir + '\\' + author_name + u'简介.txt'
        view_file = codecs.open(author_file_path, 'w', 'utf8')
        if view_content and fanyi_content:
            wrcont = author_name + u'简介\n\n' + u'作者介绍链接：' + author_link + '\n\n' \
                     + view_content + '\n\n' + fanyi_content
            view_file.write(wrcont)
            view_file.close()
            print '已经写入', author_name, '简介'


    def quit(self):
        self.cur.close()
        self.conn.commit()
        self.conn.close()


if __name__ == '__main__':

    save = SaveGushiwen()
    save.read_view()
    save.read_author()
    save.quit()

