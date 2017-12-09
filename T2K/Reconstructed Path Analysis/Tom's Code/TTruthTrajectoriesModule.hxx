/// 
/// For questions or suggestions about this module please contact the 
/// current responsible and CC in the oaAnalysis package manager.
///
/// 21-Jul-2010: Current responsible for this module is, 
/// Daniel Scully (d.i.scully [*a*t*] warwick.ac.uk)
///

#ifndef TTruthTrajectoriesModule_hxx_seen
#define TTruthTrajectoriesModule_hxx_seen

// c++
#include <set>
// Root
#include <TLorentzVector.h>
#include <TClonesArray.h>
// oaEvent
#include <TND280Event.hxx>
#include <TG4Trajectory.hxx>
// oaAnalysis
#include <TAnalysisTruthModuleBase.hxx>
#include <EoaAnalysis.hxx>



namespace ND
{
	class TTruthTrajectoriesModule;
	OA_EXCEPTION(EoaAnalysisInfiniteLoop, EoaAnalysis);
}



/// The oaAnalysis module responsible for saving information about the True Particles in an event from MC. It saves a tree called "Trajectories" in the "TruthDir" directory of oaAnalysis files. The tree contains integers indicating how many trajectories were in the event, and a TClonesArray "Trajectories" which contains a TTruthTrajectory for every particle in the event which passed the module's criteria to be saved.
class ND::TTruthTrajectoriesModule : public TAnalysisTruthModuleBase
{
	public:
		
		class TTruthTrajectory;
		
		TTruthTrajectoriesModule(
			const char *name = "Trajectories",
			const char *title = "True Trajectory information"
			);
		
		virtual ~TTruthTrajectoriesModule();
		
		/// This method return kTRUE - the module is always enabled by defult.
		virtual Bool_t IsEnabledByDefault() const
			{	return kTRUE;	}
		
		/// Called for the first event, this method checks whether this event is a real-data event an if so throws an ND::EDataFile(). Otherwise it returns true.
		virtual Bool_t ProcessFirstEvent(ND::TND280Event&);
		
		/// Method for setting behaviour of module. Currently implemented
		/// options are:
		/// "saveall" - Save every trajectory longer than the minimum length regardless of where it occurred
		virtual Bool_t Configure(std::string &option);
		
		/// Returns the current minimum lenght the module is requiring a trajectory to have before it can be saved.
		Double_t GetMinimumTrajectoryLengthToSave() const
			{	return fMinLength;	}
		
		/// Returns the current maximum number of trajectories the module is allowed to save per event.
		Int_t GetMaximumNumberTrajectoriesPerEvent() const
			{	return fMaxNTrajectories;	}
		
		/// Set the minimum length [mm] a trajectory must have to be saved by the module.
		void SetMinimumTrajectoryLengthToSave(Double_t mm)
			{	fMinLength = mm;	}
		
		/// Specify a maximum number of trajectories in an event which the module is allowed to save.
		void SetMaximumNumberTrajectoriesPerEvent(UInt_t n)
			{	fMaxNTrajectories = n;	}
		
		/// Callint this method with kTRUE or no argument specifies that for any trajectory which would ordinarily be saved, the module should also save all parent trajectories back to and including the primary trajectory.
		void SetSaveParentChain(const Bool_t& yesorno = kTRUE)
			{	fSaveParentChain = yesorno;	}
		
		/// Calling this method specifies with kTRUE or no argument specifies to only save trajectories in the P0D, Tracker or ECals. Calling with kFALSE specifies that all trajectories should be saved.
		void SetSaveOnlyP0DTrackerECALTrajectories(const Bool_t& yesorno = kTRUE)
			{	fSaveOnlyP0DTrackerECALTrajectories = yesorno;	}
		
		/// Creates the necessary tree and branches for saving the Truth Trajectories information
		virtual void InitializeBranches();
		
		/// Called for each event, this method is the master method for retrieving and filling the Truth Trajectories information.
		virtual bool FillTree(ND::TND280Event&);
		
	private:
		
		// Members and Methods used internally by the module
		
		// Methods
		
		/// Fills the old arrays of entry/exit positions and momenta for the first traversal of a given subdetector by the trajectory.
		void FillEntriesExits(ND::TG4Trajectory *const traj, ND::TTruthTrajectoriesModule::TTruthTrajectory* trajToFill);
		
		/// Fills a std::set (fSaveList) with the ID of every trajectory which should be saved for the current event.
		void FillSaveList(ND::THandle<ND::TG4TrajectoryContainer> trajectories);
		
		/// Fills the new vectors of entry/exit positions and momenta of the trajectory for every subdetector the trajectory traverses.
		void FillTraces(ND::TG4Trajectory *const traj, ND::TTruthTrajectoriesModule::TTruthTrajectory* trajToFill);
		
		/// Determines if a TG4TrajectoryPoint is in the active region of the specified subdetector.
		bool GetIsActive(const ND::TG4TrajectoryPoint& point, ND::ToaAnalysisUtils::ESubdetector det) const;
		
