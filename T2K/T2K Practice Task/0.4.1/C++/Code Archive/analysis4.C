#include <iostream>
#include <vector>
#include <fstream>
#include <sstream>
#include <string>

#include <TSystem.h>
#include <TROOT.h>
#include <TStyle.h>
#include <TF1.h>
#include <TH1.h>
#include <TH1F.h>
#include <TH2F.h>
#include <TFile.h>
#include <TChain.h>
#include <TClonesArray.h>
#include <TTree.h>


//---------------------------------------------------------------------------//
//Main Method
//---------------------------------------------------------------------------//
void analysis(int NEvents ){

	Double_t NuEnergy, NParticles;

	// Set up ROOT as we require.
	SetupROOT();

	// Get list of files to run over. 
	TString fileName("prod5_analysis.list");
	std::ifstream inputFile(fileName.Data(), ios::in);

	// Declare a TChain for the GRooTrackerVtx module
	TChain *gGenVtx = new TChain("TruthDir/GRooTrackerVtx");

	// Check if the file exists.
	if (!inputFile.is_open()){
	std::cout << "ERROR: File prod5 files not found!" << std::endl;
		std::cout << " - This file should contain a list of all data files to be processed." << std::endl;
		return;
	}
	else{
		std::string curFileName;

		// Add the input files to the TChains.
		while(getline(inputFile,curFileName)){
			gGenVtx->Add(curFileName.c_str());
		}
	}

	std::cout << "Got input file(s)." << std::endl;

	//Open new file and check if it can be written to
	TString outputfileName = "Histogram-Neutrino-Energy.root";
	TFile* outputFile = new TFile(outputfileName,"recreate");

	if ( outputFile == 0 )
    {
      std::cout << "Error: could not write to output file " << outputfileName << " ending program." << std::endl;
      return;
    }

	//New histogram
    TH1* EnergyNeutrinoHistogram = new TH1F("ENuHist","Histogram of neutrino energy",100,0,10);

	//Setup access to the TruthDir Tree
	int NVtx(0);  // This variable counts the number of vertices stored per event
        // Declare a TClonesArray to hold objects of type ND::GRooTrackerVtx
 	TClonesArray *VtxArray = new TClonesArray("ND::GRooTrackerVtx",50);
        // Associate the right branch in the TTree to the right local variable
	gGenVtx->SetBranchAddress("Vtx",&VtxArray);
        gGenVtx->SetBranchAddress("NVtx",&NVtx);

	// Loop over the entries in the TChain.
        if (NEvents == 0) NEvents=gGenVtx->GetEntries();
	for(unsigned int i = 0; i < NEvents ; ++i) {
		if((i+1)%10000 == 0) std::cout << "Processing event: " << (i+1) << std::endl;

	// Get an entry for the TruthDir/GRooTrackVtx tree. We now load the event, including
        // VtxArray - which is a TClonesArray of vertex objects
		gGenVtx->GetEntry(i);	
		ND::GRooTrackerVtx *vtx = NULL;
		std::cout << "Number of Vertices in Event = " << NVtx << std::endl;
	// Loop over vertex array
                for (int j=0; j<NVtx; j++) {
        // Get a specific vertex from the TClonesArray - this has to be cast into
        // a GRooTrackerVtx object
  		 vtx = (ND::GRooTrackerVtx*)VtxArray->At(j);
        // Get the event code string - this is a pointer to a TObjString which contains
        // the information about the event category. To find the methods in this class you need
        // to look up TObjString in ROOT.
                 TObjString* evtCode = vtx->EvtCode;
        // Print the string
                 cout << evtCode->GetString() << endl;

        // Now find out the number of particles in the event list
                 cout << "Number of particles in event listing : " << vtx->StdHepN << endl;
//                 cout << "Energy of incoming neutrino: " << vtx->StdHepP4[0][3] << " GeV" << endl;


				
				NParticles=vtx->StdHepN;

					for (int k=0;k<NParticles;k++) {//Iterate over all particles in the event
						if(((vtx->StdHepPdg[k]==14)||(vtx->StdHepPdg[k]==-14))&&(vtx->StdHepStatus[k]==0)) {
							//Looks for an incoming muon neutrino or antineutrino. Should this include electron and tau neutrinos?
							NuEnergy=vtx->StdHepP4[k][3];
							EnergyNeutrinoHistogram->Fill(NuEnergy);						
						}

					}
				
                }

	} // End loop over events

	EnergyNeutrinoHistogram->SetTitle("Energy of incident neutrino");
	
	TAxis* xAxis = EnergyNeutrinoHistogram->GetXaxis();
	xAxis->SetTitle("Energy (GeV)");
	xAxis->CenterTitle();
	//xAxis->SetTitleOffset( 1.2 );

	TAxis* yAxis = EnergyNeutrinoHistogram->GetYaxis();
	yAxis->SetTitle("Number");
	yAxis->CenterTitle();
	//yAxis->SetTitleOffset( 1.2 )

	outputFile->WriteTObject(EnergyNeutrinoHistogram);

	outputFile->Close();

	cout<<"Test1"<<endl;

}

//---------------------------------------------------------------------------//
//										Method to set up ROOT as required.										 //
//---------------------------------------------------------------------------//
void SetupROOT(){
	gROOT->SetBatch(1);
	gSystem->AddIncludePath("-I$OAEVENTROOT/src");
	gSystem->AddIncludePath("-I$OAANALYSISROOT/src");

	gSystem->Load("libPhysics");
	gSystem->Load("libGeom");
	gSystem->Load("libTree");
	gSystem->Load("libEG");
	gSystem->Load("libMinuit");
	gSystem->Load("libCLHEP.so");
	gSystem->Load("librecpack.so");
	gSystem->Load("liboaEvent.so");
	gSystem->Load("liboaRuntimeParameters.so");
	gSystem->Load("liboaOfflineDatabase.so");
	gSystem->Load("liboaUtility.so");
	gSystem->Load("libBeamData.so");
	gSystem->Load("liboaBeamData.so");
	gSystem->Load("liboaAnalysis.so");
}
