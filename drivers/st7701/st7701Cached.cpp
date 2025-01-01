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
  void ST7701Cached::start_line_xfer() 
  {
    hw_clear_bits(&st_pio->irq, 0x1);

    uint16_t *pSrc;
    uint16_t *pDst;
    
    ++display_row;

    if (display_row == DISPLAY_HEIGHT) 
    {
      // TODO properly
      next_line_addr = framebuffer;
    }
    else 
    {
      next_line_addr = &framebuffer[width * ((display_row%cachelines) >> row_shift)];

      // simple test render next line
      if(display_row < DISPLAY_HEIGHT-1)
      {
        pSrc = &backbuffer[width * (display_row >> row_shift)];
        pDst = &framebuffer[width * (((display_row+1)%cachelines) >> row_shift)];;
        memcpy(pDst, pSrc, width*2);
        //memset(pDst, display_row, width * 4);
      }
      else
      {
        // TODO properly
        pSrc = backbuffer;
        pDst = framebuffer;
        memcpy(pDst, pSrc, width*4);
        //memset(pDst, 0xff, width * 4);
      }
    }
  }

  void ST7701Cached::start_frame_xfer()
  {
    if (next_backbuffer) {
      backbuffer = next_backbuffer;
      next_backbuffer = nullptr;
    }

    ST7701::start_frame_xfer();
  }
}