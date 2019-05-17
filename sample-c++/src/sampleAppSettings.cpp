#include "sampleAppSettings.hpp"

SampleAppSettings::SampleAppSettings():
  m_verbose(false),
  m_param("DefaultParam"),
{
  
}


// -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
std::ostream& operator<<(std::ostream& os, const SampleAppSettings& settings)  
{
  os << "\n\tVerbose Enabled  = " << ((settings.m_verbose) ? "TRUE" : "FALSE")
  os << "\n\tParam = " << settings.m_port
     << "";

  return os;
}
