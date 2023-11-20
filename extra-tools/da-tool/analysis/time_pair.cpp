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
#include <unordered_map>
#include <vector>
#include <string>
#include <iomanip>
#include <cmath>
#include "trace_resolve.h"
#include "config.h"
#include "limits.h"
#include "time_pair.h"

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

typedef enum {
    DEBUG_POS_0,
    DEBUG_POS_1,
    DEBUG_POS_2,
    DEBUG_POS_3,
    DEBUG_POS_4,
    DEBUG_POS_5,
    DEBUG_POS_MAX,
} DEBUG_POS_E;

TimePair::TimePair()
{
}

const std::unordered_map <int, std::unordered_map<int, TimePairInfo>> &TimePair::getTimePairMap() const
{
    return timePairMap;
}

void TimePair::saveFuncStkDebugToFile(std::ofstream &file, const int &pid, const int &functionIndex,
    const int &isRet, const int &timestamp, const int &fatherFunction, const int &debugPos)
{
    Config &cfg = Config::getInstance();
    if (cfg.getDebugLevel() < DEBUG_LEVEL_4) {
        return;
    }

    if (cfg.filterCfgMap.size() != 0 && cfg.filterCfgMap.count(pid) == 0) {
        return;
    }

    for (const auto &stk : funcStkMap) {
        int stk_pid = stk.first;
        if (cfg.filterCfgMap.size() != 0 && cfg.filterCfgMap.count(stk_pid) == 0) {
            continue;
        }
        file << "pid" << "," << pid << ",";
        file << "timestamp" << "," << timestamp << ",";
        file << "functionIndex" << "," << functionIndex << ",";
        file << "isRet" << "," << isRet << ",";
        file << "fatherFunction" << "," << fatherFunction << ",";
        file << "debugPos" << "," << debugPos << ",";
        file << "strFunctionStk.size()" << funcStkMap[stk_pid].size() << ",";
        file << "strFunctionStk" << ",";
        for (const auto &stk_vec : stk.second) {
            file << stk_vec << ",";
        }
        file << std::endl;
    }

}
int TimePair::getFatherFunctionIdLoop(const int &pid, const int &functionIndex, const int &isRet, int &debugPos)
{
    debugPos = DEBUG_POS_0;

    if (funcStkMap.count(pid) == 0) {
        std::vector<int> tmp;
        funcStkMap.emplace(pid, tmp);
    }

    if (funcStkMap[pid].size() == 0) {
        if (isRet) // stk empty
        {
            debugPos = DEBUG_POS_1;
            return 0;
        } else {
            funcStkMap[pid].emplace_back(functionIndex);
            debugPos = DEBUG_POS_2;
        }
    } else {
        if (funcStkMap[pid][funcStkMap[pid].size() - 1] == functionIndex) { // stk not empty
            funcStkMap[pid].pop_back(); // match ,pop
            if (funcStkMap[pid].size() > 0) {
                debugPos = DEBUG_POS_3;
                return funcStkMap[pid][funcStkMap[pid].size() - 1];
            } else {
                debugPos = DEBUG_POS_4;
                return 0; //  can't find father function
            }
        } else { // function unmath , push
            funcStkMap[pid].emplace_back(functionIndex);
            debugPos = DEBUG_POS_5;
            return funcStkMap[pid][funcStkMap[pid].size() - 2];
        }
    }
    return 0;
}

