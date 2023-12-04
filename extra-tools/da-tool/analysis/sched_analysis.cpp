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

void SchedAnalysis::processSchedAnalysisLoop(const int &pid, const int &timestamp, const int &coreIndex, const bool &isRet)
{
    if (processSchedMap.count(pid) == 0) {
        ProcessSchedInfo tmp;
        processSchedMap.emplace(pid, tmp);
    }
    int size = processSchedMap[pid].coreTrace.size();
    ProcessCoreTrace pct;
    pct.startTime = timestamp;
    pct.endTime = timestamp;
    pct.startCoreId = coreIndex;
    pct.endCoreId = coreIndex;
    pct.startIsRet = isRet;
    pct.endIsRet = isRet;
    pct.coreTraceType = CORE_TRACE_INVALID;

    if (size > 0) {
        processSchedMap[pid].coreTrace[size - 1].endTime = timestamp;
        processSchedMap[pid].coreTrace[size - 1].endCoreId = coreIndex;
        processSchedMap[pid].coreTrace[size - 1].endIsRet = isRet;
    }
    processSchedMap[pid].coreTrace.emplace_back(pct);
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
        if (cfg.funcCfgMap.count(functionName) == 0) {
            continue;
        }
        int timestamp = line_info_tmp.timestamp;
        int coreIndex = line_info_tmp.core;
        int functionIndex = cfg.funcCfgMap[functionName].functionIndex;

        if (functionIndex == sched_switch_funcidx) {
            int nextPid = line_info_tmp.schedSwitchLine.nextPid;
            processSchedAnalysisLoop(pid, timestamp, coreIndex, false); // pid1 - > pidn
            processSchedAnalysisLoop(nextPid, timestamp, coreIndex, true); // pidm - > pid1
        }
    }
    // last coreTrace always invalid
    for (auto &sched_tmp : processSchedMap) {
        if (!sched_tmp.second.coreTrace.empty()) {
            sched_tmp.second.coreTrace.pop_back();
        }
    }
}

void SchedAnalysis::schedInfoVaildMark()
{
    for (auto &sched_tmp : processSchedMap) {
        for (auto &coreTrace : sched_tmp.second.coreTrace) {
            if (!coreTrace.startIsRet && coreTrace.endIsRet) {
                coreTrace.coreTraceType = CORE_TRACE_SCHEDULING;
            }

            if (coreTrace.startIsRet && !coreTrace.endIsRet && (coreTrace.startCoreId == coreTrace.endCoreId)) {
                coreTrace.coreTraceType = CORE_TRACE_ONCORE;
            }
        }
    }
}


