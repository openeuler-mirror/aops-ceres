
# da-tool

通过`uprobe`或`kprobe`采样可获得函数执行的`trace`，但配置比较复杂，`trace`包含的信息很多，显示不直观。本工具旨在简易配置采样，以及分析所配置的函数的时延特征。

主要应用场景：分析`tcp/udp`收发相关函数时延特征。

## 文件夹说明
**工程文件夹**
+ script : shell脚本
    + da-tool.sh  利用`uprobe/kprobe` 采集程序 `trace`，同时可生成analysis需要的配置文件
+ config 配置文件夹
    + da-tool.conf 放置`/etc` 目录下
+ analysis `C++`程序文件
    + config(.cpp/ch ): 解析外部参数 和 `function_config`
    + common.h : 通用参数
    + trace_resolve(.cpp/.h) : 解析`trace`
    + time_pair(.cpp/.h)::获取各函数的起止时间等信息
    + function_strack(.cpp/.h): 获取各pid 函数调用栈及其时延信息 
    + sched_analysis(.cpp/.h): 计算线程调度信息
+ main.cpp
+ CMakeLists.txt
+ test : 测试程序



## 详情

|主题|内容简介|是否发布|
|:----|:-----|:----|
|[openEuler指南](https://gitee.com/openeuler/community/blob/master/zh/contributors/README.md)| 如何参与openEuler社区 | 已发布 |
|[da-tool 使用指南](https://gitee.com/openeuler/docs/blob/stable2-20.03_LTS_SP3/docs/zh/docs/A-Ops/da-tool%E4%BD%BF%E7%94%A8%E6%89%8B%E5%86%8C.md)|1. 安装、配置和运行应用程序<br>2. 分析结果说明<br>3. 使用注意事项|已发布|
|da-tool设计文档|1. 技术原理<br> 2. 开发指南 |暂未发布|

