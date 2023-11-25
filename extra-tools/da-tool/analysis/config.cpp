/*******************************************************************************
* Copyright (c) Huawei Technologies Co., Ltd. 2023-2023. All rights reserved.
* licensed under the Mulan PSL v2.
* You can use this software according to the terms and conditions of the Mulan PSL v2.
* You may obtain a copy of Mulan PSL v2 at:
*     http://license.coscl.org.cn/MulanPSL2
* THIS SOFTWARE IS PROVIDED ON AN 'AS IS' BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
* IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
* PURPOSE.
* See the Mulan PSL v2 for more details.
*******************************************************************************/

#include <iostream>
#include <unistd.h>
#include <fstream>
#include <sstream>
#include "config.h"

Config::Config()
{
    debugLevel = DEBUG_LEVEL_0;
}

DEBUG_LEVEL_E Config::getDebugLevel()
{
    return debugLevel;
}

void Config::pathInit()
{

    std::string pathInput = "/var/da-tool/tmp/analysis_input";
    std::string pathOutput = "/var/da-tool/analysis_output/output";
    std::string pathOutputDebug = "/var/da-tool/analysis_output/debug";

    // input
    filename[FILE_TYPE_TRACE] = pathInput + "/trace";
    filename[FILE_TYPE_FUNC_CFG] = pathInput + "/analysis_config";

    // output
    filename[FILE_TYPE_OUTPUT_DELAY] = pathOutput + "/summary_delay.csv";
    filename[FILE_TYPE_OUTPUT_FUNC_STACK_DELALY] = pathOutput + "/func_delay_stack";
    filename[FILE_TYPE_OUTPUT_PROCESS_SCHED_INFO] = pathOutput + "/process_sched_info";
    filename[FILE_TYPE_OUTPUT_SUMMARY_SCHED_INFO] = pathOutput + "/summary_sched.csv";

    // debug
    filename[FILE_TYPE_OUTPUT_RUN_LOG] = pathOutputDebug + "/run.log";
    filename[FILE_TYPE_DEBUG_TIME_PAIE] = pathOutputDebug + "/debug_time_pair";
    filename[FILE_TYPE_DEBUG_TRACE] = pathOutputDebug + "/debug_trace";
    filename[FILE_TYPE_DEBUG_FUNC_STACK_TRACE] = pathOutputDebug + "/debug_funcstk_trace";
    filename[FILE_TYPE_DEBUG_REGEX] = pathOutputDebug + "/debug_resolve_function_trace";
    filename[FILE_TYPE_DEBUG_CONFIG] = pathOutputDebug + "/debug_config_resolve";
    filename[FILE_TYPE_DEBUG_TIME_PAIR_ALIGN] = pathOutputDebug + "/debug_time_pair_align";
    filename[FILE_TYPE_DEBUG_TIME_PAIR_MARK] = pathOutputDebug + "/debug_time_pair_mark";
    filename[FILE_TYPE_DEBUG_DELAY_FUNC_STACK_TRACE] = pathOutputDebug + "/debug_delay_func_stack_trace";

    if (debugLevel >= DEBUG_LEVEL_1) {
        for (int i = 0; i < FILE_TYPE_MAX; i++) {
            std::cout << filename[i] << std::endl;
        }
    }
}


