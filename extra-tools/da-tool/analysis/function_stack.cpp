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

#include <vector>
#include <string>
#include <unordered_map>
#include <sstream>
#include <iostream>
#include <iomanip>
#include <cmath>
#include "function_stack.h"
#include "trace_resolve.h"
#include "config.h"
#include "time_pair.h"
#include "common.h"


FunctionStack::FunctionStack()
{
}

void FunctionStack::delayMapInit()
{
    TimePair &tpInst = TimePair::getInstance();
    for (const auto &processInfo : tpInst.getTimePairMap()) {
        int pid = processInfo.first;
        if (delayMap.count(pid) == 0) {
            std::unordered_map<int, FsDelayInfo> map_tmp;
            delayMap.emplace(pid, map_tmp);
        }

        for (const auto &funcInfo : processInfo.second) {
            int functionIndex = funcInfo.first;
            if (delayMap[pid].count(functionIndex) == 0) {
                FsDelayInfo infoTmp;
                delayMap[pid].emplace(functionIndex, infoTmp);
            }
            delayMap[pid][functionIndex].delay[FS_DELAY_TYPE_GLOBAL] = funcInfo.second.delay;
            delayMap[pid][functionIndex].delay[FS_DELAY_TYPE_LOCAL] = funcInfo.second.delay;
            delayMap[pid][functionIndex].childFuncTimes = funcInfo.second.childFuncTimes;
            delayMap[pid][functionIndex].isStackFinish.resize(funcInfo.second.delay.size(), false);
            delayMap[pid][functionIndex].retVal = funcInfo.second.retVal;
        }
    }
}

void FunctionStack::stackMapInit()
{
    Config &cfg = Config::getInstance();
    std::ofstream debugFile(cfg.filename[FILE_TYPE_DEBUG_DELAY_FUNC_STACK_TRACE], std::ios::out | std::ios::trunc);
    if (!debugFile) {
        std::cout << "file open failed:" << cfg.filename[FILE_TYPE_DEBUG_DELAY_FUNC_STACK_TRACE] << std::endl;
        return;
    }

    TimePair &tpInst = TimePair::getInstance();
    for (const auto &processInfo : tpInst.getTimePairMap()) {
        int pid = processInfo.first;
        if (pid == 0) {
            continue;
        }
        if (funcStackMap.count(pid) == 0) {
            std::unordered_map<std::string, StackInfo> stktmp;
            funcStackMap.emplace(pid, stktmp);
        }

        // In theory, this judgment condition should be fatherFuncTimes=0, but for fear of a dead loop, 
        // modify the logic to exit the loop when fatherFuncTimes is equal twice
        int fatherFuncTimes = 0;
        int lastFatherFuncTimes = -1;
        while (lastFatherFuncTimes != fatherFuncTimes) {
            lastFatherFuncTimes = fatherFuncTimes;
            if (cfg.getDebugLevel() >= DEBUG_LEVEL_1) {
                debugFile << "pid," << pid << ",fatherFuncTimes," << fatherFuncTimes << std::endl;
            }
            fatherFuncTimes = 0;
            for (const auto &funcInfo : processInfo.second) {
                int functionIndex = funcInfo.first;
                int len = funcInfo.second.startTime.size();
                int maxDelay = 0;

                for (int i = 0; i < len; i++) {
                    if (funcInfo.second.isInvalid[i] == 1 || delayMap[pid][functionIndex].isStackFinish[i] == true) {
                        if (cfg.getDebugLevel() >= DEBUG_LEVEL_4) {
                            debugFile << "pid," << pid << ",functionIndex," << functionIndex << ",invalid" << std::endl;
                        }

                        continue;
                    }

                    if (delayMap[pid][functionIndex].childFuncTimes[i] > 0) {
                        fatherFuncTimes++;
                        if (cfg.getDebugLevel() >= DEBUG_LEVEL_4) {
                            debugFile << "pid," << pid << ",functionIndex," << functionIndex << ",fatherFuncTimes," << fatherFuncTimes << std::endl;
                        }
                        continue;
                    }

                    // The time pair has already been calculated, skip next time
                    delayMap[pid][functionIndex].isStackFinish[i] = true; 

                    std::string strFunctionStk = funcInfo.second.strFunctionStk[i];
                    int fatherFunction = funcInfo.second.fatherFunction[i];
                    int globalDelay = delayMap[pid][functionIndex].delay[FS_DELAY_TYPE_GLOBAL][i];
                    int localDelay = delayMap[pid][functionIndex].delay[FS_DELAY_TYPE_LOCAL][i];
                    // Because it is uncertain whether the return value is 32-bit or 64-bit, 
                    // in order to find a number less than 0, compromise to take 32-bit, otherwise 0xfffff5 will be considered as>0
                    int retVal = (int)delayMap[pid][functionIndex].retVal[i];

                    if (fatherFunction != 0) {
                        int fatherFuncPos = funcInfo.second.fatherFuncPos[i];
                        delayMap[pid][fatherFunction].childFuncTimes[fatherFuncPos]--;
                        delayMap[pid][fatherFunction].delay[FS_DELAY_TYPE_LOCAL][fatherFuncPos] -= globalDelay;
                    }

                    if (funcStackMap[pid].count(strFunctionStk) == 0) {
                        StackInfo stkInfoTmp;
                        stkInfoTmp.delaySum[FS_DELAY_TYPE_LOCAL] = 0;
                        stkInfoTmp.delaySum[FS_DELAY_TYPE_GLOBAL] = 0;
                        stkInfoTmp.num = 0;
                        funcStackMap[pid].emplace(strFunctionStk, stkInfoTmp);
                    }

                    funcStackMap[pid][strFunctionStk].delaySum[FS_DELAY_TYPE_GLOBAL] += globalDelay;
                    funcStackMap[pid][strFunctionStk].delaySum[FS_DELAY_TYPE_LOCAL] += localDelay;

                    funcStackMap[pid][strFunctionStk].retValLessZeroTimes += retVal < 0 ? 1 : 0;
                    if (cfg.getDebugLevel() >= DEBUG_LEVEL_4) {
                        debugFile << "pid," << pid << ",localDelay," << localDelay << ",globalDelay," << globalDelay << std::endl;
                    }
                    funcStackMap[pid][strFunctionStk].num++;
                }
            }
        }
    }
    debugFile.close();
}

