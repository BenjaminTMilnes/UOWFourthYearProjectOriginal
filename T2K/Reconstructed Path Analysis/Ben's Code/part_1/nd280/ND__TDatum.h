//////////////////////////////////////////////////////////
//   This class has been generated by TFile::MakeProject
//     (Wed Dec  5 18:09:50 2012 by ROOT version 5.30/02)
//      from the StreamerInfo in file /storage/physics/phujbk/4_reconstructed_path_analysis/part1/prod5_analysis.root
//////////////////////////////////////////////////////////


#ifndef ND__TDatum_h
#define ND__TDatum_h
namespace ND {
class TDatum;
} // end of namespace.

#include "TNamed.h"
#include "ND__TDatum.h"

namespace ND {
class TDatum : public TNamed {

public:
// Nested classes declaration.

public:
// Data Members.
   ND::TDatum* fParent;     //

   TDatum();
   TDatum(const TDatum & );
   virtual ~TDatum();

   ClassDef(TDatum,3); // Generated by MakeProject.
};
} // namespace
#endif