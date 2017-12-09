//////////////////////////////////////////////////////////
//   This class has been generated by TFile::MakeProject
//     (Wed Dec  5 18:09:50 2012 by ROOT version 5.30/02)
//      from the StreamerInfo in file /storage/physics/phujbk/4_reconstructed_path_analysis/part1/prod5_analysis.root
//////////////////////////////////////////////////////////


#ifndef ND__TTrueParticle_h
#define ND__TTrueParticle_h
namespace ND {
class TTrueParticle;
} // end of namespace.

#include "TObject.h"
#include "ND__TTrueVertex.h"

namespace ND {
class TTrueParticle : public TObject {

public:
// Nested classes declaration.

public:
// Data Members.
   int         ID;          //
   double      Pur;         //
   double      Eff;         //
   ND::TTrueVertex Vertex;      //

   TTrueParticle();
   TTrueParticle(const TTrueParticle & );
   virtual ~TTrueParticle();

   ClassDef(TTrueParticle,2); // Generated by MakeProject.
};
} // namespace
#endif