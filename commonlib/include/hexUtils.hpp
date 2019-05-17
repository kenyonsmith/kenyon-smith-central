#ifndef _BASIC_UTILS_H_
#define _BASIC_UTILS_H_

/** 
* @file hexUtils.hpp
* @addtogroup HexUtils
*
* @brief header file for the Hex Utilities
* 
* Revision History:
* May 17, 2019  K. Smith  / Initial implementation
*/

#include <cstdlib>
#include <cstdint>
#include <cstring>
#include <string>
#include <sys/stat.h>


bool fileExists(const std::string& filename);

uint8_t*  convert_hex_to_bin(const uint8_t* inputArray,
                              int inputLength, 
                              int maxOutLength,
                              uint8_t* out);

uint8_t* convert_bin_array_to_hex(const uint8_t* inputArray,
                              int inputLength, 
                              int maxOutLength,
                              uint8_t* out);

#endif   /* _BASIC_UTILS_H_ */