void Config::functionCfgInit()
{
    std::ifstream file(filename[FILE_TYPE_FUNC_CFG]);
    if (!file) {
        std::cout << "file open failed:" << filename[FILE_TYPE_FUNC_CFG] << std::endl;
        return;
    }

    std::string line;
    int functionIndex = 0;
    while (std::getline(file, line)) {

        if (line.empty() || line[0] == '#') {
            continue;
        }

        std::stringstream ss(line);
        std::string cfgType;
        functionCfg funcCfgTmp;
        FilterConfig filterCfgTmp;
        CFG_TYPE_E cfgTypeTmp;

        getline(ss, cfgType, ',');
        if (cfgType == "u") {
            cfgTypeTmp = CFG_TYPE_USER;
        } else if (cfgType == "k") {
            cfgTypeTmp = CFG_TYPE_KERNEL;
        } else if (cfgType == "s") {
            cfgTypeTmp = CFG_TYPE_SCHED;
        } else if (cfgType == "p") {
            cfgTypeTmp = CFG_TYPE_FILTER_PID;
        } else {
            std::cout << "function cfg error :" << "cfgType=" << cfgTypeTmp << std::endl;
        }

        if (cfgTypeTmp >= CFG_TYPE_FUNC_BEGIN && cfgTypeTmp <= CFG_TYPE_FUNC_END) {
            funcCfgTmp.cfgType = cfgTypeTmp;
            funcCfgTmp.isRet = 0;
            funcCfgTmp.functionIndex = ++functionIndex; // functionIndex start at 1 , 0 means root func
            std::string functionName;
            getline(ss, functionName, ',');

            funcCfgMap.emplace(functionName, funcCfgTmp);
            if (cfgTypeTmp != CFG_TYPE_SCHED) {
                funcCfgTmp.isRet = 1;
                funcCfgMap.emplace(functionName + "__return", funcCfgTmp);
            }
            IndexToFunction.emplace(funcCfgTmp.functionIndex, functionName);
        } else if (cfgTypeTmp >= CFG_TYPE_FILTER_BEGIN && cfgTypeTmp <= CFG_TYPE_FILTER_END) {
            filterCfgTmp.cfgType = cfgTypeTmp;
            std::string pidFilter;
            getline(ss, pidFilter, ',');
            filterCfgTmp.pidFilter = std::stoi(pidFilter);

            if (filterCfgMap.count(filterCfgTmp.pidFilter) == 0) {
                filterCfgMap.emplace(filterCfgTmp.pidFilter, filterCfgTmp);
            } else {
                std::cout << "pid " << filterCfgTmp.pidFilter << " Config duplicate" << std::endl;
            }
        }
    }

    if (debugLevel >= DEBUG_LEVEL_1) {
        std::ofstream fileDebug(filename[FILE_TYPE_DEBUG_CONFIG], std::ios::out | std::ios::trunc);
        if (!fileDebug) {
            std::cout << "file open failed:" << filename[FILE_TYPE_DEBUG_CONFIG] << std::endl;
            file.close();
            return;
        }

        for (const auto &cfg : funcCfgMap) {
            fileDebug << cfg.first << "," << cfg.second.cfgType << "," << cfg.second.functionIndex << "," << cfg.second.isRet << std::endl;
        }
        for (const auto &cfg : filterCfgMap) {
            fileDebug << "filter," << cfg.first << "," << cfg.second.cfgType << "," << cfg.second.pidFilter << std::endl;
        }
        fileDebug.close();
    }

    file.close();
}

void Config::configInit(int argc, char *argv[])
{
    int option;
#ifdef WITH_DEBUG
    while ((option = getopt(argc, argv, "b:l:g:")) != -1) {
#else
    while ((option = getopt(argc, argv, "b:l:")) != -1) {
#endif
        switch (option) {
        case 'b':
            readTraceBegin = std::stoi(optarg);
            break;
        case 'l':
            readTraceLen = std::stoi(optarg);
            break;
        case 'g':
            if (std::stoi(optarg) < DEBUG_LEVEL_MAX) {
                debugLevel = (DEBUG_LEVEL_E)std::stoi(optarg);
            } else {
                std::cout << "debugLevel error" << std::endl;
            }
            std::cout << "debugLevel : " << debugLevel << std::endl;
            break;
        case '?':
            std::cout << "Unknown option: " << static_cast<char>(optopt) << std::endl;
            break;
        default:
            std::cout << "Unrecognized option" << std::endl;
            break;
        }
    }

    for (int i = optind; i < argc; ++i) {
        std::cout << "Non option parameters: " << argv[i] << std::endl;
    }

    pathInit();
    functionCfgInit();
}