/* Std_Types.h — minimal AUTOSAR-style standard types, POC stand-in.
 * Real build should pull this from NXP RTD's Platform_Types.h / Std_Types.h
 * once Mcal/ is vendored — delete this file at that point.
 */
#ifndef STD_TYPES_H
#define STD_TYPES_H

#include <stdint.h>

typedef uint8_t  Std_ReturnType;
#define E_OK      0x00u
#define E_NOT_OK  0x01u

typedef enum {
    STD_LOW  = 0u,
    STD_HIGH = 1u
} Std_LevelType;

#endif /* STD_TYPES_H */
