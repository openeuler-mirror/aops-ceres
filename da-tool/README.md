
# da-tool

通过`uprobe`或`kprobe`采样可获得函数执行的`trace`,但配置比较复杂，`trace`包含的信息很多，显示不直观。本工具旨在简易配置采样，以及分析所配置的函数的时延特征。

主要应用场景：分析tcp/udp收发相关函数时延特征。

## 原理
基于u/kprobe 采样，可获得内核态和用户态函数的起止执行时间和结束执行时间的trace。
可推导出:
+ 函数间的调用关系
+ 函数的执行时间
+ 线程的调度特征

## 主要功能
+ 分析出内核态函数/用户态函数(C/C++)/sched_switch的时延
+ 统计各调用栈时延平均值
+ 推导调用关系（乱序）
+ 线程调度特征
+ 记录系统信息

## 使用限制
+ 不支持递归函数分析

## 文件夹说明

+ script : shell脚本
    + da-tool.sh  利用`uprobe/kprobe` 采集程序trace，同时可生成analysis需要的配置文件
+ config 配置文件夹
    + da-tool.conf 放置`/etc` 目录下
+ analysis `C++`程序文件
    + config(.cpp/ch ): 解析外部参数 和 `function_config`
    + common.h : 通用参数
    + trace_resolve(.cpp/.h) : 解析trace
    + time_pair(.cpp/.h)::获取各函数的起止时间等信息
    + function_strack(.cpp/.h): 获取各pid 函数调用栈及其时延信息 
    + sched_analysis(.cpp/.h): 计算线程调度信息
+ main.cpp
+ CMakeLists.txt

**本地文件夹**

+ /etc/da-tool.conf : 配置文件，主要配置需要抓取的函数
+ /var/da-tool: 
    + tmp
        + sample_output_* : 采样文件存放位置，可打包
        + analysis_input : 临时用于分析程序的依赖文件
    + analysis_output 
        + debug : 可用于调试的参考日志
        + output : 时延结果信息

## 使用方法

#### 1 配置需要采集的函数
配置文件：da-tool.conf
+ k 开头为 kernel 符号，u 开头为内核符号， s 开头为调度配置（目前仅支持`sched_switch`）
+ k 和 s 只能一行配置完
+ u 可以多行配置, 格式：`[u , 程序路径,二进制名称 ,追踪的函数]`
+ 函数务必存在，否则uprobe 配置不成功，配置的内核符号应在`/proc/kallsyms`能够查询到，配置的用户态程序符号仅支持`C/C++`,配置的符号应用`objdump`能够查询到
+ 每行末尾不要有逗号

配置文件举例如下：
```
# kernel symbol config
k,ksys_write,udp_recvmsg,udp_sendmsg

# sched config
s,sched_switch

# user symbol config (path ,bin,func1,func2)
u,/home/git_repo/nda-tool/nda-tool/test/base_demo/,base_demo_cpp,_Z5func1v,_Z5func2v,_Z5func2i,_Z5func3v,_Z5func4v
u,/home/git_repo/nda-tool/nda-tool/test/net_demo1/,client,sendto,recvfrom
```
备注，为了支持用户态不同二进制重名函数采集，配置`event`时，命名为`u0_func1``、u1_func1`...,以上面配置为例，`loop_func`为`u2_loop_func`,
观测`trace` 结果时不要产生歧义。
#### 2 采集trace并分析

```shell
da-tool.sh -t 10 # 采集10秒并分析结果
```
采集后会在`/var/da-tool/tmp`文件夹下生成一个`output_时间`格式的文件夹,包含此次采样的结果。
分析完成后会在`/var/da-tool/analysis-output/ouput/`下生成分析结果

```
├──pid:1473358{(868869,100.000%)}
│          │          ├─────u0__Z5func1v{(local: 19, 0.002%, 19.000)(global:150399, 17.310% ,150399.000), times:1, (int)ret>=0 times:1}
│          │          │          ├─────sched_switch{(local: 150380, 17.308%, 150380.000)(global:150380, 17.308% ,150380.000), times:1, (int)ret>=0 times:1}
```
以此结果为例，`u0__Z5func1v` 和 `sched_switch` 为 该进程在运行期间执行的函数，`sched_switch`执行周期在 `u0__Z5func1v` 周期内，`(local: 19, 0.002%, 19.000)` 表示该函数剔除子函数和调度所执行的时间，三个参数分别为，总时间、所占整个pid有效时间的百分比，平均时间，`global` 为不剔除子函数所占的时间，`times` 是该函数调用栈的次数，`(int)ret>=0 times`:表示该函数返回值转换为(int)后大于等于0的次数，无返回值函数返回值认为是0.
以上时间单位为微秒。
## 注意
+ 确保trace 中有需要采集的函数的完整调用栈
+ 采样时间和函数需要人为评估，某些函数短时间可能采到大量trace，日志过大，解析过慢

### 扩展功能
da-tool 生成的结果信息可调用 火焰图生成工具，可视化分析结果，
`./flamegraph.pl` 可在 https://gitee.com/mirrors/FlameGraph 中获取
```shell
# 全部信息
cat /var/da-tool/analysis_output/output/func_delay_stack | grep -o '^[^,]*' | ./flamegraph.pl --countname "delay sum" > allpid.svg
# 指定pid
cat /var/da-tool/analysis_output/output/func_delay_stack | grep -o '^[^,]*' | grep -E 'pid1|pid2' | ./flamegraph.pl --countname "delay sum" > pid.svg
```

### 常见错误说明

**配置了不存在的符号**
```
Failed to find symbol aaaa in kernel
  Error: Failed to add events.
```
**符号已存在,重复配置**
```
Error: event "aaaa" already exists.
 Hint: Remove existing event by 'perf probe -d'
       or force duplicates by 'perf probe -f'
       or set 'force=yes' in BPF source.
  Error: Failed to add events.
```

### 注意事项
+ 配置注意事项
    + 配置`/etc/da-tool.conf` 时，注意所配置符号一定存在
    + 内核符号可在`/proc/kallsyms` 中查看，用户态程序符号 可用`objdump -d 二进制 | grep 函数名` 匹配正确的符号
    + 某些函数名可能存在点(eg:A.B.C),暂**不支持配置此类函数**，例如经过gcc优化选项`-fipa-sra`优化后，函数符号后缀会有`.rsra.num`。
    + 某些函数可能短时间执行大量次数，此时`trace`很大，解析时间会很长，需要认为评估配置的函数运行情况，合理设置采样时间
    + 由于`trace`可能存在不完整的调用关系，很有可能在`trace`中存在的数据分析时舍弃，如果单次采样没有抓到需要的pid信息，建议多采样几次
    + 有时`trace`中会有数据丢失，结果可能异常，常见的异常原因为`trace`过大，内核刷新数据时不正常，建议减小采样时间。
    + 不支持递归函数



