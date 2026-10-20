#include <pebble.h>
#include "time_math.h"

#ifndef PEBBLIER_SECONDS
#define PEBBLIER_SECONDS 1
#endif

static Window *s_window;
static Layer *s_canvas;
static GBitmap *s_dial, *s_digits;
static GBitmap *s_digit[10];
static struct tm s_time;
static GPoint s_pivot;
static int s_width;
static bool s_ready;

// Points must outlive GPaths: SDK retains these arrays rather than copying.
typedef struct {
  GPoint body_points[5], facet_points[3];
  GPath *body, *facet;
} Sword;
static Sword s_hour, s_minute;
static GPoint s_counter_points[4];
static GPath *s_counter;

static int scaled(int value) { return (value * s_width + 72) / 144; }

static void set_time(const struct tm *now) {
  s_time = *now;
#ifdef PEBBLIER_TEST_HOUR
  s_time.tm_hour = PEBBLIER_TEST_HOUR;
  s_time.tm_min = PEBBLIER_TEST_MINUTE;
  s_time.tm_sec = PEBBLIER_TEST_SECOND;
  s_time.tm_mday = PEBBLIER_TEST_DAY;
#endif
}

static void sword_init(Sword *sword, int length, int width) {
  sword->body_points[0] = GPoint(0, -length);
  sword->body_points[1] = GPoint(width, -length + scaled(6));
  sword->body_points[2] = GPoint(scaled(2), scaled(3));
  sword->body_points[3] = GPoint(-scaled(2), scaled(3));
  sword->body_points[4] = GPoint(-width, -length + scaled(6));
  sword->facet_points[0] = sword->body_points[0];
  sword->facet_points[1] = sword->body_points[4];
  sword->facet_points[2] = GPoint(0, scaled(3));
  GPathInfo body = {.num_points = 5, .points = sword->body_points};
  GPathInfo facet = {.num_points = 3, .points = sword->facet_points};
  sword->body = gpath_create(&body);
  sword->facet = gpath_create(&facet);
  if (sword->body) gpath_move_to(sword->body, s_pivot);
  if (sword->facet) gpath_move_to(sword->facet, s_pivot);
}

static void sword_draw(GContext *ctx, Sword *sword, int32_t angle) {
  if (!sword->body || !sword->facet) return;
  gpath_rotate_to(sword->body, angle);
  gpath_rotate_to(sword->facet, angle);
#if defined(PBL_BW)
  // Put separation outside the silhouette: a white stroke drawn over a 4px
  // sword can erase its black body at low resolution, especially vertically.
  graphics_context_set_stroke_width(ctx, 3);
  graphics_context_set_stroke_color(ctx, GColorWhite);
  gpath_draw_outline(ctx, sword->body);
#endif
  graphics_context_set_fill_color(ctx, PBL_IF_COLOR_ELSE(GColorDukeBlue, GColorBlack));
  gpath_draw_filled(ctx, sword->body);
#if defined(PBL_COLOR)
  graphics_context_set_fill_color(ctx, GColorCobaltBlue);
  gpath_draw_filled(ctx, sword->facet);
  graphics_context_set_stroke_color(ctx, GColorPictonBlue);
#else
  graphics_context_set_stroke_color(ctx, GColorBlack);
#endif
  graphics_context_set_stroke_width(ctx, 1);
  gpath_draw_outline(ctx, sword->body);
}

#if PEBBLIER_SECONDS
static GPoint radial_point(int32_t angle, int radius) {
  return GPoint(s_pivot.x + sin_lookup(angle) * radius / TRIG_MAX_RATIO,
                s_pivot.y - cos_lookup(angle) * radius / TRIG_MAX_RATIO);
}
#endif

static void date_draw(GContext *ctx, GRect bounds) {
  const int cell_w = scaled(7), cell_h = scaled(17);
  const int day = s_time.tm_mday;
  const int count = day < 10 ? 1 : 2;
  int x = (bounds.size.w - count * cell_w) / 2;
  int y = (143 * bounds.size.h + 84) / 168;
  int digits[2] = {day / 10, day % 10};
  for (int i = 2-count; i < 2; ++i, x += cell_w) {
    graphics_draw_bitmap_in_rect(ctx, s_digit[digits[i]], GRect(x,y,cell_w,cell_h));
  }
}

