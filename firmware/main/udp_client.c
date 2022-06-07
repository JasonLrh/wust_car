/* BSD Socket API Example

   This example code is in the Public Domain (or CC0 licensed, at your option.)

   Unless required by applicable law or agreed to in writing, this
   software is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
   CONDITIONS OF ANY KIND, either express or implied.
*/
#include <string.h>
#include <sys/param.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/event_groups.h"
#include "esp_system.h"
#include "esp_wifi.h"
#include "esp_event.h"
#include "esp_log.h"
#include "nvs_flash.h"
#include "esp_netif.h"
#include "protocol_examples_common.h"

#include "lwip/err.h"
#include "lwip/sockets.h"
#include "lwip/sys.h"
#include <lwip/netdb.h>
#include "addr_from_stdin.h"

#include "esp_camera.h"
#include <esp_log.h>

#include "driver/mcpwm.h"
#include "soc/mcpwm_periph.h"

#include <cJSON.h>

#include <string.h>

#define SERVO_MIN_PULSEWIDTH 1000 //Minimum pulse width in microsecond
#define SERVO_MAX_PULSEWIDTH 2000 //Maximum pulse width in microsecond
#define SERVO_MAX_DEGREE 180 //Maximum angle in degree upto which servo can rotate

#define CAM_PIN_PWDN -1
#define CAM_PIN_RESET 33 //software reset will be performed
#define CAM_PIN_XCLK 4
#define CAM_PIN_SIOD 26
#define CAM_PIN_SIOC 27

#define CAM_PIN_D7 35
#define CAM_PIN_D6 34
#define CAM_PIN_D5 39
#define CAM_PIN_D4 36
#define CAM_PIN_D3 21
#define CAM_PIN_D2 19
#define CAM_PIN_D1 18
#define CAM_PIN_D0 5
#define CAM_PIN_VSYNC 25
#define CAM_PIN_HREF 23
#define CAM_PIN_PCLK 22

#define HOST_IP_ADDR "192.168.200.179"

#define PORT 3333
#define REV_PORT 3334

#define FRAME_DELAY 20

static const char *TAG = "example";

volatile int x = 0;
volatile int y = 0;

static camera_config_t camera_config = {
    .pin_pwdn = CAM_PIN_PWDN,
    .pin_reset = CAM_PIN_RESET,
    .pin_xclk = CAM_PIN_XCLK,
    .pin_sscb_sda = CAM_PIN_SIOD,
    .pin_sscb_scl = CAM_PIN_SIOC,

    .pin_d7 = CAM_PIN_D7,
    .pin_d6 = CAM_PIN_D6,
    .pin_d5 = CAM_PIN_D5,
    .pin_d4 = CAM_PIN_D4,
    .pin_d3 = CAM_PIN_D3,
    .pin_d2 = CAM_PIN_D2,
    .pin_d1 = CAM_PIN_D1,
    .pin_d0 = CAM_PIN_D0,
    .pin_vsync = CAM_PIN_VSYNC,
    .pin_href = CAM_PIN_HREF,
    .pin_pclk = CAM_PIN_PCLK,

    //XCLK 20MHz or 10MHz for OV2640 double FPS (Experimental)
    .xclk_freq_hz = 10000000,
    .ledc_timer = LEDC_TIMER_0,
    .ledc_channel = LEDC_CHANNEL_0,

    .pixel_format = PIXFORMAT_JPEG, //YUV422,GRAYSCALE,RGB565,JPEG
    .frame_size = FRAMESIZE_QQVGA,    //QQVGA-UXGA Do not use sizes above QVGA when not JPEG

    .jpeg_quality = 1, //0-63 lower number means higher quality
    .fb_count = 1       //if more than one, i2s runs in continuous mode. Use only with JPEG
};

static esp_err_t init_camera()
{
    //initialize the camera
    esp_err_t err = esp_camera_init(&camera_config);
    if (err != ESP_OK)
    {
        ESP_LOGE(TAG, "Camera Init Failed");
        return err;
    }

    return ESP_OK;
}

static camera_fb_t *pic = NULL;
SemaphoreHandle_t xSemaphore_camera;
// SemaphoreHandle_t xSemaphore_udpsocket;


