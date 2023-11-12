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
#include "trace_resolve.h"
#include "config.h"
#include "function_stack.h"
#include "sched_analysis.h"
#include "time_pair.h"

using namespace std;

int main(int argc, char *argv[])
{
    cout << "analysis start..." << endl;
    Config &cfg = Config::getInstance();
    cfg.configInit(argc, argv);
    cout << "analysis Config completed" << endl;

    TraceResolve &trace_resolve_inst = TraceResolve::getInstance();
    trace_resolve_inst.trace_resolve_proc();
    cout << "analysis resolve completed" << endl;

    TimePair &tpInst = TimePair::getInstance();
    tpInst.timePairAnalysis();
    cout << "analysis time pair completed" << endl;

    SchedAnalysis &schedAnalysisInst = SchedAnalysis::getInstance();
    schedAnalysisInst.schedAnalysisProc();
    cout << "analysis sched completed" << endl;

    FunctionStack &fstk = FunctionStack::getInstance();
    fstk.function_stack_proc();
    cout << "analysis FunctionStack completed" << endl;
    cout << "analysis finish" << endl;
    return 0;
}