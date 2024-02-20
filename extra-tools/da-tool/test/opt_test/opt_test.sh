#!/bin/bash

script_dir=$(
	cd "$(dirname "$0")" >/dev/null 2>&1 || exit 1
	pwd
)
cd "$script_dir"/ || exit 1

datool_path="${script_dir}/../../script/"

err_commands=(
	"./da-tool.sh -t 0"
	"./da-tool.sh -t 101"
	"./da-tool.sh -t 1000000000000000000000000000"
	"./da-tool.sh -t -10"
	"./da-tool.sh -t 0.12345"
	"./da-tool.sh -t abc"
	"./da-tool.sh -t ~"
	"./da-tool.sh -t -m 5"
	"./da-tool.sh -a"
	"./da-tool.sh -x 1"
	"./da-tool.sh -"
	"./da-tool.sh 1"
)

right_commands=(
	"./da-tool.sh -h"
	#"./da-tool.sh -t 1"
	#"./da-tool.sh"
)

output_file="opt_test.log"
echo >$output_file

{
	echo "========================================================================================="
	echo "===================================== err_commands ======================================"
	echo "========================================================================================="
} >>"$output_file"
for command in "${err_commands[@]}"; do
	echo "================================" "$command" "================================" >>$output_file
	"${datool_path}${command}" >>$output_file 2>&1
done

{
	echo "========================================================================================="
	echo "===================================== right_commands ===================================="
	echo "========================================================================================="
} >>"$output_file"
for command in "${right_commands[@]}"; do
	echo "================================" "$command" "================================" >>$output_file
	"${datool_path}${command}" >>$output_file 2>&1
done
