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
//    PROCESS_STATE_TASK_UNINTERRUPTIBL,  // D
//    PROCESS_STATE_TASK_STOPPED,		  // T
//    PROCESS_STATE_TASK_TRACED,		  //t
//
//    PROCESS_STATE_EXIT_DEAD,		// X
//    PROCESS_STATE_EXIT_ZOMBIE,    // Z
//    PROCESS_STATE_EXIT_TRACE,		
//
//    PROCESS_STATE_TASK_PARKED,	// P
//    PROCESS_STATE_TASK_DEAD,		// I
    PROCESS_STATE_MAX,
} PROCESS_STATE_E;

typedef enum {
  LINE_TYPE_FUNC,
  LINE_TYPE_SCHED_SWITCH,
  LINE_TYPE_SCHED_SWITCH_RET,
  LINE_TYPE_MAX,
} LINE_TYPE_E;

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

public:
  const std::vector<TraceLineReslove> &getTraceLine() const;
  double convertTimeIntToDouble(const int &timestamp);
  void trace_resolve_proc();
};

#endif