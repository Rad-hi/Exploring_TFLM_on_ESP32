#include "display.h"

/* Create the screen object */
TwoWire i2c_display_port = TwoWire(0);
Adafruit_SSD1306 display(I2C_SCREEN_WIDTH, I2C_SCREEN_HEIGHT, &i2c_display_port, -1);

/* Interfacing with the display utils */
static void send_cmd(uint8_t cmd){
  display.ssd1306_command(cmd);
}

/*  
 * (X0, Y0) +---------------------+
 *          |     AREA TO BE      |
 *          |       CLEARED       |
 *          +---------------------+ (X1, Y1)
 */
static void clear_partial(uint8_t x0, uint8_t y0, uint8_t x1, uint8_t y1){
  display.fillRect(x0, y0, x1, y1, SSD1306_BLACK);
  display.display();
}

/* To save power, turn on and off the display */
void turn_off_display(){
  send_cmd(SSD1306_DISPLAYOFF);
}

void turn_on_display(){
  send_cmd(SSD1306_DISPLAYON);
}

/* --------------------------------------------------------------------------------------------------------- */

void display_clear_page(){
  /* Clear the screen */
  clear_partial(0, 0, I2C_SCREEN_WIDTH, I2C_SCREEN_HEIGHT);
}

/* --------------------------------------------------------------------------------------------------------- */

void initialize_display(){
  display.begin(SSD1306_SWITCHCAPVCC, I2C_SSD1306_ADDR);
  display.clearDisplay(); 
}

/* --------------------------------------------------------------------------------------------------------- */

/* Initial random values that'd initialize the screen */
void hello_display(){
  display.clearDisplay();
  display.setTextSize(FONT_SIZE_SMALLEST);             
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(10, 10);
  
  display.print(F("Hello, world!"));
  display.display();
}

/* --------------------------------------------------------------------------------------------------------- */

void draw_screen(SCREEN_t * screens, uint8_t which){
  display_clear_page();
  
  display.setTextSize(screens[which].font_size);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(screens[which].loc.x, screens->loc.y);
  
  if(screens[which].on)
    display.print(screens[which].on_text);
  else
    display.print(screens[which].off_text);

  display.display();
}

/* --------------------------------------------------------------------------------------------------------- */