void TimePair::timePairUpdateLoop(const int &pid, const int &functionIndex, const int &isRet,
    const int &timestamp, const int &fatherFunction, const TraceLineReslove &line_info_tmp)
{
    // [pid][func]
    if (timePairMap.count(pid) == 0) {
        std::unordered_map<int, TimePairInfo> delayTmp;
        timePairMap.emplace(pid, delayTmp);
    }

    if (timePairMap[pid].count(functionIndex) == 0) {
        TimePairInfo infoTmp;
        infoTmp.maxStartTimeInvaild = 0;
        infoTmp.minEndTimeInvalid = INT_MAX;
        timePairMap[pid].emplace(functionIndex, infoTmp);
    }

    if (isRet) {
        if (timePairMap[pid][functionIndex].startTime.size() == 0) { //  fist is endtime ,startime=endtime
            timePairMap[pid][functionIndex].startTime.emplace_back(timestamp);
            timePairMap[pid][functionIndex].childFuncTimes.emplace_back(0);
            timePairMap[pid][functionIndex].strFunctionStk.emplace_back('.' + std::to_string(functionIndex));
            timePairMap[pid][functionIndex].fatherFunction.emplace_back(0);
            timePairMap[pid][functionIndex].fatherFuncPos.emplace_back(-1);
            timePairMap[pid][functionIndex].isInvalid.emplace_back(true); // only have retval , invalid
            timePairMap[pid][functionIndex].maxStartTimeInvaild = timestamp;
        }  // Be careful when adding else branches. Only when there is no exit at the entrance, you will not be able to enter else
        timePairMap[pid][functionIndex].endTime.emplace_back(timestamp);
        if (line_info_tmp.args.size() != 0) {
            timePairMap[pid][functionIndex].retVal.emplace_back(line_info_tmp.args[0]);
        } else {
            timePairMap[pid][functionIndex].retVal.emplace_back(0);
        }
    } else {
        timePairMap[pid][functionIndex].startTime.emplace_back(timestamp);
        timePairMap[pid][functionIndex].childFuncTimes.emplace_back(0);
        std::string father_func_stk = fatherFunction != 0 ? \
            timePairMap[pid][fatherFunction].strFunctionStk[timePairMap[pid][fatherFunction].strFunctionStk.size() - 1] : "";
        std::string strFunctionStk = father_func_stk + '.' + std::to_string(functionIndex);
        timePairMap[pid][functionIndex].strFunctionStk.emplace_back(strFunctionStk);
        timePairMap[pid][functionIndex].fatherFunction.emplace_back(fatherFunction);
        int fatherFuncPos = 0;
        if (fatherFunction == 0) {
            fatherFuncPos = -1;
        } else {
            fatherFuncPos = timePairMap[pid][fatherFunction].startTime.size() - 1;
            timePairMap[pid][fatherFunction].childFuncTimes[fatherFuncPos]++;
        }
        timePairMap[pid][functionIndex].fatherFuncPos.emplace_back(fatherFuncPos);
        timePairMap[pid][functionIndex].isInvalid.emplace_back(false);
    }
}

void TimePair::timePairAlignment()
{
    Config &cfg = Config::getInstance();
    std::ofstream file(cfg.filename[FILE_TYPE_DEBUG_TIME_PAIR_ALIGN], std::ios::out | std::ios::trunc);
    if (!file) {
        std::cout << "file open failed:" << cfg.filename[FILE_TYPE_DEBUG_TIME_PAIR_ALIGN] << std::endl;
        return;
    }
    int isOutputDebugFile = 1;
    if (cfg.getDebugLevel() < DEBUG_LEVEL_3) {
        isOutputDebugFile = 0;
    }

    for (auto &processInfo : timePairMap) {
        for (auto &funcInfo : processInfo.second) {
            int diffLen = funcInfo.second.startTime.size() - funcInfo.second.endTime.size();
            bool updateEndTimeInvalid = false;
            if (diffLen == 0) {
                if (isOutputDebugFile) {
                    file << diffLen << "," << processInfo.first << " ," << funcInfo.first << " ," << \
                        funcInfo.second.startTime.size() << " ," << funcInfo.second.endTime.size() << std::endl;
                }
                continue;
            }

            if (diffLen < 0) {
                if (isOutputDebugFile) {
                    file << "run error(diffLen<0)!!!,";
                    file << diffLen << "," << processInfo.first << " ," << funcInfo.first << " ," << \
                        funcInfo.second.startTime.size() << " ," << funcInfo.second.endTime.size() << std::endl;
                }
            } else {
                if (isOutputDebugFile) {
                    if (diffLen > 1) {
                        // A normal trace usually does not have a startTime greater than endtime dimension greater than 1, 
                        // indicating that a function has not returned and has been pushed back onto the stack.
                        file << "run error(diffLen>1)!!!,";
                    }
                    file << diffLen << "," << processInfo.first << " ," << funcInfo.first << " ," << \
                        funcInfo.second.startTime.size() << " ," << funcInfo.second.endTime.size() << std::endl;
                }
                for (int i = 0; i < diffLen; i++) {
                    int endTime = funcInfo.second.startTime[funcInfo.second.startTime.size() - diffLen + i];
                    funcInfo.second.endTime.emplace_back(endTime);
                    if (updateEndTimeInvalid == false) {
                        funcInfo.second.minEndTimeInvalid = endTime;
                        updateEndTimeInvalid = true;
                    }
                }
            }
        }
    }

    file.close();
}

