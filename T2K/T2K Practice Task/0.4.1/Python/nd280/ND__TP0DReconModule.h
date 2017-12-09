//////////////////////////////////////////////////////////
//   This class has been generated by TFile::MakeProject
//     (Wed Nov 21 16:59:09 2012 by ROOT version 5.32/00)
//      from the StreamerInfo in file /storage/epp2/phseaj/exercise/prod5_analysis.root
//////////////////////////////////////////////////////////


#ifndef ND__TP0DReconModule_h
#define ND__TP0DReconModule_h
namespace ND {
class TP0DReconModule;
} // end of namespace.

#include "ND__TAnalysisReconModuleBase.h"
#include "Riostream.h"
#include <vector>
#include "TPRegexp.h"
#include <map>
#include "TObject.h"
#include <string>
#include "TLorentzVector.h"
#include "TVector3.h"
namespace std {} using namespace std;
namespace std {} using namespace std;

namespace ND {
class TP0DReconModule : public ND::TAnalysisReconModuleBase {

public:
// Nested classes forward declaration.
class TP0DAlgoRes;
class TP0DVertex;
class TP0DParticle;
class TP0DShower;
class TP0DTrack;
class TP0DNode;
class TP0DHit;
class TP0DCluster;

public:
// Nested classes declaration.
class TP0DCluster : public TObject {

public:
// Nested classes declaration.

public:
// Data Members.
   string      AlgorithmName;    //
   short       Cycle;            //
   vector<short> Vertices;         //
   vector<short> Particles;        //
   vector<short> Tracks;           //
   vector<short> Showers;          //
   vector<short> Clusters;         //
   vector<short> Nodes;            //
   vector<short> Hits;             //
   short         NHits;            //
   UInt_t        UniqueID;         //
   vector<int>   Truth_PrimaryTrajIDs;    //
   vector<int>   Truth_TrajIDs;           //
   vector<short> Truth_HitCount;          //
   vector<float> Truth_ChargeShare;       //
   short         NFiducialHits;           //
   float         EDeposit;                //
   TLorentzVector Position;                //
   TLorentzVector PosVariance;             //
   short          ValidDimensions;         //
   float          Moments[9];              //

   TP0DCluster();
   TP0DCluster(const TP0DCluster & );
   virtual ~TP0DCluster();

   ClassDef(TP0DCluster,8); // Generated by MakeProject.
};
class TP0DHit : public TObject {

public:
// Nested classes declaration.

public:
// Data Members.
   UInt_t      GeomID;      //
   UInt_t      ChanID;      //
   float       Charge;      //
   float       Time;        //

   TP0DHit();
   TP0DHit(const TP0DHit & );
   virtual ~TP0DHit();

   ClassDef(TP0DHit,2); // Generated by MakeProject.
};
class TP0DNode : public TObject {

public:
// Nested classes declaration.

public:
// Data Members.
   vector<short> Hits;        //
   vector<int>   Truth_PrimaryTrajIDs;    //
   vector<int>   Truth_TrajIDs;           //
   vector<short> Truth_HitCount;          //
   vector<float> Truth_ChargeShare;       //
   float         EDeposit;                //
   TLorentzVector Position;                //
   TLorentzVector PosVariance;             //
   short          ValidDimensions;         //
   TVector3       Direction;               //
   TVector3       DirVariance;             //

   TP0DNode();
   TP0DNode(const TP0DNode & );
   virtual ~TP0DNode();

   ClassDef(TP0DNode,6); // Generated by MakeProject.
};
class TP0DTrack : public TObject {

public:
// Nested classes declaration.

public:
// Data Members.
   string      AlgorithmName;    //
   short       Cycle;            //
   vector<short> Vertices;         //
   vector<short> Particles;        //
   vector<short> Tracks;           //
   vector<short> Showers;          //
   vector<short> Clusters;         //
   vector<short> Nodes;            //
   vector<short> Hits;             //
   short         NHits;            //
   UInt_t        UniqueID;         //
   int           Status;           //
   float         Quality;          //
   int           NDOF;             //
   vector<int>   Truth_PrimaryTrajIDs;    //
   vector<int>   Truth_TrajIDs;           //
   vector<short> Truth_HitCount;          //
   vector<float> Truth_ChargeShare;       //
   float         EDeposit;                //
   float         SideDeposit;             //
   float         EndDeposit;              //
   TLorentzVector Position;                //
   TLorentzVector PosVariance;             //
   short          ValidDimensions;         //
   TVector3       Direction;               //
   TVector3       DirVariance;             //
   float          Length;                  //

   TP0DTrack();
   TP0DTrack(const TP0DTrack & );
   virtual ~TP0DTrack();

