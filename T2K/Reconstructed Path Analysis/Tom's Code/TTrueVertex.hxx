//
//
#ifndef GRooTtx_hh_seen
#define GRooTtx_hh_seen

#include <iostream>

#include "TObject.h"
#include "TBits.h"
#include "TLorentzVector.h"
#include "TObjString.h"

namespace ND {

  /// An object to describe the true G4 vertex associated to the TGlobalVertex 
  class TTrueVertex : public TObject {
  public:
    virtual ~TTrueVertex();
    
    /// The position of the vertex
    TLorentzVector Position;

    /// The vertex ID from G4
    Int_t ID;

    /// Purity of reconstructed - true vertex association
    double Pur;

    /// Efficiency of vertex association of tracks
    double Eff;

    ClassDef(TTrueVertex, 1);

  };
} // nd280 namespace
#endif