void TimePair::timePairMarkInvalidData()
{
    for (auto &processInfo : timePairMap) {
        int pid = processInfo.first;
        VaildRange vr_tmp;
        validTimeOfPid.emplace(pid, vr_tmp);
        int validStartTime = INT_MAX;
        int validEndTime = 0;
        int maxInvalidStartTime = 0;
        int minInvalidEndTime = INT_MAX;

        // maxInvalidStartTime choose max value of every func
        for (const auto &funcInfo : processInfo.second) {
            if (funcInfo.second.maxStartTimeInvaild > maxInvalidStartTime) {
                maxInvalidStartTime = funcInfo.second.maxStartTimeInvaild;
            }
            if (funcInfo.second.minEndTimeInvalid < minInvalidEndTime) {
                minInvalidEndTime = funcInfo.second.minEndTimeInvalid;
            }
        }
        //  [start, maxInvalidStartTime] and [minInvalidEndTime, end] data invalid
        for (auto &funcInfo : processInfo.second) {
            for (int i = 0; i < funcInfo.second.startTime.size(); i++) {
                if (funcInfo.second.startTime[i] <= maxInvalidStartTime) {
                    funcInfo.second.isInvalid[i] = true;
                }
                if (funcInfo.second.endTime[i] >= minInvalidEndTime) {
                    funcInfo.second.isInvalid[i] = true;
                }
            }
        }

        for (const auto &funcInfo : processInfo.second) {
            for (int i = 0; i < funcInfo.second.startTime.size(); i++) {
                if (funcInfo.second.isInvalid[i] != true) {
                    if (funcInfo.second.startTime[i] <= validStartTime) {
                        validStartTime = funcInfo.second.startTime[i];
                    }
                    if (funcInfo.second.endTime[i] >= validEndTime) {
                        validEndTime = funcInfo.second.endTime[i];
                    }
                }
            }
        }
        validTimeOfPid[pid].validStartTime = validStartTime;
        validTimeOfPid[pid].validEndTime = validEndTime;
    }

    Config &cfg = Config::getInstance();
    if (cfg.getDebugLevel() >= DEBUG_LEVEL_3) {
        std::ofstream file(cfg.filename[FILE_TYPE_DEBUG_TIME_PAIR_MARK], std::ios::out | std::ios::trunc);
        if (!file) {
            std::cout << "file open failed:" << cfg.filename[FILE_TYPE_DEBUG_TIME_PAIR_MARK] << std::endl;
            return;
        }
        for (const auto &range_info : validTimeOfPid) {
            file << "pid," << range_info.first << ",validStartTime ," << range_info.second.validStartTime << \
                ", validEndTime ," << range_info.second.validEndTime << std::endl;
        }
        file.close();
    }
}

