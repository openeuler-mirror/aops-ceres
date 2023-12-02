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

#ifndef __TIME_PAIR_H__
#define __TIME_PAIR_H__

#include "common.h"
#include <fstream>
#include <iostream>
#include <regex>
#include <string>
#include <unordered_map>
#include <vector>

class VaildRange {
public:
  // Invalid timestamps divide the trace into several valid parts
  std::vector<int> validStartTime;
  std::vector<int> validEndTime;

  int procStartTime{0};
  int procEndTime{0};
  int procTime{0};
  int validTime{0};
  // tmp var
  bool lastTimeValid{false};
};

typedef enum {
  DELAY_SUMMARY_SUM,
  DELAY_SUMMARY_MIN,
  DELAY_SUMMARY_MAX,
  DELAY_SUMMARY_P50,
  DELAY_SUMMARY_P80,
  DELAY_SUMMARY_P95,
  DELAY_SUMMARY_P99,
  DELAY_SUMMARY_ENUM_MAX,
} DELAY_SUMMARY_E;

typedef enum {
  DELAY_INFO_ALL,
  DELAY_INFO_RETVAL_GEOREQ_ZERO, // ret>=0
  DELAY_INFO_RETVAL_LESS_ZERO,   // ret<0
  DELAY_INFO_MAX,
} DELAY_INFO_E;

class TimePairSummary {
public:
  double aveDelay[DELAY_INFO_MAX];
  int callTimes[DELAY_INFO_MAX];
  int delay[DELAY_INFO_MAX][DELAY_SUMMARY_ENUM_MAX];
};

class TimePairInfo {
public:
  // The time relative to the integer time of the first trace , Unit:
  // microseconds
  std::vector<int> startTime;
  std::vector<int> endTime;
  std::vector<int> delay; // endTime - startTime
  // If there is no function to call this function , fatherFunction = 0;
  std::vector<int> fatherFunction;
  // pos = timePairMap[pid][functionIndex].fatherFuncPos[i],
  // timePairMap[pid][fatherFunction].fatherFuncPos[pos] , Reverse Find Call
  // Relationship
  std::vector<int> fatherFuncPos;
  std::vector<int> childFuncTimes; // Number of calls to other functions.
  std::vector<uintptr_t> retVal;   // return value
  std::vector<bool> isInvalid;     // isInvalid=true indicates that there is no
                                   // complete call stack data
  std::vector<std::string> strFunctionStk;

  int maxStartTimeInvaild;
  int minEndTimeInvalid;

  // analysis result
  TimePairSummary summary;
};

class TimePair {
public:
  static TimePair &getInstance() {
    static TimePair instance;
    return instance;
  }
  TimePair(const TimePair &) = delete;
  TimePair &operator=(const TimePair &) = delete;
  TimePair();
  ~TimePair() {}

private:
  std::unordered_map<int, VaildRange> validTimeOfPid;
  // Store function call stacks for each pid
  std::unordered_map<int, std::vector<int>> funcStkMap;
  std::unordered_map<int, std::unordered_map<int, TimePairInfo>>
      timePairMap; // [pid][functionName]

private:
  int getFatherFunctionIdLoop(const int &pid, const int &functionIndex,
                              const int &isRet, int &debugPos);
  void timePairUpdateLoop(const int &pid, const int &functionIndex,
                          const int &isRet, const int &timestamp,
                          const int &fatherFunction,
                          const TraceLineReslove &line_info_tmp);
  void saveFuncStkDebugToFile(std::ofstream &file, const int &pid,
                              const int &functionIndex, const int &isRet,
                              const int &timestamp, const int &fatherFunction,
                              const int &debugPos);
  void functionDelayUpdate();
  void functionDelayUpdateValidTimeLoop(const int &pid, const int &timestamp,
                                        const bool &valid);
  void functionStatisticsAnalysis();

  void timePairMatching();
  void timePairAlignment();
  void timePairMarkInvalidData();

  void saveTimePairToFile();
  void saveDelayInfoToFile();

public:
  const std::unordered_map<int, std::unordered_map<int, TimePairInfo>> &
  getTimePairMap() const;
  int getProcessValidTime(const int &pid);
  int getProcessTime(const int &pid);
  void timePairAnalysis();
};

#endif