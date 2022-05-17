# ServerStatus-Jasmine

[![Python Support](https://img.shields.io/badge/python-2.7%2B%20-blue.svg)](https://github.com/Spritesmine/ServerStatus-Jasmine)
[![C++ Compiler](http://img.shields.io/badge/C++-GNU-blue.svg?style=flat&logo=cplusplus)](https://github.com/Spritesmine/ServerStatus-Jasmine)
[![License](https://img.shields.io/badge/license-MIT-4EB1BA.svg?style=flat-square)](https://github.com/Spritesmine/ServerStatus-Jasmine)
[![Version](https://img.shields.io/badge/Version-Beta%202.2.0-red)](https://github.com/Spritesmine/ServerStatus-Jasmine)

项目暂未完善，暂未测试，耐心等待，大佬可自行测试

云探针、多服务器探针、云监控、多服务器云监控

基于 ServerStatus-Toyo 与 ServerStatus-Hotaru 的版本修改。

![](https://raw.githubusercontent.com/Spritesmine/Jasmine-Theme/master/Jasmine-Theme/Jasmine-Theme%20(1).jpg)

## 特性

服务端客户端脚本支持系统：Centos 7、Debian 8、Ubuntu 15.10 及以上、ArchLinux 等...

Python 客户端：支持 Python 版本：Python 2.7 +

流量计算：客户端可以选择使用 vnStat 按月计算流量，会自动编译安装最新版本vnStat（ArchLinux 会从软件源安装最新版本）。如不使用 vnStat ，则默认计算流量方式为重启后流量清零。请注意 ServerStatus 不会把协议为 GPLv2 的 vnStat 作为必须的依赖。

前端基于HTML+CSS+JS 制作，如需修改前端建议自行修改。

前端所使用一些调用见前端仓库的声明。

前端开源地址：https://github.com/Spritesmine/Jasmine-Theme

# 目录介绍：

* clients       	客户端文件
* server       	 	服务端文件  
* web           	网站文件
* server/config.json	探针配置文件                                
* web/json      	探针月流量 

## 安装方法

### docker-compose （telegram机器人提醒功能需要使用docker，不推荐新手使用）

只提供安装代码，其他请自行搜索，不推荐新手，但爱捣鼓可以试一试

`curl -sSL https://get.docker.com/ | sh && apt -y install docker-compose` 

### 服务端：

```bash
wget https://raw.githubusercontent.com/Spritesmine/ServerStatus-Jasmine/master/status.sh
# wget https://qisansui.coding.net/p/agony/d/ServerStatus-Jasmine/git/raw/master/status.sh 若服务器位于中国大陆建议选择Coding.net仓库
bash status.sh s
```

1、选择1，配置服务端

2、没什么需求的话，端口建议默认就好

3、如果本地没装别的如Nginx或者Apache之类的，直接Y就好

4、绑定域名或IP访问

5、端口自主选择

6、添加客户端：选择7后选1

剩下的信息自己填就好了

7、删除（修改）服务端：选7后在选择


### 客户端：

```
bash status.sh c
```


后选1然后按照服务端填写的即可

## 修改方法

配置文件：/usr/local/ServerStatus/server/config.json备份并可自行添加里面部分内容与Region（仅限爱捣鼓或高手修改）

![](https://raw.githubusercontent.com/Spritesmine/Jasmine-Theme/master/Jasmine-Theme/Jasmine-Theme%20(9).png)
