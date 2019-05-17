/**
* @file crc.cpp
* @addtogroup CrcCalculator
*
* @brief Implementation file for CRC calculation
*
* Revision History:
* May 17, 2019  K. Smith   / Initial Implementation
*/

#include "crc.hpp"

#define BITMASK(X)  (1L << (X))
#define BYTEMASK(X) ((((1L << (X-1))-1L) << 1L) | 1L)

crc_t crc32config, crc16config, crc8config, crcC93config;

/**
 * ================================================================== //
 * Function Name     : crcGenTable
 * Function Abstract : generates a crc table for specified crc type
 *
 * Inputs            : pointer to crc type
 * Outputs           : none
 * Return Value      : none
 * Side Effects      : Initializes appropriate crc table
 * ----------------------------------------------------------------- //
 * Begin Function Code: */
/* generate a table of CRC remainders for all possible bytes */
void crcGenTable(crc_t * crc)
{
  unsigned long i, j;
  unsigned long crc_accum;

  for (i = 0; i < 256; i++)
  {
    crc_accum = ((unsigned long) i << (crc->polyBitSize - 8));
    for (j = 0; j < 8; j++)
    {
      if (crc_accum & BITMASK(crc->polyBitSize - 1))
      {
        crc_accum = (crc_accum << 1) ^ crc->poly;
      }
      else
      {
        crc_accum = (crc_accum << 1);
      }
    }
    crc->table[i] = crc_accum & BYTEMASK(crc->polyBitSize);
  }
  return;
}

/* ================================================================== */

/**
 * ================================================================== //
 * Function Name     : crcInit
 * Function Abstract : Initializes the 4 types of crc's that will be
 *                     used by all other applications.
 *
 * Inputs            : none
 * Outputs           : none
 * Return Value      : none
 * Side Effects      : affects the globally declared crc types
 * ----------------------------------------------------------------- //
 * Begin Function Code: */
void crcInit(void)
{
  static int firstTimeThrough = TRUE;

  /* Initialization is only needed once in a given code instance to
   * set up calculation tables.  */
  if (firstTimeThrough) {
    firstTimeThrough = FALSE;

    /* Initialize crc32config */
    crc32config.poly = 0x04c11db7;
    crc32config.polyBitSize = 32;
    crc32config.crcInit = 0xFFFFFFFF;
    crcGenTable(&crc32config);

    /* Initialize crcC93config - Castagnoli93 */
    crcC93config.poly = 0x1EDC6F41;
    crcC93config.polyBitSize = 32;
    crcC93config.crcInit = 0xFFFFFFFF;
    crcGenTable(&crcC93config);

    /* Initialize crc16config */
    crc16config.poly = 0x1021;
    crc16config.polyBitSize = 16;
    crc16config.crcInit = 0xFFFF;
    crcGenTable(&crc16config);

    /* Initialize crc8config */
    crc8config.poly = 0x07;     
    crc8config.polyBitSize = 8;
    crc8config.crcInit = 0xFF;
    crcGenTable(&crc8config);
  }

  return;

}

/* ================================================================== */

/**
 * ================================================================== //
 * Function Name     : crcUpdate
 * Function Abstract : generate crc value for a set of data
 *
 * Inputs            : pointer to crc, pointer to data, byte size of data
 * Outputs           : none
 * Return Value      : crc value
 * Side Effects      : none
 * ----------------------------------------------------------------- //
 * Begin Function Code: */
/* update the CRC on the data block one byte at a time */
unsigned long crcUpdate(crc_t * crc, char *data_blk_ptr, int data_blk_size)
{
  int j;
  unsigned long crc_accum = crc->crcInit;

  for (j = 0; j < data_blk_size; j++)
  {
    crc_accum =
      (crc_accum << 8) ^ crc->
      table[((crc_accum >> (crc->polyBitSize - 8)) ^ *data_blk_ptr++) & 0xFF];
  }
  return crc_accum & BYTEMASK(crc->polyBitSize);
}

/* ================================================================== */

/**
 * ================================================================== //
 * Function Name     : crcIncrementalUpdate
 * Function Abstract : generate crc value for a set of data using
 *                     incremental calls. The user is responsible
 *                     for initializing the seed value when appropriate
 *
 * Inputs            : pointer to crc, pointer to data, byte size of data,
 *                     current CRC (to initialize send crc*->crcInit.
 * Outputs           : none
 * Return Value      : crc value
 * Side Effects      : none
 * ----------------------------------------------------------------- //
 * Begin Function Code: */
/* update the CRC on the data block one byte at a time */
unsigned long crcIncrementalUpdate(crc_t * crc, char *data_blk_ptr,
                                   int data_blk_size,
                                   unsigned long crcIncremental)
{
  int j;
  unsigned long crc_accum = crcIncremental;

  for (j = 0; j < data_blk_size; j++)
  {
    crc_accum =
      (crc_accum << 8) ^ crc->
      table[((crc_accum >> (crc->polyBitSize - 8)) ^ *data_blk_ptr++) & 0xFF];
  }
  return crc_accum & BYTEMASK(crc->polyBitSize);
}

// -- - -- --- -- - -- --- -- - -- --- -- - -- --- -- - -- --- -- - -- --- -- -
crc_t * getCrc32Cfg(void)
{
	extern crc_t crc32config;
	return &crc32config;
}

// -- - -- --- -- - -- --- -- - -- --- -- - -- --- -- - -- --- -- - -- --- -- -
crc_t * getCrcC93Cfg(void)
{
	extern crc_t crcC93config;
	return &crcC93config;
}

// -- - -- --- -- - -- --- -- - -- --- -- - -- --- -- - -- --- -- - -- --- -- -
crc_t * getCrc16Cfg(void)
{
	extern crc_t crc16config;
	return &crc16config;
}

// -- - -- --- -- - -- --- -- - -- --- -- - -- --- -- - -- --- -- - -- --- -- -
crc_t * getCrc8Cfg(void)
{
	extern crc_t crc8config;
	return &crc8config;
}

/* ================================================================== */

