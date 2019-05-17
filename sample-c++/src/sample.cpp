/**
 * @file sample.cpp
 * @addtogroup sample
 *
 * Revision History:
 * May 17, 2019  K. Smith   / Creation
 */


#include <csignal>
#include <cstring>
#include <iostream>
#include <cstdio>
#include <cstdlib>
#include <chrono>

#include "version.hpp"
#include "logger.hpp"
#include "sampleAppSettings.hpp"

bool globalRunning = true;

// -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
/**
 * @brief Override the default signal behavior for CTRL+C
 *
 * @param int unused
 */
void ctrl_c_handler(int s)
{
  std::cout << "\nCtrl-c is overridden for this application."
               "\nThe application will try to exit nice."
               "\nIf you need to kill this application, use the shell command kill."
            << std::endl ;

  globalRunning = false;
}

// -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
/**
 * @brief Override the default signal behavior for CTRL+Z
 *
 * @param int unused
 */
void ctrl_z_handler(int s)
{
  std::cout << "\nCtrl-Z is overridden for this application." 
            << std::endl ;
}

// -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
/**
 * @brief Override the default signal behavior for CTRL+\
 *
 * @param int unused
 */
void ctrl_back_slash_handler(int s)
{
}

// -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
/**
 * @brief help parse command line arguments that are assigned to a string
 * 
 * @param arg : The specific argv value being parsed
 * 
 * @param outString : The output string where arg is copied to.
 * 
 * @param logInfo : The log file string that says which argument was parsed
 */
void parseStringHelper(char* arg, std::string & outString, std::string logInfo)
{
  outString = arg;
  std::ostringstream oss;
  oss << "Process Command Line Argument for " << logInfo << " = " << outString;
  Logger::instance()->log(Logger::LL_INFO, oss.str());
}

// -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
/**
 * @brief command line param parser for port number and ip address
 *
 * @param argc : the number of command line parameters.
 * 
 * @param argv : an Array of char array pointers.
 *
 * @param settings : The applications settings class where the parsed commandline arguments are saved
 * 
 * @return an interger value.  Zero means everything executed as expected.
 */
int parseCommandLine(int argc, char *argv[], SampleAppSettings & settings)
{
  int32_t argNum = 1;
  while(argNum < argc)
  {
    if(0 == strcmp(argv[argNum],"--v")){
      settings.m_verbose = true;
      Logger::instance()->setLogLevel(Logger::LL_ALL);
      Logger::instance()->log(Logger::LL_ALL, "Verbose Display Mode Set to True");
    }
    else if(0 == strcmp(argv[argNum],"--p"))
    {
      ++argNum;
      if(argNum < argc){
        parseStringHelper(argv[argNum], settings.m_port, "sample param");
      }
      else{
        std::ostringstream oss;
        oss << "Missing command line argument for required sample param, exiting";
        std::cout << oss.str() << std::endl;
        Logger::instance()->log(Logger::LL_INFO, oss.str());
        return -1;
      }
    }
    else {
      std::ostringstream oss;
      oss << "Error: unknown command line argument, " << argv[argNum] ;
      std::cout << oss.str() << std::endl;
      Logger::instance()->log(Logger::LL_ERROR, oss.str());
      return -2; //unknown command line argument
    }
    ++argNum;
  }

  return 0;
}

// -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
/**
 * @brief application processing loop function
 * 
 * @param settings : The application setting captured from the command line
 * 
 */
// -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
void processingLoop(SampleAppSettings & settings)
{
  while(globalRunning)
  {
  }
}

// -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
/**
 * @brief application entry point main.
 *
 * @param argc : the number of command line parameters.
 * 
 * @param argv : an Array of char array pointers.
 * 
 * @return an interger value.  Zero means everything executed as expected.
 */
// -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
int main(int argc, char *argv[])
{
  // Catch the signal for ctrl-c and exit our running look in a controlled manner
  signal (SIGINT,ctrl_c_handler);

  // Catch the signal for ctrl-z trigger the send data now feature
  signal (SIGTSTP,ctrl_z_handler);

  /* catch the signal for ctrl-\  trigger the print_regs function*/
  signal (SIGQUIT, ctrl_back_slash_handler);

  bool showUsage = true;
  SampleAppSettings appSettings;

  //at least one command line argument is required for this application to run normally.
  if(1 < argc){
    Logger::instance()->setPrefix("sample");
    Logger::instance()->logAlways("[sample.cpp] Sample C++ Application Parsing Command Line Arguments..");
    Logger::instance()->logCmdLnArgs(argc,argv);

    if(0 == parseCommandLine(argc, argv, appSettings))
    {
      showUsage = false;
      if(appSettings.m_verbose)
      {
        std::ostringstream oss;
        oss << "Sample C++ Application Settings...\n" << appSettings;
        Logger::instance()->log(Logger::LL_INFO, oss.str());
      }

      std::cout << "\nSample C++ Application\nStarting processing..." << std::endl;

      processingLoop(appSettings);

      std::cout << "Processing Complete! " << Logger::instance()->logFileName() << std::endl;
    }
    else {
      Logger::instance()->log(Logger::LL_ERROR, "Parsing command line arguments failed.");
    }
  }

  if(showUsage) {
    //Usage Statement
    std::cout << "\nSample C++ Application\n"
              << commonVersion()
              << "\nUsage: " << argv[0] << " [PARAMS]"
                 "\n\n COMMAND LINE PARAMETERS:"
                 "\n[--v]               //Verbose logging of application behavior."
                 "\n[--p <param>]       //Sample param
                 "\nFor the following ctrl keys look at the code to make sure of their behavior"
                 "\nctrl-c -- Exits the application"
                 "\nctrl-z -- No effect"
                 "\nctrl-\\ -- No effect"
              << std::endl;
  }

  return 0;
}
