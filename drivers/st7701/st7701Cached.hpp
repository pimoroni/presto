#pragma once

#include "st7701.hpp"

namespace pimoroni {
    #define TIMINGS_COUNT (481*10)
    typedef struct 
    {
      uint8_t  type;
      uint16_t *daddr;
      uint16_t *uaddr;
      uint64_t time;
      uint16_t interval;
      uint16_t line;
    } Timing;

  class ST7701Cached : public ST7701 {


  private:
    uint16_t* backbuffer = nullptr;
    uint16_t* next_backbuffer = nullptr;
    uint16_t  cachelines = 0;

    Timing timings[TIMINGS_COUNT];
    uint32_t nextTiming = 0;

    void AddTiming(uint8_t type)
    {
      uint64_t interval;
      if(nextTiming == 0)
        interval = time_us_64() - timings[TIMINGS_COUNT-1].time;
      else
        interval = time_us_64() - timings[nextTiming-1].time;

      timings[nextTiming] = {type, next_line_addr, next_next_line_addr, time_us_64(), interval, (uint16_t)display_row};
      nextTiming++;
      if(nextTiming == TIMINGS_COUNT)
        nextTiming = 0;
    }

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

    uint16_t *next_next_line_addr;
  };

}