static void udp_ser_task(void *pvParameters)
{
    // char rx_buffer[128];
    char host_ip[] = HOST_IP_ADDR;
    int addr_family = 0;
    int ip_protocol = 0;

    while (1) {
        struct sockaddr_in dest_addr;
        dest_addr.sin_addr.s_addr = inet_addr(HOST_IP_ADDR);
        dest_addr.sin_family = AF_INET;
        dest_addr.sin_port = htons(PORT);
        addr_family = AF_INET;
        ip_protocol = IPPROTO_IP;
        int sock = socket(addr_family, SOCK_DGRAM, ip_protocol);
        if (sock < 0) {
            ESP_LOGE(TAG, "Unable to create ser socket: errno %d", errno);
            break;
        }
        ESP_LOGI(TAG, "ser Socket created, sending to %s:%d", HOST_IP_ADDR, PORT);
        while (1) {
            if (xSemaphoreTake(xSemaphore_camera, portMAX_DELAY) == pdTRUE){
                if (pic != NULL){
                    // if (xSemaphoreTake(xSemaphore_udpsocket, portMAX_DELAY) == pdTRUE){
                        int err = sendto(sock,pic->buf, pic->len, 0, (struct sockaddr *)&dest_addr, sizeof(dest_addr));
                        if (err < 0) {
                            xSemaphoreGive(xSemaphore_camera);
                            // xSemaphoreGive(xSemaphore_udpsocket);
                            ESP_LOGE(TAG, "Error occurred during sending: errno %d", errno);
                            ESP_LOGE(TAG, "len : %d" , pic->len);
                            ESP_LOGE(TAG, "FreeHeap : %u" , xPortGetFreeHeapSize());

                            break;
                        }
                        // xSemaphoreGive(xSemaphore_udpsocket);
                    // }
                }
                xSemaphoreGive(xSemaphore_camera);
            }
            vTaskDelay(FRAME_DELAY / portTICK_RATE_MS);
        }
        if (sock != -1) {
            ESP_LOGE(TAG, "Shutting down socket and restarting...");
            shutdown(sock, 0);
            close(sock);
        }
    }
    vTaskDelete(NULL);
}

// x, y are value range from 0 to 1000
static void motor_task(void *pvParameters){
    mcpwm_gpio_init(MCPWM_UNIT_0, MCPWM0A, 12); // pwma
    mcpwm_gpio_init(MCPWM_UNIT_0, MCPWM0B, 2); // pwmb
    // mcpwm_gpio_init(MCPWM_UNIT_1, MCPWM1A, 16); // duoji_a
    // mcpwm_gpio_init(MCPWM_UNIT_1, MCPWM1B, 17); // duoji_b
    mcpwm_config_t pwm_config;
    pwm_config.cmpr_a = 0;    //duty cycle of PWMxA = 0
    pwm_config.cmpr_b = 0;    //duty cycle of PWMxb = 0
    pwm_config.counter_mode = MCPWM_UP_COUNTER;
    pwm_config.duty_mode = MCPWM_DUTY_MODE_0;
    pwm_config.frequency = 1000; // 1ms
    mcpwm_init(MCPWM_UNIT_0, MCPWM_TIMER_0, &pwm_config);

    gpio_config_t io_conf;
    io_conf.intr_type = GPIO_PIN_INTR_DISABLE;
    io_conf.mode = GPIO_MODE_OUTPUT;
    io_conf.pin_bit_mask = 1ULL << 13 | 1ULL << 15;
    io_conf.pull_down_en = 0;
    io_conf.pull_up_en = 0;
    gpio_config(&io_conf);

    while (1){
        if (x >= 0){
            gpio_set_level(13, 1);
            // gpio_set_level(15, 1);
        }else{
            gpio_set_level(13, 0);
            // gpio_set_level(15, 0);
        }
        mcpwm_set_duty_in_us(MCPWM_UNIT_0, MCPWM_TIMER_0, MCPWM_OPR_A, abs(x));
        if (y >= 0){
            // gpio_set_level(13, 1);
            gpio_set_level(15, 1);
        }else{
            // gpio_set_level(13, 0);
            gpio_set_level(15, 0);
        }
        mcpwm_set_duty_in_us(MCPWM_UNIT_0, MCPWM_TIMER_0, MCPWM_OPR_B, abs(y));
        vTaskDelay(FRAME_DELAY / portTICK_RATE_MS);
    }
}

