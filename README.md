# ServerStatus-Jasmine

- - 项目暂未完善，暂未测试，耐心等待，大佬可自行测试 - -

云探针、多服务器探针、云监控、多服务器云监控

基于 ServerStatus-Toyo 与 ServerStatus-Hotaru 的版本修改。

## 特性

服务端客户端脚本支持系统：Centos 7、Debian 8、Ubuntu 15.10 及以上、ArchLinux 等...

Python 客户端：支持 Python 版本：Python 2.7 +

流量计算：客户端可以选择使用 vnStat 按月计算流量，会自动编译安装最新版本vnStat（ArchLinux 会从软件源安装最新版本）。如不使用 vnStat ，则默认计算流量方式为重启后流量清零。请注意 ServerStatus 不会把协议为 GPLv2 的 vnStat 作为必须的依赖。

前端基于HTML+CSS+JS 制作，如需修改前端建议自行修改。

前端所使用一些调用见前端仓库的声明。

前端开源地址：https://github.com/Spritesmine/Jasmine-Theme

## 安装方法

服务端：

```bash
wget https://raw.githubusercontent.com/Spritesmine/ServerStatus-Jasmine/master/status.sh
# wget https://qisansui.coding.net/p/agony/d/ServerStatus-Jasmine/git/raw/master/status.sh 若服务器位于中国大陆建议选择Coding.net仓库
bash status.sh s
```

客户端：

```
bash status.sh c
```
