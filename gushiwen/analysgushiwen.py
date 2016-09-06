# _*_ coding:utf8 _*_

# 作者: W.S.K
"""
遍历指定目录下的所有文件，根据获取到的文件名判断是否为目录，递归判断
根据目录结构创建字典文件，字典文件保存到本地
字典结构见val = dict()
"""
import re
import os
from glob import glob


class AnalysGushiwen():

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

            account_poetry=dict(
                author_all=0,  # 所有作者总数
                author_list=[],
                poetry_all=0,  # 所有作品个数
                poetry_list=[],
                author_single=dict(
                    # 统计每个作者的作品数量
                    # author2=20,
                ),
            ),

            # 统计所有数据部分，用于数据分析
            account_score=dict(
                score_people=0,
                score_total=0,
                score_average=0,
                score_single_author={
                    # author_name = {
                    #     score_max = 0,
                    #     score_min = 0,
                    #     score_average = 0,
                    #     score_total = 0，
                    #     score_people_account = 0,
                    # },
                },

                score_single_poetry={
                    # poetry = dict(peoples=0, score=0)
                },
            ),
        )

        # 初始化所有的字典，朝代为键值
        self.dic_dystany = {k: self.val for k in self.keyslist}
        self.basepath = base_path



    def egodpath(self):
        base_dir = u'F:\Github\输出文件\古诗文\统计'
        # for dystany in self.keyslist:
        for dystany in [u'金朝', u'先秦']:  # 以金朝为测试目标

            # I:\Stu\Python\Scrapy105\gushiwen\文件输出\全量\金朝
            # dystany_path = os.path.join(self.basepath, dystany)

            # 各朝代内容（正文、翻译、作者介绍）汇总
            con_pty_mrg = self.dic_dystany[dystany]['content_poetry_merge']
            con_fy_mrg = self.dic_dystany[dystany]['content_fanyi_merge']
            con_ath_intr_mrg = self.dic_dystany[dystany]['content_author_intro_merge']
            author_list = os.listdir(os.path.join(base_dir, dystany))  # [u'元好问', u'刘迎', u'赵秉文']
            self.dic_dystany[dystany]['account_poetry']['author_all'] = len(author_list)
            self.dic_dystany[dystany]['account_poetry']['author_list'] = author_list
            dystany_poetry_list = self.dic_dystany[dystany]['account_poetry']['poetry_list']
            # 各朝评分数据汇总
            score_people = self.dic_dystany[dystany]['account_score']['score_people']
            score_total = self.dic_dystany[dystany]['account_score']['score_total']  # 所有作品分数累加
            for author in author_list:
                # 各作者内容（正文、翻译、作者介绍）汇总
                self.dic_dystany[dystany]['content_poetry_single'][author] = ''
                con_pty_sgl = self.dic_dystany[dystany]['content_poetry_single'][author]
                self.dic_dystany[dystany]['content_fanyi_single'][author] = ''
                con_fy_sgl = self.dic_dystany[dystany]['content_fanyi_single'][author]
                # 单个作者介绍不需要累加记录，如果是佚名的话没有介绍
                self.dic_dystany[dystany]['content_author_intro_single'][author] = ''
                con_ath_inr_sgl = self.dic_dystany[dystany]['content_author_intro_single'][author]

                # 单个作者作品统计
                self.dic_dystany[dystany]['account_poetry']['author_single'][author] = 0
                acnt_pty_ath_sgl = self.dic_dystany[dystany]['account_poetry']['author_single'][author]

                # 评分内容统计：  作者评分汇总 ， 作品评分汇总
                self.dic_dystany[dystany]['account_score']['score_single_author'][author] = {}
                scr_sgl_ath = self.dic_dystany[dystany]['account_score']['score_single_author'][author]
                scr_sgl_ath['score_max'] = 0.0
                scr_sgl_ath['score_min'] = 10.0
                scr_sgl_ath['score_people_account'] = 0  #  总评分人数
                scr_sgl_ath['score_total'] = 0           # 各作品评分累加
                scr_sgl_ath['score_average'] = 0         # 总分除以作品数

                # 获取作者目录下的所有文件，识别作者介绍与作品
                cur_path = os.path.join(base_dir, dystany, author)
                txt_list = os.listdir(cur_path)
                ath_intr_file_name_list = [fn for fn in txt_list if u'简介' in fn]
                # 判断有无作者，有作者的才会统计作者相关
                if ath_intr_file_name_list:
                    ath_intr_file_name = ath_intr_file_name_list[0]
                    ath_intr_file = open(os.path.join(cur_path, ath_intr_file_name), 'r')
                    ath_intr = ath_intr_file.read()
                    ath_intr_file.close()

                    # 处理作者介绍部分
                    con_ath_intr_mrg = con_ath_intr_mrg + ath_intr  # 计入所有作者简介总和
                    con_ath_inr_sgl = ath_intr  # 单独一个作者的介绍

                    # 处理作品部分,当前作者名下的所有作品列表
                    cur_ath_poetry_list = txt_list.remove(ath_intr_file_name)
                    dystany_poetry_list = dystany_poetry_list + cur_ath_poetry_list
                    for ptr in cur_ath_poetry_list:
                        ptr_file = open(os.path.join(cur_path, ptr), 'r')
                        ptr_con = ptr_file.read()
                        ptr_file.close()

                else:
                    # 佚名或者类似于孟子及其弟子或者刘向 撰暂且忽略不计，只有先秦和两汉有一小部分
                    ath_intr_file_name = 'NoAuthor'
                    # 无作者简介，全部都是作品了
                    dystany_poetry_list = dystany_poetry_list + txt_list

                print ath_intr_file_name, dystany

                #  作品评分汇总
                # scr_sgl_pty = self.dic_dystany[dystany]['account_single_poetry']['poetry']



            # 统计本朝代的所有作品的平均评分
            self.dic_dystany[dystany]['account_poetry']['poetry_all'] = len(dystany_poetry_list)
            self.dic_dystany[dystany]['account_score']['score_average'] = score_total/len(dystany_poetry_list)




    def extract_content(self, content):
        """
        内容处理注意事项
        1、 剔除的文本内容
        2、正文部分提取， 需考虑译文是否存在。评分是否存在
        """
        rm_con1 = '本页内容整理自网络（或由匿名网友上传），原作者已无法考证，版权归原作者所有。' \
                  '本站免费发布仅供学习参考，其观点不代表本站立场。站务邮箱：service@gushiwen.org'
        content = content.replace(rm_con1, '')

        if '译文及注释' in content:
            if '评分人数不足' in content:
                # 记为0分
                pattern = ''

            else:
                pattern = ''

        elif '译文' in content:
            if '评分人数不足' in content:
                pattern = ''

            else:
                pattern = ''

        else:
            zhengwen = '',
            fanyi = ''  # 翻译为空

        title = ''
        score = 0

        return title, score



if __name__ == '__main__':
    base_path = u'F:\Github\输出文件\古诗文\统计'
    EgdPath = AnalysGushiwen(base_path)
    EgdPath.egodpath()


