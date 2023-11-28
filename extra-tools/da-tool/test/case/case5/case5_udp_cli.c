#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <pthread.h>
#define BUFFER_SIZE 1024
#define PORT 8888

void* sendRequest(void* arg) {
    int clientSocket = *(int*)arg;

    while (1) {
        struct sockaddr_in serverAddress;
        memset(&serverAddress, 0, sizeof(serverAddress));
        serverAddress.sin_family = AF_INET;
        serverAddress.sin_port = htons(PORT);

        if (inet_pton(AF_INET, "127.0.0.1", &(serverAddress.sin_addr)) <= 0) {
            perror("Invalid server address");
            return NULL;
        }

        // Send a message to the server
        char* message = "Hello, Server!";
        ssize_t sentBytes = sendto(clientSocket, message, strlen(message), 0,
                                   (struct sockaddr*)&serverAddress, sizeof(serverAddress));

        if (sentBytes < 0) {
            perror("Sending message failed");
            return NULL;
        }

        printf("Sent message to server\n");

        // Receive server response
        char buffer[BUFFER_SIZE] = {0};
        socklen_t serverAddressLength = sizeof(serverAddress);
        ssize_t receivedBytes = recvfrom(clientSocket, buffer, BUFFER_SIZE, 0,
                                         (struct sockaddr*)&serverAddress, &serverAddressLength);

        if (receivedBytes < 0) {
            perror("Receive response failed");
            return NULL;
        }

        printf("Received response from server:%s\n", buffer);

        usleep(100000);
    }

    close(clientSocket);

    return NULL;
}

int main() {
    int clientSocket = socket(AF_INET, SOCK_DGRAM, 0);
    if (clientSocket == -1) {
        perror("Unable to create socket");
        return -1;
    }

    const int numThreads = 5;
    pthread_t tids[numThreads];

    for (int i = 0; i < numThreads; ++i) {
        if (pthread_create(&tids[i], NULL, sendRequest, &clientSocket) != 0) {
            perror("Unable to create socket");
            return -1;
        }
    }

    for (int i = 0; i < numThreads; ++i) {
        pthread_join(tids[i], NULL);
    }

    return 0;
}
