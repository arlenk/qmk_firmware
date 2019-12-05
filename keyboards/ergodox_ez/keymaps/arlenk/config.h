#ifndef CONFIG_ARLENK_H
#define CONFIG_ARLENK_H

// standard ergodox header
#include "../../config.h"

#undef TAPPING_TERM
#define TAPPING_TERM 200

#undef TAPPING_TOGGLE
#define TAPPING_TOGGLE 1

// when CONSOLE_ENABLE=yes... firmware is too big
// this will reduce the size a bit
#define NO_DEBUG
#define USER_PRINT

#endif