void TimePair::timePairMatching()
{
    Config &cfg = Config::getInstance();
    std::ofstream file(cfg.filename[FILE_TYPE_DEBUG_FUNC_STACK_TRACE], std::ios::out | std::ios::trunc);
    if (!file) {
        std::cout << "file open failed:" << cfg.filename[FILE_TYPE_DEBUG_FUNC_STACK_TRACE] << std::endl;
        return;
    }
    bool isCfgSchedSwitch = cfg.funcCfgMap.count("sched_switch") > 0;
    int sched_switch_funcidx = -1;
    if (isCfgSchedSwitch) {
        sched_switch_funcidx = cfg.funcCfgMap["sched_switch"].functionIndex;
    }

    TraceResolve &trace_resolve_inst = TraceResolve::getInstance();
    for (const auto &line_info_tmp : trace_resolve_inst.getTraceLine()) {
        std::string functionName = line_info_tmp.functionName;
        if (cfg.funcCfgMap.count(functionName) == 0) {
            continue;
        }
        int pid = line_info_tmp.pid;
        int timestamp = line_info_tmp.timestamp;
        int functionIndex = cfg.funcCfgMap[functionName].functionIndex;
        int isRet = cfg.funcCfgMap[functionName].isRet;
        int debugPos = 0;
        int fatherFunction = getFatherFunctionIdLoop(pid, functionIndex, isRet, debugPos);
        saveFuncStkDebugToFile(file, pid, functionIndex, isRet, timestamp, fatherFunction, debugPos);
        timePairUpdateLoop(pid, functionIndex, isRet, timestamp, fatherFunction, line_info_tmp);

        if (isCfgSchedSwitch && functionIndex == sched_switch_funcidx) // pid1->pid2 : pid1->sched() sched_ret()->pid2
        {
            int nextPid = line_info_tmp.schedSwitchLine.nextPid;
            isRet = 1;
            fatherFunction = getFatherFunctionIdLoop(nextPid, functionIndex, isRet, debugPos);
            saveFuncStkDebugToFile(file, nextPid, functionIndex, isRet, timestamp, fatherFunction, debugPos);
            timePairUpdateLoop(nextPid, functionIndex, isRet, timestamp, fatherFunction, line_info_tmp);
        }
    }
    file.close();
}

void TimePair::functionDelayUpdate()
{
    for (auto &processInfo : timePairMap) {
        for (auto &funcInfo : processInfo.second) {
            for (int i = 0; i < funcInfo.second.startTime.size(); i++) {
                funcInfo.second.delay.emplace_back(funcInfo.second.endTime[i] - funcInfo.second.startTime[i]);
            }
        }
    }
}

