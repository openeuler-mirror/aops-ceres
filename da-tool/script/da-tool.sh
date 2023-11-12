#!/bin/sh
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2023-2023. All rights reserved.
# licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN 'AS IS' BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# ******************************************************************************/
# Create: 2023-11-07
# Author: LiuChanggeng <liuchanggeng@huawei.com>
# Description: Collection and analysis function delay

# dir
# /var/da-tool
#    |----tmp
#    |     |------sample_output_$date
#    |     |------analysis_input
#    |----analysis_output

#set -e
#set -x # debug

base_dir=/var/da-tool/
mkdir -p $base_dir
cd $base_dir

mkdir -p tmp

# extern para
sleep_time=10
sleep_time_max=100

# base para
declare -a kernel_symbols
declare -a sched_symbols
declare -a user_symbols_arr # fake two-dimensional array
declare -a user_symbols_event_arr
declare -a user_symbols_arr_split
declare -a pid_filter
config_file="/etc/da-tool.conf"
config_analysis="analysis_config"

# log path

testtime=$(date +%Y%m%d-%H-%M-%S)
sample_output_dir=./tmp/sample_output_$testtime
analysis_input_dir=./tmp/analysis_input
analysis_output_dir=./analysis_output
probe_dir=$sample_output_dir/kprobe_trace/
sysinfo_dir=$sample_output_dir/sysinfo/
config_analysis_dir=$sample_output_dir/config_analysis/
sample_log_dir=$sample_output_dir/da-tool
sample_log=$sample_log_dir/sample.log
analysis_dir=./analysis/
analysis_bin=/usr/bin/da-tool-analysis

is_analysis_only_mode=false
is_sample_only_mode=false
is_sample_with_analysis=true # default analysis + sample
is_uprobe_sample=true
is_kprobe_sample=true
is_clear=false
is_show_verbose=false

handle_error() {
	echo "Program exited abnormally"
	echo "run log: " $base_dir$sample_log
	exit 1
}

trap 'handle_error' ERR

# get opt
# while getopts "b:l:t:p:as" opt; do # debug
while getopts "t:" opt; do
	case $opt in
	a)
		is_analysis_only_mode=true
		is_sample_with_analysis=false
		;;
	s)
		is_sample_only_mode=true
		is_sample_with_analysis=false
		;;
	t)
		sleep_time=$OPTARG
		;;
	p)
		parameter="$OPTARG"
		IFS=',' read -ra value_array <<<"$parameter"
		for value in "${value_array[@]}"; do
			pid_filter+=("$value")
		done
		;;
	\?)
		echo "Invalid option: -$OPTARG" >&2
		exit 1
		;;
	esac
done

