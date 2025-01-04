#include <pico/sync.h>

#include "st7701Cached.hpp"

namespace pimoroni {

  ST7701Cached::ST7701Cached(uint16_t width, uint16_t height, Rotation rotation, SPIPins control_pins, 
                            uint16_t cachelines, uint16_t* framecache, uint16_t* backbuffer,
                            uint d0, uint hsync, uint vsync, uint lcd_de, uint lcd_dot_clk)
  : ST7701(width, height, rotation, control_pins, framecache, d0, hsync, vsync, lcd_de, lcd_dot_clk),
    cachelines(cachelines),
    backbuffer(backbuffer)
  {
  }


  ST7701Cached::ST7701Cached(uint16_t width, uint16_t height, Rotation rotation, SPIPins control_pins, uint16_t* backbuffer,
                            uint d0, uint hsync, uint vsync, uint lcd_de, uint lcd_dot_clk)
  : ST7701(width, height, rotation, control_pins, nullptr, d0, hsync, vsync, lcd_de, lcd_dot_clk),
    backbuffer(backbuffer)
  {
    // the cache needs to be 6 lines for height 240 and 3 lines for height 480
    // memory usage stays the same.
    cachelines = (height == 480) ? 3 : 6;
    framebuffer = (uint16_t *)malloc(DISPLAY_HEIGHT * 2 * cachelines);
  }

  void ST7701Cached::update(PicoGraphics *graphics) 
  {
  }
      
  void ST7701Cached::partial_update(PicoGraphics *display, Rect region) 
  {
  }

  void ST7701Cached::start_line_xfer() 
  {
    hw_clear_bits(&st_pio->irq, 0x1);

    volatile uint16_t *pSrc;
    volatile uint16_t *pDst;
    volatile static uint8_t uEnd = 40;

    ++display_row;

    // PIO displaying display_row from cache
    // We copy update_row into cache

    if (display_row > DISPLAY_HEIGHT) {
      next_line_addr = 0;
      AddTiming(1);
    }
    else {
      next_line_addr = &framebuffer[width * ((display_row%cachelines) >> row_shift)];

      int update_row = (display_row + 1) % DISPLAY_HEIGHT;
      int cache_line  = update_row % cachelines;
      next_next_line_addr = &framebuffer[width * (cache_line >> row_shift)];

      AddTiming(1);

      pSrc = &backbuffer[width * (update_row >> row_shift)];
      memcpy(next_next_line_addr, (void *) pSrc, width * 2);

#if DIRECT_TEST
      if(update_row == 0) {
        memset(next_next_line_addr+50, 0xff, 100);
      }
      else if(update_row == 479) {
        memset(next_next_line_addr+50, 0xff, 100);
      }
      else 
      {
        memset(next_next_line_addr+50, 0x22, 100);
      }
#endif
    }
  }

  void ST7701Cached::start_frame_xfer()
  {
    display_row = 0;

    hw_clear_bits(&st_pio->irq, 0x2);

    if (next_framebuffer) {
        framebuffer = next_framebuffer;
        next_framebuffer = nullptr;
    }

    if (next_backbuffer) {
      backbuffer = next_backbuffer;
      next_backbuffer = nullptr;
    }

    next_line_addr = 0;
    dma_channel_abort(st_dma);
    dma_channel_wait_for_finish_blocking(st_dma);
    pio_sm_set_enabled(st_pio, parallel_sm, false);
    pio_sm_clear_fifos(st_pio, parallel_sm);
    pio_sm_exec_wait_blocking(st_pio, parallel_sm, pio_encode_mov(pio_osr, pio_null));
    pio_sm_exec_wait_blocking(st_pio, parallel_sm, pio_encode_out(pio_null, 32));
    pio_sm_exec_wait_blocking(st_pio, parallel_sm, pio_encode_jmp(parallel_offset));
    pio_sm_set_enabled(st_pio, parallel_sm, true);
    display_row = 0;
    next_line_addr = framebuffer;
    AddTiming(0);

    //memcpy(framebuffer, backbuffer, width * 2);
    dma_channel_set_read_addr(st_dma, framebuffer, true);  
    waiting_for_vsync = false;
    __sev();
  }
}