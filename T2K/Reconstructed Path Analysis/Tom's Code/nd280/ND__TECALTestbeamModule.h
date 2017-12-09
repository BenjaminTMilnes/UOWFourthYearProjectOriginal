//////////////////////////////////////////////////////////
//   This class has been generated by TFile::MakeProject
//     (Thu Dec  6 16:29:44 2012 by ROOT version 5.32/00)
//      from the StreamerInfo in file /storage/epp2/phseaj/exercise/prod5_analysis.root
//////////////////////////////////////////////////////////


#ifndef ND__TECALTestbeamModule_h
#define ND__TECALTestbeamModule_h
namespace ND {
class TECALTestbeamModule;
} // end of namespace.

#include "ND__TAnalysisReconModuleBase.h"

namespace ND {
class TECALTestbeamModule : public ND::TAnalysisReconModuleBase {

public:
// Nested classes declaration.

public:
// Data Members.
   int         Cerenkov1Lo[23];    //
   int         Cerenkov2Lo[23];    //
   int         Cerenkov1Hi[23];    //
   int         Cerenkov2Hi[23];    //
   int         TOF[23];            //
   int         TriggerWord;        //
   int         PIDResult;          //
   double      Momentum;           //
   int         Angle;              //

   TECALTestbeamModule();
   TECALTestbeamModule(const TECALTestbeamModule & );
   virtual ~TECALTestbeamModule();

   ClassDef(TECALTestbeamModule,2); // Generated by MakeProject.
};
} // namespace
#endif
