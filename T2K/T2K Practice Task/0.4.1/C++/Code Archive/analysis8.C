#include <iostream>
#include <vector>
#include <fstream>
#include <sstream>
#include <string>
#include <math.h>

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
	int IntModeIndex, InFGD;
	Double_t XVertex,YVertex,ZVertex;
	Double_t XMomentum,YMomentum,ZMomentum,TotalMomentum;
	int DaughterNumber;
	int ProtonPresent=0,PionPresent=0,PhotonPresent=0;
	int PhotonProtonCount=0;
	
	////////////////////////////////
	std::string Codes;
	std::ostringstream ss;
	///////////////////////////////
	
	int count=0; //Counter for testing

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
	TH2* vertexXYHist = new TH2F("VTXXYHist","Vertex location in x-y plane",100,-3000,3000,100,-3000,3000);
	TH2* vertexYZHist = new TH2F("VTXYZHist","Vertex location in y-z plane",100,-3000,3000,100,-3000,3000);
	TH1* EnergyNeutrinoHistogramDeltaFGD = new TH1F("ENuHistDeltaFGD","Histogram of neutrino energy",100,0,10);
	TH1* DeltaMomentumHistogram = new TH1F("MomDelta","Histogram of delta baryon momentum",100,0,10);
	TH1* ProtonPionMomentumHistogramP = new TH1F("MomPPiP","Histogram of proton momentum from Delta -> p + pi0 decay",100,0,10);
	TH1* ProtonPionMomentumHistogramPI = new TH1F("MomPPiPi","Histogram of pion momentum from Delta -> p + pi0 decay",100,0,10);
    
    //New canvas for both histograms to fit on
	TCanvas *c1 = new TCanvas("c1","c1",600,400);
	EnergyNeutrinoHistogram->SetStats(0);//Removes stats box
	EnergyNeutrinoHistogramDelta->SetStats(0);
	InteractionModeHistogram->SetStats(0);
	vertexXYHist->SetStats(0);
	vertexYZHist->SetStats(0);
    EnergyNeutrinoHistogramDeltaFGD->SetStats(0);
    DeltaMomentumHistogram->SetStats(0);
    ProtonPionMomentumHistogramP->SetStats(0);
    ProtonPionMomentumHistogramPI->SetStats(0);
    
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
						
							//Final bullet point
						
							XMomentum=vtx->StdHepP4[k][0];
							YMomentum=vtx->StdHepP4[k][1];
							ZMomentum=vtx->StdHepP4[k][2];
							
							TotalMomentum=sqrt(XMomentum*XMomentum+YMomentum*YMomentum+ZMomentum*ZMomentum);

							DeltaMomentumHistogram->Fill(TotalMomentum);

							// Search for pion and proton

							DaughterNumber=vtx->StdHepLd[k]-vtx->StdHepFd[k]+1;
							
							if(DaughterNumber==2) {//Only 2 daughters in Delta-> Pi + p
								for(int m=vtx->StdHepFd[k];m<vtx->StdHepLd[k]+1;m++) {//Iterate over daughter particles
									if(vtx->StdHepPdg[m]==2212) {//Proton check
										ProtonPresent=m;
									}

									if(vtx->StdHepPdg[m]==111) {//Checking for (including higher energy?) pions (currently just pi 0's)
										PionPresent=m;
									}
								}
							}

							if((ProtonPresent!=0)&&(PionPresent!=0)) {//check if proton + pion channel

								XMomentum=vtx->StdHepP4[ProtonPresent][0];
								YMomentum=vtx->StdHepP4[ProtonPresent][1];
								ZMomentum=vtx->StdHepP4[ProtonPresent][2];
							
								TotalMomentum=sqrt(XMomentum*XMomentum+YMomentum*YMomentum+ZMomentum*ZMomentum);
				
								ProtonPionMomentumHistogramP->Fill(TotalMomentum);
								
								XMomentum=vtx->StdHepP4[PionPresent][0];
								YMomentum=vtx->StdHepP4[PionPresent][1];
								ZMomentum=vtx->StdHepP4[PionPresent][2];
							
								TotalMomentum=sqrt(XMomentum*XMomentum+YMomentum*YMomentum+ZMomentum*ZMomentum);

								ProtonPionMomentumHistogramPI->Fill(TotalMomentum);
							}

							ProtonPresent=0;//Reset flag for next loop
							PionPresent=0;
							
							// Search for photon and proton

							DaughterNumber=vtx->StdHepLd[k]-vtx->StdHepFd[k]+1;
							
							if(DaughterNumber==2) {//Only 2 daughters in Delta-> gamma + p
								for(int m=vtx->StdHepFd[k];m<vtx->StdHepLd[k]+1;m++) {//Iterate over daughter particles
									if(vtx->StdHepPdg[m]==2212) {//Proton check
										ProtonPresent=m;
									}

									if(vtx->StdHepPdg[m]==22) {//Checking for photons
										PhotonPresent=m;

										/////////////////////////////////////

										if(vtx->StdHepPdg[m-1]==2212) {//Proton check
											ss<<vtx->StdHepPdg[m-1];
											Codes.append(ss.str());
											Codes.append(" ");
										}
										
										if(vtx->StdHepPdg[m+1]==2212) {//Proton check
											ss<<vtx->StdHepPdg[m+1];
											Codes.append(ss.str());
											Codes.append(" ");
										}
										
										Codes.append("   ");
										
										/////////////////////////////////////
										
									}
								}
							}
							
							if((ProtonPresent!=0)&&(PionPresent!=0)) {//check if proton + pion channel
								PhotonProtonCount++;
							}

							ProtonPresent=0;//Reset flags for next loop
							PhotonPresent=0;

						}

					}
					
					//Vertex section
					XVertex=vtx->EvtVtx[0];
					YVertex=vtx->EvtVtx[1];
					ZVertex=vtx->EvtVtx[2];

					vertexXYHist->Fill(XVertex,YVertex);
					vertexYZHist->Fill(YVertex,ZVertex);
					
					//FGD
					InFGD=((XVertex>-832.2)&&(XVertex<832.2)&&(YVertex>-777.2)&&(YVertex<887.2))&&(((ZVertex>123.45)&&(ZVertex<446.95))||((ZVertex>1481.45)&&(ZVertex<1807.95)));
					
					if(InFGD) {
						EnergyNeutrinoHistogramDeltaFGD->Fill(NuEnergy);
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
	
	vertexYZHist->SetTitle("Vertex location in y-z plane");

	TAxis* xAxis = vertexYZHist->GetXaxis();
	xAxis->SetTitle("y axis");
	xAxis->CenterTitle();
//	xAxis->SetTitleOffset( 1.2 );


	TAxis* yAxis = vertexYZHist->GetYaxis();
	yAxis->SetTitle("z axis");
	yAxis->CenterTitle();
//	yAxis->SetTitleOffset( 1.2 );

	outputFile->WriteTObject(vertexYZHist);

	TCanvas *c2 = new TCanvas("c2","c2",600,400);
	
	EnergyNeutrinoHistogramDeltaFGD->SetLineColor(kGreen);
	
	EnergyNeutrinoHistogram->Draw();
	EnergyNeutrinoHistogramDelta->Draw("same");
	EnergyNeutrinoHistogramDeltaFGD->Draw("same");
	
	outputFile->WriteTObject(c2);
	
	TCanvas *c3 = new TCanvas("c3","c3",600,400);
	
	EnergyNeutrinoHistogramDeltaFGD->SetLineColor(kGreen);
	
	EnergyNeutrinoHistogramDelta->Draw("");
	EnergyNeutrinoHistogramDeltaFGD->Draw("same");
	
	outputFile->WriteTObject(c3);
	
	DeltaMomentumHistogram->SetTitle("Momentum of delta baryons");

	TAxis* xAxis = DeltaMomentumHistogram->GetXaxis();
	xAxis->SetTitle("Momentum (GeV/c)");
	xAxis->CenterTitle();
//	xAxis->SetTitleOffset( 1.2 );


	TAxis* yAxis = DeltaMomentumHistogram->GetYaxis();
	yAxis->SetTitle("Number");
	yAxis->CenterTitle();
//	yAxis->SetTitleOffset( 1.2 );

	outputFile->WriteTObject(DeltaMomentumHistogram);
	
	ProtonPionMomentumHistogramP->SetTitle("Momentum of protons from Delta -> p + pi0 decay");

	TAxis* xAxis = ProtonPionMomentumHistogramP->GetXaxis();
	xAxis->SetTitle("Momentum (GeV/c)");
	xAxis->CenterTitle();
//	xAxis->SetTitleOffset( 1.2 );


	TAxis* yAxis = ProtonPionMomentumHistogramP->GetYaxis();
	yAxis->SetTitle("Number");
	yAxis->CenterTitle();
//	yAxis->SetTitleOffset( 1.2 );

	outputFile->WriteTObject(ProtonPionMomentumHistogramP);
	
	ProtonPionMomentumHistogramPI->SetTitle("Momentum of pions from Delta -> p + pi0 decay");

	TAxis* xAxis = ProtonPionMomentumHistogramPI->GetXaxis();
	xAxis->SetTitle("Momentum (GeV/c)");
	xAxis->CenterTitle();
//	xAxis->SetTitleOffset( 1.2 );


	TAxis* yAxis = ProtonPionMomentumHistogramPI->GetYaxis();
	yAxis->SetTitle("Number");
	yAxis->CenterTitle();
//	yAxis->SetTitleOffset( 1.2 );

	outputFile->WriteTObject(ProtonPionMomentumHistogramPI);
	
	outputFile->Close();

	cout << "Number of Delta decays which produce a proton and a photon: " << PhotonProtonCount << endl;
	cout << Codes << endl;
	cout << "Test4 " << count << endl;

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
