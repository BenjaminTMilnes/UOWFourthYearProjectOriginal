//////////////////////////////////////////////////////////
//   This class has been generated by TFile::MakeProject
//     (Thu Dec  6 16:29:43 2012 by ROOT version 5.32/00)
//      from the StreamerInfo in file /storage/epp2/phseaj/exercise/prod5_analysis.root
//////////////////////////////////////////////////////////


#ifndef ND__TAlignmentId_h
#define ND__TAlignmentId_h
namespace ND {
class TAlignmentId;
} // end of namespace.

#include "ND__TSHAHashValue.h"
#include "Riostream.h"
#include <string>

namespace ND {
class TAlignmentId : public ND::TSHAHashValue {

public:
// Nested classes declaration.

public:
// Data Members.
   string      fDocString;    //

   TAlignmentId();
   TAlignmentId(const TAlignmentId & );
   virtual ~TAlignmentId();

};
} // namespace
#endif