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

typedef enum {
  CORE_TRACE_INVALID,    // valid when (s sr) or (sr s and startcore = endcore)
  CORE_TRACE_SCHEDULING, // (s sr)
  CORE_TRACE_ONCORE,     // (sr s and startcore = endcore)
  CORE_TRACE_MAX,
} CORE_TRACE_E;

typedef enum {
  SCHED_SUMMARY_VAILD,
  SCHED_SUMMARY_ALL, // "all" means "valid" + "invalid"
  SCHED_SUMMARY_MAX,
} SCHED_SUMMARY_E;

class ProcessCoreTrace {
public:
  int startTime;
  int endTime;
  int startCoreId;
  int endCoreId;
  bool startIsRet; // pid1->pid2  ret for pid2, not ret for pid1
  bool endIsRet;

  CORE_TRACE_E coreTraceType;
};

class ProcessSchedInfo {
public:
  std::vector<int> runTimeOfCore{
      std::vector<int>(CPU_CORE_NUM_MAX, 0)}; // Time running on each CPU
  std::vector<ProcessCoreTrace>
      coreTrace; // CPU information of pid in each time period

  int vaildSchedSwitchDelay;
  double validPercentSchedSwitch; // valid / valid
  int schedSwitchTimes[SCHED_SUMMARY_MAX];
  int cpuSwitchTimes[SCHED_SUMMARY_MAX];
  int delaySum[SCHED_SUMMARY_MAX];
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
                                const int &coreIndex, const bool &isRet);
  void schedInfoProc();
  void schedInfoVaildMark();
  void schedInfoAnalysis();
  void saveSchedInfoToFile();
  void saveSchedInfoSummaryToFile();

public:
  void schedAnalysisProc();
};

#endif