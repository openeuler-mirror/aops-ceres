
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

+ 推导调用关系（乱序）
+ 统计各函数调用栈时延信息
+ 线程调度特征
+ 记录系统信息

## 使用限制
+ 不支持递归函数分析

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
### 命令格式
时延分析工具通过`da-tool.sh`命令采集和分析函数时延，使用格式为

**da-tool.sh**  [-t <*probe time*>]

|参数|是否必选|参数函数|
|----|--------|-------|
|-t |否| 采集函数 `trace` 的时长，单位秒，最大限制 100，默认10|

### 自定义配置函数
配置文件：`/etc/da-tool.conf`

举例如下：
```
# /etc/da-tool.conf

# kernel symbol config (ref: /proc/kallsyms)
k,udp_recvmsg,udp_sendmsg,dev_queue_xmit,udp_send_skb,sock_recvmsg,__skb_recv_udp,udp_rcv

# sched config
s,sched_switch

# user symbol config (format : u,path,bin_name,func1,func2,...,funcN)
# u,/path/,bin_name,sendto
u,/home/git_repo/nda-tool/nda-tool/test/net_demo2/,server_no_blk,recvfrom
u,/home/git_repo/nda-tool/nda-tool/test/net_demo2/,client_to_noblk,sendto
u,/home/git_repo/nda-tool/nda-tool/test/base_demo/,base_demo_cpp,_Z5func1v,_Z5func2v,_Z5func2i,_Z5func3v,_Z5func4v
# end
```

+ k 开头为 kernel 符号，u 开头为用户态程序符号， s 开头为调度配置（目前仅支持`sched_switch`且必须配置）
+ k 和 s 只能一行配置完
+ u 可以多行配置, 格式：`[u,程序路径,二进制名称,追踪的函数]`
+ 请确保函数存在，否则 `uprobe` 配置不成功，所配置的内核符号应在`/proc/kallsyms`能够查询到，所配置的用户态程序符号仅支持`C/C++`，且通过`objdump`应能够查询到
+ 每行末尾不要有逗号


注意，为了支持用户态不同二进制重名函数采集，配置`event`时，命名为`u0_func1`、`u1_func1`...，以上面配置为例，`_Z5func1v`为`u2__Z5func1v`。
### 分析结果说明

+ 终端输出结果：各函数调用栈的时延信息
+ 文件夹输出结果 ： `/var/da-tool/analysis-output/ouput/`
    + func_delay_stack : 函数调用栈时延结果
    + process_sched_info ：进程的调度信息
    + summary_delay.csv ： 时延分析总结报告
    + summary_sched.csv ： 调度分析总结报告

#### 终端输出结果介绍
```
├──pid: 222459{local:(450040, 44.988%), global:(1000346, 100.000%)}
│         ├─────sched_switch{local:(13160, 1.316%, 453.793), global:(13160, 1.316%, 453.793), times:29, (int)ret>=0 times:29}
│         └─────u0_recvfrom{local:(422312, 42.217%, 10.729), global:(537146, 53.696%, 13.646), times:39362, (int)ret>=0 times:20}
│                  ├─────sched_switch{local:(2927, 0.293%, 209.071), global:(2927, 0.293%, 209.071), times:14, (int)ret>=0 times:14}
│                  └─────sock_recvmsg{local:(55313, 5.529%, 1.405), global:(111907, 11.187%, 2.843), times:39362, (int)ret>=0 times:20}
│                           └─────udp_recvmsg{local:(36357, 3.634%, 0.924), global:(56594, 5.657%, 1.438), times:39362, (int)ret>=0 times:20}
│                                    └─────__skb_recv_udp{local:(20237, 2.023%, 0.514), global:(20237, 2.023%, 0.514), times:39362, (int)ret>=0 times:39342}

```
以此结果为例，该进程是一个udp非阻塞收包进程。
+ `u0_recvfrom` 为该进程在运行后执行的用户态函数，`u0_` 前缀表示第一个应用程序的函数，实际函数名为`recvfrom`；`sched_switch` 为调度函数；其余函数为内核函数
+ `global` 和 `local` 对应的括号内为该函数执行的时延信息，其中 `local` 是剔除掉子函数和调度所执行的时间 ， `global` 为该函数实际执行时长
+ 每个函数的 `global` 和 `local` 的括号内三个信息分别为，时延，该时延所占进程全部时间的百分比，平均时延（时延/执行次数）
+ 每一级函数的 `global` 时间等于本级函数`local`时间与下一级所有函数的 `global` 时间之和
+ `times` 是该函数调用栈的次数，
+ `(int)ret>=0 times`:表示该函数返回值转换为`int`后大于等于0的次数，无返回值函数返回值是无效的值
+ 以上时间单位为微秒

#### 文件夹结果介绍

