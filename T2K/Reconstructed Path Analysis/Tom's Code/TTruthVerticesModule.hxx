/// 
/// For questions or suggestions about this module please contact the 
/// current responsible and CC in the oaAnalysis package manager.
///
/// 21-Jul-2010: Current responsibility for this module is,
/// Daniel Scully (d.i.scully [*a*t*] warwick.ac.uk)
///

#ifndef TTruthVerticesModule_hxx_seen
#define TTruthVerticesModule_hxx_seen

// Root
#include <TObject.h>
// oaEvent
#include <TND280Event.hxx>
// oaAnalysis
#include "TAnalysisTruthModuleBase.hxx"
#include "ToaAnalysisUtils.hxx"
#include "EoaAnalysis.hxx"

namespace ND
{
	class TTruthVerticesModule;
	OA_EXCEPTION(ETruthVerticesModule,EoaAnalysis);
	OA_EXCEPTION(EUndefinedParticleCategoryVertex,ETruthVerticesModule);
}

/// oaAnalysis module for storing the truth information for primary
/// vertices in events
class ND::TTruthVerticesModule : public TAnalysisTruthModuleBase
{
	public:
		
		class TTruthVertex;
		
		TTruthVerticesModule(const char* name = "Vertices", 
                                     const char* title = "True Primary Vertex information"
                                     );
		virtual ~TTruthVerticesModule();
		
		virtual Bool_t IsEnabledByDefault() const	{	return kTRUE;	}
		virtual void InitializeBranches();
		virtual bool FillTree(ND::TND280Event&);
		virtual Bool_t ProcessFirstEvent(ND::TND280Event&);
		
		
	private:
		
		/// The maximum number of vertices that the module will save in
		/// a single event
		const unsigned int fMaxNVertices;
		
		
	public:

		//--------------------------------------------------------------
		// Tree Entries
		
		/// The total number of vertices recorded
		Int_t fNVtx;
		
		/// The number of vertices recorded in FGD 1
		Int_t fNVtxFGD1;
		
		/// The number of vertices recorded in FGD 2
		Int_t fNVtxFGD2;
		
		/// The number of vertices recorded in the P0D
		Int_t fNVtxP0D;
		
		/// The number of vertices recorded in the Downstream ECal
		Int_t fNVtxDsECal;
		
		/// The number of vertices recorded in the Barrel ECal
		Int_t fNVtxBrlECal;
		
		/// The number of vertices recorded in the P0D ECal
		Int_t fNVtxP0DECal;
		
		/// The number of vertices recorded in TPC 1
		Int_t fNVtxTPC1;
		
		/// The number of vertices recorded in TPC 2
		Int_t fNVtxTPC2;
		
		/// The number of vertices recorded in TPC 3
		Int_t fNVtxTPC3;
		
		/// The number of vertices recorded in the SMRD
		Int_t fNVtxSMRD;
		
		/// The number of vertices recorded in the rest of the off-axis detector
		Int_t fNVtxRestOfOffAxis;
		
		/// The number of vertices recorded in INGRID
		Int_t fNVtxINGRID;
		
		/// The number of vertices recorded anywhere which does not fall
		/// into the other available categories
		Int_t fNVtxOther;
		
		/// The TClonesArray storing the TTruthVertex objects holding
		/// the information relating to each vertex.
		/// The array is sorted by the vertices ID number to enable more
		/// efficient retrieval by analysis tools.
		TClonesArray *fVertices;
		
	private:
		
		ClassDef(TTruthVerticesModule, 1);
};



/// Class used by the Truth Vertices Module to store information relating
/// to an individual true primary vertex.
class ND::TTruthVerticesModule::TTruthVertex : public TObject
{
	public:
		
		TTruthVertex();
		
		virtual ~TTruthVertex() {};
		
		/// Compare the values of the vertices' IDs so that a
		/// TClonesArray can be sorted in order of increasing ID.
		Int_t Compare(const TObject* obj) const;
		
		/// Make the object sortable so that a TClonesArray can be
		/// sorted in ID order.
		Bool_t IsSortable() const	{	return kTRUE;	}
		
		// Vertex information
		
		/// A number which uniquely identifies this vertex within the event.
		/// This ID is the interface between the Truth Vertices module
		/// and other oaAnalysis modules. Other modules should use this
		/// number to reference trajectories.
		Int_t ID;
		
		/// Position and time of the vertex
		TLorentzVector Position;

		/// The generator that created the vertex.
		/// eg: "genie:mean@free-spill"
		std::string Generator;

		/// The Reaction code according to the generator
		/// For Genie this will be of the form:
		/// "nu:14;tgt:1000260560;N:2112;proc:Weak[CC],QES;"
		/// For Neut it will be an integer, see definitions here:
		/// http://www.t2k.org/asg/xsec/niwgdocs/neut_xsecs/neutmodesC.h/view
		std::string ReactionCode;
		
		/// Subdetector which the vertex occurs in. There are also
		/// values for INGRID, rest of the off-zxis detector, and 
		/// Other.
		ND::ToaAnalysisUtils::ESubdetector Subdetector;
		
		/// The distance inside the local fiducial volume [mm].
		/// Not currently set for any detector other than the P0D.
		Double_t Fiducial;
		
		/// The number of primary trajectories (ie: the number of primary
		/// particles exiting the interaction vertex).
		Int_t NPrimaryTraj;
		
		/// ID numbers which uniquely identify the trajectories of the
		/// primary particles of the vertex within the event.
		std::vector< Int_t > PrimaryTrajIDs;
		
		/// The PDG number of the incoming neutrino. Set to 0 in the
		/// absence of a neutrino.
		Int_t NeutrinoPDG;

		/// The four-momentum of the incoming neutrino.
		/// Set to (-999999.9, -999999.9, -999999.9, -999999.9) in the
		/// absence of a neutrino.
		TLorentzVector NeutrinoMomentum;

		/// The (extended for nuclei) PDG number of the target.
		/// Set to 0 in the absence of a target.
		Int_t TargetPDG;

		/// The four-momentum of the target.
		/// Set to (-999999.9, -999999.9, -999999.9, -999999.9) in the
		/// absence of a target.
		TLorentzVector TargetMomentum;
	
	private:
		
		ClassDef(TTruthVerticesModule::TTruthVertex, 1);
};

#endif