function config_display() {
	echo "kernel_symbols:" >>$sample_log
	for item in "${kernel_symbols[@]}"; do
		echo "$item" >>$sample_log
	done

	echo "sched_symbols:" >>$sample_log
	for item in "${sched_symbols[@]}"; do
		echo "$item" >>$sample_log
	done

	spl_begin=0
	user_bin_num=0
	for ((i = 0; i < ${#user_symbols_arr_split[@]}; i++)); do
		spl_end=${user_symbols_arr_split[$i]}
		echo begin: $spl_begin end: $spl_end >>$sample_log
		echo path: ${user_symbols_arr[$((${spl_begin}))]} >>$sample_log
		echo bin:${user_symbols_arr[$((${spl_begin} + 1))]} >>$sample_log
		for ((j = ${spl_begin} + 2; j < ${spl_end}; j++)); do
			user_symbols_event_arr[$j]=u${user_bin_num}_${user_symbols_arr[$j]} # Avoid using the same name
			echo event:${user_symbols_event_arr[$j]} func:${user_symbols_arr[$j]} >>$sample_log
		done
		spl_begin=${spl_end}
		user_bin_num=$((user_bin_num + 1))
	done
}

function config_file_resolve() {
	cum_tmp=0
	while IFS= read -r line; do
		# null or #
		if [[ -z "$line" || "$line" == "#"* ]]; then
			continue
		fi

		# kernel
		if [[ "$line" == "k,"* ]]; then
			IFS=',' read -ra fields <<<"$line"
			kernel_symbols+=("${fields[@]:1}")
			continue
		fi

		# sched
		if [[ "$line" == "s,"* ]]; then
			IFS=',' read -ra fields <<<"$line"
			sched_symbols+=("${fields[@]:1}")
			continue
		fi

		# user
		if [[ "$line" == "u,"* ]]; then
			IFS=',' read -ra fields <<<"$line"
			user_symbols_arr+=("${fields[@]:1}")
			user_symbols_event_arr+=("${fields[@]:1}")
			cum_tmp=$((cum_tmp + ${#fields[@]} - 1)) # -1 delete u
			user_symbols_arr_split+=("${cum_tmp}")
			continue
		fi
	done <$config_file

	mkdir -p $sample_log_dir
	touch $sample_log
	config_display
}

function gen_config_for_analysis() {
	echo >${config_analysis}
	for symbol in "${kernel_symbols[@]}"; do
		echo k,${symbol} >>${config_analysis}
	done

	for symbol in "${sched_symbols[@]}"; do
		echo s,${symbol} >>${config_analysis}
	done

	spl_begin=0
	for ((i = 0; i < ${#user_symbols_arr_split[@]}; i++)); do
		spl_end=${user_symbols_arr_split[$i]}
		for ((j = ${spl_begin} + 2; j < ${spl_end}; j++)); do
			echo u,${user_symbols_event_arr[$j]} >>${config_analysis}
		done
		spl_begin=${spl_end}
	done
}

function opt_check() {
	if [ $is_uprobe_sample = false ] && [ $is_kprobe_sample = false ]; then
		echo "use -m u|k|uk to set uprobe/kprobe/both"
		exit 1
	fi

    if [ $sleep_time -ge $((sleep_time_max+1)) ] || [ $sleep_time -le 0 ];then
        echo "sampling time should > 0 and <= $sleep_time_max"
        exit 1
    fi
}

function clear_env() {
	echo "clear env..."
	echo 0 >/sys/kernel/debug/tracing/tracing_on

	events_folder="/sys/kernel/debug/tracing/events/"

	# find probe* start dir
	probe_folders=$(find "$events_folder" -type d -name "probe*")

	# turn off probe*/enable
	for folder in $probe_folders; do
		enable_file="$folder/enable"
		echo 0 >"$enable_file"
		echo "close $enable_file" >>$sample_log
	done

	for symbol in "${sched_symbols[@]}"; do
		event_file=/sys/kernel/debug/tracing/events/sched/${symbol}/enable
		if [ -f "$event_file" ]; then
			echo 0 >"$event_file"
		fi
	done

	spl_begin=0
	for ((i = 0; i < ${#user_symbols_arr_split[@]}; i++)); do
		spl_end=${user_symbols_arr_split[$i]}
		target=${user_symbols_arr[$((${spl_begin} + 1))]}
		spl_begin=${spl_end}
		# after group disable ,group event disable
		event_file=/sys/kernel/debug/tracing/events/probe_${target}/enable
		if [ -f "$event_file" ]; then
			echo 0 >"$event_file"
		fi
	done

	for symbol in "${kernel_symbols[@]}"; do
		# perf probe
		event_file=/sys/kernel/debug/tracing/events/probe/${symbol}/enable
		if [ -f "$event_file" ]; then
			echo 0 >"$event_file"
		fi
		event_file=/sys/kernel/debug/tracing/events/probe/${symbol}__return/enable
		if [ -f "$event_file" ]; then
			echo 0 >"$event_file"
		fi
	done
	echo "clear env finish"
}

function sample_init() {
	echo 0 >/sys/kernel/debug/tracing/tracing_on
	echo >/sys/kernel/debug/tracing/trace
	echo 4096 >/sys/kernel/debug/tracing/buffer_size_kb

	echo >/sys/kernel/debug/tracing/uprobe_events
	echo >/sys/kernel/debug/tracing/kprobe_events
}

function uprobe_event_config() {
	if [ $1 = false ]; then
		return
	fi

	spl_begin=0
	for ((i = 0; i < ${#user_symbols_arr_split[@]}; i++)); do
		spl_end=${user_symbols_arr_split[$i]}
		target_path=${user_symbols_arr[$((${spl_begin}))]}${user_symbols_arr[$((${spl_begin} + 1))]}
		for ((j = ${spl_begin} + 2; j < ${spl_end}; j++)); do
			perf probe -x ${target_path} -a ${user_symbols_event_arr[$j]}=${user_symbols_arr[$j]} --no-demangle >>$sample_log 2>&1
			perf probe -x ${target_path} -a "${user_symbols_event_arr[$j]}=${user_symbols_arr[$j]}%return \$retval" --no-demangle >>$sample_log 2>&1
		done
		spl_begin=${spl_end}
	done
}

function kprobe_event_config() {
	if [ $1 = false ]; then
		return
	fi

	# by perf probe , then /sys/kernel/debug/tracing/kprobe_events have new events
	for symbol in "${kernel_symbols[@]}"; do
		perf probe --add ${symbol} >>$sample_log 2>&1
		perf probe --add "${symbol}%return \$retval" >>$sample_log 2>&1
	done
}

function show_verbose() {
	if [ $1 = false ]; then
		return
	fi
	cat /sys/kernel/debug/tracing/uprobe_events
	cat /sys/kernel/debug/tracing/kprobe_events
}

function kprobe_event_enable() {
	if [ $1 = false ]; then
		return
	fi
	for symbol in "${kernel_symbols[@]}"; do
		# by perf
		echo 1 >/sys/kernel/debug/tracing/events/probe/${symbol}/enable
		echo 1 >/sys/kernel/debug/tracing/events/probe/${symbol}__return/enable
	done
}

function uprobe_event_enable() {
	if [ $1 = false ]; then
		return
	fi

	spl_begin=0
	for ((i = 0; i < ${#user_symbols_arr_split[@]}; i++)); do
		spl_end=${user_symbols_arr_split[$i]}
		target=${user_symbols_arr[$((${spl_begin} + 1))]}
		for ((j = ${spl_begin} + 2; j < ${spl_end}; j++)); do
			echo 1 >/sys/kernel/debug/tracing/events/probe_${target}/${user_symbols_event_arr[$j]}/enable
			echo 1 >/sys/kernel/debug/tracing/events/probe_${target}/${user_symbols_event_arr[$j]}__return/enable
		done
		spl_begin=${spl_end}
		echo 1 >/sys/kernel/debug/tracing/events/probe_${target}/enable
	done

}

function sched_event_enable() {
	if [ $1 = false ]; then
		return
	fi
	for symbol in "${sched_symbols[@]}"; do
		echo 1 >/sys/kernel/debug/tracing/events/sched/${symbol}/enable
	done
}

function storage_data() {
	mkdir -p $probe_dir
	mkdir -p $sysinfo_dir
	mkdir -p $config_analysis_dir
	# sys info
	cat /sys/kernel/debug/tracing/uprobe_events >$sysinfo_dir"uprobe_events"
	cat /sys/kernel/debug/tracing/kprobe_events >$sysinfo_dir"kprobe_events"

	if command -v gcc >/dev/null 2>&1; then
		gcc --version >$sysinfo_dir"gcc_info"
	else
		echo "GCC not found" >$sysinfo_dir"gcc_info"
	fi

	interfaces=$(ip link show | awk -F': ' '/^[0-9]+:/{print $2}')
	if command -v ethtool >/dev/null 2>&1; then
		for interface in $interfaces; do
			echo "network card: $interface" >>$sysinfo_dir"network_cfg"
			ethtool "$interface" >>$sysinfo_dir"network_cfg"
			echo "" >>$sysinfo_dir"network_cfg"
		done
	else
		echo "ethtool not found"
	fi

	uname -a >$sysinfo_dir"kernel"
	cat /etc/os-release >$sysinfo_dir"os-release"
	ldd --version >$sysinfo_dir"glibc_v"

	if command -v openssl >/dev/null 2>&1; then
		openssl version >$sysinfo_dir"openssl"
	else
		echo "openssl not found"
	fi
	lscpu >$sysinfo_dir"lscpu"
	lspci -v >$sysinfo_dir"lspci_v"
	lspci -tv >$sysinfo_dir"lspci_tv"
	lspci >$sysinfo_dir"lspci"

	dmidecode >$sysinfo_dir"dmidecode"
	dmesg >$sysinfo_dir"dmesg"
	lsmod >$sysinfo_dir"lsmod"
	free -m >$sysinfo_dir"free"

	# trace
	cp -f /sys/kernel/debug/tracing/trace $probe_dir
	cp -f ${config_analysis} $config_analysis_dir

	# copy for analysis
	mkdir -p $analysis_input_dir
	mv -f $config_analysis $analysis_input_dir/
	cp -f $analysis_input_dir/${config_analysis} $analysis_input_dir/${config_analysis}_orig
	cp -f $probe_dir/trace $analysis_input_dir/
}

function trace_record_begin() {
	echo 1 >/sys/kernel/debug/tracing/tracing_on
}

function trace_record_end() {
	echo 0 >/sys/kernel/debug/tracing/tracing_on
}

function trace_analysis() {
	rm -rf $analysis_output_dir/debug/*
	rm -rf $analysis_output_dir/output/*

	cp -f $analysis_input_dir/${config_analysis}_orig $analysis_input_dir/${config_analysis}

	for pid in "${pid_filter[@]}"; do
		echo p,$pid >>$analysis_input_dir/${config_analysis}
	done

	mkdir -p $analysis_output_dir/debug/
	mkdir -p $analysis_output_dir/output/
	$analysis_bin
}

###################### main proc ####################################
config_file_resolve

if [ $is_clear = true ]; then
	echo "clear"
	clear_env
	exit 1
fi

opt_check

if [ $is_analysis_only_mode = true ]; then # only analysis
	trace_analysis
	exit 1
fi

clear_env
sample_init

uprobe_event_config $is_uprobe_sample
kprobe_event_config $is_kprobe_sample

show_verbose $is_show_verbose

uprobe_event_enable $is_uprobe_sample
kprobe_event_enable $is_kprobe_sample
sched_event_enable $is_kprobe_sample

# sampling
trace_record_begin

for ((i = 1; i <= ${sleep_time}; i++)); do
	# trace_line_num=$(wc -l < /sys/kernel/debug/tracing/trace) # wrong
	echo "sampling " $i/${sleep_time} #", trace line" $trace_line_num
	sleep 1
done
#trace_line_num=$(wc -l < /sys/kernel/debug/tracing/trace) # slow
#echo "trace line" $trace_line_num

trace_record_end

clear_env
gen_config_for_analysis
storage_data
echo "" >/sys/kernel/debug/tracing/trace
# only enable =  0 , clear event
echo >/sys/kernel/debug/tracing/uprobe_events
echo >/sys/kernel/debug/tracing/kprobe_events
echo "sample finish"

if [ $is_sample_with_analysis = true ]; then # only sample
	trace_analysis
fi
