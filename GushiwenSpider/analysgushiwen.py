# _*_ coding:utf8 _*_

# 作者: W.S.K
"""
遍历指定目录下的所有文件，根据获取到的文件名判断是否为目录，递归判断
根据目录结构创建字典文件，字典文件保存到本地
字典结构见val = dict()
"""
import re
import os
import pickle
import codecs
import numpy
import copy
import pandas as pd
import thulac
from pandas import DataFrame, Series,ExcelWriter


class AnalysGushiwen:

    def __init__(self, basepath):
        self.keyslist = [u'先秦', u'两汉', u'魏晋', u'南北朝', u'隋代', u'唐代',
                         u'五代', u'宋代', u'金朝', u'元代', u'明代', u'清代', ]
        self.val = dict(
            #  统计所有文本部分，用于词频分析
            content_poetry_merge='',  # 所有作品正文累加
            content_fanyi_merge='',  # 所有作品翻译、赏析累加
            content_author_intro_merge='',  # 所有作者介绍累加
            content_poetry_single=dict(
                # 统计该作者名下所有作品原文
                # author1 = 'author1',
            ),
            content_fanyi_single=dict(
                # 统计该作者名下所有作品翻译、赏析
                #  author1= 'author1',
            ),
            content_author_intro_single=dict(
                # 统计该作者的介绍
            ),

            # 统计所有数据部分，用于数据分析
            account_poetry=dict(
                author_all=0,  # 所有作者总数
                # author_list=list(),  copy字典后，字典里的list依然是copy的index
                poetry_all=0,  # 所有作品个数
                # poetry_list=list(),
                author_single=dict(
                    # 统计每个作者的作品数量
                    # author2=20,
                ),
            ),

            # 统计所有评分数据部分
            account_score=dict(
                score_max=10,  # 分数排名通过内置函数（如sort）或者pandas处理
                score_min=0,
                score_populate=0,  # 打分总人数
                score_total=0,
                score_average=0,
                score_single_author=dict(
                    # author_name = {
                    #     score_max = 0,
                    #     score_min = 0,
                    #     score_populate = 0,  #打分总人数
                    #     score_total = 0，
                    #     score_average = 0,
                    #     poetryname={score=float(score), score_populate=score_populate},
                    # },
                ),
            ),
        )

        # 初始化所有的字典，朝代为键值
        self.dic_dystany = {k: copy.deepcopy(self.val) for k in self.keyslist}
        self.basepath = basepath

    def extractdata(self):
        # base_dir = u'I:\Stu\Python\Scrapy105\gushiwen\文件输出\全量'  # 优盘
        # base_dir = u'F:\Github\输出文件\古诗文\统计'   # PC
        for dystany in self.keyslist:
        # for dystany in [u'金朝', u'先秦']:  # 以金朝为测试目标
            # 各朝代内容（正文、翻译、作者介绍）汇总
            con_pty_mrg = ''  # self.dic_dystany[dystany]['content_poetry_merge']
            con_fy_mrg = ''  # self.dic_dystany[dystany]['content_fanyi_merge']
            con_ath_intr_mrg = ''  # self.dic_dystany[dystany]['content_author_intro_merge']
            author_list = os.listdir(os.path.join(self.basepath, dystany))  # [u'元好问', u'刘迎', u'赵秉文']
            self.dic_dystany[dystany]['account_poetry']['author_list'] = copy.deepcopy(author_list)
            len_author_list = len(self.dic_dystany[dystany]['account_poetry']['author_list'])
            self.dic_dystany[dystany]['account_poetry']['author_all'] = len_author_list
            poetry_list = list()
            # self.dic_dystany[dystany]['account_poetry']['poetry_list'] = copy.copy(poetry_list)
            # 各朝评分数据汇总
            # dystany_score_populate = self.dic_dystany[dystany]['account_score']['score_populate']
            for author in self.dic_dystany[dystany]['account_poetry']['author_list']:
                # 各作者内容（正文、翻译、作者介绍）汇总
                con_pty_sgl = ''  # self.dic_dystany[dystany]['content_poetry_single'][author]
                con_fy_sgl = ''  # self.dic_dystany[dystany]['content_fanyi_single'][author]
                # 评分内容统计：  作者评分汇总 ， 作品评分汇总
                scr_sgl_ath = dict()  # self.dic_dystany[dystany]['account_score']['score_single_author'][author]

                # 获取作者目录下的所有文件，识别作者介绍与作品
                cur_path = os.path.join(self.basepath, dystany, author)
                txt_list = os.listdir(cur_path)
                ath_intr_file_name_list = [fn for fn in txt_list if u'简介' in fn]
                # 判断有无作者，有作者的才会统计作者相关
                if ath_intr_file_name_list:
                    ath_intr_file_name = ath_intr_file_name_list[0]
                    ath_intr_file = open(os.path.join(cur_path, ath_intr_file_name), 'r')
                    ath_intr = ath_intr_file.read().decode('utf8')
                    ath_intr = self.rm_invld_charaters(ath_intr)
                    ath_intr_file.close()

                    # 处理作者介绍部分
                    con_ath_intr_mrg += ath_intr  # 计入所有作者简介总和
                    # 单个作者介绍不需要累加记录
                    self.dic_dystany[dystany]['content_author_intro_single'][author] = ath_intr

                    # 处理作品部分,当前作者名下的所有作品列表
                    txt_list.remove(ath_intr_file_name)  # 返回值为None，不能直接赋值给新列表
                    acnt_pty_ath_sgl = len(txt_list)
                    poetry_list += txt_list
                    for ptr in txt_list:
                        ptr_file = open(os.path.join(cur_path, ptr), 'r')
                        ptr_con = ptr_file.read().decode('utf8')
                        ptr_file.close()
                        title, score, score_populate, yuanwen, yuanwen_link, fanyi = self.extract_content(ptr_con)
                        # 正文汇总、翻译汇总
                        con_pty_mrg += yuanwen
                        con_fy_mrg += fanyi
                        # 各作者所有文章的正文、翻译汇总
                        con_pty_sgl += yuanwen
                        con_fy_sgl += fanyi
                        # 各作者名下单作品评分
                        poetry_name = ptr.replace(u'.txt', '')
                        scr_sgl_ath[poetry_name] = dict(score=float(score), score_populate=int(score_populate))
                else:
                    # 佚名或者类似于孟子及其弟子或者刘向 撰暂且忽略不计，只有先秦和两汉有一小部分
                    # con_ath_inr_sgl = u'NoAuthor'
                    # 无作者简介，全部都是作品了
                    acnt_pty_ath_sgl = len(txt_list)
                    poetry_list += txt_list
                    for ptr in txt_list:
                        ptr_file = open(os.path.join(cur_path, ptr), 'r')
                        ptr_con = ptr_file.read().decode('utf8')
                        ptr_file.close()
                        title, score, score_populate, yuanwen, yuanwen_link, fanyi = self.extract_content(ptr_con)
                        # 正文汇总、翻译汇总
                        con_pty_mrg += yuanwen
                        con_fy_mrg += fanyi
                        # 各作者所有文章的正文、翻译汇总
                        con_pty_sgl += yuanwen
                        con_fy_sgl += fanyi
                        # 各作者名下单作品评分
                        poetry_name = ptr.replace(u'.txt', '')
                        scr_sgl_ath[poetry_name] = dict(score=float(score), score_populate=int(score_populate))
                # 单个作者作品数量统计
                self.dic_dystany[dystany]['content_poetry_single'][author] = con_pty_sgl
                self.dic_dystany[dystany]['content_fanyi_single'][author] = con_fy_sgl
                self.dic_dystany[dystany]['account_poetry']['author_single'][author] = acnt_pty_ath_sgl
                self.dic_dystany[dystany]['account_score']['score_single_author'][author] = scr_sgl_ath

            # 整个朝代的作品汇总
            self.dic_dystany[dystany]['account_poetry']['poetry_list'] = copy.deepcopy(poetry_list)
            self.dic_dystany[dystany]['account_poetry']['poetry_all'] = len(
                self.dic_dystany[dystany]['account_poetry']['poetry_list'])
            self.dic_dystany[dystany]['content_poetry_merge'] = con_pty_mrg
            self.dic_dystany[dystany]['content_fanyi_merge'] = con_fy_mrg
            self.dic_dystany[dystany]['content_author_intro_merge'] = con_ath_intr_mrg

    @staticmethod
    def rm_invld_charaters(text):
        # 清除一些非法字符串，比如说控制字符
        pattern = u'[^\u0020-\uD7FF\u0009\u000A\u000D\uE000-\uFFFD\u10000-\u10FFFF]+'
        return re.sub(pattern=pattern, repl='', string=text)

    def extract_content(self, content):
        """
        内容处理注意事项
        1、 剔除的文本内容
        2、正文部分提取， 需考虑译文是否存在。评分是否存在
        """
        rm_con1 = u'本页内容整理自网络（或由匿名网友上传）'
        rm_con2 = u'原作者已无法考证'
        rm_con3 = u'版权归原作者所有'
        rm_con4 = u'本站免费发布仅供学习参考'
        rm_con5 = u'，其观点不代表本站立场'
        rm_con6 = u'。站务邮箱'
        rm_con7 = u'service@gushiwen.org'
        rm_con_list = [rm_con1, rm_con2, rm_con3, rm_con4, rm_con5, rm_con6, rm_con7]
        for rm_con in rm_con_list:
            content = content.replace(rm_con, '')
        content = self.rm_invld_charaters(content)

        if u'译文及注释' in content:
            if u'评分人数不足' in content:
                # 记为0分
                pattern = u'(.*?)原文链接：(.*?)\(评分人数不足\)(.*?)原文：(.*?)译文及注释(.*)'
                match = re.findall(pattern, content, re.S)
                try:
                    title = match[0][0]
                except IndexError:
                    # 存在一些脏数据，在翻译后面缀上不完整的原文和评分人数不足，由于太少，手工清理。
                    print content[:100]
                yuanwen_link = match[0][1]
                score_populate = 0
                score = 0
                yuanwen = match[0][3]   # 2 是作者，忽略
                fanyi = match[0][4]
            else:
                pattern = u'(.*?)原文链接：(.*?)\((.*?)人评分\)(.*?)朝代(.*?)原文：(.*?)译文及注释(.*)'
                match = re.findall(pattern, content, re.S)
                title = match[0][0]
                yuanwen_link = match[0][1]
                score_populate = match[0][2]
                score = match[0][3]
                yuanwen = match[0][5]  # 4 是作者，忽略
                fanyi = match[0][6]
        elif u'译文' in content:
            if u'评分人数不足' in content:
                pattern = u'(.*?)原文链接：(.*?)\(评分人数不足\)(.*?)原文：(.*?)译文(.*)'
                match = re.findall(pattern, content, re.S)
                title = match[0][0]
                yuanwen_link = match[0][1]
                score_populate = 0
                score = 0
                yuanwen = match[0][3]  # 2 是作者，忽略
                fanyi = match[0][4]
            else:
                pattern = u'(.*?)原文链接：(.*?)\((.*?)人评分\)(.*?)朝代(.*?)原文：(.*?)译文(.*)'
                match = re.findall(pattern, content, re.S)
                title = match[0][0]
                yuanwen_link = match[0][1]
                score_populate = match[0][2]
                score = match[0][3]
                yuanwen = match[0][5]  # 4 是作者，忽略
                fanyi = match[0][6]
        else:
            # 没有译文的文章，部分会有赏析部分，但数量极少。整个文本内容既作为正文又作为翻译部分处理
            title = ''
            score = 0
            score_populate = 0
            yuanwen = content
            yuanwen_link = '',
            fanyi = content  # 翻译为空

        return title, score, score_populate, yuanwen, yuanwen_link, fanyi

    @staticmethod
    def analysedata():
        # 从上面生成的pickle文件中读取字典里的数据
        pkl_file = open('analyse.pkl', 'rb')
        dic_dystany = pickle.load(pkl_file)
        pkl_file.close()

        # 处理stop words
        stp_file = codecs.open('gswstpwrds.txt', 'r', 'utf8')
        stop_words = stp_file.read()
        stp_file.close()
        stop_words = stop_words.split('\n')
        stop_words = stop_words + [u'\r\n', u'...', u'\r\r', u'so.gushiwen.org', u'佚名\r', ]
        stop_words = Series(stop_words)

        # dy_fanyi_list = [dic_dystany[dy]['content_fanyi_merge'] for dy in dic_dystany.keys()]
        dy_list = [u'先秦', u'两汉', u'魏晋', u'南北朝', u'隋代', u'唐代',
                   u'五代', u'宋代', u'金朝', u'元代', u'明代', u'清代', ]
        # 先秦、唐代、宋代、清代、元代占了全部内容的五分之四，故暂时只考虑这五个朝代
        # dy_list = [u'先秦', u'唐代', u'宋代', u'元代', u'清代']
        # dy_list = [u'金朝']

        # 整合所有翻译文件，用作训练源数据
        # for dystany in dy_list:
        #     filename = dystany + 'fanyi.txt'
        #     merger_file = codecs.open(filename, 'w', 'utf8')
        #     fy_content = dic_dystany[dystany]['content_fanyi_merge']
        #     fy_content = fy_content.replace('\r', '\n').replace('\n\n', '\n').replace('\n\n', '\n')
        #     fy_content = fy_content.replace(u'\u3000\u3000\n', '').replace(u'\u3000\n', '')
        #     merger_file.write(fy_content)
        #     merger_file.close()

        thul = thulac.thulac('-seg_only')
        thul.run()

        writer = ExcelWriter('gushiwen.xlsx')
        for dystany in dy_list:
            fy_content = dic_dystany[dystany]['content_fanyi_merge']
            ls = []
            while len(fy_content) > 10000:
                con = fy_content[:10000]
                fy_content = fy_content[10000:]
                ls = ls + thul.cut(con.encode('utf8'))
            if fy_content:
                ls += thul.cut(fy_content.encode('utf8'))
            fy_cont_seg = [val for val in ls if len(val) > 3]  # 剔除所有单字符,thulac返回的是str,str长度为3
            print type(fy_cont_seg), ' ', len(fy_cont_seg), ' ', dystany
            fy_cont_seg = [val.decode('utf8') for val in fy_cont_seg]
            fy_cont_seg_df = DataFrame({'segment': fy_cont_seg})
            fy_cont_seg_df = fy_cont_seg_df[~fy_cont_seg_df.segment.isin(stop_words)]
            segtat = fy_cont_seg_df.groupby(by=['segment'])['segment'].agg(
                {'count': numpy.size}).reset_index().sort_values(by=['count'], ascending=False)
            segtat.to_excel(writer, dystany)
            writer.save()
            print 'End of dystany : ', dystany
        writer.close()

if __name__ == '__main__':

    # 由本地文件中提取出所有数据，存储在本地pickle文件analyse.pkl中供下一步分析使用
    base_path = u'M:\Stu\Python\Scrapy105\gushiwen\文件输出\全量'
    Analys = AnalysGushiwen(base_path)

    # 导出数据
    Analys.extractdata()
    analysedic = open('analyse.pkl', 'wb')
    pickle.dump(Analys.dic_dystany, analysedic)
    analysedic.close()

    # 分析数据，结果保存在excel表格中
    # Analys.analysedata()