
# da-tool

`da-tool` is a lightweight performance analysis utility based on `uprobe` and `kprobe`. While standard tracing often involves complex configurations and yields overwhelming, non-intuitive raw data, this tool streamlines the sampling process and focuses specifically on analyzing the latency characteristics of targeted functions.

Key application scenario: Analyze latency characteristics for TCP/UDP transmission and reception functions.

## Directory Structure

**Project Folders**

+ `script/`: Shell scripts
    + `da-tool.sh`: Utilizes `trace` of `uprobe` or `kprobe` to collect program traces and generates configuration files for the analysis module.
+ `config/`: Configuration files.
    + `da-tool.conf`: Configuration file to be deployed in the `/etc` directory.
+ `analysis/`: C++ source files for the analysis engine.
    + `config.cpp/h`: Parses external parameters and `function_config`.
    + `common.h`: Common parameters.
    + `trace_resolve.cpp/h`: Parses `trace`.
    + `time_pair.cpp/h`: Obtains the start and end time of each function.
    + `function_strack.cpp/h`: Manages per-PID function call stacks and associated latency metrics.
    + `sched_analysis.cpp/h`: Calculates thread scheduling information.
+ `main.cpp`
+ `CMakeLists.txt`
+ `test`: Test programs.

## Documentation

|Topic|Content Overview|Status|
|:----|:-----|:----|
|[openEuler Guide](https://gitcode.com/openeuler/community/blob/master/en/contributors/README.md)| Get involved in the openEuler Community.| Released |
|da-tool User Guide|1. Application installation, configuration, and execution<br>2. Analysis results<br>3. Precautions|Released|
|da-tool design document|1. Technical principles<br> 2. Developer guide|To be released|