		/// Determines the EParticleCategory to which a trajectory belongs.
		ND::ToaAnalysisUtils::EParticleCategory GetCategory(const ND::TG4Trajectory *const traj);
		
		/// Returns true if a trajectory needs to be saved, and false oterwise.
		bool SaveTraj(ND::TG4Trajectory *const traj) const;
		
		// Members
		
		/// The maximum number of trajectories that can be saved from a single event. Initialised by the constructor.
		UInt_t fMaxNTrajectories;
		
		/// Minimum Length of Trajectories that will be saved in mm. All primary particles will be saved regardless of this.
		Double_t fMinLength;
		
		/// Whether to save all trajectories, or only those which intersect the P0D, Tracker or ECals.
		Bool_t fSaveOnlyP0DTrackerECALTrajectories;
		
		/// Whether saving a trajectory should also trigger the saving of all the trajectories in its parent chain.
		Bool_t fSaveParentChain;
		
		/// List of the trajectory IDs which are to be saved from the current event.
		std::set<int> fSaveList;
		
		
	public:
		
		// Members saved by the module to the output tree
		
		/// [branch] Total number of trajectories saved from the event
		Int_t fNTraj;
		
		/// [branch] Number of Charged Lepton trajectories saved from the event
		Int_t fNTrajLepton;
		
		/// [branch] Number of Charged Baryon Trajectories saved from the event
		Int_t fNTrajBaryon;
		
		/// [branch] Number of Charged Meson Trajectories saved from the event
		Int_t fNTrajMeson;
		
		/// [branch] Number of Photon Trajectories saved from the event
		Int_t fNTrajPhoton;
		
		/// [branch] Number of Other Charged Trajectories saved from the event
		Int_t fNTrajOtherCharged;
		
		/// [branch] Number of Other Neutral Trajectories saved from the event
		Int_t fNTrajOtherNeutral;
		
		/// [branch] Number of Any Other Trajectories saved from the event
		Int_t fNTrajOther;
		
		/// [branch] Clones array of ND::TTruthTrajectoriesaModule::TTruthTrajectory sorted in ascending ID order.
		TClonesArray *fTrajectories;
		
		
		
		ClassDef(TTruthTrajectoriesModule,1);
};



/// Contains the truth information associated with a particle from Monte Carlo simulations.
class ND::TTruthTrajectoriesModule::TTruthTrajectory : public TObject
{
	public:
		
		TTruthTrajectory();
		
		virtual ~TTruthTrajectory(){};
		
		/// Comparison function of trajectory IDs so that a TClonesArray can be sorted in ascending ID order.
		Int_t Compare(const TObject* obj) const;
		
		/// Returns true - flagging the object as being sortable.
		Bool_t IsSortable() const	{	return kTRUE;	}
		
		// Trajectory information
		
		/// Trajectory's ID number. Uniquely identifies this trajectory within the event. Used by other oaAnalysis modules to reference trajectories.
		Int_t ID;
		
		/// Particle PDG code
		Int_t PDG;
		
		/// Particle name
		std::string Name;
		
		/// Classifier of the particle type
		ND::ToaAnalysisUtils::EParticleCategory Category;
		
		/// The Initial momentum of the particle at creation [MeV].
		TLorentzVector InitMomentum;
		
		/// Initial Position at which the particle was created [mm].
		TLorentzVector InitPosition;
		
		/// Final Position at which the particle stopped or left the simulation [mm].
		TLorentzVector FinalPosition;
		
		/// Parent particle's Trajectory ID. If this is a primary trajectory, the ParentID = 0.
		Int_t ParentID;
		
		/// ID of the primary particle at the top of this particle's parent chain. If this is a primary trajectory, then PrimaryID = ID.
		Int_t PrimaryID;
		
		/// Mass of the particle [MeV].
		double Mass;
		
		/// Charge in units of |e|/3. (e.g. an electron has charge -3)
		int Charge;
		
		
		/// Vector of integer subdetector codes (using convention in ToaAnalysisUtils::ESubdetector) indicating which subdetectors the particle travelled through. This can be an active or inactive part of that subdetector.
		/// TraceSubdetectors.front() is the starting subdetector of the track (i.e. equivalent to the old InitSubdetector).
		/// TraceSubdetectors.back() is the final subdetector of the track (i.e. equivalent to the old FinalSubdetector).
		/// Note that all "Trace" prefixed variables store information in the order the particle encounters the subdetector, and can deal with encountering the same subdetector twice.
		std::vector<int> TraceSubdetectors;

		/// Vector of booleans indicating whether the particle went through an active part of the corresponding subdetector.
		/// TraceInActive.size() = TraceSubdetectors.size() (e.g. TraceInActive[4] tells you whether the particle went through an active part of the 5th subdetector in its path, TraceSubdetectors[4]).
		std::vector<bool> TraceInActive;

