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
	std::string IntCode, IntMode;
	int IntModeIndex;
	Double_t XVertex,YVertex;

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
	TH1* EnergyNeutrinoHistogramDelta = new TH1F("ENuHistDelta","Histogram of neutrino energy",100,0,10);
	TH1* InteractionModeHistogram = new TH1F("IntModeHist","Histogram of interaction mode",3,0,3);
	TH2* vertexXYHist = new TH2F("VTXXYHist","Vertex location in x-y plane",100,0,1.5,100,0,1);
    
    //New canvas for both histograms to fit on
	TCanvas *c1 = new TCanvas("c1","c1",600,400);
	EnergyNeutrinoHistogram->SetStats(0);//Removes stats box
	EnergyNeutrinoHistogramDelta->SetStats(0);
	InteractionModeHistogram->SetStats(0);
	vertexXYHist->SetStats(0);
    
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

				/*while(getline(evtCode->GetString(),IntMode,",")) {
					cout << IntMode << endl;
				}*/
				
				IntCode=evtCode->GetString();
				
				IntModeIndex=IntCode.find_last_of(",");//The event mode is just after the last comma

				IntMode=IntCode.substr(IntModeIndex+1,3);//The event mode is 3 characters long
								
				NParticles=vtx->StdHepN;

					for (int k=0;k<NParticles;k++) {//Iterate over all particles in the event
						if(((vtx->StdHepPdg[k]==14)||(vtx->StdHepPdg[k]==-14))&&(vtx->StdHepStatus[k]==0)) {
							//Looks for an incoming muon neutrino or antineutrino. Should this include electron and tau neutrinos?
							NuEnergy=vtx->StdHepP4[k][3];
							EnergyNeutrinoHistogram->Fill(NuEnergy);						
						}

					}

					for (int k=0;k<NParticles;k++) {//Iterate over all particles in the event
						if((vtx->StdHepPdg[k]==2214)&&(vtx->StdHepStatus[k]!=0)) {
							//Looks for a Delta+ baryon that is not an initial state particle
							NuEnergy=vtx->StdHepP4[k][3];
							EnergyNeutrinoHistogramDelta->Fill(NuEnergy);
						
							if(IntMode=="QES") {
								InteractionModeHistogram->Fill(0);
							}
							if(IntMode=="DIS") {
								InteractionModeHistogram->Fill(1);
							}
							if(IntMode=="RES") {
								InteractionModeHistogram->Fill(2);
							}
						

						}

					}
					
					XVertex=vtx->EvtVtx[0];
					YVertex=vtx->EvtVtx[1];
					
					vertexXYHist->Fill(XVertex,YVertex);

				
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
	//yAxis->SetTitleOffset( 1.2 );

	EnergyNeutrinoHistogramDelta->SetLineColor(kRed);
	
	EnergyNeutrinoHistogram->Draw();
	EnergyNeutrinoHistogramDelta->Draw("same");
	
	outputFile->WriteTObject(c1);

	InteractionModeHistogram->SetTitle("Interaction mode of D+ baryon generation");

	TAxis* xAxis = InteractionModeHistogram->GetXaxis();
	xAxis->SetTitle("Interaction Mode");
	xAxis->CenterTitle();
	xAxis->SetTitleOffset( 1.2 );
	xAxis->SetBinLabel(1,"QES");
	xAxis->SetBinLabel(2,"DIS");
	xAxis->SetBinLabel(3,"RES");

	TAxis* yAxis = InteractionModeHistogram->GetYaxis();
	yAxis->SetTitle("Number");
	yAxis->CenterTitle();
	yAxis->SetTitleOffset( 1.2 );

	outputFile->WriteTObject(InteractionModeHistogram);

	vertexXYHist->SetTitle("Vertex location in x-y plane");

	TAxis* xAxis = vertexXYHist->GetXaxis();
	xAxis->SetTitle("x axis");
	xAxis->CenterTitle();
//	xAxis->SetTitleOffset( 1.2 );


	TAxis* yAxis = vertexXYHist->GetYaxis();
	yAxis->SetTitle("y axis");
	yAxis->CenterTitle();
//	yAxis->SetTitleOffset( 1.2 );

	outputFile->WriteTObject(vertexXYHist);

	outputFile->Close();

	cout << "Test3" << endl;

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
