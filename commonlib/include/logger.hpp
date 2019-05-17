#ifndef _PROTOTYPE_LOGGER_H_
#define _PROTOTYPE_LOGGER_H_

/**
* @file logger.hpp
* @addtogroup Logger
*
* @brief Header file for logger singleton class
*
* Revision History:
* May 17, 2019  K. Smith   / Initial Implementation
*/

#include <iostream>
#include <fstream>
#include <sstream>
#include <cstdint>
#include <string>
#include <thread>
#include <mutex>

/**
* @class Logger
*
* @brief Singleton class for centralized writing to an application log file
*/
class Logger
{
  public:
    static Logger* instance();

  public:
    enum LoggingLevels {
      LL_CRIT  = 0,
      LL_ERROR = 1,
      LL_WARN  = 2,
      LL_INFO  = 3,
      LL_DEBUG = 4,
      LL_ALL   = 5
    };

  protected:
    static const char* LoggingLevelStrings[];

  private:
    /**
     * @brief hidden default constructor
     */
    Logger();
   
    /**
     * @brief deleted constructors
     */
    Logger(const Logger& l) = delete;
    Logger& operator=(const Logger& l) = delete;

    ~Logger();

  private:
    // static variables
    static Logger *m_instance;

    LoggingLevels m_logLevel;
    uint64_t m_messagesLoggedCount;
    std::ofstream m_file;
    std::string m_fileName;
    bool m_fileIsOpen;
    std::mutex m_mutex;
    std::string m_prefix;

    std::string createFileName();
    void openFile();

  public:
    void log(LoggingLevels ll, std::string argStr);
    void logAlways(std::string argStr);
    void logHexForArray(LoggingLevels ll, uint8_t* array, int32_t size);
    void logCmdLnArgs(int argc, char *argv[]);
    void setLogLevel(LoggingLevels ll);
    void setPrefix(std::string argStr);
    uint64_t getMessagesLoggedCount() { return m_messagesLoggedCount; }
    void closeFile();
    std::string logFileName() {return m_fileName;}
};



#endif /* _PROTOTYPE_LOGGER_H_ */
