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

## 目录介绍：

* clients       	客户端文件
* server       	 	服务端文件  
* web           	网站文件
* server/config.json	探针配置文件                                
* web/json      	探针月流量 

## 安装方法

### docker-compose （telegram机器人提醒功能需要使用docker，不推荐新手使用）

只提供安装代码，其他请自行搜索，不推荐新手，但爱捣鼓可以试一试，自行研究

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

### 防止受到CC attack时候方便查看机器状态

打开云探针页面，就可以正常的监控。接下来把服务器和客户端脚本自行加入开机启动，或者进程守护，或以后台方式运行即可！例如： nohup python3 client-linux.py &  

`extra scene (run web/ssview.py)`

![Shell View](http://dl.cpp.la/Archive/serverstatus-shell.png)

## 修改方法

配置文件：/usr/local/ServerStatus/server/config.json备份并可自行添加里面部分内容与Region（仅限爱捣鼓或高手修改）

![](https://raw.githubusercontent.com/Spritesmine/Jasmine-Theme/master/Jasmine-Theme/Jasmine-Theme%20(9).png)

## 更新前端

默认服务端更新不会更新前端。因为更新前端会导致自己自定义的前端消失。

```bash
rm -rf /usr/local/ServerStatus/web/*
wget https://github.com/Spritesmine/Jasmine-Theme/releases/latest/download/Jasmine-theme.zip
unzip Jasmine-Theme.zip
mv ./hotaru-theme/* /usr/local/ServerStatus/web/
service status-server restart
# systemctl restart status-server
```

## 关于前端旗帜图标

目前通过脚本使用旗帜图标仅支援当前国家/地区在 ISO 3166-1 标准里，否则可能会出现无法添加的情况，如欧盟 `EU`，但是前端是具备该旗帜的。你可能需要手动加入。方法是修改`/usr/local/ServerStatus/server/config.json`，将你想修改的服务器的`region`改成你需要的。

同时，前端还具备以下特殊旗帜，可供选择使用，启用也是需要上述修改。

Transgender flag: `trans`

Rainbow flag: `rainbow`

Pirate flag: `pirate`

## Toyo版本修改方法

如果你使用 Toyo 版本或其他版本的 ServerStatus，请备份你的config文件并重新编译安装本版本服务端

配置文件: /usr/local/ServerStatus/server/config.json 备份并自行添加`region`

```json
{
   "username": "Name",
   "password": "Password",
   "name": "Your Servername",
   "type": "KVM",
   "host": "None",
   "location": "洛杉矶",
   "disabled": false,
   "region": "US"
},
```

替换配置文件，重启 ServerStatus

## 相关开源项目 ： 
* ServerStatus-Toyo：https://github.com/ToyoDAdoubiBackup/ServerStatus-Toyo MIT License
* ServerStatus：https://github.com/BotoX/ServerStatus WTFPL License
* ServerStatus-Hotaru：https://github.com/cokemine/ServerStatus-Hotaru WTFPL License
* mojeda's ServerStatus: https://github.com/mojeda/ServerStatus WTFPL License -> GNU GPLv3 License (ServerStatus is a full rewrite of mojeda's ServerStatus script and not affected by GPL)
* BlueVM's project: http://www.lowendtalk.com/discussion/comment/169690#Comment_169690 WTFPL License

## 感谢

* i18n-iso-countries: https://github.com/michaelwittig/node-i18n-iso-countries MIT License (To convert country name in Chinese to iso 3166-1 and check if the code is valid)
* jq: https://github.com/stedolan/jq CC BY 3.0 License
* caddy: https://github.com/caddyserver/caddy Apache-2.0 License
* twemoji: https://github.com/twitter/twemoji CC-BY 4.0 License (The flag icons are designed by Twitter)
