# Scrabble Cheat

A simple Scrabble cheat program.

Scrabble: https://en.wikipedia.org/wiki/Scrabble

#### English:
When I played Scrabble with my daughter, I found that there was no reliable assistant(cheat) software on the Apple's iPad (but Android has), so I wrote a simple web based cheat program that she could use it via browser on the iPad.

#### Chinese:
最近在和女儿玩Scrabble，但是女儿的iPad却没有好用的作弊（辅助）工具软件，所以自己用Python做了一个简单的基于WEB的工具，这样她通过浏览器就可以查询单词，顺利游戏了。

#### Requirement:
	sudo apt install python3-tornado

#### Download:
	git clone https://github.com/gzhechu/scrabblecheat.git --depth=1

#### Run:
	hechu@home:~/study/english/scrabblecheat$ ./cheat.py 
	load 3449 new 高中 words from file
	load 1252 new PET words from file
	load 1442 new CET4 words from file
	load 1013 new CET6 words from file
	time consuming: 0.09710734000000001s
	[I 200131 17:47:08 cheat:297] listening on port: 8123

Default listening port is 8123, visit it via web browser, such as: http://192.168.1.100:8123/

#### Issues:
To avoid the decode problem when load word list, set system locales to UTF-8 before run the script. For example: 

	export LC_ALL="zh_CN.UTF-8"
	export LC_CTYPE="zh_CN.UTF-8"

#### User Interface:
![user interface](./static/ui.png  "UI")