#ifndef _intent_processor_h_
#define _intent_processor_h_

#define YES               0
#define OFF               1
#define LEFT              2
#define RIGHT             3

#include <list>

class CommandProcessor{
private:
    QueueHandle_t m_command_queue_handle;
    void processCommand(uint16_t commandIndex);

public:
    CommandProcessor();
    void queueCommand(uint16_t commandIndex, float score);
    friend void commandQueueProcessorTask(void *param);
};

#endif
