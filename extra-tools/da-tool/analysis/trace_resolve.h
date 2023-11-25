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

#ifndef __TRACE_RESOLVE_H__
#define __TRACE_RESOLVE_H__

#include <fstream>
#include <iostream>
#include <regex>
#include <string>
#include <unordered_map>
#include <vector>

// include\linux\sched.h
typedef enum
{
    PROCESS_STATE_TASK_RUNNING,           // R
    PROCESS_STATE_TASK_INTERRUPTIBLE,     // S
    PROCESS_STATE_MAX,
} PROCESS_STATE_E;

class SchedSwitchLine {
public:
  int prevPid;
  int prevPrio;
  PROCESS_STATE_E prevState;
  int nextPid;
  int nextPrio;

public:
  void processStateToEnum(std::string state);
};

class TraceLineReslove {
public:
  int traceLineNum;
  int pid;
  int core;
  int timestamp;
  std::string functionName;
  SchedSwitchLine schedSwitchLine;
  std::vector<uintptr_t> args;

  // after convert
  int functionIndex;
};

class FirstInfo {
public:
  std::vector<int> schedSwitchTime; // [coreId]
  std::vector<int> coreTime;        // [coreId]
  int coreId;                       // first core in trace
  int startTime;
};

class TraceResolve {
public:
  static TraceResolve &getInstance() {
    static TraceResolve instance;
    return instance;
  }
  TraceResolve(const TraceResolve &) = delete;
  TraceResolve &operator=(const TraceResolve &) = delete;
  TraceResolve();
  ~TraceResolve() {}

private: // regex
  int startTimeIntPart;
  std::vector<TraceLineReslove> traceLineVec; // line info by regex
  void resolveTrace();
  void saveTraceRegexRstToFile();

private:
  FirstInfo firstInfo;
  void firstSchedSwitchTimeAnalysis();

public:
  const std::vector<TraceLineReslove> &getTraceLine() const;
  const FirstInfo &getTraceFirstInfo() const;
  double convertTimeIntToDouble(const int &timestamp);
  void trace_resolve_proc();
  void trace_check_show();
};

#endif