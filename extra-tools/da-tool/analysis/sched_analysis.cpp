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
#include <iomanip>
#include <cmath>
#include "trace_resolve.h"
#include "sched_analysis.h"
#include "config.h"
#include "limits.h"

SchedAnalysis::SchedAnalysis()
{

}

void SchedAnalysis::processSchedAnalysisLoop(const int &pid, const int &timestamp, const int &coreIndex, LINE_TYPE_E lineType)
{
    if (processSchedMap.count(pid) != 0) {
        ProcessSchedInfo tmp;
        processSchedMap.emplace(pid, tmp);
    }
    int size = processSchedMap[pid].coreTrace.size();
    if (lineType == LINE_TYPE_FUNC) {
        if (size == 0) {
            ProcessCoreTrace pct;
            pct.startTime = timestamp;
            pct.endTime = 0;
            pct.coreIndex = coreIndex;
            processSchedMap[pid].coreTrace.emplace_back(pct);
        } else {
            processSchedMap[pid].coreTrace[size - 1].endTime = timestamp;
        }

    } else if (lineType == LINE_TYPE_SCHED_SWITCH) // pid1 - > pidn
    {
        if (size != 0) {
            processSchedMap[pid].coreTrace[size - 1].endTime = timestamp;
        }
        ProcessCoreTrace pct;
        pct.startTime = timestamp;
        pct.endTime = timestamp;
        pct.coreIndex = -1;
        processSchedMap[pid].coreTrace.emplace_back(pct);

    } else if (lineType == LINE_TYPE_SCHED_SWITCH_RET) // pidm - > pid1
    {
        if (size != 0) {
            processSchedMap[pid].coreTrace[size - 1].endTime = timestamp;
        }
        ProcessCoreTrace pct;
        pct.startTime = timestamp;
        pct.endTime = timestamp;
        pct.coreIndex = coreIndex;
        processSchedMap[pid].coreTrace.emplace_back(pct);
    }

}

void SchedAnalysis::schedInfoProc()
{
    Config &cfg = Config::getInstance();
    bool isCfgSchedSwitch = cfg.funcCfgMap.count("sched_switch") > 0;
    int sched_switch_funcidx = -1;
    if (isCfgSchedSwitch) {
        sched_switch_funcidx = cfg.funcCfgMap["sched_switch"].functionIndex;
    } else {
        return;
    }

    TraceResolve &slv = TraceResolve::getInstance();
    for (const auto &line_info_tmp : slv.getTraceLine()) {
        std::string functionName = line_info_tmp.functionName;
        int pid = line_info_tmp.pid;
        if (cfg.funcCfgMap.count(functionName) == 0 || pid == 0) {
            continue;
        }
        int timestamp = line_info_tmp.timestamp;
        int coreIndex = line_info_tmp.core;
        int functionIndex = cfg.funcCfgMap[functionName].functionIndex;

        if (functionIndex != sched_switch_funcidx) {
            processSchedAnalysisLoop(pid, timestamp, coreIndex, LINE_TYPE_FUNC);
        } else {
            int nextPid = line_info_tmp.schedSwitchLine.nextPid;
            processSchedAnalysisLoop(pid, timestamp, coreIndex, LINE_TYPE_SCHED_SWITCH);
            processSchedAnalysisLoop(nextPid, timestamp, coreIndex, LINE_TYPE_SCHED_SWITCH_RET);
        }
    }
}

void SchedAnalysis::schedInfoAnalysis()
{
    for (auto &sched_tmp : processSchedMap) {
        int lastCoreIndex = -1;
        int delaySum = 0;
        int delaySched = 0;
        int cpuSwichTimes = 0;
        for (auto &coreTrace : sched_tmp.second.coreTrace) {
            int delay = coreTrace.endTime - coreTrace.startTime;
            int coreIndex = coreTrace.coreIndex;
            delaySum += delay;
            if (coreIndex == -1) {
                delaySched += delay;
            } else {
                sched_tmp.second.runTimeOfCore[coreIndex] += delay;
            }

            if (lastCoreIndex == -1 && coreIndex != -1) {
                lastCoreIndex = coreIndex;
            }

            if (lastCoreIndex != coreIndex && coreIndex != -1) {
                cpuSwichTimes++;
                lastCoreIndex = coreTrace.coreIndex;
            }

        }
        sched_tmp.second.schedSwitchDelay = delaySched;
        sched_tmp.second.cpuSwichTimes = cpuSwichTimes;
        sched_tmp.second.delaySum = delaySum;
    }
}

void SchedAnalysis::saveSchedInfoToFile()
{
    Config &cfg = Config::getInstance();
    std::ofstream file(cfg.filename[FILE_TYPE_OUTPUT_PROCESS_SCHED_INFO], std::ios::out | std::ios::trunc);
    if (!file) {
        std::cout << "file open failed:" << cfg.filename[FILE_TYPE_OUTPUT_PROCESS_SCHED_INFO] << std::endl;
        return;
    }
    TraceResolve &slv = TraceResolve::getInstance();
    for (const auto &sched_tmp : processSchedMap) {
        int pid = sched_tmp.first;
        if (pid == 0) {
            continue;
        }
        file << "pid," << pid << ",";
        file << "delaySum ," << sched_tmp.second.delaySum << ",";
        file << "schedSwitchDelay ," << sched_tmp.second.schedSwitchDelay << ",";
        file << "runtime ," << sched_tmp.second.delaySum - sched_tmp.second.schedSwitchDelay << ",";
        file << "cpuSwichTimes ," << sched_tmp.second.cpuSwichTimes << ",";
        file << std::endl;
        for (int coreIndex = 0; coreIndex < sched_tmp.second.runTimeOfCore.size(); coreIndex++) {
            int run_time = sched_tmp.second.runTimeOfCore[coreIndex];
            if (run_time != 0) {
                file << " core  " << coreIndex << ", run time " << run_time << std::endl;
            }
        }

        for (const auto &coreTrace : sched_tmp.second.coreTrace) {
            file << "startTime," << std::fixed << std::setprecision(6) << slv.convertTimeIntToDouble(coreTrace.startTime) << ",";
            file << "endTime," << std::fixed << std::setprecision(6) << slv.convertTimeIntToDouble(coreTrace.endTime) << ",";
            file << "coreIndex," << coreTrace.coreIndex;
            file << std::endl;
        }
        file << std::endl;
    }

    file.close();
}

void SchedAnalysis::schedAnalysisProc()
{
    schedInfoProc();
    schedInfoAnalysis();
    saveSchedInfoToFile();
}
