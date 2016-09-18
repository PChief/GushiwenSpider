
GushiwenSpider
========

本项目用于爬取古诗文网（gushiwen.org），以scrapy框架为基础爬取提取数据，通过MySQL存储临时数据，最终保存在本地TXT文件中。

爬取完毕后对数据进行了统计分析，详见[古诗文网词频简要分析](https://github.com/PChief/GushiwenSpider/blob/master/%E5%8F%A4%E8%AF%97%E6%96%87%E7%BD%91%E8%AF%8D%E9%A2%91%E7%AE%80%E8%A6%81%E5%88%86%E6%9E%90.md)

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
十二个朝代

![image](https://github.com/PChief/GushiwenSpider/blob/master/imgs/%E5%8D%81%E4%BA%8C%E6%9C%9D%E7%9B%AE%E5%BD%95%E7%BB%93%E6%9E%84.png)

唐代-诗仙李白

![image](https://github.com/PChief/GushiwenSpider/blob/master/imgs/%E5%94%90%E6%9C%9D-%E6%9D%8E%E7%99%BD.png)

唐代-诗圣杜甫

![image](https://github.com/PChief/GushiwenSpider/blob/master/imgs/%E5%94%90%E6%9C%9D-%E6%9D%9C%E7%94%AB.png)

唐代-诗魔白居易

![image](https://github.com/PChief/GushiwenSpider/blob/master/imgs/%E5%94%90%E6%9C%9D-%E7%99%BD%E5%B1%85%E6%98%93.png)


宋代-词中女神李清照

![image](https://github.com/PChief/GushiwenSpider/blob/master/imgs/%E5%AE%8B%E4%BB%A3-%E8%AF%8D%E4%B8%AD%E5%A5%B3%E7%A5%9E%E6%9D%8E%E6%B8%85%E7%85%A7.png)
    
 
   
宋代-苏轼

![image](https://github.com/PChief/GushiwenSpider/blob/master/imgs/%E5%AE%8B%E4%BB%A3-%E8%8B%8F%E8%BD%BC.png)

宋代-陆游

![image](https://github.com/PChief/GushiwenSpider/blob/master/imgs/%E5%AE%8B%E4%BB%A3-%E9%99%86%E6%B8%B8.png)

金朝元好问

![image](https://github.com/PChief/GushiwenSpider/blob/master/imgs/%E9%87%91%E6%9C%9D%E5%85%83%E5%A5%BD%E9%97%AE01.png)


清代-曹雪芹

![image](https://github.com/PChief/GushiwenSpider/blob/master/imgs/%E6%B8%85%E4%BB%A3-%E6%9B%B9%E9%9B%AA%E8%8A%B9.png)

清代-纳兰性德

![image](https://github.com/PChief/GushiwenSpider/blob/master/imgs/%E6%B8%85%E4%BB%A3-%E7%BA%B3%E5%85%B0%E5%AE%B9%E8%8B%A5.png)