**时延和调用关系信息**：`/var/da-tool/analysis_output/output/func_delay_stack`
```
# 此部分信息为终端输出结果的文件格式存储
pid_222459;sched_switch 13160, localDelaySum ,13160, localAvedelay ,453.793103, localPercentage, 1.316%, globalDelaySum ,13160, globalAvedelay, 453.793103, globalPercentage, 1.316%, times ,   29, (int)ret>=0 times ,29
pid_222459;u0_recvfrom;sched_switch 2927, localDelaySum ,2927, localAvedelay ,209.071429, localPercentage, 0.293%, globalDelaySum ,2927, globalAvedelay, 209.071429, globalPercentage, 0.293%, times ,   14, (int)ret>=0 times ,14
pid_222459;u0_recvfrom 422312, localDelaySum ,422312, localAvedelay ,10.728926, localPercentage, 42.217%, globalDelaySum ,537146, globalAvedelay, 13.646309, globalPercentage, 53.696%, times ,39362, (int)ret>=0 times ,20
pid_222459;u0_recvfrom;sock_recvmsg 55313, localDelaySum ,55313, localAvedelay ,1.405239, localPercentage, 5.529%, globalDelaySum ,111907, globalAvedelay, 2.843021, globalPercentage, 11.187%, times ,39362, (int)ret>=0 times ,20
pid_222459;u0_recvfrom;sock_recvmsg;udp_recvmsg 36357, localDelaySum ,36357, localAvedelay ,0.923657, localPercentage, 3.634%, globalDelaySum ,56594, globalAvedelay, 1.437783, globalPercentage, 5.657%, times ,39362, (int)ret>=0 times ,20
pid_222459;u0_recvfrom;sock_recvmsg;udp_recvmsg;__skb_recv_udp 20237, localDelaySum ,20237, localAvedelay ,0.514125, localPercentage, 2.023%, globalDelaySum ,20237, globalAvedelay, 0.514125, globalPercentage, 2.023%, times ,39362, (int)ret>=0 times ,39342
```

**调度信息**：`/var/da-tool/analysis_output/output/process_sched_info`
```
# delaySum : 该pid分析的总时长
# schedSwitchDelay : 调度所占的时间
# runtime ：delaySum - schedSwitchDelay
# cpuSwitchTimes ： 该pid从一个核切换到另一个核的次数
# core  2, run time 704927 ： 表示在cpu2 上运行时长为 704927
# startTime,67551.691078,endTime,67551.701193,coreIndex,2 ：在这个时间段内在cpu2上运行
# coreIndex,-1 表示该pid被切走的时长(sched_switch)

pid,222459,delaySum ,1000368,schedSwitchDelay ,37201,runtime ,963167,cpuSwitchTimes ,1,
 core  2, run time 704927
 core  3, run time 258240
startTime,67551.691078,endTime,67551.701193,coreIndex,2
startTime,67551.701193,endTime,67551.701970,coreIndex,-1
startTime,67551.701970,endTime,67551.702503,coreIndex,2
startTime,67551.702503,endTime,67551.713700,coreIndex,-1
startTime,67551.713700,endTime,67551.723964,coreIndex,2
startTime,67551.723964,endTime,67551.724119,coreIndex,-1
...

```
**时延分析总结报告**：`/var/da-tool/analysis_output/output/summary_delay.csv`

包含信息如下，其中`(r>=0)`表示函数返回值转成`int`后大于等于0的情况。
`ave,sum,min,max,p50,p80,p95,p99`等为时延信息的平均值、总和、极值、各百分位下的数值。
```
pid,function,call_times,ave,sum,min,max,p50,p80,p95,p99,
call_times(r>=0),ave(r>=0),sum(r>=0),min(r>=0),max(r>=0),p50(r>=0),p80(r>=0),p95(r>=0),p99(r>=0),
call_times(r<0),ave(r<0),sum(r<0),min(r<0),max(r<0),p50(r<0),p80(r<0),p95(r<0),p99(r<0),
```

**调度分析总结报告**：`/var/da-tool/analysis_output/output/summary_sched.csv`
```
pid,delaySum,schedSwitchDelay,schedSwitchPercentage,schedSwitchTimes,cpuSwitchTimes
```
+ delaySum : 总耗时
+ schedSwitchDelay ： 调度总耗时
+ schedSwitchPercentage ： schedSwitchDelay 占 delaySum 的百分比
+ schedSwitchTimes ： 调度次数
+ cpuSwitchTimes : cpu 切换次数

### 扩展功能
`da-tool` 生成的结果信息可调用 火焰图生成工具，可视化分析结果，
`./flamegraph.pl` 可在 `https://gitee.com/mirrors/FlameGraph` 中获取
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

采集后会在`/var/da-tool/tmp`文件夹下生成一个`output_时间`格式的文件夹，包含此次采样的结果。
采样脚本的采样日志在此路径下：
```
/var/da-tool/tmp/sample_output_时间/da-tool/sample.log
```

### 注意事项
+ 配置注意事项
    + 配置`/etc/da-tool.conf` 时，注意所配置符号一定存在
    + 某些函数名可能存在点(eg:A.B.C)，暂**不支持配置此类函数**，例如经过gcc优化选项`-fipa-sra`优化后，函数符号后缀会有`.rsra.num`。
    + 应用程序名也不要有点，建议函数和应用程序**不要包含特殊符号**
    + 某些函数可能短时间执行大量次数，此时`trace`很大，解析时间会很长，需要认为评估配置的函数运行情况，合理设置采样时间
    + 由于`trace`可能存在不完整的调用关系，很有可能在`trace`中存在的数据分析时舍弃，如果单次采样没有抓到需要的pid信息，建议多采样几次
    + 有时`trace`中会有数据丢失，结果可能异常，常见的异常原因为`trace`过大，内核刷新数据时不正常，比如会出现同一个函数只有返回时间没有进入时间的现象，建议减小采样时间。
    + 不支持递归函数
+ 本工具单个CPU所使用的跟踪缓存`RingBuffer`大小为 `40960kb` ，当单核的`trace`大小接近此值时数据可能异常，进而导致分析结果错误。
+ 确保`trace` 中有需要采集的函数的完整调用栈
