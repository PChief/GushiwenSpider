
GushiwenSpider
========

本项目用于爬取[古诗文网](http://www.gushiwen.org)，以[**scrapy**](https://scrapy.org/)开源框架为基础提取历朝历代诗词作品、作者介绍等内容，结合[**scrapy_redis**](https://github.com/rolando/scrapy-redis)部署分布式爬虫，通过**MySQL**存储提取数据，最终可根据需要保存在本地TXT文件中。

爬取完毕后对数据进行了统计分析，详见[古诗文网词频简要分析](https://github.com/PChief/GushiwenSpider/blob/master/%E5%8F%A4%E8%AF%97%E6%96%87%E7%BD%91%E8%AF%8D%E9%A2%91%E7%AE%80%E8%A6%81%E5%88%86%E6%9E%90.md)

爬取古诗文网主要内容：

     作品：名称、朝代、作者、原文、评分
     
     参考翻译：译文及注释
     
     参考赏析：创作背景、鉴赏、赏析、
     
     作者介绍：作者名、生卒年、字、参考资料
     



Spiders
=========


   一共四只爬虫，采用分布式部署：
   
      爬虫执行顺序：
          gushiwen --> view_spider --> author_spider --> fanyi_spider
   
  [gushiwen](https://github.com/PChief/GushiwenSpider/blob/master/gushiwen/spiders/gushiwen_spider.py)
  
     本程序为主程序，负责提取作品的URL (http://so.gushiwen.org/view_xxxx.apsx) ， 写入redis队列view:start_urls中，交给view_spider爬取处理。
     
     从作品URL中提取：
     
     view编号(view_xxxx)，lpush到本地redis的view_num，在保存作品内容(执行save脚本)到本地的时候，从中读取view编号，再查询数据库提取相关内容。
     author链接(http://so.gushiwen.org/author_xxxx.apsx)，lpush到本地redis的author:start_urls,供author_spider爬取处理。
     author编号(author_xxx),同上，lpush到本地redis的author_num，在保存作品内容(执行save脚本)到本地的时候，从中读取author编号，再查询数据库提取相关内容。 
     fanyi链接(fanyi_xxx)，lpush到本地redis的fanyi:start_urls。在保存作品内容(执行save脚本)到本地的时候，首先从表bview中读取fanyi_list,该fanyi_list为fanyi_num以逗号(',')相隔，再依据fanyi_numc从表fanyi中读取content，再保存到本地。 
       
  [author_spider](https://github.com/PChief/GushiwenSpider/blob/master/gushiwen/spiders/author_spider.py)
  
     处理作者介绍部分
     作者简介与作品正文处理方式相同
     作者生平事迹等与作品翻译处理方式相同
       
  [fanyi_spider](https://github.com/PChief/GushiwenSpider/blob/master/gushiwen/spiders/fanyi_spider.py)

    从redis队列 fanyi:start_urls
       获取链接：
           http://so.gushiwen.org/shangxi_4323.aspx
           http://so.gushiwen.org/fanyi_3024.aspx
       提取翻译正文部分，存入数据库
           fanyi_3024 content
           shangxi_4323 content





  URL规则：
    
    so.gushiwen.org/tpye.aspx?p=1&t=写景&c=唐代
    页码: p=1
    类别：t=写景
    朝代: c=唐代





执行save脚本保存提取内容到本地，目录结构如下：
=========

先秦/
        

    佚名/
    
	     作品1
	     作品2
		
		.....
		
	左丘明/
	
	      左丘明简介.txt
	      曹刿论战.txt
	      子鱼论战.txt
	      .....
		  
	屈原/
	  
	      屈原简介.txt
	      离骚.txt
	      九歌.txt
	      .....
	    
两汉/
    

        .../
	   

        .../
    
# 保存结果示例
**十二个朝代**

![image](https://github.com/PChief/GushiwenSpider/blob/master/imgs/%E5%8D%81%E4%BA%8C%E6%9C%9D%E7%9B%AE%E5%BD%95%E7%BB%93%E6%9E%84.png)

**唐代-诗仙李白**

![image](https://github.com/PChief/GushiwenSpider/blob/master/imgs/%E5%94%90%E6%9C%9D-%E6%9D%8E%E7%99%BD.png)

**唐代-诗圣杜甫**

![image](https://github.com/PChief/GushiwenSpider/blob/master/imgs/%E5%94%90%E6%9C%9D-%E6%9D%9C%E7%94%AB.png)

**唐代-诗魔白居易**

![image](https://github.com/PChief/GushiwenSpider/blob/master/imgs/%E5%94%90%E6%9C%9D-%E7%99%BD%E5%B1%85%E6%98%93.png)


**宋代-词中女神李清照**

![image](https://github.com/PChief/GushiwenSpider/blob/master/imgs/%E5%AE%8B%E4%BB%A3-%E8%AF%8D%E4%B8%AD%E5%A5%B3%E7%A5%9E%E6%9D%8E%E6%B8%85%E7%85%A7.png)
    
 
   
**宋代-苏轼**

![image](https://github.com/PChief/GushiwenSpider/blob/master/imgs/%E5%AE%8B%E4%BB%A3-%E8%8B%8F%E8%BD%BC.png)

**宋代-陆游**

![image](https://github.com/PChief/GushiwenSpider/blob/master/imgs/%E5%AE%8B%E4%BB%A3-%E9%99%86%E6%B8%B8.png)

**金朝-元好问**

![image](https://github.com/PChief/GushiwenSpider/blob/master/imgs/%E9%87%91%E6%9C%9D%E5%85%83%E5%A5%BD%E9%97%AE01.png)


**清代-曹雪芹**

![image](https://github.com/PChief/GushiwenSpider/blob/master/imgs/%E6%B8%85%E4%BB%A3-%E6%9B%B9%E9%9B%AA%E8%8A%B9.png)

**清代-纳兰性德**

![image](https://github.com/PChief/GushiwenSpider/blob/master/imgs/%E6%B8%85%E4%BB%A3-%E7%BA%B3%E5%85%B0%E5%AE%B9%E8%8B%A5.png)


# 数据库查询结果示例



唐代作品评分排名前三十且评分人数超过一千人：

![image](https://github.com/PChief/GushiwenSpider/blob/master/imgs/%E5%94%90%E4%BB%A3%E8%AF%84%E5%88%86%E4%BA%BA%E6%95%B0%E8%B6%85%E8%BF%871000%E4%BA%BA%E8%AF%84%E5%88%86%E5%89%8D30.png)

宋代作品评分排名前三十且评分人数超过一千人：

![image](https://github.com/PChief/GushiwenSpider/blob/master/imgs/%E5%AE%8B%E4%BB%A3%E8%AF%84%E5%88%86%E4%BA%BA%E6%95%B0%E8%B6%85%E8%BF%871000%E4%BA%BA%E8%AF%84%E5%88%86%E5%89%8D30.png)

唐代和宋代作品评分排名前三十且评分人数超过一千人：

![image](https://github.com/PChief/GushiwenSpider/blob/master/imgs/%E5%94%90%E5%AE%8B%E8%AF%84%E5%88%86%E4%BA%BA%E6%95%B0%E8%B6%85%E8%BF%871000%E4%BA%BA%E8%AF%84%E5%88%86%E5%89%8D30.png)

