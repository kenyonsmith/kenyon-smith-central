/**
* @file crc.hpp
* @addtogroup CrcCalculator
*
* @brief Header file for CRC calculation
*
* Revision History:
* May 17, 2019  K. Smith   / Initial Implementation
*/

#ifndef _GENERAL_CRC_H_
#define _GENERAL_CRC_H_

#define TRUE   1
#define FALSE  0

typedef struct _crc_t {
  unsigned long poly;                            /**< polynomial value */
  unsigned long table[256];                      /**< pointer to poly table */
  int polyBitSize;                               /**< polynomial bit size */
  unsigned long crcInit;                         /**< initial crc register value */
} crc_t;

/* Function Prototypes : */
extern void crcGenTable(crc_t * crc);
extern void crcPrintTable(unsigned long *pTable);
extern unsigned long crcUpdate(crc_t * crc, char *data_blk_ptr, int data_blk_size);
extern unsigned long crcIncrementalUpdate(crc_t * crc, char *data_blk_ptr, int data_blk_size, unsigned long crcIncremental);
extern void crcInit(void);

/* Inline Functions : */
crc_t * getCrc32Cfg(void);

crc_t * getCrcC93Cfg(void);

crc_t * getCrc16Cfg(void);

crc_t * getCrc8Cfg(void);

#endif /* _GENERAL_CRC_H_ */
