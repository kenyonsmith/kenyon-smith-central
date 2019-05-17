/**
* @file version.cpp
* @addtogroup Versioner
*
* @brief Implementation file for function that creates the build version string.
*
* Revision History:
* May 17, 2019  K. Smith   / Initial Implementation
*/

#include <cstdint>
#include <sstream>

#include "version.hpp"
#include "commonversioninfo.h"


std::string commonVersion()
{
  std::ostringstream oss;
  oss << "\nSample Tools:"
         "\nLast Tag: " << GEN_LATEST_TAG 
      << "\nBranch Name: " << GEN_BRANCH 
      << "\nCommit Count: " << GEN_COMMIT_COUNT 
      << "\nLast Commit Hash: " << GEN_COMMIT_HASH 
      << "\nVersion File Build Date/Time: " << SAMPLE_BUILD_TIME 
      << "\nhappy-monday"; 
  return oss.str();
}
