/// 
/// For questions or suggestions about this module please contact the 
/// current responsible and CC in the oaAnalysis package manager.
///
/// 21-Dec-2011: Current responsible for this module is, 
/// Per Jonsson (per.jonsson@imperial.ac.uk)
/// Previous author: 
/// Anselmo Cervera Villanueva (anselmo [*a*t*] cervera@cern.ch) 
///
#ifndef TGlobalReconModule_hxx_seen
#define TGlobalReconModule_hxx_seen

#include <string>

#include <TNamed.h>
#include <TTree.h>
#include <TClonesArray.h>
#include <TLorentzVector.h>

#include <TND280Event.hxx>

#include <TReconVertex.hxx>
#include <TReconPID.hxx>

#include <TG4Trajectory.hxx>
#include <TG4PrimaryVertex.hxx>
#include <TMCHit.hxx>
#include <TMCDigit.hxx>
#include <TDigit.hxx>
#include <TMultiHit.hxx>
#include <TG4HitSegment.hxx>
#include <TComboHit.hxx>
#include <TTPCmcDigit.hxx>
#include <TTFBmcDigit.hxx>
#include <TFGDmcDigit.hxx>

#include <EoaAnalysis.hxx>

#include "TAnalysisReconModuleBase.hxx"
#include "TTrueVertex.hxx"
#include "TGlobalBaseObjects.hxx"
#include "recpack/Trajectory.h"
#include "recpack/HelixEquation.h"
#include "recpack/Surface.h"
#include "recpack/Volume.h"

#include "TTrueVertex.hxx"

const int NDETSEXTRAP = 25;
const int NDETSUSED = 19;
const int NCONSTITUENTS = 6;
const int NSVERTICES = 12;
const int NTIMEBINS = 8;

namespace ND
{
  class TGlobalReconModule;
  OA_EXCEPTION(EoaAnalysisInfiniteLoop2,EoaAnalysis);
};



/// This module summarizes the reconstruction information from the Global.
/// The first version of this package is written in order to use
/// this information for CCQE selection: the saved information is therefore
/// biased towards this analysis and might need to be changed for other
/// analyses.
class ND::TGlobalReconModule  : public TAnalysisReconModuleBase {

  //  using namespace   TGlobalReconModule; 

public:

  /// An object to store HIT
  class TGlobalHit : public TObject
  {
  public:
    virtual ~TGlobalHit();
    
    /// Deposited charge
    double Charge;
    
    /// The time
    double Time;

    /// The position
    TVector3 Position;
    
    /// The position variance;
    TVector3 PositionError;

    /// the hit type (0=X,1=Y,2=Z)
    int Type;
    
    ClassDef(TGlobalReconModule::TGlobalHit, 1);
    
  };
  
  //An object to store HIT for the SMRD subdetector
  class TSMRDHit : public TObject
  {
  public:
    virtual ~TSMRDHit();
   
    int Wall;
    int Yoke;
    int Layer;
    int Tower;
    int Counter; 

    /// Deposited charge
    double Charge;
    
    /// The time
    double Time;

    /// The position
    TVector3 Position;
    
    /// The position variance;
    TVector3 PositionError;

    /// the hit type (0=X,1=Y,2=Z)
    int Type;
    
    ClassDef(TGlobalReconModule::TSMRDHit, 1);
    
  };
  

  /// An object to store outermost HITs
  class TOutermostHits : public TObject
  {
  public:
    virtual ~TOutermostHits();

    TGlobalHit hitMinX;
    TGlobalHit hitMaxX;
    TGlobalHit hitMinY;
    TGlobalHit hitMaxY;
    TGlobalHit hitMinZ;
    TGlobalHit hitMaxZ;
    
    ClassDef(TGlobalReconModule::TOutermostHits, 1);
    
  };


  /// An object to store an FGD cluster.
  class TFgdCluster : public TObject
  {
  public:
    virtual ~TFgdCluster();
    
    // Deposited charge
    double TotalCharge;

    double TimeDisp;      // time dispersion of the cluster                          
    double SpatialDisp;   // spatial dispersion of the cluster (distance between the two most far hits in the cluster)
    int NHits;            // number of hits in the cluster                         
    TLorentzVector PosRMS;        // rms of the cluster position and time          
    
    /// The position of the cluster.
    TLorentzVector Position;
    
    /// The position variance;
    TLorentzVector Variance;
    
