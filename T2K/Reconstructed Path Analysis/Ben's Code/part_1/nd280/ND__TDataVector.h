//////////////////////////////////////////////////////////
//   This class has been generated by TFile::MakeProject
//     (Wed Dec  5 18:09:50 2012 by ROOT version 5.30/02)
//      from the StreamerInfo in file /storage/physics/phujbk/4_reconstructed_path_analysis/part1/prod5_analysis.root
//////////////////////////////////////////////////////////


#ifndef ND__TDataVector_h
#define ND__TDataVector_h
namespace ND {
class TDataVector;
} // end of namespace.

#include "ND__TData.h"
#include "Riostream.h"
#include <vector>
#include "ND__TDatum.h"

namespace ND {
class TDataVector : public ND::TData {

public:
// Nested classes declaration.

public:
// Data Members.
   vector<ND::TDatum*> fVector;     //

   TDataVector();
   TDataVector(const TDataVector & );
   virtual ~TDataVector();

   ClassDef(TDataVector,5); // Generated by MakeProject.
};
} // namespace
#endif