void TimePair::functionStatisticsAnalysis()
{
    for (auto &processInfo : timePairMap) {
        for (auto &funcInfo : processInfo.second) {
            std::vector<int> delayTmp[DELAY_INFO_MAX];
            int len = funcInfo.second.delay.size();
            int delaySum[DELAY_INFO_MAX] = { 0 };
            for (int i = 0; i < len; i++) {
                if (funcInfo.second.isInvalid[i]) {
                    continue;
                }
                int delay = funcInfo.second.delay[i];
                delayTmp[DELAY_INFO_ALL].emplace_back(delay);
                delaySum[DELAY_INFO_ALL] += delay;
                if ((int)funcInfo.second.retVal[i] < 0) {
                    delayTmp[DELAY_INFO_RETVAL_LESS_ZERO].emplace_back(delay);
                    delaySum[DELAY_INFO_RETVAL_LESS_ZERO] += delay;
                } else {
                    delayTmp[DELAY_INFO_RETVAL_GEOREQ_ZERO].emplace_back(delay);
                    delaySum[DELAY_INFO_RETVAL_GEOREQ_ZERO] += delay;
                }
            }
            for (int i = 0; i < DELAY_INFO_MAX; i++) {
                DELAY_INFO_E type = (DELAY_INFO_E)i;
                sort(delayTmp[type].begin(), delayTmp[type].end());
                int valid_len = delayTmp[type].size();
                if (valid_len > 0) {
                    funcInfo.second.summary.delay[type][DELAY_SUMMARY_SUM] = delaySum[type];
                    funcInfo.second.summary.delay[type][DELAY_SUMMARY_MIN] = delayTmp[type][0];
                    funcInfo.second.summary.delay[type][DELAY_SUMMARY_MAX] = delayTmp[type][valid_len - 1];
                    funcInfo.second.summary.delay[type][DELAY_SUMMARY_P50] = delayTmp[type][ceil(0.50 * valid_len) - 1];
                    funcInfo.second.summary.delay[type][DELAY_SUMMARY_P80] = delayTmp[type][ceil(0.80 * valid_len) - 1];
                    funcInfo.second.summary.delay[type][DELAY_SUMMARY_P95] = delayTmp[type][ceil(0.95 * valid_len) - 1];
                    funcInfo.second.summary.delay[type][DELAY_SUMMARY_P99] = delayTmp[type][ceil(0.99 * valid_len) - 1];
                    funcInfo.second.summary.callTimes[type] = valid_len;
                    funcInfo.second.summary.aveDelay[type] = delaySum[type] * 1.0 / valid_len;
                } else {
                    funcInfo.second.summary.delay[type][DELAY_SUMMARY_SUM] = 0;
                    funcInfo.second.summary.delay[type][DELAY_SUMMARY_MIN] = 0;
                    funcInfo.second.summary.delay[type][DELAY_SUMMARY_MAX] = 0;
                    funcInfo.second.summary.delay[type][DELAY_SUMMARY_P50] = 0;
                    funcInfo.second.summary.delay[type][DELAY_SUMMARY_P80] = 0;
                    funcInfo.second.summary.delay[type][DELAY_SUMMARY_P95] = 0;
                    funcInfo.second.summary.delay[type][DELAY_SUMMARY_P99] = 0;
                    funcInfo.second.summary.callTimes[type] = 0;
                    funcInfo.second.summary.aveDelay[type] = 0;
                }
            }
        }
    }
}

void TimePair::saveTimePairToFile()
{
    Config &cfg = Config::getInstance();

    if (cfg.getDebugLevel() < DEBUG_LEVEL_3) {
        return;
    }

    std::ofstream file(cfg.filename[FILE_TYPE_DEBUG_TIME_PAIE], std::ios::out | std::ios::trunc);
    if (!file) {
        std::cout << "file open failed:" << cfg.filename[FILE_TYPE_DEBUG_TIME_PAIE] << std::endl;
        return;
    }

    for (const auto &processInfo : timePairMap) {
        for (const auto &funcInfo : processInfo.second) {
            int pid = processInfo.first;
            file << "pid:" << pid << "," << std::endl;
            file << "functionIndex:" << funcInfo.first << "," << cfg.IndexToFunction[funcInfo.first] << std::endl;
            file << "info num," << funcInfo.second.startTime.size() << ",valid info num," << funcInfo.second.callTimes << ",";
            file << "validStartTime," << validTimeOfPid[pid].validStartTime << ",validEndTime," << validTimeOfPid[pid].validEndTime << std::endl;
            file << "startTime" << ",";
            for (const auto &startTime : funcInfo.second.startTime) {
                file << std::fixed << std::setprecision(6) << startTime << ",";
            }
            file << std::endl;
            file << "endTime" << ",";
            for (const auto &endTime : funcInfo.second.endTime) {
                file << std::fixed << std::setprecision(6) << endTime << ",";
            }
            file << std::endl;
            file << "delay" << ",";
            for (const auto &delay : funcInfo.second.delay) {
                file << std::fixed << std::setprecision(6) << delay << ",";
            }
            file << std::endl;
            file << "fatherFunction" << ",";
            for (const auto &fatherFunction : funcInfo.second.fatherFunction) {
                file << fatherFunction << ",";
            }
            file << std::endl;
            file << "fatherFuncPos" << ",";
            for (const auto &fatherFuncPos : funcInfo.second.fatherFuncPos) {
                file << fatherFuncPos << ",";
            }
            file << std::endl;
            file << "childFuncTimes" << ",";
            for (const auto &childFuncTimes : funcInfo.second.childFuncTimes) {
                file << childFuncTimes << ",";
            }
            file << std::endl;

            file << "strFunctionStk" << ",";
            for (const auto &strFunctionStk : funcInfo.second.strFunctionStk) {
                file << strFunctionStk << ",";
            }
            file << std::endl;
            file << "isInvalid" << ",";
            for (const auto &isInvalid : funcInfo.second.isInvalid) {
                file << isInvalid << ",";
            }
            file << std::endl;
        }
    }

    file.close();
}

