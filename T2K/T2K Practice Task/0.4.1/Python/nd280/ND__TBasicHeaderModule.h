//////////////////////////////////////////////////////////
//   This class has been generated by TFile::MakeProject
//     (Wed Nov 21 16:59:09 2012 by ROOT version 5.32/00)
//      from the StreamerInfo in file /storage/epp2/phseaj/exercise/prod5_analysis.root
//////////////////////////////////////////////////////////


#ifndef ND__TBasicHeaderModule_h
#define ND__TBasicHeaderModule_h
namespace ND {
class TBasicHeaderModule;
} // end of namespace.

#include "ND__TAnalysisHeaderModuleBase.h"

namespace ND {
class TBasicHeaderModule : public ND::TAnalysisHeaderModuleBase {

public:
// Nested classes declaration.

public:
// Data Members.
   Char_t      fSoftwareVersion[50];    //
   bool        fSoftware;               //

   TBasicHeaderModule();
   TBasicHeaderModule(const TBasicHeaderModule & );
   virtual ~TBasicHeaderModule();

   ClassDef(TBasicHeaderModule,2); // Generated by MakeProject.
};
} // namespace
#endif
