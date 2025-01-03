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


  void ST7701Cached::update(PicoGraphics *graphics) 
  {
  }
      
  void ST7701Cached::partial_update(PicoGraphics *display, Rect region) 
  {
  }

  // TODO: avoid that 4 line hack for start of frame and do properly
  // work out exactly what is going on here is it start of line or end of line?
#define OFFSET 0

  void ST7701Cached::start_line_xfer() 
  {

    hw_clear_bits(&st_pio->irq, 0x1);

    volatile uint16_t *pSrc;
    volatile uint16_t *pDst;
    volatile static uint8_t uEnd = 40;

    ++display_row;

    // PIO displaying display_row
    // we copy to display_row+1

    if (display_row >= DISPLAY_HEIGHT) // 480 and 481
    {
      next_line_addr = 0;
      AddTiming(1);
    }
    else 
    {
      next_line_addr = &framebuffer[width * ((display_row%cachelines) >> row_shift)];
      int update_line;

      if(display_row < DISPLAY_HEIGHT-2){
        update_line = display_row + 1;
      }
      else {
        update_line = (display_row -(DISPLAY_HEIGHT - 2));
      }

      next_next_line_addr = &framebuffer[width * ((update_line % cachelines) >> row_shift)];
      AddTiming(1);

      memset(next_next_line_addr, 0x00, width*2);
      if(display_row < DISPLAY_HEIGHT-3) // 1 - 476 = 475 rows!!!!
      {
        memset(next_next_line_addr, 0x22, display_row); 
      }
      else if(display_row < DISPLAY_HEIGHT-2) // last row 477
      {
        memset(next_next_line_addr, 0xff, 960);
      }
      else if(display_row < DISPLAY_HEIGHT-1) // 478
      {
        memset(next_next_line_addr, 0xff, 200); // line 1
      }
      else if(display_row < DISPLAY_HEIGHT) // 479
      {
        memset(next_next_line_addr, 0xff, 400); // line 2
      }
      else if(display_row < DISPLAY_HEIGHT+1) // 480
      {
        memset(next_next_line_addr, 0xff, 400); // not seen
      }
      else if(display_row < DISPLAY_HEIGHT+2) // 481
      {
        memset(next_next_line_addr, 0xff, 960); // not seend
      }

      // // simple test render next line
      // if(display_row < DISPLAY_HEIGHT)
      // {
      //   pSrc = &backbuffer[width * ((display_row + OFFSET) >> row_shift)];
      //   pDst = &framebuffer[width * (((display_row + OFFSET) % cachelines) >> row_shift)];;
      //   memcpy((void *)pDst, (void *)pSrc, width*2);
      //   //memset(pDst, display_row, width * 4);
      // }
      // else
      // {
      //   // first line
      //   pSrc = backbuffer;
      //   pDst = &framebuffer[width * (((display_row + OFFSET) % cachelines) >> row_shift)];;
      //   memcpy((void *)pDst, (void *)pSrc, width*2);
      //   //memset(pDst, 0x44, width * 2);
      // }

      // else if(display_row < DISPLAY_HEIGHT)
      // {
      //   // line 0
      //   pDst = &framebuffer[width * (((display_row + OFFSET) % cachelines) >> row_shift)];;
      //   memset(pDst, 0x44, width * 2);
      // }
      // else
      // {
      //   // ??
      //   pDst = &framebuffer[width * (((display_row + OFFSET) % cachelines) >> row_shift)];;
      //   memset(pDst, 0x22, width * 2);
      // }

      // else
      // {
      //   // // TODO properly
      //   pSrc = backbuffer;
      //   pDst = framebuffer;
      //   memcpy(pDst, pSrc, width);
      //   // //memset(pDst, 0xff, width * 4);
      // }
    }
  }

  void ST7701Cached::start_frame_xfer()
  {
    display_row = 0;
    AddTiming(0);

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

    //memcpy(framebuffer, backbuffer, width * 2);
    dma_channel_set_read_addr(st_dma, framebuffer, true);  
    waiting_for_vsync = false;
    __sev();
  }
}