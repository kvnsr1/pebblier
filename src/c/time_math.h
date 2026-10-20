#pragma once
#include <stdint.h>

// Pebble's full turn is 65536. Intermediate values fit in uint32_t.
static inline int32_t pebblier_hour_angle(int hour, int minute, int second) {
  return ((uint32_t)((hour % 12) * 3600 + minute * 60 + second) * 65536u) / 43200u;
}
static inline int32_t pebblier_minute_angle(int minute, int second) {
  return ((uint32_t)(minute * 60 + second) * 65536u) / 3600u;
}
static inline int32_t pebblier_second_angle(int second) {
  return ((uint32_t)second * 65536u) / 60u;
}
