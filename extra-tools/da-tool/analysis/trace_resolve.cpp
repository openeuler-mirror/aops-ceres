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
#include <fstream>
#include <regex>
#include <iomanip>
#include <cmath>
#include "trace_resolve.h"
#include "config.h"
#include "limits.h"
#include "common.h"

typedef enum {
    TRACE_INFO_ALL,
    TRACE_INFO_COMMAD,
    TRACE_INFO_PID,
    TRACE_INFO_CPU,
    TRACE_INFO_IRQS_OFF,
    TRACE_INFO_NEED_RESCHED,
    TRACE_INFO_HW_OR_SW_IRQ,
    TRACE_INFO_PREEMPT_DEPTH,
    TRACE_INFO_TIMESTAMP_INT,
    TRACE_INFO_TIMESTAMP_FLOAT,
    TRACE_INFO_FUNCNAME,
    TRACE_INFO_BASE_MAX,

    TRACE_INFO_ARGS_0,
} TRACE_INFO_E;

typedef enum {
    TRACE_INFO_PREV_PID = TRACE_INFO_BASE_MAX,
    TRACE_INFO_PREV_PRIO,
    TRACE_INFO_PREV_STATE,
    TRACE_INFO_NEXT_PID,
    TRACE_INFO_NEXT_PRIO,
    TRACE_INFO_SHCEMAX,
} TRACE_INFO_SCHED_SWITCH_E;

TraceResolve::TraceResolve()
{

}

const std::vector<TraceLineReslove> &TraceResolve::getTraceLine() const
{
    return traceLineVec;
}

void SchedSwitchLine::processStateToEnum(std::string state)
{
    if (state == "R") {
        prevState = PROCESS_STATE_TASK_RUNNING;

    } else if (state == "S") {
        prevState = PROCESS_STATE_TASK_INTERRUPTIBLE;
    } else {
        prevState = PROCESS_STATE_MAX;
    }
}