void SchedAnalysis::schedInfoAnalysis()
{
    for (auto &sched_tmp : processSchedMap) {
        int delaySum[SCHED_SUMMARY_MAX] = { 0 };
        int schedSwitchTimes[SCHED_SUMMARY_MAX] = { 0 };
        int cpuSwitchTimes[SCHED_SUMMARY_MAX] = { 0 };
        int vaildDelaySched = 0; // Invalid scheduling cannot be analyzed
        for (const auto &coreTrace : sched_tmp.second.coreTrace) {
            int delay = coreTrace.endTime - coreTrace.startTime;
            delaySum[SCHED_SUMMARY_ALL] += delay;
            if (!coreTrace.startIsRet) { // count pid1->pidn times
                schedSwitchTimes[SCHED_SUMMARY_ALL]++;
            }
            if (coreTrace.startCoreId != coreTrace.endCoreId) {
                cpuSwitchTimes[SCHED_SUMMARY_ALL]++;
            }
            if (coreTrace.coreTraceType != CORE_TRACE_INVALID) {
                delaySum[SCHED_SUMMARY_VAILD] += delay;
            }
            if (coreTrace.coreTraceType == CORE_TRACE_ONCORE) {
                int coreIndex = coreTrace.startCoreId;
                sched_tmp.second.runTimeOfCore[coreIndex] += delay;
            }

            if (coreTrace.coreTraceType == CORE_TRACE_SCHEDULING) {
                vaildDelaySched += delay;
                schedSwitchTimes[SCHED_SUMMARY_VAILD]++;
                if (coreTrace.startCoreId != coreTrace.endCoreId) {
                    // CPU switching only occurs during scheduling
                    cpuSwitchTimes[SCHED_SUMMARY_VAILD]++;
                }
            }
        }
        sched_tmp.second.vaildSchedSwitchDelay = vaildDelaySched;
        sched_tmp.second.validPercentSchedSwitch = delaySum[SCHED_SUMMARY_VAILD] == 0 ? 0.0 : vaildDelaySched * 1.0 / delaySum[SCHED_SUMMARY_VAILD];
        sched_tmp.second.schedSwitchTimes[SCHED_SUMMARY_VAILD] = schedSwitchTimes[SCHED_SUMMARY_VAILD];
        sched_tmp.second.schedSwitchTimes[SCHED_SUMMARY_ALL] = schedSwitchTimes[SCHED_SUMMARY_ALL];
        sched_tmp.second.cpuSwitchTimes[SCHED_SUMMARY_VAILD] = cpuSwitchTimes[SCHED_SUMMARY_VAILD];
        sched_tmp.second.cpuSwitchTimes[SCHED_SUMMARY_ALL] = cpuSwitchTimes[SCHED_SUMMARY_ALL];
        sched_tmp.second.delaySum[SCHED_SUMMARY_VAILD] = delaySum[SCHED_SUMMARY_VAILD];
        sched_tmp.second.delaySum[SCHED_SUMMARY_ALL] = delaySum[SCHED_SUMMARY_ALL];
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
        file << "pid," << pid << "," << std::endl;
        file << "cpuSwitchTimes," << sched_tmp.second.cpuSwitchTimes[SCHED_SUMMARY_ALL] << ",";
        file << "schedSwitchTimes," << sched_tmp.second.schedSwitchTimes[SCHED_SUMMARY_ALL] << ",";
        file << "delaySum," << sched_tmp.second.delaySum[SCHED_SUMMARY_ALL] << "," << std::endl;
        file << "vaildCpuSwitchTimes," << sched_tmp.second.cpuSwitchTimes[SCHED_SUMMARY_VAILD] << ",";
        file << "vaildSchedSwitchTimes," << sched_tmp.second.schedSwitchTimes[SCHED_SUMMARY_VAILD] << ",";
        file << "validDelaySum," << sched_tmp.second.delaySum[SCHED_SUMMARY_VAILD] << ",";
        file << "vaildSchedSwitchDelay," << sched_tmp.second.vaildSchedSwitchDelay << ",";
        file << "validRuntime," << sched_tmp.second.delaySum[SCHED_SUMMARY_VAILD] - sched_tmp.second.vaildSchedSwitchDelay << "," << std::endl;
        for (int coreIndex = 0; coreIndex < sched_tmp.second.runTimeOfCore.size(); coreIndex++) {
            int run_time = sched_tmp.second.runTimeOfCore[coreIndex];
            if (run_time != 0) {
                file << " core  " << coreIndex << ", run time " << run_time << std::endl;
            }
        }

        for (const auto &coreTrace : sched_tmp.second.coreTrace) {
            file << "startTime," << std::fixed << std::setprecision(6) << slv.convertTimeIntToDouble(coreTrace.startTime) << ",";
            file << "endTime," << std::fixed << std::setprecision(6) << slv.convertTimeIntToDouble(coreTrace.endTime) << ",";
            file << "startCoreId," << coreTrace.startCoreId << ",";
            file << "endCoreId," << coreTrace.endCoreId << ",";
            file << "coreTraceType,";
            if (coreTrace.coreTraceType == CORE_TRACE_INVALID) {
                file << "invalid";
            } else if (coreTrace.coreTraceType == CORE_TRACE_SCHEDULING) {
                file << "scheduling";
            } else if (coreTrace.coreTraceType == CORE_TRACE_ONCORE) {
                file << "running";
            }
            file << std::endl;
        }
        file << std::endl;
    }

    file.close();
}

void SchedAnalysis::saveSchedInfoSummaryToFile()
{
    Config &cfg = Config::getInstance();
    std::ofstream file(cfg.filename[FILE_TYPE_OUTPUT_SUMMARY_SCHED_INFO], std::ios::out | std::ios::trunc);
    if (!file) {
        std::cout << "file open failed:" << cfg.filename[FILE_TYPE_OUTPUT_SUMMARY_SCHED_INFO] << std::endl;
        return;
    }
    file << "pid,validDelaySum,vaildSchedSwitchDelay,validSchedSwitchPercentage,validSchedSwitchTimes,validCpuSwitchTimes" << std::endl;
    TraceResolve &slv = TraceResolve::getInstance();
    for (const auto &sched_tmp : processSchedMap) {
        int pid = sched_tmp.first;
        if (pid == 0) {
            continue;
        }
        file << pid << ",";
        file << sched_tmp.second.delaySum[SCHED_SUMMARY_VAILD] << ",";
        file << sched_tmp.second.vaildSchedSwitchDelay << ",";
        file << std::fixed << std::setprecision(3) << sched_tmp.second.validPercentSchedSwitch * 100 << "%,";
        file << sched_tmp.second.schedSwitchTimes[SCHED_SUMMARY_VAILD] << ",";
        file << sched_tmp.second.cpuSwitchTimes[SCHED_SUMMARY_VAILD] << "," << std::endl;
    }

    file.close();
}

void SchedAnalysis::schedAnalysisProc()
{
    schedInfoProc();
    schedInfoVaildMark();

    schedInfoAnalysis();
    saveSchedInfoToFile();
    saveSchedInfoSummaryToFile();
}