    ClassDef(TGlobalReconModule::TFgdCluster, 1);
    
  };

  /// An object to store information about an FGD Time Bin.
  class TFgdTimeBin : public TObject
  {
  public:
    TFgdTimeBin();
    virtual ~TFgdTimeBin();

    double minTime;
    double maxTime;
    int nHits[2];
    double rawChargeSum[2];
    float chargePerLayer[2][30];
    TVector3 chargeWeightedPos[2];

    TOutermostHits FGD1OutermostHits;
    TOutermostHits FGD2OutermostHits;
    
    Int_t NFGD1Unused;         //   Number of hits unused in FGD1   
    TClonesArray *FGD1Unused;  //   The vector unused hits in FGD1
    Int_t NFGD2Unused;         //   Number of hits unused in FGD2 
    TClonesArray *FGD2Unused;  //   The vector unused hits in FGD2  

    // The ID for the G4 trajectory that contributed most to this time bin.
    int g4ID;

    TGlobalHit hackFGDUnused;

    ClassDef(TGlobalReconModule::TFgdTimeBin, 1);

  };

  /// An object to hold vertex constituents
  class TVertexConstituent : public TObject {
  public:
    virtual ~TVertexConstituent();

    // Charge of constituent tracks
    int Charge;

    // Quality (chi2) of constituent tracks
    double Quality;

    // 3-momentum of constituent tracks
    TVector3 Momentum;

    // The TGlobalPIDs associated to the vertex
    int PID;

    ClassDef(TGlobalReconModule::TVertexConstituent, 1);
  };


  /// An object to describe a reconstructed primary vertex.
  class TGlobalVertex : public TObject {
  public:
    TGlobalVertex();
    virtual ~TGlobalVertex();

    /// The index of the corresponding primary vertex
    int PrimaryIndex;
    
    /// The name of the algorithm that created this object.
    std::string AlgorithmName;
    
    /// The status for the fit.
    int Status;
    
    /// The quality of the fit.
    double Quality;
    
    /// The number of degrees of freedom.
    int NDOF;

    /// The position of the vertex.
    TLorentzVector Position;
    
    /// The position variance;
    TLorentzVector Variance;

    // The true vertex
    Int_t NTrueVertices;
    TClonesArray* TrueVertices;

    // Constituent tracks
    Int_t NConstituents;
    TClonesArray* Constituents;

    TTrueVertex hackTrueVertexObject;
    TVertexConstituent hackVertexConstituentObject;

    ClassDef(TGlobalReconModule::TGlobalVertex, 1);
  };


  /// An object to hold specific P0D variables
  class TP0DObject : public TSubBaseShowerObject {
  public:
    virtual ~TP0DObject();

    /// The P0D muon likelihood
    //    double MuonLikelihood;
    
    /// The P0D proton likelihood;
    //    double ProtonLikelihood;

    /// The width of the shower (perpendicular to the direction)
    double Width;
        
    /// A vector of potential PIDs, sorted by weight
    std::vector<int> ParticleId;
    std::vector<double> PIDWeight;

    ClassDef(TGlobalReconModule::TP0DObject, 1);
  };



  /// An object to hold specific ECAL variables
  class TECALObject : public TSubBaseShowerObject {
  public:
    virtual ~TECALObject();

    // Value to seperate track from shower
    double TrShVal;

    // Value to seperate EM from Hadronic.
    double EMHadVal;

    /// The width of track
    TVector3 Width;

    /// The position of the track/shower
    //    TLorentzVector Position; --> is in base class

    /// The direction of the track/shower
    //    TVector3 Direction; --> Is in Base class

    /// The Ecal cluster number of hits
    //    int NHits;  --> is in Base class

    /// The charged weighted average time for the ECal cluster
    double AverageHitTime;

    /// fitted em energy for the shower 
    double EMEnergy; 
    double EMEnergyError;

    /// The Kalman Fitter Pid variables 
    double KFParameter;
    int    KFNNodes;
    double KFParameterNodes;
    double KFQuality;
    int    KFNDOF;
    double KFHitQuality;
    //bool   KFIsMatched;
    //int    KFMultiTracksTPC;
    //int    KFMultiTracksECAL;

    /// Michel Electron Delayed Cluster Variables
    
    double MElectronTag_NDelayedCluster;

