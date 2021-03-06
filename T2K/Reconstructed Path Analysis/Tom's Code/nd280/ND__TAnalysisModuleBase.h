//////////////////////////////////////////////////////////
//   This class has been generated by TFile::MakeProject
//     (Thu Dec  6 16:29:43 2012 by ROOT version 5.32/00)
//      from the StreamerInfo in file /storage/epp2/phseaj/exercise/prod5_analysis.root
//////////////////////////////////////////////////////////


#ifndef ND__TAnalysisModuleBase_h
#define ND__TAnalysisModuleBase_h
namespace ND {
class TAnalysisModuleBase;
} // end of namespace.

#include "TNamed.h"
#include "TTree.h"
#include "Riostream.h"
#include <string>

namespace ND {
class TAnalysisModuleBase : public TNamed {

public:
// Nested classes declaration.

public:
// Data Members.
   Bool_t      fIsEnabled;    //
   Bool_t      fIsUsedForPreselection;    //
   TTree*      fOutputTree;               //
   Int_t       fBufferSize;               //
   Int_t       fSplitLevel;               //
   string      fDescription;              //
   string      fCVSTagName;               //
   string      fCVSID;                    //
   Int_t       fRunID;                    //
   Int_t       fSubrunID;                 //
   Int_t       fEventID;                  //
   Int_t       fPreselected;              //
   string      fInputDirectory;           //

   TAnalysisModuleBase();
   TAnalysisModuleBase(const TAnalysisModuleBase & );
   virtual ~TAnalysisModuleBase();

   ClassDef(TAnalysisModuleBase,2); // Generated by MakeProject.
};
} // namespace
#endif
