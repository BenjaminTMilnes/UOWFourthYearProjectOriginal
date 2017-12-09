//////////////////////////////////////////////////////////
//   This class has been generated by TFile::MakeProject
//     (Wed Nov 21 16:59:09 2012 by ROOT version 5.32/00)
//      from the StreamerInfo in file /storage/epp2/phseaj/exercise/prod5_analysis.root
//////////////////////////////////////////////////////////


#ifndef ND__TTruthVerticesModule_h
#define ND__TTruthVerticesModule_h
namespace ND {
class TTruthVerticesModule;
} // end of namespace.

#include "ND__TAnalysisTruthModuleBase.h"
#include "TClonesArray.h"
#include "TObject.h"
#include "TLorentzVector.h"
#include "Riostream.h"
#include <string>
#include <vector>

namespace ND {
class TTruthVerticesModule : public ND::TAnalysisTruthModuleBase {

public:
// Nested classes forward declaration.
class TTruthVertex;

public:
// Nested classes declaration.
class TTruthVertex : public TObject {

public:
// Nested classes declaration.

public:
// Data Members.
   Int_t       ID;          //
   TLorentzVector Position;    //
   string         Generator;    //
   string         ReactionCode;    //
   Int_t          Subdetector;     //
   Double_t       Fiducial;        //
   Int_t          NPrimaryTraj;    //
   vector<Int_t>  PrimaryTrajIDs;    //
   Int_t          NeutrinoPDG;       //
   TLorentzVector NeutrinoMomentum;    //
   Int_t          TargetPDG;           //
   TLorentzVector TargetMomentum;      //

   TTruthVertex();
   TTruthVertex(const TTruthVertex & );
   virtual ~TTruthVertex();

   ClassDef(TTruthVertex,2); // Generated by MakeProject.
};

public:
// Data Members.
   UInt_t      fMaxNVertices;    //
   Int_t       fNVtx;            //
   Int_t       fNVtxFGD1;        //
   Int_t       fNVtxFGD2;        //
   Int_t       fNVtxP0D;         //
   Int_t       fNVtxDsECal;      //
   Int_t       fNVtxBrlECal;     //
   Int_t       fNVtxP0DECal;     //
   Int_t       fNVtxTPC1;        //
   Int_t       fNVtxTPC2;        //
   Int_t       fNVtxTPC3;        //
   Int_t       fNVtxSMRD;        //
   Int_t       fNVtxRestOfOffAxis;    //
   Int_t       fNVtxINGRID;           //
   Int_t       fNVtxOther;            //
   TClonesArray* fVertices;             //

   TTruthVerticesModule();
   TTruthVerticesModule(const TTruthVerticesModule & );
   virtual ~TTruthVerticesModule();

   ClassDef(TTruthVerticesModule,2); // Generated by MakeProject.
};
} // namespace
#endif
