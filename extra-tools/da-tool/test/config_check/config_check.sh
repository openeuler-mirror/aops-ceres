#!/bin/bash

script_dir=$(
	cd $(dirname $0)
	pwd
)
cd $script_dir/

datool="../../script/da-tool.sh"
case1_path="../../test"
config_file="/etc/da-tool.conf"
config_tmp="config.tmp"
output_file="config_test.log"

err_config=(
	./"config_test1.conf"
	./"config_test2.conf"
	./"config_test3.conf"
	./"config_test4.conf"
	./"config_test5.conf"
	./"config_test6.conf"
	./"config_test7.conf"
)

cat $config_file >$config_tmp

echo >$output_file

# loop test config
echo "=========================================================================================" >>$output_file
echo "===================================== err_configs ======================================" >>$output_file
echo "=========================================================================================" >>$output_file
for config_test in "${err_config[@]}"; do
	echo >$config_file
	echo "================================" "$config_test" "================================" >>$output_file
	cat $config_test >$config_file
	echo "#config start" >>$output_file
	cat $config_test >>$output_file
	echo "#config end" >>$output_file
	$datool -t 1 >>$output_file 2>&1
done

# user check
g++ $case1_path/case/case1/case1.cpp -o case1_test

err_user_config=(
	./"config_user_test1.conf"
	./"config_user_test2.conf"
	./"config_user_test3.conf"
)

echo "u,$script_dir/,case1_test,_Z5funcAv,aaaa" >./"config_user_test1.conf"
echo "u,$script_dir/,case1_test,_Z5funcAv,_Z5funcAv" >./"config_user_test2.conf"
echo "u,$script_dir/,case1_test,_Z5funcAv.a" >./"config_user_test3.conf"

# loop test config
echo "=========================================================================================" >>$output_file
echo "===================================== user err_configs ======================================" >>$output_file
echo "=========================================================================================" >>$output_file
for config_test in "${err_user_config[@]}"; do
	echo >$config_file
	echo "================================" "$config_test" "================================" >>$output_file
	cat $config_test >$config_file
	echo "#config start" >>$output_file
	cat $config_test >>$output_file
	echo "#config end" >>$output_file
	$datool -t 1 >>$output_file 2>&1
done

cat $config_tmp >$config_file
