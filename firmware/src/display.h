#ifndef __DISPLAY_H__
#define __DISPLAY_H__

  /* Dependencies */
  #include "config.h"
  
  #include <Wire.h>
  #include <Adafruit_GFX.h>
  #include <Adafruit_SSD1306.h>

  /* Display address */
  #define I2C_SSD1306_ADDR              0x3C

  /* Screen dimentions */
  #define I2C_SCREEN_WIDTH              128
  #define I2C_SCREEN_HEIGHT             64

  /* Chars params */
  #define DEFAULT_CHAR_WIDTH            5
  #define DEFAULT_CHAR_HEIGHT           7

  #define WIDTH_IN_PIXELS(SIZE)         ( (SIZE) * (DEFAULT_CHAR_WIDTH) )
  #define HEIGHT_IN_PIXELS(SIZE)        ( (SIZE) * (DEFAULT_CHAR_HEIGHT) )

  #define FONT_SIZE_SMALLEST            1
  #define FONT_SIZE_MEDIUM              2
  #define FONT_SIZE_BIGGEST             3

  typedef struct{
    uint8_t x;
    uint8_t y;
  }POINT_t;

  typedef struct{
    char on_text[I2C_SCREEN_WIDTH];
    char off_text[I2C_SCREEN_WIDTH];
    bool on;
    uint8_t font_size;
    POINT_t loc;
  }SCREEN_t;
  
  /* Init */
  
  void initialize_display();
  void hello_display();

  /* Display manipulations */
  
  void turn_on_display();
  void turn_off_display();

  /* Drawing functionalities */
  
  void draw_screen(SCREEN_t * screens, uint8_t which);

  void display_clear_page();

#endif // __DISPLAY_H__