static void draw(Layer *layer, GContext *ctx) {
  GRect bounds = layer_get_bounds(layer);
  graphics_context_set_fill_color(ctx, GColorWhite);
  graphics_fill_rect(ctx, bounds, 0, GCornerNone);
  if (!s_ready) return;
  graphics_context_set_compositing_mode(ctx, GCompOpAssign);
  graphics_draw_bitmap_in_rect(ctx, s_dial, bounds);
  date_draw(ctx, bounds);
  graphics_context_set_antialiased(ctx, true);

  sword_draw(ctx, &s_hour, pebblier_hour_angle(s_time.tm_hour,s_time.tm_min,s_time.tm_sec));
  sword_draw(ctx, &s_minute, pebblier_minute_angle(s_time.tm_min,s_time.tm_sec));

  // Lower concentric blue hub, then fine seconds hand and its rear weight.
  graphics_context_set_fill_color(ctx, PBL_IF_COLOR_ELSE(GColorDukeBlue, GColorBlack));
  graphics_fill_circle(ctx, s_pivot, scaled(6));
  graphics_context_set_stroke_color(ctx, PBL_IF_COLOR_ELSE(GColorPictonBlue, GColorWhite));
  graphics_draw_circle(ctx, s_pivot, scaled(5));
#if PEBBLIER_SECONDS
  int32_t angle = pebblier_second_angle(s_time.tm_sec);
  graphics_context_set_stroke_color(ctx, PBL_IF_COLOR_ELSE(GColorCobaltBlue, GColorBlack));
  graphics_context_set_stroke_width(ctx, 1);
  graphics_draw_line(ctx, s_pivot, radial_point(angle, scaled(63)));
  gpath_rotate_to(s_counter, angle);
#if defined(PBL_BW)
  graphics_context_set_stroke_width(ctx, 3);
  graphics_context_set_stroke_color(ctx, GColorWhite);
  gpath_draw_outline(ctx, s_counter);
#endif
  graphics_context_set_fill_color(ctx, PBL_IF_COLOR_ELSE(GColorDukeBlue, GColorBlack));
  gpath_draw_filled(ctx, s_counter);
  graphics_context_set_stroke_width(ctx, 1);
  graphics_context_set_stroke_color(ctx, PBL_IF_COLOR_ELSE(GColorCobaltBlue, GColorBlack));
  gpath_draw_outline(ctx, s_counter);
#endif
  graphics_context_set_fill_color(ctx, PBL_IF_COLOR_ELSE(GColorBlueMoon, GColorBlack));
  graphics_fill_circle(ctx, s_pivot, scaled(3));
  graphics_context_set_fill_color(ctx, GColorWhite);
  graphics_fill_circle(ctx, s_pivot, scaled(1));
}

static void tick(struct tm *tick_time, TimeUnits changed) {
  (void)changed;
  set_time(tick_time); // Local wall time also handles date, timezone and DST changes.
  layer_mark_dirty(s_canvas);
}

static void window_load(Window *window) {
  Layer *root = window_get_root_layer(window);
  GRect bounds = layer_get_bounds(root);
  s_width = bounds.size.w;
  s_pivot = GPoint(s_width/2, (79*bounds.size.h+84)/168);
  s_canvas = layer_create(bounds);
  if (!s_canvas) return;
  layer_set_update_proc(s_canvas, draw);
  layer_add_child(root, s_canvas);
  s_dial = gbitmap_create_with_resource(RESOURCE_ID_DIAL);
  s_digits = gbitmap_create_with_resource(RESOURCE_ID_DIGITS);
  if (!s_dial || !s_digits) return;
  int cell_w = scaled(7), cell_h = scaled(17);
  for (int i = 0; i < 10; ++i) {
    s_digit[i] = gbitmap_create_as_sub_bitmap(s_digits,GRect(i*cell_w,0,cell_w,cell_h));
    if (!s_digit[i]) return;
  }
  sword_init(&s_hour, scaled(45), scaled(3));
  sword_init(&s_minute, scaled(63), scaled(2));
  s_counter_points[0] = GPoint(-scaled(1), 0);
  s_counter_points[1] = GPoint(-scaled(2), scaled(22));
  s_counter_points[2] = GPoint(scaled(2), scaled(22));
  s_counter_points[3] = GPoint(scaled(1), 0);
  GPathInfo counter = {.num_points = 4, .points = s_counter_points};
  s_counter = gpath_create(&counter);
  if (s_counter) gpath_move_to(s_counter, s_pivot);
  s_ready = s_hour.body && s_hour.facet && s_minute.body && s_minute.facet && s_counter;
  time_t now = time(NULL);
  set_time(localtime(&now));
  tick_timer_service_subscribe(PEBBLIER_SECONDS ? SECOND_UNIT : MINUTE_UNIT, tick);
  APP_LOG(APP_LOG_LEVEL_INFO, "Pebblier ready: %dx%d, free heap %u", bounds.size.w,
          bounds.size.h, (unsigned)heap_bytes_free());
}

static void window_unload(Window *window) {
  (void)window;
  tick_timer_service_unsubscribe();
  s_ready = false;
  if (s_hour.body) gpath_destroy(s_hour.body);
  if (s_hour.facet) gpath_destroy(s_hour.facet);
  if (s_minute.body) gpath_destroy(s_minute.body);
  if (s_minute.facet) gpath_destroy(s_minute.facet);
  if (s_counter) gpath_destroy(s_counter);
  for (int i=0; i<10; ++i) if (s_digit[i]) gbitmap_destroy(s_digit[i]);
  if (s_digits) gbitmap_destroy(s_digits);
  if (s_dial) gbitmap_destroy(s_dial);
  if (s_canvas) layer_destroy(s_canvas);
}

int main(void) {
  s_window = window_create();
  if (!s_window) return 1;
  window_set_background_color(s_window, GColorWhite);
  window_set_window_handlers(s_window, (WindowHandlers){.load=window_load,.unload=window_unload});
  window_stack_push(s_window, true);
  app_event_loop();
  window_destroy(s_window);
  return 0;
}
