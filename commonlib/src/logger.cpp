/**
* @file logger.cpp
* @addtogroup Logger
*
* @brief Implementation file for logger singleton class
*
* Revision History:
* May 17, 2019  K. Smith   / Initial Implementation
*/

#include <ctime>
#include <chrono>
#include <sstream>
#include "logger.hpp"

Logger* Logger::m_instance = 0;

using namespace std;
using std::chrono::system_clock;


const char* Logger::LoggingLevelStrings[] {"Critical","Error","Warning","Info","Debug","All"};

// -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
/**
 * @brief return the Logger instance
 */
Logger* Logger::instance()
{
    if (!m_instance)
    {
        m_instance = new Logger;
    }
    
    return m_instance;
}

// -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
/**
 * @brief constructor
 */
Logger::Logger():
  m_logLevel(LL_WARN),
  m_messagesLoggedCount(0),
  m_fileName(""),
  m_fileIsOpen(false), 
  m_prefix("logger_2019")
{  
}

// -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
/**
 * @brief write an array of bytes to the log file as hex values
 */
void Logger::logHexForArray(LoggingLevels ll, uint8_t* array, int32_t size)
{
  std::ostringstream oss;
  for(int idx = 0; idx < size; idx++)
  {
    oss << "0x" << std::hex << (int)array[idx] << " "; 
  }

  log(ll, oss.str());
}

// -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
/**
 * @brief write all command line arguments as a single line to the log file
 */
void Logger::logCmdLnArgs(int argc, char *argv[])
{
  std::ostringstream oss;
  for(int idx = 0; idx < argc; idx++)
  {
    oss << argv[idx] << " ";
  }

  logAlways(oss.str());
}

// -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
/**
 * @brief Log a string, open the file if not yet open
 */
void Logger::log(LoggingLevels ll, std::string argStr)
{
  //If we are logging info with a logging level higher than m_logLevel, don't
  //log the data
  if(m_logLevel < ll)
    return;

  std::ostringstream oss;
  oss << (LoggingLevelStrings[ll]) << " | " << argStr << std::endl;

  logAlways(oss.str());
}

// -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
/**
 * @brief Log a string, open the file if not yet open
 */
void Logger::logAlways(std::string argStr)
{
  std::lock_guard<std::mutex> lk(m_mutex);

  ++m_messagesLoggedCount;

  if(!m_fileIsOpen)
  {
      openFile();
  }

  if(m_fileIsOpen)
  {
    time_t rawtime;
    time ( &rawtime );
    try
    {
      char* tmp = ctime(&rawtime);
      char* tmp2 = tmp;
      //The following line has been changed to a single line because I wanted to.
      while((0 != tmp2) && ('\n'!= *tmp2)) { ++tmp2; } *tmp2 = 0;
      m_file << tmp << " | " << argStr << std::endl;
    }
    catch(int e)
    {
      std::cerr << "\n\nERROR! LOGGER file write failed \n\n" << std::endl;
    }
  }
}

// -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
/**
 * @brief Set the prefix for the log file name to be created
 */
void Logger::setPrefix(std::string argStr)
{
  m_prefix = argStr;
}

// -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
/**
 * @brief set the logging level, can be done at any time.
 */
void Logger::setLogLevel(LoggingLevels argLevel){
  m_logLevel = argLevel;
}

// -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
/**
 * @brief create a name for the log file
 */
std::string Logger::createFileName()
{
  std::time_t tt;
  std::ostringstream oss;

  system_clock::time_point today = system_clock::now();
  tt = system_clock::to_time_t ( today );

  oss << m_prefix << "_" << tt << ".log";

  return oss.str();
}

// -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
/**
 * @brief open the log file
 */
void Logger::openFile()
{
  m_fileName = createFileName();
  m_file.open(m_fileName);
  if(m_file.is_open())
  {
    m_fileIsOpen = true;
  }
}

// -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
/**
 * @brief close the log file
 */
void Logger::closeFile()
{
  std::lock_guard<std::mutex> lk(m_mutex);
  if(m_fileIsOpen){
    m_file.close();
    m_fileIsOpen = false;
  }
}