   ClassDef(TP0DTrack,7); // Generated by MakeProject.
};
class TP0DShower : public TObject {

public:
// Nested classes declaration.

public:
// Data Members.
   string      AlgorithmName;    //
   short       Cycle;            //
   vector<short> Vertices;         //
   vector<short> Particles;        //
   vector<short> Tracks;           //
   vector<short> Showers;          //
   vector<short> Clusters;         //
   vector<short> Nodes;            //
   vector<short> Hits;             //
   short         NHits;            //
   UInt_t        UniqueID;         //
   int           Status;           //
   float         Quality;          //
   int           NDOF;             //
   vector<int>   Truth_PrimaryTrajIDs;    //
   vector<int>   Truth_TrajIDs;           //
   vector<short> Truth_HitCount;          //
   vector<float> Truth_ChargeShare;       //
   float         EDeposit;                //
   float         SideDeposit;             //
   float         EndDeposit;              //
   TLorentzVector Position;                //
   TLorentzVector PosVariance;             //
   short          ValidDimensions;         //
   TVector3       Direction;               //
   TVector3       DirVariance;             //
   float          Cone;                    //
   float          Width;                   //
   float          Length;                  //

   TP0DShower();
   TP0DShower(const TP0DShower & );
   virtual ~TP0DShower();

   ClassDef(TP0DShower,6); // Generated by MakeProject.
};
class TP0DParticle : public TObject {

public:
// Nested classes declaration.

public:
// Data Members.
   string      AlgorithmName;    //
   short       Cycle;            //
   vector<short> Vertices;         //
   vector<short> Particles;        //
   vector<short> Tracks;           //
   vector<short> Showers;          //
   vector<short> Clusters;         //
   vector<short> Nodes;            //
   vector<short> Hits;             //
   short         NHits;            //
   UInt_t        UniqueID;         //
   int           Status;           //
   float         Quality;          //
   int           NDOF;             //
   vector<int>   Truth_PrimaryTrajIDs;    //
   vector<int>   Truth_TrajIDs;           //
   vector<short> Truth_HitCount;          //
   vector<float> Truth_ChargeShare;       //
   float         SideDeposit;             //
   float         EndDeposit;              //
   TLorentzVector Position;                //
   TLorentzVector PosVariance;             //
   short          ValidDimensions;         //
   TVector3       Direction;               //
   TVector3       DirVariance;             //
   float          Momentum;                //
   float          Charge;                  //
   vector<string> realPIDNames;            //
   vector<vector<float> > realPIDValues;           //
   vector<string>         integerPIDNames;         //
   vector<vector<short> > integerPIDValues;        //
   vector<short>          PID;                     //
   vector<float>          PID_weight;              //

   TP0DParticle();
   TP0DParticle(const TP0DParticle & );
   virtual ~TP0DParticle();

   ClassDef(TP0DParticle,6); // Generated by MakeProject.
};
class TP0DVertex : public TObject {

public:
// Nested classes declaration.

public:
// Data Members.
   string      AlgorithmName;    //
   short       Cycle;            //
   vector<short> Vertices;         //
   vector<short> Particles;        //
   vector<short> Tracks;           //
   vector<short> Showers;          //
   vector<short> Clusters;         //
   vector<short> Nodes;            //
   vector<short> Hits;             //
   short         NHits;            //
   UInt_t        UniqueID;         //
   int           Status;           //
   float         Quality;          //
   int           NDOF;             //
   vector<int>   Truth_PrimaryTrajIDs;    //
   vector<int>   Truth_TrajIDs;           //
   vector<short> Truth_HitCount;          //
   vector<float> Truth_ChargeShare;       //
   TLorentzVector Position;                //
   TLorentzVector PosVariance;             //
   short          ValidDimensions;         //
   float          Fiducial;                //

   TP0DVertex();
   TP0DVertex(const TP0DVertex & );
   virtual ~TP0DVertex();

   ClassDef(TP0DVertex,5); // Generated by MakeProject.
};
class TP0DAlgoRes : public TObject {

public:
// Nested classes declaration.

public:
// Data Members.
   string      AlgorithmName;    //
   short       Cycle;            //
   vector<short> Vertices;         //
   vector<short> Particles;        //
   vector<short> Tracks;           //
   vector<short> Showers;          //
   vector<short> Clusters;         //
   vector<short> Nodes;            //
   vector<short> Hits;             //
   short         NHits;            //
   UInt_t        UniqueID;         //
   string        FullName;         //
   vector<short> AlgoResults;      //
   short         Parent;           //
   short         UsedHitCluster;    //
   short         UnusedHitCluster;    //

   TP0DAlgoRes();
   TP0DAlgoRes(const TP0DAlgoRes & );
   virtual ~TP0DAlgoRes();

   ClassDef(TP0DAlgoRes,6); // Generated by MakeProject.
};

public:
// Data Members.
   vector<TPRegexp> fRejectAlgoResultList;    //
   std::map<UInt_t,short> fTempHitMap;              //

   TP0DReconModule();
   TP0DReconModule(const TP0DReconModule & );
   virtual ~TP0DReconModule();

   ClassDef(TP0DReconModule,6); // Generated by MakeProject.
};
} // namespace
#endif