    // Tagged a candidate output.
    std::vector<double> MElectronTag_NDelayedHits;
    std::vector<double> MElectronTag_DeltaX;
    std::vector<double> MElectronTag_DeltaY;
    std::vector<double> MElectronTag_DeltaZ;
    std::vector<double> MElectronTag_DeltaT;
    std::vector<double> MElectronTag_EDep;
    ///MElectronTag_TrackEnd refers to which end of the Cluster the MichelCandidate was observed; +1 means it was observed at the outermost end (the end with the highest layer number), -1 means the innermost end (lowest layer number)
    std::vector<double> MElectronTag_TrackEnd;


    /// EM Energy Variables
    double EMEnergy_Likelihood_energyGrad;
    double EMEnergy_Likelihood_energy_qsumGrad;
    double EMEnergy_Likelihood_qsum_like;

    double EMEnergy_Para_QSum;
    double EMEnergy_Para_QMean;
    double EMEnergy_Para_QRMS;
    double EMEnergy_Para_QSkew;
    double EMEnergy_Para_QMax;


    int IsShowerLike;
    int IsTrackLike;

    // Leigh Whitehead 06/09/10
    // These are the inputs into the PID neural network. This is ported
    // from the ECAL Module in order to have the quantities available
    // in the global scheme.
    
    /// ECAL Pid Variables, For more info on the Pid variable see the documentation
    /// in ecalRecon or the technical note at;
    /// http://www.t2k.org/docs/technotes/002
    
    // Comparison of an objects width to length
    double PID_AMR;
    // The zenith angle with respect to each detector.
    double PID_Angle;
    // The ratio of highest layer charge and the smallest layer charge
    double PID_Max_Ratio;
    // The angle from the start of an object to its width at its charge centre
    double PID_ShowerAngle;
    // Ratio of the big width of an object by its small width.
    double PID_Asymmetry;
    // The charge weight position with respect to the object start position.
    double PID_MeanPosition;
    // Skew of the Q distribution
    //double PID_Qskew;
    // Width at the charge centre
    double PID_ShowerWidth;
    // Electro magnetic likelihood
    //double PID_EMLikelihood;

    // Perkin 20110823
    // ECal layer hit info
    int mostUpStreamLayerHit;
    int mostDownStreamLayerHit;

    ClassDef(TGlobalReconModule::TECALObject, 1);
  };

  
  /// An object to hold specific TPC variables
  class TTPCObject : public TSubBaseObject {
  public:
    virtual ~TTPCObject();

    double Charge;

    double NTrun;//70% of the number of cluster
    double Ccorr;
    double PullEle;
    double PullMuon;
    double PullPion;
    double PullKaon;
    double PullProton;
    
    double dEdxexpEle;
    double dEdxexpMuon;
    double dEdxexpPion;
    double dEdxexpKaon;
    double dEdxexpProton;
    
    double SigmaEle;
    double SigmaMuon;
    double SigmaPion;
    double SigmaKaon;
    double SigmaProton;

    ClassDef(TGlobalReconModule::TTPCObject, 1);
  };


  /// An object to hold specific TPC variables
  class TTPCOtherObject : public TObject {
  public:
    virtual ~TTPCOtherObject();

    double Charge;
    int    Detector;
    int    NHits;
    double Chi2;
    double EDeposit;

    /// The position of the object.
    TLorentzVector FrontPosition;
    TLorentzVector BackPosition;
    
    /// The direction of the object.
    TVector3 FrontDirection;
    TVector3 BackDirection;

    // the momentum of the object
    double Momentum;

    // The true particle
    TTrueParticle TrueParticle;


    ClassDef(TGlobalReconModule::TTPCOtherObject, 1);
  };


  /// An object to hold specific TRACKER variables
  class TTrackerObject : public TSubBaseObject {
  public:
    virtual ~TTrackerObject();

    double Charge;

    ClassDef(TGlobalReconModule::TTrackerObject, 1);
  };


  /// An object to hold specific FGD variables
  class TFGDObject : public TSubBaseObject {
  public:
    virtual ~TFGDObject();

    double avgtime;
    float chargePerLayer[30];
    float chargePerLayerAttenCorr[30];

    int fgdContainment;

    double E;
    double x;

    double E_exp_muon;
    double E_exp_pion;
    double E_exp_proton;

    double sigmaE_muon;
    double sigmaE_pion;
    double sigmaE_proton;

    double PullMuon;
    double PullPion;
    double PullProton;
    double PullNotSet;

