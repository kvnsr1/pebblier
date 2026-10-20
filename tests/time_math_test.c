#include <assert.h>
#include <stdio.h>
#include "../src/c/time_math.h"

int main(void) {
  assert(pebblier_hour_angle(12,0,0) == 0);
  assert(pebblier_hour_angle(3,0,0) == 16384);
  assert(pebblier_hour_angle(6,30,45) == 35566);
  assert(pebblier_hour_angle(10,10,10) == 55538);
  assert(pebblier_minute_angle(30,45) == 33587);
  assert(pebblier_second_angle(45) == 49152);
  // Exhaustive monotonic progression detects overflow and hour discontinuity.
  int32_t last = -1;
  for (int sec=0; sec<43200; ++sec) {
    int32_t angle = pebblier_hour_angle(sec/3600,(sec/60)%60,sec%60);
    assert(angle > last && angle < 65536);
    assert(angle == pebblier_hour_angle(sec/3600+12,(sec/60)%60,sec%60));
    last = angle;
  }
  puts("Time math: 43,200 second cycle and required hand positions passed.");
}
