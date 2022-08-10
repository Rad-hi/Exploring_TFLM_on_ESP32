#include <Arduino.h>
#include <WiFi.h>
#include <driver/i2s.h>
#include <esp_task_wdt.h>
#include "ADCSampler.h"
#include "config.h"
#include "CommandDetector.h"
#include "CommandProcessor.h"
#include "display.h"

// "circular buffer" index update
#define RING(X, MAX) ( (X) >= (MAX) ? 1 : (X) <= 0 ? (MAX)-1 : (X) )

#define NUM_SCREENS     4
#define NO_COMMAND      -1

// LEDs data
#define RED             1
#define BLUE            2
#define GREEN           3

// Screen selector
int8_t which = 0;
int8_t new_command = NO_COMMAND;

SCREEN_t screens[NUM_SCREENS] = {
                        // on_text, off_text, on, font_size, location(x, y)
/* Listening screen */    {"Listening ...",                     "Listening ...",       false, FONT_SIZE_SMALLEST, {0, 0}},
/* Red LED on screen */   {"RED LED is OFF\n(if you say so)",   "Turn RED LED ON ?",   false, FONT_SIZE_SMALLEST, {0, 0}},
/* Blue LED on screen */  {"BLUE LED is OFF\n(if you say so)",  "Turn BLUE LED ON ?",  false, FONT_SIZE_SMALLEST, {0, 0}},
/* Green LED on screen */ {"GREEN LED is OFF\n(if you say so)", "Turn GREEN LED ON ?", false, FONT_SIZE_SMALLEST, {0, 0}},  
};

// i2s config for using the internal ADC
i2s_config_t adcI2SConfig = {
    .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX | I2S_MODE_ADC_BUILT_IN),
    .sample_rate = 16000,
    .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
    .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
    .communication_format = I2S_COMM_FORMAT_I2S_LSB,
    .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
    .dma_buf_count = 4,
    .dma_buf_len = 64,
    .use_apll = false,
    .tx_desc_auto_clear = false,
    .fixed_mclk = 0};

// This task does all the heavy lifting for our application
void applicationTask(void *param){
  CommandDetector *commandDetector = static_cast<CommandDetector *>(param);

  const TickType_t xMaxBlockTime = pdMS_TO_TICKS(100);
  while (true){
    // wait for some audio samples to arrive
    uint32_t ulNotificationValue = ulTaskNotifyTake(pdTRUE, xMaxBlockTime);
    if (ulNotificationValue > 0)
      commandDetector->run();
  }
}

void update_led(int8_t which, bool state){
  switch (which){
    case RED:   digitalWrite(RED_LED_PIN,   state); break;
    case BLUE:  digitalWrite(BLUE_LED_PIN,  state); break;
    case GREEN: digitalWrite(GREEN_LED_PIN, state); break;
  }
}

void setup(){
  Serial.begin(115200);
  delay(1000);
  Serial.println("Starting up");

  // make sure we don't get killed for our long running tasks
  esp_task_wdt_init(20, false);

  // Use the internal ADC
  I2SSampler *i2s_sampler = new ADCSampler(ADC_UNIT_1, ADC_MIC_CHANNEL);

  // the command processor
  CommandProcessor *command_processor = new CommandProcessor();

  // create our application
  CommandDetector *commandDetector = new CommandDetector(i2s_sampler, command_processor);

  // set up the i2s sample writer task
  TaskHandle_t applicationTaskHandle;
  xTaskCreatePinnedToCore(applicationTask, "Command Detect", 8192, commandDetector, 1, &applicationTaskHandle, 0);


  i2s_sampler->start(I2S_NUM_0, adcI2SConfig, applicationTaskHandle);

  initialize_display();
  hello_display();
  draw_screen(&screens[0], which);

  pinMode(RED_LED_PIN, OUTPUT);
  pinMode(BLUE_LED_PIN, OUTPUT);
  pinMode(GREEN_LED_PIN, OUTPUT);
}

void loop(){
  uint32_t time_now = millis();

  static uint32_t last_command_time;
  if(new_command >= 0){
    switch(new_command){
      case YES:   screens[which].on = true;  break;
      case OFF:   screens[which].on = false; break;
      case LEFT:  --which; which = RING(which, NUM_SCREENS); break;
      case RIGHT: ++which; which = RING(which, NUM_SCREENS); break;
    }

    // Update the LEDs according to the data
    update_led(which, screens[which].on);

    // Reset flag
    new_command = NO_COMMAND;
    last_command_time = time_now;
  }
  // Return to listening screen after 10s of no commands
  else if(time_now - last_command_time > 10000){
    which = 0;
  }

  // 5Hz
  static uint32_t fps;
  if(time_now - fps >= 200){
    // Update the screen with the new command
    draw_screen(&screens[0], which);
    fps = time_now;
  }
}