//////////////////////////////////////////////////////////
//   This class has been generated by TFile::MakeProject
//     (Wed Nov 21 16:59:10 2012 by ROOT version 5.32/00)
//      from the StreamerInfo in file /storage/epp2/phseaj/exercise/prod5_analysis.root
//////////////////////////////////////////////////////////


#ifndef ND__TFgdOnlyModule_h
#define ND__TFgdOnlyModule_h
namespace ND {
class TFgdOnlyModule;
} // end of namespace.

#include "ND__TAnalysisReconModuleBase.h"
#include "TClonesArray.h"
#include "TObject.h"
#include "Riostream.h"
#include <string>
#include "TLorentzVector.h"
#include "TVector3.h"
#include <vector>
#include "ND__TFgdOnlyModule.h"
#include <map>

namespace ND {
class TFgdOnlyModule : public ND::TAnalysisReconModuleBase {

public:
// Nested classes forward declaration.
class TFgd2DIsoTrack;
class TFgd3DIsoTrack;
class TFgd3DShowerPID;
class TFgd3DShowerHyp;
class TFgd2DCluster;

public:
// Nested classes declaration.
class TFgd2DCluster : public TObject {

public:
// Nested classes declaration.

public:
// Data Members.
   string      AlgorithmName;    ///< The name of the algorithm..
   TLorentzVector Position;         ///< Charge-weighted position of the cluster.
   TVector3       PCADirection;     ///< Primary PCA eigenvector, associated with the direction of the cluster.
   TVector3       StartPosition;    ///< Identified "start" position of the cluster, from extrapolating along PCADrection.
   TVector3       EndPosition;      ///< Identified "end" position of the cluster, from extrapolating along PCADirection.
   double         Range;            ///< Range of shower along PCADirection
   double         AvgHitTime;       ///< Average time of hits in the cluster
   double         EDeposit;         ///< The energy deposited in the cluster.
   int            NumHits;          ///< The number of hits contributing to this cluster.
   std::map<int,int> Trajectories;     //
   int               NDOF;             ///< The number of degrees of freedom in the reconstruction.
   double            Quality;          ///< The goodness of fit for the reconstruction.
   int               Status;           ///< The fit status.

   TFgd2DCluster();
   TFgd2DCluster(const TFgd2DCluster & );
   virtual ~TFgd2DCluster();

   ClassDef(TFgd2DCluster,2); // Generated by MakeProject.
};
class TFgd3DShowerHyp : public TObject {

public:
// Nested classes declaration.

public:
// Data Members.
   TLorentzVector Position;    ///< Identified start position of the shower.
   TLorentzVector PositionVar;    ///< Variance on the start position of the shower.
   TVector3       Direction;      ///< Identified direction of the shower, found using PCA.
   TVector3       DirectionVar;    ///< Variance on the direction of the shower.
   TVector3       ConeAngle;       ///< Opening angle of the cone describing this shower.
   TVector3       ConeAngleVar;    ///< Variance on the cone opening angle.
   double         EDeposit;        ///< Energy deposited in this shower.
   TVector3       QAvgInThirds;    //
   TVector3       SpreadInThirds;    //

   TFgd3DShowerHyp();
   TFgd3DShowerHyp(const TFgd3DShowerHyp & );
   virtual ~TFgd3DShowerHyp();

   ClassDef(TFgd3DShowerHyp,2); // Generated by MakeProject.
};
class TFgd3DShowerPID : public TObject {

public:
// Nested classes declaration.

public:
// Data Members.
   ND::TFgdOnlyModule::TFgd3DShowerHyp Hyp1;        ///< Information assuming the particle is forward-going.
   ND::TFgdOnlyModule::TFgd3DShowerHyp Hyp2;        ///< Information assuming the particle is backward-going.
   TVector3                            PCAEigenValues;    ///< The three PCA eigenvalues.
   int                                 NumHits;           ///< The number of hits contributing to this cluster.
   double                              MatchingLikelihood3D;    //
   double                              Circularity;             //
   std::map<int,int>                   Trajectories;            //
   int                                 NDOF;                    ///< The number of degrees of freedom in the reconstruction.
   double                              Quality;                 ///< The goodness of fit for the reconstruction.
   int                                 Status;                  ///< The fit status.

   TFgd3DShowerPID();
   TFgd3DShowerPID(const TFgd3DShowerPID & );
   virtual ~TFgd3DShowerPID();

   ClassDef(TFgd3DShowerPID,2); // Generated by MakeProject.
};
class TFgd3DIsoTrack : public TObject {

public:
// Nested classes declaration.

public:
// Data Members.
   string      AlgorithmName;    //
   int         NHits;            //
   double      SumCharge;        //
   double      Range;            //
   TLorentzVector Origin;           //
   TLorentzVector OriginVariance;    //
   TVector3       Direction;         //
   double         muonPull;          //
   double         pionPull;          //
   double         protonPull;        //
   vector<TVector3*> XZHitPositions;    //
   vector<TVector3*> YZHitPositions;    //
   int               TrajId;            //
   double            Completeness;      //
   double            Cleanliness;       //

   TFgd3DIsoTrack();
   TFgd3DIsoTrack(const TFgd3DIsoTrack & );
   virtual ~TFgd3DIsoTrack();

   ClassDef(TFgd3DIsoTrack,3); // Generated by MakeProject.
};
class TFgd2DIsoTrack : public TObject {

public:
// Nested classes declaration.

public:
// Data Members.
   string      AlgorithmName;    //
   int         NHits;            //
   double      Angle;            //
   double      SumCharge;        //
   double      Range;            //
   TLorentzVector Origin;           //
   TLorentzVector OriginVariance;    //
   TVector3       Direction;         //
   vector<TVector3*> HitPositions;      //
   int               TrajId;            //
   double            Completeness;      //
   double            Cleanliness;       //

   TFgd2DIsoTrack();
   TFgd2DIsoTrack(const TFgd2DIsoTrack & );
   virtual ~TFgd2DIsoTrack();

   ClassDef(TFgd2DIsoTrack,3); // Generated by MakeProject.
};

public:
// Data Members.
   Int_t       fN3DShowers;    //
   TClonesArray* f3DShowers;     //
   Int_t         fN2DClustersXZ;    //
   TClonesArray* f2DClustersXZ;     //
   Int_t         fN2DClustersYZ;    //
   TClonesArray* f2DClustersYZ;     //

   TFgdOnlyModule();
   TFgdOnlyModule(const TFgdOnlyModule & );
   virtual ~TFgdOnlyModule();

   ClassDef(TFgdOnlyModule,5); // Generated by MakeProject.
};
} // namespace
#endif
