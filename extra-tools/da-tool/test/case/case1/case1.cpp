#include <iostream>
#include <unistd.h>

using namespace std;

void delay_1us()
{
    usleep(1);
}

void delay_10us()
{
    usleep(10);
}

void delay_1ms()
{
    usleep(1000);
}

void delay_10ms()
{
    usleep(10000);
}

void funcC()
{
    for (int i = 0; i < 1000; i++) {
    }
}
void funcB()
{
    for (int i = 0; i < 100; i++) {
        for (int j = 0; j < 1000; j++) {
        }
        funcC();
    }
}
void funcA()
{
    for (int i = 0; i < 100; i++) {
        funcB();
    }
}

int main()
{
    int loopnum = 0;
    while (1) {
        cout << "loopnum:" << loopnum << endl;
        loopnum++;
        delay_10us();
        delay_1us();
        delay_1ms();
        delay_10ms();
        funcA();
        funcB();
        funcC();
    }
    return 0;
}

//  g++ case1.cpp -o case1
// _Z9delay_1usv,_Z10delay_10usv,_Z9delay_1msv,_Z10delay_10msv,_Z5funcCv,_Z5funcBv,_Z5funcAv