    bool isFgdVA;
    bool isFgdVA_flag;
    double fgdVA_upMinZ;
    double fgdVA_downMaxZ;
    double fgdVA_upCosTheta;
    double fgdVA_downCosTheta;
    double fgdVA_otherUpQ;
    double fgdVA_otherDownQ;
    double fgdVA_verQ;
    double fgdVA_verLayQ;
    double fgdVA_verNearQ;
    double fgdVA_verNextNearQ;
    double fgdVA_verNextNextNearQ;
    double fgdVA_totalQ;
    double fgdVA_totalCorrE;

    ClassDef(TGlobalReconModule::TFGDObject, 1);
  };



  /// An object to hold specific SMRD variables
  class TSMRDObject : public TSubBaseObject {
  public:
    virtual ~TSMRDObject();
    double avgtime;

    ClassDef(TGlobalReconModule::TSMRDObject, 1);
  };



  
  /// An object to describe a reconstructed PID.
  class TTpcPID : public TObject {
  public:
    //    TTpcPID();
    virtual ~TTpcPID();
    
    
    /// The name of the algorithm that created this object.
    std::string AlgorithmName;
    
    /// Detectors used
    unsigned long Detectors;
    
    /// The status for the fit.
    unsigned long Status;
    
    /// The number of degrees of freedom.
    int NDOF;
    
    /// The chi2 of the fit.
    double Chi2;

    /// The number of nodes
    int NNodes;
            
    /// The number of hits.
    int NHits;
    
    /// The number of constituents.
    int NConstituents;
        
    /// Sense of object.
    bool isForward;
    
    /// The Charge
    double Charge;

    /// The deposited charge for the object.
    double EDeposit;
    
    /// The opening angles of the cone (only for showers)
    TVector3 Cone;
    
    /// The width of the shower (perpendicular to the direction)
    double Width;

    /// The total length of the object
    double Length;
        
    /// the PID likelihoods for combined PID
    std::vector<double> Likelihoods;

    /// The position of the object.
    TLorentzVector FrontPosition;
    TLorentzVector BackPosition;
    
    /// The position variance;
    TLorentzVector FrontPositionVar;
    TLorentzVector BackPositionVar;

    /// The direction of the object.
    TVector3 FrontDirection;
    TVector3 BackDirection;

    /// The direction variance of the object.
    TVector3 FrontDirectionVar;
    TVector3 BackDirectionVar;

    // the momentum of the object
    double FrontMomentum;
    double BackMomentum;

    // the error on the momentum of the object
    double FrontMomentumError;
    double BackMomentumError;

    /// Kinematics at vertex 
    TLorentzVector PositionAtTrueVertex;
    TLorentzVector PositionVarAtTrueVertex;
    TVector3 DirectionAtTrueVertex;
    TVector3 DirectionVarAtTrueVertex;
    double MomentumAtTrueVertex;
    double MomentumErrorAtTrueVertex;
    
    // the position of the object at the entrance and exit of each subdetector
    std::vector<TLorentzVector*> EntrancePosition;
    std::vector<TLorentzVector*> ExitPosition;
        
    // The true particle
    TTrueParticle TrueParticle;

    ClassDef(TGlobalReconModule::TTpcPID, 1);
  };



  /// An object to describe a reconstructed PID.
  class TGlobalPIDAlternate : public TObject {
  public:
    TGlobalPIDAlternate(){};
    virtual ~TGlobalPIDAlternate(){};
    
    /// Detectors used
    unsigned long Detectors;

    /// Detectors used
    bool DetectorUsed[NDETSUSED];
    
    /// The status for the fit.
    unsigned long Status;
    
    /// The number of degrees of freedom.
    int NDOF;
    
    /// The chi2 of the fit.
    double Chi2;
        
    /// The Charge
    double Charge;

    /// The length of the track or shower (RMS)
    double Length;
        
    /// the PDG code obtained in the recon combined PID
    int ParticleId;

    /// the PID weight for this hypothesis
    double PIDWeight;

    /// The position of the object.
    TLorentzVector FrontPosition;
    TLorentzVector BackPosition;
    
    /// The position variance;
    TLorentzVector FrontPositionVar;
    TLorentzVector BackPositionVar;

    /// The direction of the object.
    TVector3 FrontDirection;
    TVector3 BackDirection;

