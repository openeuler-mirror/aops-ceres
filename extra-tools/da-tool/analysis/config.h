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

#ifndef __CONFIG_H__
#define __CONFIG_H__
#include <string>
#include <unordered_map>
#include <vector>

typedef enum {

  FILE_TYPE_TRACE,
  FILE_TYPE_TRACE_CSV,
  FILE_TYPE_FUNC_CFG,

  // output
  FILE_TYPE_OUTPUT_DELAY,
  FILE_TYPE_OUTPUT_RUN_LOG,
  FILE_TYPE_OUTPUT_FUNC_STACK_DELALY,
  FILE_TYPE_OUTPUT_PROCESS_SCHED_INFO,
  FILE_TYPE_OUTPUT_SUMMARY_SCHED_INFO,

  // debug 1
  FILE_TYPE_DEBUG_CONFIG,
  FILE_TYPE_DEBUG_TIME_PAIR_MARK,
  // debug 2
  // debug 3
  FILE_TYPE_DEBUG_TRACE,
  FILE_TYPE_DEBUG_REGEX,
  FILE_TYPE_DEBUG_TIME_PAIR_ALIGN,
  FILE_TYPE_DEBUG_TIME_PAIE,
  FILE_TYPE_DEBUG_DELAY_FUNC_STACK_TRACE,
  // debug 4
  FILE_TYPE_DEBUG_FUNC_STACK_TRACE,
  FILE_TYPE_MAX,
} FILE_TYPE_E;

typedef enum {
  DEBUG_LEVEL_0,
  DEBUG_LEVEL_1,
  DEBUG_LEVEL_2,
  DEBUG_LEVEL_3,
  DEBUG_LEVEL_4,
  DEBUG_LEVEL_MAX,
} DEBUG_LEVEL_E;

typedef enum {
  CFG_TYPE_FUNC_BEGIN,
  CFG_TYPE_KERNEL = CFG_TYPE_FUNC_BEGIN,
  CFG_TYPE_USER,
  CFG_TYPE_SCHED,
  CFG_TYPE_FUNC_END = CFG_TYPE_SCHED,

  CFG_TYPE_FILTER_BEGIN,
  CFG_TYPE_FILTER_PID = CFG_TYPE_FILTER_BEGIN,
  CFG_TYPE_FILTER_END = CFG_TYPE_FILTER_PID,

  CFG_TYPE_MAX = CFG_TYPE_FILTER_END,
} CFG_TYPE_E;

class functionCfg {
public:
  CFG_TYPE_E cfgType;
  int isRet; // 0 : entry 1 return ,only FUNC_TYPE_KERNEL and FUNC_TYPE_USER use
  int functionIndex; // Function globally unique identifier, used for fast
                     // storage and differentiation of functions
};

class FilterConfig {
public:
  CFG_TYPE_E cfgType;
  int pidFilter;
};

class Config {
public:
  static Config &getInstance() {
    static Config instance;
    return instance;
  }
  Config(const Config &) = delete;
  Config &operator=(const Config &) = delete;
  Config();
  ~Config() {}

private:
  DEBUG_LEVEL_E debugLevel;

  void pathInit();
  void functionCfgInit();

public: // function cfg
  std::unordered_map<std::string, functionCfg> funcCfgMap;
  std::unordered_map<int, FilterConfig>
      filterCfgMap; // cfg.filterCfgMap.size() = 0 , then not filter
  std::unordered_map<int, std::string>
      IndexToFunction; // [functionIndex, function string]
  std::vector<std::string> filename{
      std::vector<std::string>(FILE_TYPE_MAX, "")};

  int readTraceBegin;
  int readTraceLen;
  void configInit(int argc, char *argv[]);
  DEBUG_LEVEL_E getDebugLevel();
};

#endif