void FunctionStack::stackMapAnalysis()
{
    TimePair &tpInst = TimePair::getInstance();
    for (auto &processInfo : funcStackMap) {
        int pid = processInfo.first;
        int pidDelay = tpInst.getProcessValidTime(pid);
        for (auto &stkInfo : processInfo.second) {
            stkInfo.second.aveDelay[FS_DELAY_TYPE_GLOBAL] = stkInfo.second.delaySum[FS_DELAY_TYPE_GLOBAL] * 1.0 / stkInfo.second.num;
            stkInfo.second.aveDelay[FS_DELAY_TYPE_LOCAL] = stkInfo.second.delaySum[FS_DELAY_TYPE_LOCAL] * 1.0 / stkInfo.second.num;
            stkInfo.second.percentage[FS_DELAY_TYPE_LOCAL] = stkInfo.second.delaySum[FS_DELAY_TYPE_LOCAL] * 1.0 / pidDelay;
            stkInfo.second.percentage[FS_DELAY_TYPE_GLOBAL] = stkInfo.second.delaySum[FS_DELAY_TYPE_GLOBAL] * 1.0 / pidDelay;
        }
    }
}

void FunctionStack::saveFunctionStackToFile()
{
    Config &cfg = Config::getInstance();
    std::ofstream file(cfg.filename[FILE_TYPE_OUTPUT_FUNC_STACK_DELALY], std::ios::out | std::ios::trunc);
    if (!file) {
        std::cout << "file open failed:" << cfg.filename[FILE_TYPE_OUTPUT_FUNC_STACK_DELALY] << std::endl;
        return;
    }

    for (const auto &processInfo : funcStackMap) {

        for (const auto &stkInfo : processInfo.second) {
            int pid = processInfo.first;
            if (cfg.filterCfgMap.size() != 0 && cfg.filterCfgMap.count(pid) == 0) {
                continue;
                
            }
            file << "pid_" + std::to_string(pid);
            std::stringstream ss(stkInfo.first);
            std::string token;
            while (std::getline(ss, token, '.')) {
                if (!token.empty()) {
                    int functionIndex = std::stoi(token);
                    file << ";" << cfg.IndexToFunction[functionIndex];
                }
            }

            file << " " << stkInfo.second.delaySum[FS_DELAY_TYPE_LOCAL]; // for flame graph
            file << ", localDelaySum ," << stkInfo.second.delaySum[FS_DELAY_TYPE_LOCAL];
            file << ", localAvedelay ," << std::fixed << std::setprecision(6) << stkInfo.second.aveDelay[FS_DELAY_TYPE_LOCAL];
            file << ", localPercentage, " << std::fixed << std::setprecision(3) << stkInfo.second.percentage[FS_DELAY_TYPE_LOCAL] * 100 << "%";
            file << ", globalDelaySum ," << stkInfo.second.delaySum[FS_DELAY_TYPE_GLOBAL];
            file << ", globalAvedelay, " << std::fixed << std::setprecision(6) << stkInfo.second.aveDelay[FS_DELAY_TYPE_GLOBAL];
            file << ", globalPercentage, " << std::fixed << std::setprecision(3) << stkInfo.second.percentage[FS_DELAY_TYPE_GLOBAL] * 100 << "%";
            file << ", times ," << std::setw(5) << std::setfill(' ') << stkInfo.second.num;
            file << ", (int)ret>=0 times ," << stkInfo.second.num - stkInfo.second.retValLessZeroTimes;

            file << std::endl;
        }
        file << std::endl;
    }

    file.close();
}