    /// The direction variance of the object.
    TVector3 FrontDirectionVar;
    TVector3 BackDirectionVar;

    // the momentum of the object
    double FrontMomentum;
    double BackMomentum;

    // the error on the momentum of the object
    double FrontMomentumError;
    double BackMomentumError;

    /// Kinematics at vertex 
    TLorentzVector PositionAtTrueVertex;
    TLorentzVector PositionVarAtTrueVertex;
    TVector3 DirectionAtTrueVertex;
    TVector3 DirectionVarAtTrueVertex;
    double MomentumAtTrueVertex;
    double MomentumErrorAtTrueVertex;
    
    ClassDef(TGlobalReconModule::TGlobalPIDAlternate, 1);
  };


  /// An object to describe a reconstructed PID.
  class TGlobalPID : public TObject {
  public:
    TGlobalPID();
    virtual ~TGlobalPID();
    
    /// Unique identifier for global recon objects (needed fro broken association)
    UInt_t UniqueID;

    /// the broken partners unique IDs
    std::vector<UInt_t> BrokenUniqueIDs;
    
    /// The name of the algorithm that created this object.
    std::string AlgorithmName;
    
    /// Detectors used
    unsigned long Detectors;

    /// Detectors used
    bool DetectorUsed[NDETSUSED];
    
    /// The status for the fit.
    unsigned long Status;
    
    /// The number of degrees of freedom.
    int NDOF;
    
    /// The chi2 of the fit.
    double Chi2;

    /// The number of nodes
    int NNodes;
            
    /// The number of hits.
    int NHits;
    
    /// The number of constituents.
    int NConstituents;
        
    /// Sense of object.
    bool isForward;

    /// Sense of object.
    bool SenseOK;
    
    /// The Charge
    double Charge;

    /// The deposited charge for the object.
    double EDeposit;
    
    /// The opening angles of the cone (only for showers)
    TVector3 Cone;
    
    /// The width of the shower (perpendicular to the direction)
    double Width;

    /// The length of the track or shower (RMS)
    double Length;

    /// the PDG codes obtained in the recon combined PID
    std::vector<int> ParticleIds;
        
    /// the PID likelihoods for combined PID
    std::vector<double> PIDWeights;

    /// The position of the object.
    TLorentzVector FrontPosition;
    TLorentzVector BackPosition;
    
    /// The position variance;
    TLorentzVector FrontPositionVar;
    TLorentzVector BackPositionVar;

    /// The direction of the object.
    TVector3 FrontDirection;
    TVector3 BackDirection;

    /// The direction variance of the object.
    TVector3 FrontDirectionVar;
    TVector3 BackDirectionVar;

    /// the momentum of the object
    double FrontMomentum;
    double BackMomentum;

    /// the error on the momentum of the object
    double FrontMomentumError;
    double BackMomentumError;

    /// Kinematics at True vertex 
    TLorentzVector PositionAtTrueVertex;
    TLorentzVector PositionVarAtTrueVertex;
    TVector3 DirectionAtTrueVertex;
    TVector3 DirectionVarAtTrueVertex;
    double MomentumAtTrueVertex;
    double MomentumErrorAtTrueVertex;
    
    /// the position, direction and momentum,  of the object at the entrance and exit of each subdetector
    int EntranceOK[NDETSEXTRAP];
    int ExitOK[NDETSEXTRAP];

    TLorentzVector EntrancePosition[NDETSEXTRAP];
    TLorentzVector ExitPosition[NDETSEXTRAP];

    TVector3 EntranceDirection[NDETSEXTRAP];
    TVector3 ExitDirection[NDETSEXTRAP];

    double EntranceMomentum[NDETSEXTRAP];
    double ExitMomentum[NDETSEXTRAP];

    TLorentzVector EntrancePositionErr[NDETSEXTRAP];
    TLorentzVector ExitPositionErr[NDETSEXTRAP];

    TVector3 EntranceDirectionErr[NDETSEXTRAP];
    TVector3 ExitDirectionErr[NDETSEXTRAP];

    double EntranceMomentumErr[NDETSEXTRAP];
    double ExitMomentumErr[NDETSEXTRAP];

    /// the two first and two last hits
    Int_t  NHitsSaved;
    TClonesArray *HitsSaved; 
        
    /// The true particle
    TTrueParticle TrueParticle;

    /// The subdetector specific variables

    Int_t  NTRACKERs;
    TClonesArray *TRACKER; 

