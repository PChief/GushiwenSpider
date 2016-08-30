
gushiwen
========

本scrapy项目用于爬取古诗文网（gushiwen.org），以scrapy框架为基础爬取提取数据，通过MySQL作为临时数据存储，最终保存在本地TXT文件中。

***仅用于学习交流使用***



爬取古诗文网主要内容：

     作品：名称、朝代、作者、原文、评分
     
     参考翻译：译文及注释
     
     参考赏析：创作背景、鉴赏、赏析、
     
     作者介绍：作者名、生卒年、字、参考资料
     



Spiders
=========


    URL规则：
    
         so.gushiwen.org/tpye.aspx?p=1&t=写景&c=唐代
         
    页码: p=1
    
    类别：t=写景
    
    朝代: c=唐代









保存文件目录结构：
=========

先秦/
        

    佚名/
    
	     作品1
	     作品2
		
		.....
		
	左丘明/
	
	      左丘明简介.txt
	      左丘明头像.jpg
	      曹刿论战.txt
	      子鱼论战.txt
	      .....
		  
	屈原/
	  
	      屈原简介.txt
	      屈原头像.jpg
	      离骚.txt
	      九歌.txt
	      .....
	    
    两汉/
    

        .../
	   

        .../
    
# 保存结果示例
十二个朝代

![image](https://github.com/PChief/GushiwenSpider/blob/master/imgs/%E5%8D%81%E4%BA%8C%E6%9C%9D%E7%9B%AE%E5%BD%95%E7%BB%93%E6%9E%84.png)

宋朝截图01

![image](https://github.com/PChief/GushiwenSpider/blob/master/imgs/%E5%AE%8B%E6%9C%9D%E6%88%AA%E5%9B%BE01.png)
    
 
   
宋朝截图02-曾巩

![image](https://github.com/PChief/GushiwenSpider/blob/master/imgs/%E5%AE%8B%E6%9C%9D%E6%88%AA%E5%9B%BE02-%E6%9B%BE%E5%B7%A9.png)

金朝元好问01

![image](https://github.com/PChief/GushiwenSpider/blob/master/imgs/%E9%87%91%E6%9C%9D%E5%85%83%E5%A5%BD%E9%97%AE01.png)

金朝元好问02

![image](https://github.com/PChief/GushiwenSpider/blob/master/imgs/%E9%87%91%E6%9C%9D%E5%85%83%E5%A5%BD%E9%97%AE02.png)  
    
