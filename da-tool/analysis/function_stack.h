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

#ifndef __FUNCTION_STACK_H__
#define __FUNCTION_STACK_H__

#include <string>
#include <unordered_map>
#include <vector>

typedef enum {
  // The whole delay of the function stk, including sched and sub function time
  // consumption
  FS_DELAY_TYPE_GLOBAL,
  // The inner delay of the function stk, excluding sched and sub function time
  // consumption
  FS_DELAY_TYPE_LOCAL,
  FS_DELAY_TYPE_MAX,
} FS_DELAY_TYPE;

class FsDelayInfo // function stack delay info
{
public:
  std::vector<int> delay[FS_DELAY_TYPE_MAX];
  std::vector<uintptr_t> retVal;

  // tmp data
  std::vector<bool> isStackFinish;
  std::vector<int> childFuncTimes;
};

class StackInfo {
public:
  int delaySum[FS_DELAY_TYPE_MAX];
  int num;                              // function stack sample times
  double aveDelay[FS_DELAY_TYPE_MAX];   // delaySum / num
  double percentage[FS_DELAY_TYPE_MAX]; // delaySum / run time

  long long int retValLessZeroTimes;

  // Contains all the delays of the function stack, which can be sorted by time
  // to represent the variation pattern of the call stack
  std::vector<int> delay;
};

class StackNode {
public:
  int functionIndex;
  std::vector<std::string> nextStack;
};

class FunctionStack {
public:
  static FunctionStack &getInstance() {
    static FunctionStack instance;
    return instance;
  }
  FunctionStack(const FunctionStack &) = delete;
  FunctionStack &operator=(const FunctionStack &) = delete;
  FunctionStack();
  ~FunctionStack() {}

private:
  std::unordered_map<int, std::unordered_map<std::string, StackInfo>>
      funcStackMap; // [pid][strFunctionStk]
  std::unordered_map<int, std::unordered_map<int, FsDelayInfo>>
      delayMap; // [pid][functionIndex] , copy from trace_reslove
  void delayMapInit();
  void stackMapInit();

  void stackMapAnalysis();
  void saveFunctionStackToFile();

private: // stack node
  std::unordered_map<int, std::unordered_map<std::string, StackNode>>
      stackNodeMap; // [pid][strFunctionStk]
  void stackNodeMapInit();
  void stackNodeMapDisplay();
  void stackNodeMapDfs(int pid, int functionIndex, std::string strFunctionStk,
                       int space_len);

public:
  void function_stack_proc();
};

#endif