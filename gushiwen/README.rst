========
gushiwen
========

本scrapy项目用于爬取古诗文网（gushiwen.org）
仅用于学习交流使用

Items
=========

该Items定义爬取古诗文网主要内容：
   作品：名称、朝代、作者、原文、评分
   参考翻译：译文及注释
   参考赏析：创作背景、鉴赏、赏析、
   作者介绍：作者名、生卒年、字、参考资料

class::
      
	  
	  gushiwen.items.Poetry

参见源码


Spiders
=========


URL规则：
so.gushiwen.org/tpye.aspx?p=1&t=写景&c=唐代
页码: p=1
类别：t=写景
朝代: c=唐代






Pipelines
=========


保存文件目录结构：

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
	
		