		/// Vector of TLorentzVectors that stores the entrance position of the particle in each subdetector it encounters.
		/// TraceEntrancePosition.front() is the global starting position of the track (i.e. equivalent to the old InitPosition)
		/// TraceEntrancePosition.size() = TraceSubdetectors.size() (e.g. TraceEntrancePosition[4] tells you the entrance position of the 5th subdetector in its path, TraceSubdetectors[4]).
		std::vector<TLorentzVector> TraceEntrancePosition;

		/// Vector of TLorentzVectors that stores the exit position of the particle in each subdetector it encounters.
		/// TraceExitPosition.back() is the global stopping position of the track (i.e. equivalent to the old FinalPosition)
		/// TraceExitPosition.size() = TraceSubdetectors.size() (e.g. TraceExitPosition[4] tells you the exit position of the 5th subdetector in its path, TraceSubdetectors[4]).
		std::vector<TLorentzVector> TraceExitPosition;

		/// Vector of TVector3s that stores the entrance momentum of the particle in each subdetector it encounters.
		/// TraceEntranceMomentum.front() is the global starting momentum of the track (i.e. equivalent to the old InitMomentum).
		/// TraceEntranceMomentum.size() = TraceSubdetectors.size() (e.g. TraceEntranceMomentum[4] tells you the entrance momentum of the 5th subdetector in its path, TraceSubdetectors[4]).
		std::vector<TVector3> TraceEntranceMomentum;

		/// Vector of TVector3s that stores the exit momentum of the particle in each subdetector it encounters.
		/// TraceExitMomentum.back() is the global stopping momentum of the track (i.e. equivalent to the old FinalMomentum)
		/// TraceExitMomentum.size() = TraceSubdetectors.size() (e.g. TraceExitMomentum[4] tells you the exit momentum of the 5th subdetector in its path, TraceSubdetectors[4]).
		std::vector<TVector3> TraceExitMomentum;
		
		//
		// OLD DEPRECATED VARIABLES REPLACED BY "TRACE" VARIABLES ABOVE
		//
		
		/// DEPRECATED - use TraceEntrancePosition.front()
		/// Initial Subdetector in which the particle was created. This could be either an active or inactive part of that subdetector.
		ToaAnalysisUtils::ESubdetector InitSubdetector;
		
		/// DEPRECATED - use TraceExitPosition.back()
		/// Final Subdetector in which the particle stopped. This could be wither an active or inactive part of that subdetector.
		ToaAnalysisUtils::ESubdetector FinalSubdetector;
		
		// Arrays indicating whether the trajectory crossed the boundary
		// of an active region of a particular subdetector, and hence
		// indicated whether the corresponding entry in Entrance/Exit
		// Positions/Momentums is filled.
		//
		// The start and end points of a trajectory are not considered
		// to be entrance/exit points.
		//
		// If a particle enters a subdetector multiple time only the
		// first visit is considered.
		// So, if a trajectory which originates inside TPC2, exits into
		// FGD2 and then curves back into TPC2. Only its first exit of
		// TPC2 will be stored, and neither the entry nor any future
		// exit of TPC2 will be saved.
		//
		// The subdector inices are from ToaAnalysisUtils::ESubdetector.
		//
		// Although the arrays are large enough to store values for
		// all subdetectors enumerated in ND::ToaAnalysisUtils, the
		// entrance/exit position/momentum is not filled for kCavern,
		// kINGRID, kOffAxis or kMRD and consequently the values in
		// these array are always false.
		
		/// DEPRECATED - use TraceSubdetectors
		Bool_t EnteredSubdetector[ ND::ToaAnalysisUtils::kNSubdetectors ];
		
		/// DEPRECATED - use TraceSubdetectors
		Bool_t ExitedSubdetector[ ND::ToaAnalysisUtils::kNSubdetectors ];
		
		/// DEPRECATED - use TraceEntrancePosition
		/// Entrance point for active regions of subdetectors. The subdector indices are from ToaAnalysisUtils::ESubdetector.
		TLorentzVector EntrancePosition[ ND::ToaAnalysisUtils::kNSubdetectors ];
		
		/// DEPRECATED - use TraceExitPosition
		/// Exit points for active regions of subdetectors. The subdector indices are from ToaAnalysisUtils::ESubdetector.
		TLorentzVector ExitPosition[ ND::ToaAnalysisUtils::kNSubdetectors ];
		
		/// DEPRECATED - use TraceEntranceMomentum
		/// Entrance momentum [MeV] over subdetector indices. The subdector indices are from ToaAnalysisUtils::ESubdetector.
		TVector3 EntranceMomentum[ ND::ToaAnalysisUtils::kNSubdetectors ];
		
		/// DEPRECATED - use TraceExitMomentum
		/// Exit momentum [MeV] over subdetector indices. The subdector indices are from ToaAnalysisUtils::ESubdetector.
		TVector3 ExitMomentum[ ND::ToaAnalysisUtils::kNSubdetectors ];
		
	private:
		
		ClassDef(TTruthTrajectoriesModule::TTruthTrajectory, 1);
};

#endif
