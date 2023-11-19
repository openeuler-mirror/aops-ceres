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
#ifndef __SCHED_ANALYSIS_H__
#define __SCHED_ANALYSIS_H__

#include "common.h"
#include <fstream>
#include <iostream>
#include <regex>
#include <string>
#include <unordered_map>
#include <vector>

class ProcessCoreTrace {
public:
  int startTime;
  int endTime;
  int coreIndex; // -1 means sched_switch
};

class ProcessSchedInfo {
public:
  std::vector<int> runTimeOfCore{
      std::vector<int>(CPU_CORE_NUM_MAX, 0)}; // Time running on each CPU
  std::vector<ProcessCoreTrace>
      coreTrace; // CPU information of pid in each time period
  int schedSwitchDelay;
  int schedSwitchTimes;
  double percentageSchedSwitch;
  int cpuSwitchTimes;
  int delaySum;
};

class CpuSchedTrace {
public:
  int startTime;
  int endTime;
  int pid;
};

class CpuSchedInfo {
public:
  int delay;
  int processSwitchTimes;
  std::unordered_map<int, int> runTimeOfProcess;
  std::vector<CpuSchedTrace> processTrace;
};

class SchedAnalysis {
public:
  static SchedAnalysis &getInstance() {
    static SchedAnalysis instance;
    return instance;
  }
  SchedAnalysis(const SchedAnalysis &) = delete;
  SchedAnalysis &operator=(const SchedAnalysis &) = delete;
  SchedAnalysis();
  ~SchedAnalysis() {}

private: // process sched info
  std::unordered_map<int, ProcessSchedInfo> processSchedMap; // [pid]
  // std::vector <std::vector<CpuSchedInfo>> allCpuSchedInfo;  // [coreIndex]
  void processSchedAnalysisLoop(const int &pid, const int &timestamp,
                                const int &coreIndex);
  void schedInfoProc();
  void schedInfoAnalysis();
  void saveSchedInfoToFile();
  void saveSchedInfoSummaryToFile();

public:
  void schedAnalysisProc();
};

#endif