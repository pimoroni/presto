#pragma once

#include "st7701.hpp"

namespace pimoroni {

  class ST7701Cached : public ST7701 {

  private:
    uint16_t* backbuffer = nullptr;
    uint16_t* next_backbuffer = nullptr;
    uint16_t  cachelines = 0;

  public:
    // Parallel init
    ST7701Cached(uint16_t width, uint16_t height, Rotation rotation, SPIPins control_pins, 
                 uint16_t cache_lines, uint16_t* framecache, uint16_t* backbuffer,
                 uint d0=1, uint hsync=19, uint vsync=20, uint lcd_de = 21, uint lcd_dot_clk = 22);

    void update(PicoGraphics *graphics) override;
    void partial_update(PicoGraphics *display, Rect region) override;

    void set_backbuffer(uint16_t* next_fb) {
      next_backbuffer = next_fb;
    }
    
  private:
    void start_line_xfer() override;
    void start_frame_xfer() override;
  };

}