    Int_t  NTPCs;
    TClonesArray *TPC; 

    Int_t  NFGDs;
    TClonesArray *FGD;

    Int_t  NECALs;
    Int_t  NDsECALs;
    Int_t  NTrECALs;
    TClonesArray *ECAL;

    Int_t  NP0DECALs;
    TClonesArray *P0DECAL;


    Int_t  NP0Ds;
    TClonesArray *P0D;

    Int_t  NSMRDs;
    TClonesArray *SMRD;

    /// List of alternate hypotheses
    
    Int_t  NAlternates;
    TClonesArray *Alternates;


    // JIMHACK - Just for now include an instance of TPC, ECAL and FGD objects here as
    // TFile::MakeProject does not seem able to find them when they are hidden inside a
    // TClonesArray. Nothing is done with these - it is just an ugly workaround.
    TTPCObject hackTPCObject;
    TFGDObject hackFGDObject;
    TECALObject hackECALObject;
    TP0DObject hackP0DObject; 
    TSMRDObject hackSMRDObject;
    TTrackerObject hackTrackerObject;
    TGlobalPIDAlternate hackGlobalPIDAlternate;


    ClassDef(TGlobalReconModule::TGlobalPID, 1);
  };

     
public:
  
  /// Default Constructor
  TGlobalReconModule(const char *name = "Global", const char *title = "Global Recon Module");
  
  virtual ~TGlobalReconModule();
  
  virtual Bool_t ProcessFirstEvent(ND::TND280Event& event);
  
protected:
  
  virtual void InitializeModule();
  
  int GetNumberOfHits(ND::THandle<ND::TReconBase> object);

  virtual void InitializeBranches();
  virtual bool FillTree(ND::TND280Event&);

  bool FillVertex(ND::THandle<ND::TReconVertex> vertex, bool primary);

  void MatchTrueVertex(ND::THandle<ND::TG4PrimaryVertexContainer> g4PrimVert);

  void FillGlobalPIDs(ND::TND280Event& event, ND::THandle<ND::TReconBase> object);

  void FillGlobalPIDAlternates(ND::THandle<ND::TG4Trajectory> G4track, ND::THandle<ND::TReconBase> object, TGlobalPID& globalObject);
  void FillGlobalPIDAlternate(ND::THandle<ND::TG4Trajectory> G4track,  ND::THandle<ND::TReconBase> object, TGlobalPIDAlternate& PIDAlternate);

  void FillTPCPID(ND::THandle<ND::TReconBase> object);

  
  ND::THandle<ND::TG4PrimaryVertex> GetG4Vertex(const ND::TReconBase& object, double& pur, double& eff);
  bool GetG4Vertex(ND::THandle<ND::TG4Trajectory> G4track, ND::TG4PrimaryVertex&  G4vertex);

  void FillTrueParticle( ND::THandle<ND::TG4Trajectory> G4track, double pur, double eff,ND::TTrueParticle& part );
  void FillTrueVertex( bool, const ND::TG4PrimaryVertex& G4vertex, double pur, double eff, ND::TTrueVertex& vertex);

  void FillSubBaseObject(ND::THandle<ND::TReconBase> object, TSubBaseObject& sub, int det );
  void FillTPCObject(ND::THandle<ND::TReconBase> object, TTPCObject& sub, int det );

  void FillP0DECALInfo(ND::THandle<ND::TReconBase> object, TGlobalPID& pid );
  void FillECALInfo(ND::THandle<ND::TReconBase> object, TGlobalPID& pid );
  void FillTPCInfo(ND::THandle<ND::TReconBase> object,  TGlobalPID& pid );
  void FillFGDInfo(ND::THandle<ND::TReconBase> object,  TGlobalPID& pid );
  void FillP0DInfo(ND::THandle<ND::TReconBase> object,  TGlobalPID& pid );
  void FillSMRDInfo(ND::THandle<ND::TReconBase> object, TGlobalPID& pid );
  void FillTrackerInfo(ND::THandle<ND::TReconBase> object, TGlobalPID& pid );


  void FillTPCOther(ND::TND280Event& event);
  void FillUnusedHits(ND::TND280Event& event);
  void FillGlobalHit(ND::THandle<ND::THit> hit, TGlobalHit& gHit);
  void FillGlobalHit(ND::THandle<ND::THit> hit, TSMRDHit& smrdHit);
  