void TraceResolve::resolveTrace()
{
    Config &cfg = Config::getInstance();
    std::ifstream file(cfg.filename[FILE_TYPE_TRACE]);
    if (!file) {
        std::cout << "file open failed:" << cfg.filename[FILE_TYPE_TRACE] << std::endl;
        return;
    }

    std::ofstream debugFile(cfg.filename[FILE_TYPE_DEBUG_REGEX], std::ios::out | std::ios::trunc);
    if (!debugFile) {
        std::cout << "file open failed:" << cfg.filename[FILE_TYPE_DEBUG_REGEX] << std::endl;
        file.close();
        return;
    }

    int line_num = 0;
    int regex_num = 0;
    bool isFirstMatch = true;

    std::string line;
    std::regex pattern(R"(\s*(.+)-(\d+)\s+\[(\d+)\]\s+(.)(.)(.)(.)\s+(\d+)\.(\d+):\s+(\w+):(.+))");
    std::regex subpattern(R"(.+arg1=(0x[a-fA-F0-9]+))");
    std::regex patternSchedSwitch(R"(\s+(.+)-(\d+)\s+\[(\d+)\]\s+(.)(.)(.)(.)\s+(\d+)\.(\d+):\s+(sched_switch):\s+prev_comm=.+prev_pid=(\d+)\s+prev_prio=(\d+)\s+prev_state=(\S+)\s+==>\s+next_comm=.+next_pid=(\d+)\s+next_prio=(\d+))");
    while (getline(file, line)) {
        line_num++;
        if (line_num % 10000 == 0) {
            std::cout << regex_num << "/" << line_num << " (matched/lines)" << std::endl;
        }
        if (line_num < cfg.readTraceBegin) {
            continue;
        }
        if (cfg.readTraceEnd != 0 && line_num > cfg.readTraceBegin + cfg.readTraceEnd) {
            break;
        }

        std::smatch match;
        bool isMatch = false;
        TraceLineReslove match_info;
        if (regex_search(line, match, patternSchedSwitch)) {
            isMatch = true;

            if (cfg.getDebugLevel() >= DEBUG_LEVEL_3) {
                debugFile << 0 << ":" << match[TRACE_INFO_ALL].str() << std::endl;
                for (int i = 1; i < TRACE_INFO_SHCEMAX; i++) {
                    debugFile << i << ":" << match[i].str() << " ";
                }
                debugFile << std::endl;
            }
            match_info.schedSwitchLine.prevPid = std::stoi(match[TRACE_INFO_PREV_PID]);
            match_info.schedSwitchLine.prevPrio = std::stoi(match[TRACE_INFO_PREV_PRIO]);
            match_info.schedSwitchLine.nextPid = std::stoi(match[TRACE_INFO_NEXT_PID]);
            match_info.schedSwitchLine.nextPrio = std::stoi(match[TRACE_INFO_NEXT_PRIO]);
            match_info.schedSwitchLine.processStateToEnum(match[TRACE_INFO_PREV_STATE].str());

        } else if (regex_search(line, match, pattern)) {
            isMatch = true;
            if (cfg.getDebugLevel() >= DEBUG_LEVEL_3) {
                debugFile << 0 << ":" << match[TRACE_INFO_ALL].str() << std::endl;
                for (int i = 1; i < TRACE_INFO_BASE_MAX; i++) {
                    debugFile << i << ":" << match[i].str() << " ";
                }
                debugFile << std::endl;
            }
            std::smatch submatch;
            std::string tmp = match[TRACE_INFO_BASE_MAX].str();
            if (regex_search(tmp, submatch, subpattern)) {
                std::string ret = submatch[TRACE_INFO_ARGS_0 - TRACE_INFO_BASE_MAX].str();
                match_info.args.emplace_back(strtoull(ret.c_str(), nullptr, 16));
            }
        }

        if (isMatch) {
            if (isFirstMatch) {
                startTimeIntPart = std::stoi(match[TRACE_INFO_TIMESTAMP_INT].str());
                isFirstMatch = false;
            }
            match_info.timestamp = (std::stoi(match[TRACE_INFO_TIMESTAMP_INT].str()) - startTimeIntPart) * MICRO_PER_SEC \
                + std::stoi(match[TRACE_INFO_TIMESTAMP_FLOAT].str());
            match_info.pid = std::stoi(match[TRACE_INFO_PID].str());
            match_info.core = std::stoi(match[TRACE_INFO_CPU].str());
            match_info.functionName = match[TRACE_INFO_FUNCNAME].str();
            match_info.traceLineNum = line_num;

            traceLineVec.emplace_back(match_info);
            regex_num++;
        }

    }

    if (cfg.getDebugLevel() >= DEBUG_LEVEL_1) {
        debugFile << "resolve_trace finish" << std::endl;
        debugFile << "line_num :" << line_num << std::endl;
        debugFile << "regex_num :" << regex_num << std::endl;
    }

    if (traceLineVec.size() > 0) {
        std::cout << "trace delay :" << traceLineVec[traceLineVec.size() - 1].timestamp - traceLineVec[0].timestamp << std::endl;
    }

    file.close();
    debugFile.close();
}

void TraceResolve::saveTraceRegexRstToFile()
{
    Config &cfg = Config::getInstance();
    if (cfg.getDebugLevel() < DEBUG_LEVEL_1) {
        return;
    }

    std::ofstream file(cfg.filename[FILE_TYPE_DEBUG_TRACE], std::ios::out | std::ios::trunc);
    if (!file) {
        std::cout << "file open failed:" << cfg.filename[FILE_TYPE_DEBUG_TRACE] << std::endl;
        return;
    }

    file << "traceLineNum" << "," << "pid" << "," << "core" << "," << "timestamp" << "," << "functionName" << std::endl;
    for (const auto &row : traceLineVec) {
        file << row.traceLineNum << ",";
        file << row.pid << "," << row.core << "," << "," << std::fixed << std::setprecision(6) << \
            row.timestamp * 1.0 / MICRO_PER_SEC + startTimeIntPart << "," << row.functionName;
        if (row.functionName == "sched_switch") {
            file << "," << row.schedSwitchLine.prevPid << "," << row.schedSwitchLine.prevPrio << "," << \
                row.schedSwitchLine.prevState << "," << row.schedSwitchLine.nextPid << "," << row.schedSwitchLine.nextPrio;
        }
        file << std::endl;
    }

    file.close();
}


double TraceResolve::convertTimeIntToDouble(const int &timestamp)
{
    return timestamp * 1.0 / MICRO_PER_SEC + startTimeIntPart;
}

void TraceResolve::trace_resolve_proc()
{
    resolveTrace();
    saveTraceRegexRstToFile();
}