void TimePair::saveDelayInfoToFile()
{
    Config &cfg = Config::getInstance();
    std::ofstream file(cfg.filename[FILE_TYPE_OUTPUT_DELAY], std::ios::out | std::ios::trunc);
    if (!file) {
        std::cout << "file open failed:" << cfg.filename[FILE_TYPE_OUTPUT_DELAY] << std::endl;
        return;
    }

    TraceResolve &trace_resolve_inst = TraceResolve::getInstance();
    file << "note : (r>=0) => (int)return value >=0; ave => average delay,";
    file << "pid,function,";
    file << "call_times,ave,sum,min,max,p50,p80,p95,p99,";
    file << "call_times(r>=0),ave(r>=0),sum(r>=0),min(r>=0),max(r>=0),p50(r>=0),p80(r>=0),p95(r>=0),p99(r>=0),";
    file << "call_times(r<0),ave(r<0),sum(r<0),min(r<0),max(r<0),p50(r<0),p80(r<0),p95(r<0),p99(r<0),";
    file << std::endl;
    for (const auto &processInfo : timePairMap) {
        for (const auto &funcInfo : processInfo.second) {
            if (cfg.filterCfgMap.size() != 0 && cfg.filterCfgMap.count(processInfo.first) == 0) {
                continue;
            }
            if (funcInfo.second.summary.callTimes[DELAY_INFO_ALL] <= 0) {
                continue;
            }
            file << "," << processInfo.first << ",";
            file << cfg.IndexToFunction[funcInfo.first] << ",";

            for (int i = 0; i < DELAY_INFO_MAX; i++) {
                DELAY_INFO_E infoType = (DELAY_INFO_E)i;
                file << funcInfo.second.summary.callTimes[infoType] << ",";
                file << std::fixed << std::setprecision(3) << funcInfo.second.summary.aveDelay[infoType] << ",";
                for (int j = 0; j < DELAY_SUMMARY_ENUM_MAX; j++) {
                    DELAY_SUMMARY_E summaryType = (DELAY_SUMMARY_E)j;
                    file << funcInfo.second.summary.delay[infoType][summaryType] << ",";
                }
            }
            file << std::endl;
        }
    }

    file.close();
}


int TimePair::getProcessValidTime(const int &pid)
{
    if (validTimeOfPid.count(pid) != 0) {
        return validTimeOfPid[pid].validEndTime - validTimeOfPid[pid].validStartTime;
    } else {
        return 0;
    }

}

void TimePair::timePairAnalysis()
{
    // step 1 : convert trace to time pair
    timePairMatching();
    // step 2 : make sure start_time.size() = end_time.size()
    timePairAlignment();
    // step 3 : mark date whether invalid
    timePairMarkInvalidData();
    // step 4: compute statistics rst
    functionDelayUpdate();
    functionStatisticsAnalysis();
    // step 5: save rst
    saveTimePairToFile();
    saveDelayInfoToFile();
}