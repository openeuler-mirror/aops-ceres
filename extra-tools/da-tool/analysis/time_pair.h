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
  int validStartTime;
  int validEndTime;
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
  std::vector<int> isInvalid;      // isInvalid=true indicates that there is no
                                   // complete call stack data
  std::vector<std::string> strFunctionStk;

  // analysis result
  double aveDelay;
  int maxDelay;
  int minDelay;
  int delaySum;
  int maxDelayPos;
  int minDelayPos;
  int callTimes;
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
  // [pid].start/end Record the start and end times of valid traces
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
  void timePairAnalysis();
};

#endif