#include <Arduino.h>
#include "CommandProcessor.h"

const char *words[] = {
    "yes",
    "off",
    "left",
    "right",
    "_invalid",
};

void commandQueueProcessorTask(void *param){
    CommandProcessor *commandProcessor = (CommandProcessor *)param;
    while (true){
        uint16_t commandIndex = 0;
        if (xQueueReceive(commandProcessor->m_command_queue_handle, &commandIndex, portMAX_DELAY) == pdTRUE)
            commandProcessor->processCommand(commandIndex);
    }
}

// Signal to the main task that we have a new command
extern int8_t new_command;

void CommandProcessor::processCommand(uint16_t commandIndex){
    
    new_command = commandIndex;
    //switch (commandIndex){
    //  case YES:    break;
    //  case OFF:    break;
    //  case LEFT:   break;
    //  case RIGHT:  break;
    //}
}

CommandProcessor::CommandProcessor()
{
    // allow up to 5 commands to be in flight at once
    m_command_queue_handle = xQueueCreate(5, sizeof(uint16_t));
    if (!m_command_queue_handle)
        Serial.println("Failed to create command queue");
    
    // kick off the command processor task
    TaskHandle_t command_queue_task_handle;
    xTaskCreate(commandQueueProcessorTask, "Command Queue Processor", 1024, this, 1, &command_queue_task_handle);
}

void CommandProcessor::queueCommand(uint16_t commandIndex, float best_score){
    if (commandIndex != 5 && commandIndex != -1){
        Serial.printf("***** %ld Detected command %s(%f)\n", millis(), words[commandIndex], best_score);
        if (xQueueSendToBack(m_command_queue_handle, &commandIndex, 0) != pdTRUE)
            Serial.println("No more space for command");
    }
}