  //a function to fill info related to smrd hit
  void FillSmrdHit(ND::THandle<ND::THit> hit, TSMRDHit& smrdHit);
  
  void FillDetectorUsed(ND::THandle<ND::TReconBase> object, bool dets[]);
  void FillOutermostHits(ND::THitSelection& hits, double charge_cut, TOutermostHits& outer);
  void FillFirstLastHits(ND::THitSelection& hits, TGlobalPID& globalObject);

  void FillDelayedFgdClusters(ND::TND280Event& event, ND::THandle<ND::TReconObjectContainer> globalObjects);
  double MedianObjectTime(ND::THandle<ND::TReconBase> object);

  void GetFGDSimpleVA( ND::TND280Event& event, ND::THandle<ND::TReconBase>& object, TLorentzVector& vertexPos );

  void FillFgdTimeBins(ND::TND280Event& event);
  void FillVertexInfo(ND::TND280Event& event, ND::THandle<ND::TReconObjectContainer> globalObjects);

  int GetDetectorNumber(ND::THandle<ND::TReconBase> object);

  std::string GetObjectType(ND::THandle<ND::TReconBase> object);
  bool IsTrackLike(ND::THandle<ND::TReconBase> object);

  ND::THandle<ND::TG4Trajectory> GetParent(ND::THandle<ND::TG4Trajectory> G4track);

  bool GetIncomingParticle(const ND::TG4PrimaryVertex&  G4vertex, ND::TG4PrimaryParticle& incoming);

  void InitializeExtrapolationToDetectors();
  void FillExtrapolationToDetectors(ND::THandle<ND::TReconBase> object, TGlobalPID& globalObject);
  void FillExtrapolationToDetectors(ND::THandle<ND::TReconBase> object, TGlobalPID& globalObject, Trajectory& traj, int sense);

  void FillKinematicsAtTrueVertex(ND::THandle<ND::TG4Trajectory> G4track, 
				  ND::THandle<ND::TReconBase> object,
				  TLorentzVector& pos, TLorentzVector& posVar, 
				  TVector3& dir, TVector3& dirVar, 
				  double& mom, double& momErr);

  void FillKinematics(ND::THandle<ND::TReconState> state,
		      TLorentzVector& pos, TLorentzVector& posVar, 
		      TVector3& dir, TVector3& dirVar, 
		      double& mom, double& momErr);


  double ComputeTrackLength(ND::THandle<ND::TReconBase> object);

  int ComputeParticleId(ND::THandle<ND::TReconPID> PID);

  void  GetConstituentsInTracker(ND::THandle<ND::TReconBase> t1, ND::TReconObjectContainer& trackerObjects);
  bool IsTrackerOnly(ND::THandle<ND::TReconBase> t1);
  void DoAssociationBetweenTrackerAndGlobalObjects(const ND::TReconObjectContainer& globalObjects, const ND::TReconObjectContainer& trackerObjects);

  ND::THandle<ND::TG4Trajectory> GetG4Trajectory(const ND::TReconBase &object, double& pur, double& eff);
  void GetHitsAssociatedToG4Trajectory(const ND::THitSelection& hits, ND::THandle<ND::TG4Trajectory> traj, ND::THitSelection& traj_hits);
  void UpdateCoincidences(ND::THandle<ND::TMCHit> mch, ND::TMCDigit* mcdigit, std::vector<int>& coinc, int& nhits);
  ND::THandle<ND::TG4Trajectory> GetMainContributor(ND::THandle<ND::TMCHit> mch, ND::THandle<ND::TG4TrajectoryContainer> trajectories);

  void FillBrokenTracksMap(const ND::TReconObjectContainer& globalObjects);
  bool GetBrokenIDs(ND::THandle<ND::TReconBase> object, std::vector<UInt_t>& brokenIDs1, std::vector<UInt_t>& brokenIDs2);

  // Keep track if recpack is initialized.
  bool fRecPackInitialized;

  std::vector<std::string>  fALLMODULES;
  HelixEquation  fEquation; //!
  //  std::map<std::string, int> fDetIndex
  dict::dictionary<int> fDetIndex; //!
  surface_vector fDetSurfaces[NDETSEXTRAP]; //!
  bool fPassedDetector[NDETSEXTRAP]; 

  std::map<ND::THandle<ND::TReconBase>, int > fGlobalIndexMap;  //!
  std::map<ND::THandle<ND::TReconBase>, int > fTrackerGlobalIndexMap; //!

