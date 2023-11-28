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

void* handleClient(void* arg) {
    int serverSocket = *(int*)arg;

    while (1) {

        char buffer[BUFFER_SIZE] = {0};
        struct sockaddr_in clientAddress;
        socklen_t clientAddressLength = sizeof(clientAddress);
        ssize_t receivedBytes = recvfrom(serverSocket, buffer, BUFFER_SIZE, 0,
                                         (struct sockaddr*)&clientAddress, &clientAddressLength);

        if (receivedBytes < 0) {
            perror("Received message failed");
            return NULL;
        }

        printf("Received message from client:%s\n", buffer);


        char* response = "Hello, Client!";
        ssize_t sentBytes = sendto(serverSocket, response, strlen(response), 0,
                                   (struct sockaddr*)&clientAddress, clientAddressLength);

        if (sentBytes < 0) {
            perror("Sending response failed");
            return NULL;
        }

        printf("Response has been sent to the client\n");
    }


    close(serverSocket);

    return NULL;
}

int main() {

    int serverSocket = socket(AF_INET, SOCK_DGRAM, 0);
    if (serverSocket == -1) {
        perror("Unable to create socket");
        return -1;
    }


    struct sockaddr_in serverAddress;
    memset(&serverAddress, 0, sizeof(serverAddress));
    serverAddress.sin_family = AF_INET;
    serverAddress.sin_addr.s_addr = INADDR_ANY;
    serverAddress.sin_port = htons(PORT);

    if (bind(serverSocket, (struct sockaddr*)&serverAddress, sizeof(serverAddress)) < 0) {
        perror("Binding failed");
        return -1;
    }

    printf("Waiting for client connection\n");


    const int numThreads = 5;
    pthread_t tids[numThreads];

    for (int i = 0; i < numThreads; ++i) {
        if (pthread_create(&tids[i], NULL, handleClient, &serverSocket) != 0) {
            perror("Create thread failed");
            return -1;
        }
    }


    for (int i = 0; i < numThreads; ++i) {
        pthread_join(tids[i], NULL);
    }

    return 0;
}