std::string getFatherFuncStk(const std::string &strFunctionStk)
{
    size_t lastDotPos = strFunctionStk.find_last_of('.');
    if (lastDotPos != std::string::npos) {
        if (lastDotPos == 0) {
            return ".0";
        } else {
            return strFunctionStk.substr(0, lastDotPos);
        }
    } else {
        return "";
    }
}

void FunctionStack::stackNodeMapInit()
{

    for (const auto &processInfo : funcStackMap) {
        int pid = processInfo.first;
        if (stackNodeMap.count(pid) == 0) {
            std::unordered_map<std::string, StackNode> nodeMapTmp;
            stackNodeMap.emplace(pid, nodeMapTmp);
        }

        for (const auto &stkInfo : processInfo.second) {
            std::string strFunctionStk = stkInfo.first;
            if (stackNodeMap[pid].count(strFunctionStk) != 0) {
                StackNode node_tmp;
                stackNodeMap[pid].emplace(strFunctionStk, node_tmp);
            }
            int func_index_tmp = 0;
            std::stringstream ss(strFunctionStk);
            std::string token;
            while (std::getline(ss, token, '.')) {
                if (!token.empty()) {
                    func_index_tmp = std::stoi(token);
                }
            }
            stackNodeMap[pid][strFunctionStk].functionIndex = func_index_tmp;
            std::string fatherFuncStk = getFatherFuncStk(strFunctionStk);
            stackNodeMap[pid][fatherFuncStk].nextStack.emplace_back(strFunctionStk);
        }
    }
}


void FunctionStack::stackNodeMapDfs(int pid, int functionIndex, std::string strFunctionStk, int space_len)
{
    Config &cfg = Config::getInstance();
    TimePair &tpInst = TimePair::getInstance();
    if (strFunctionStk == ".0") {
        std::cout << "├──pid:" << pid;
        int pidDelay = tpInst.getProcessValidTime(pid);
        if (pidDelay > 0) {
            std::cout << "{(" << tpInst.getProcessValidTime(pid) << ",100.000%)}";
        } else {
            std::cout << "  data invalid!!!";
        }

        std::cout << std::endl;
    } else {

        for (int i = 0; i < space_len; i++) {
            if (i % SPLIT_SPACE_LEN == 0)


            {
                std::cout << "│";
            }
            std::cout << " ";
        }
        std::cout << "├─────" << cfg.IndexToFunction[stackNodeMap[pid][strFunctionStk].functionIndex];
        std::cout << "{";
        std::cout << "(local: " << funcStackMap[pid][strFunctionStk].delaySum[FS_DELAY_TYPE_LOCAL] << ", " << std::fixed << std::setprecision(3) << funcStackMap[pid][strFunctionStk].percentage[FS_DELAY_TYPE_LOCAL] * 100 << "%, " << funcStackMap[pid][strFunctionStk].aveDelay[FS_DELAY_TYPE_LOCAL] << ")";
        std::cout << "(global:" << funcStackMap[pid][strFunctionStk].delaySum[FS_DELAY_TYPE_GLOBAL] << ", " << std::fixed << std::setprecision(3) << funcStackMap[pid][strFunctionStk].percentage[FS_DELAY_TYPE_GLOBAL] * 100 << "% ," << funcStackMap[pid][strFunctionStk].aveDelay[FS_DELAY_TYPE_GLOBAL] << ")";
        std::cout << ", times:" << funcStackMap[pid][strFunctionStk].num;
        std::cout << ", (int)ret>=0 times:" << funcStackMap[pid][strFunctionStk].num - funcStackMap[pid][strFunctionStk].retValLessZeroTimes;
        std::cout << "}" << std::endl;
    }

    for (const auto &nextStack : stackNodeMap[pid][strFunctionStk].nextStack) {
        stackNodeMapDfs(pid, stackNodeMap[pid][strFunctionStk].functionIndex, nextStack, space_len + SPLIT_SPACE_LEN);
    }

}

void FunctionStack::stackNodeMapDisplay()
{
    Config &cfg = Config::getInstance();
    std::cout << "Display the function delay of each pid " << std::endl;
    // std::cout << "format:function symbol{( delay sum (microsecond) ,percentage(occupy the entire pid runtime) ),average delay | num in trace}" << std::endl;
    for (const auto &processInfo : stackNodeMap) {
        int pid = processInfo.first;
        if (cfg.filterCfgMap.size() == 0 || cfg.filterCfgMap.count(pid) != 0) {
            std::cout << "───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────" << std::endl;
            stackNodeMapDfs(processInfo.first, 0, ".0", SPLIT_SPACE_LEN);
            std::cout << "───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────" << std::endl;
        }

    }
    std::cout << std::endl;
}

void FunctionStack::function_stack_proc()
{
    delayMapInit();
    stackMapInit();
    stackMapAnalysis();
    saveFunctionStackToFile();

    stackNodeMapInit();
    stackNodeMapDisplay();
}