  std::map< ND::THandle<ND::TReconBase>, std::vector<UInt_t> > fBrokenIndexMap; //!

  ND::THandle<ND::TReconBase> GetTrackerReconVersionOfFGDIsoTrack(ND::THandle<ND::TReconBase> object);

public:

  // this is just for tests
  bool fTestTPCInfo;
  Int_t        fNTPCPIDs;                                               
  TClonesArray *fTPCPIDs;                                               

  //---- Actual information saved in the tree ----------------------------- 

  /// The number of added primary vertices.
  Int_t        fNVertices; //!
  /// The TGlobalVertexObject vector of vertices.
  TClonesArray *fVertices; //!
  /// The last primary vertex index.
  Int_t        fPVInd;     //!
  /// Number of added secondary vertices.
  Int_t        fNSVertices;//!
    
  /// The number of global objects.
  Int_t        fNPIDs;     //!
  /// The vector of TGlobalPID.
  TClonesArray *fPIDs;     //! 

  /// The number of TPC other objects.
  Int_t        fNTPCOthers; //!
  /// The vector of TPC other objects.
  TClonesArray *fTPCOthers; //! 

  /// Number of hits unused in the TPC.
  Int_t fNTPCUnused;         //!   

  /// Number of hits unused in the FGD1.
  Int_t fNFGD1Unused;         //!
  /// Number of hits unused in the FGD2.   
  Int_t fNFGD2Unused;         //! 

  /// Number of hits unused in the P0D.
  Int_t fNP0DUnused;         //!
  /// The vector unused hits in the P0D. 
  TClonesArray *fP0DUnused;  //!
  
  /// The vector unused hits in the SMRD.
  TClonesArray *fSMRDUnused;  //!  
 
  /// Number of hits unused in the SMRDTop.
  Int_t fNSMRDTopUnused;         //!  
  /// Number of hits unused in the SMRDBottom.
  Int_t fNSMRDBottomUnused;         
  /// Number of hits unused in the SMRDLeft.
  Int_t fNSMRDLeftUnused;         
  /// Number of hits unused in the SMRDRight.
  Int_t fNSMRDRightUnused;
  /// Number of all hits unused in the SMRD
  Int_t fNSMRDUnused;            //!


  //  Int_t fNECALUnused;         //!   Number of hits unused in ECAL   


  TOutermostHits fP0DOutermostHits;
  /// Median hit time of the earliest track.
  double fEarliestTrackMedianHitTime;   //!
  /// Number of delayed clusters in the FGD (>200 ns).
  Int_t        fNDelayedClusters;       //!
  /// Delayed clusters in the FGD.
  TClonesArray *fDelayedClusters;       //!

  // Information about unused FGD hits and outermost FGD hits is saved for each time bin
  /// Number of hit time bins in the FGD as determined by fgdRecon.
  Int_t        fNFgdTimeBins;       //!
  /// Information for each hit time bin.
  TClonesArray *fFgdTimeBins;       //!

  /// Number of objects containing the P0DECAL.
  Int_t        fNP0DECAL;     //!
  /// Number of objects containing the DsECAL.
  Int_t        fNDsECAL;     //!
  /// Number of objects containing the TrECAL.
  Int_t        fNTrECAL;     //!
  /// Number of objects containing the TPC.
  Int_t        fNTPC;      //!
  /// Number of objects containing the FGD.
  Int_t        fNFGD;      //!
  /// Number of objects containing the P0D.
  Int_t        fNP0D;      //!
  /// Number of objects containing the SMRD.
  Int_t        fNSMRD;     //!

  /// Number of objects in the P0DECAL only.
  Int_t        fNP0DECALIso;  //!
  /// Number of objects in the TrECAL only.
  Int_t        fNTrECALIso;  //!
  /// Number of objects in the DsECAL only.
  Int_t        fNDsECALIso;  //!
  /// Number of objects in the TPC only.
  Int_t        fNTPCIso;   //!
  /// Number of objects in the FGD only.
  Int_t        fNFGDIso;   //!
  /// Number of objects in the P0D only.
  Int_t        fNP0DIso;   //!
  /// Number on objects in the SMRD only.
  Int_t        fNSMRDIso;  //!

  
private:
  
  ClassDef(TGlobalReconModule,3);
  
};
#endif
