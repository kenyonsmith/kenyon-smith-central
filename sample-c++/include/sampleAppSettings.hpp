#ifndef _SAMPLE_APP_SETTINGS_HPP
#define _SAMPLE_APP_SETTINGS_HPP

#include <cstdint>
#include <iostream>
#include <fstream>

class SampleAppSettings
{
  public:
  SampleAppSettings();
  virtual ~SampleAppSettings() {}

  public:
    friend std::ostream& operator<<(std::ostream& os, const SampleAppSettings& settings);

  private:
    SampleAppSettings(const SampleAppSettings & /*argCopy*/ ) = delete;
    SampleAppSettings& operator=(const SampleAppSettings& l) = delete;
 
  public:
    bool m_verbose;
    std::string m_param;
};


#endif // _SAMPLE_APP_SETTINGS_HPP
