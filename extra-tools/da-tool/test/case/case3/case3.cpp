#include <iostream>
#include <vector>
#include <random>
#include <algorithm>

void sortArray(std::vector<int> &arr)
{
    std::sort(arr.begin(), arr.end());
}

int main() {
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<int> dis(1, 100);
    const int count = 100000;
    std::vector<int> numbers;
    numbers.resize(count);
    int loopCnt = 0;
    while(1)
    {
        loopCnt++;
        for (int i = 0; i < count; ++i) {
            int randomNum = dis(gen);
            numbers[i] = randomNum;
        }
        sortArray(numbers);
        std::cout<< "loopCnt:" << loopCnt << std::endl;
    }

    return 0;
}

// _Z9sortArrayRSt6vectorIiSaIiEE