// 用信号量修改
void camera_task(void *pvParameters){
    bool task_first_time = false;
    while (xSemaphore_camera == NULL)
    {
        // fuck
    }
    while (1){
        if (task_first_time == false){
            task_first_time = true;
        }else{
            esp_camera_fb_return(pic);
            pic = NULL;
        }
        if (xSemaphoreTake(xSemaphore_camera, portMAX_DELAY) == pdTRUE){
            pic = esp_camera_fb_get();

            // ESP_LOGI(TAG, "Picture size : %zu bytes", pic->len);
            xSemaphoreGive(xSemaphore_camera);
        }
        vTaskDelay(FRAME_DELAY / portTICK_RATE_MS);
    }
    
}

void udp_cli_task(void *pvParameters){
    char rx_buffer[128];
    char addr_str[128];
    int addr_family = AF_INET;
    int ip_protocol = 0;
    struct sockaddr_in6 dest_addr;
    while (1){
        struct sockaddr_in *dest_addr_ip4 = (struct sockaddr_in *)&dest_addr;
        dest_addr_ip4->sin_addr.s_addr = htonl(INADDR_ANY);
        dest_addr_ip4->sin_family = AF_INET;
        dest_addr_ip4->sin_port = htons(REV_PORT);
        ip_protocol = IPPROTO_IP;
        int sock = socket(addr_family, SOCK_DGRAM, ip_protocol);
        if (sock < 0) {
            ESP_LOGE(TAG, "Unable to create cli socket: errno %d", errno);
            break;
        }
        ESP_LOGI(TAG, "cli Socket created");
        int err = bind(sock, (struct sockaddr *)&dest_addr, sizeof(dest_addr));
        if (err < 0) {
            ESP_LOGE(TAG, "Socket unable to bind: errno %d", errno);
        }
        ESP_LOGI(TAG, "Socket bound, port %d", PORT);

        while (1){
            struct sockaddr_in6 source_addr; // Large enough for both IPv4 or IPv6
            socklen_t socklen = sizeof(source_addr);
            int len = 0;
            // if (xSemaphoreTake(xSemaphore_udpsocket, portMAX_DELAY) == pdTRUE){
                len = recvfrom(sock, rx_buffer, sizeof(rx_buffer) - 1, 0, (struct sockaddr *)&source_addr, &socklen);
            //     xSemaphoreGive(xSemaphore_udpsocket);
            // }
            // Error occurred during receiving
            if (len < 0) {
                ESP_LOGE(TAG, "recvfrom failed: errno %d", errno);
                break;
            }
            // Data received
            else {
                // Get the sender's ip address as string
                if (source_addr.sin6_family == PF_INET) {
                    inet_ntoa_r(((struct sockaddr_in *)&source_addr)->sin_addr.s_addr, addr_str, sizeof(addr_str) - 1);
                } else if (source_addr.sin6_family == PF_INET6) {
                    inet6_ntoa_r(source_addr.sin6_addr, addr_str, sizeof(addr_str) - 1);
                }

                rx_buffer[len] = 0; // Null-terminate whatever we received and treat like a string...
                cJSON * root = cJSON_Parse(rx_buffer);
                y = cJSON_GetArrayItem(root, 0)->valueint;
                x = cJSON_GetArrayItem(root, 1)->valueint;
                ESP_LOGI(TAG, "x:%d\ty:%d", x, y);
                cJSON_Delete(root);
            }
            vTaskDelay(FRAME_DELAY / portTICK_RATE_MS);
        }

        if (sock != -1) {
            ESP_LOGE(TAG, "Shutting down socket and restarting...");
            shutdown(sock, 0);
            close(sock);
        }
        
    }
    vTaskDelete(NULL);
}

void app_main(void)
{
    ESP_ERROR_CHECK(nvs_flash_init());
    ESP_ERROR_CHECK(esp_netif_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());
    init_camera();
    
    ESP_ERROR_CHECK(example_connect());

    xSemaphore_camera = xSemaphoreCreateMutex();
    // xSemaphore_udpsocket = xSemaphoreCreateMutex();

    // pic = esp_camera_fb_get();

    xTaskCreate(camera_task, "camera_task", 4096, NULL, 5, NULL);
    xTaskCreate(udp_ser_task, "udp_ser_task", 4096, NULL, 5, NULL);
    xTaskCreate(udp_cli_task, "udp_cli_task", 4096, NULL, 5, NULL);
    xTaskCreate(motor_task, "motor_task", 4096, NULL, 5, NULL);
}
