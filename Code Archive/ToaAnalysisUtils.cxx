00001 #include <iostream>
00002 #include <string>
00003 #include <TMath.h>
00004 #include <TEnv.h>
00005 #include <TSystem.h>
00006 #include <TString.h>
00007 #include <TND280Log.hxx>
00008 #include "ToaAnalysisUtils.hxx"
00009 
00010 ClassImp(ND::ToaAnalysisUtils);
00011 
00012 ND::ToaAnalysisUtils::ToaAnalysisUtils(){}
00013 ND::ToaAnalysisUtils::~ToaAnalysisUtils(){}
00014 
00015 ND::ToaAnalysisUtils::ESubdetector ND::ToaAnalysisUtils::PathToSubdetector(const std::string path) {
00016   //FGD
00017   if((path.find("FGD1") != std::string::npos) && (path.find("Basket") != std::string::npos)) {
00018     return ND::ToaAnalysisUtils::kFGD1;
00019   }
00020   else if((path.find("FGD2") != std::string::npos) && (path.find("Basket") != std::string::npos)) {
00021     return ND::ToaAnalysisUtils::kFGD2;
00022   }
00023   //P0D
00024   else if((path.find("P0D") != std::string::npos) && (path.find("Basket") != std::string::npos)) {
00025     return ND::ToaAnalysisUtils::kP0D;
00026   }
00027   //DsECal
00028   else if((path.find("DsECal") != std::string::npos) && (path.find("Basket") != std::string::npos)) {
00029     return ND::ToaAnalysisUtils::kDsECal;
00030   }
00031   //BrlECal
00032   else if((path.find("BrlECal") != std::string::npos) && (path.find("Clam") != std::string::npos)) {
00033     return ND::ToaAnalysisUtils::kBrlECal;
00034   }
00035   //P0DECal
00036   else if((path.find("P0DECal") != std::string::npos) && (path.find("Clam") != std::string::npos)) {
00037     return ND::ToaAnalysisUtils::kP0DECal;
00038   }
00039   //TPC1
00040   else if((path.find("TPC1") != std::string::npos) && (path.find("Basket") != std::string::npos)) {
00041     return ND::ToaAnalysisUtils::kTPC1;
00042   }
00043   //TPC2
00044   else if((path.find("TPC2") != std::string::npos) && (path.find("Basket") != std::string::npos)) {
00045     return ND::ToaAnalysisUtils::kTPC2;
00046   }
00047   //TPC3
00048   else if((path.find("TPC3") != std::string::npos) && (path.find("Basket") != std::string::npos)) {
00049     return ND::ToaAnalysisUtils::kTPC3;
00050   }
00051   //MRD
00052   else if(((path.find("MRD") != std::string::npos) || (path.find("FluxReturn") != std::string::npos))
00053   && (path.find("Clam") != std::string::npos)) {
00054     return ND::ToaAnalysisUtils::kMRD;
00055   }
00056   //Other parts of the off-axis
00057   else if(path.find("OA") != std::string::npos) {
00058     return ND::ToaAnalysisUtils::kOffAxis;
00059   }
00060   //INGRID
00061   else if(path.find("INGRID") != std::string::npos) {
00062     return ND::ToaAnalysisUtils::kINGRID;
00063   }
00064   else {
00065     return ND::ToaAnalysisUtils::kCavern;
00066   }
00067 }
00068 
00069 
00070 std::string ND::ToaAnalysisUtils::DetectorName(const ESubdetector subdet) {
00071   switch(subdet) {
00072     case kFGD1: return "FGD1"; break;
00073     case kFGD2: return "FGD2"; break;
00074     case kP0D: return "P0D"; break;
00075     case kDsECal: return "DsECal"; break;
00076     case kBrlECal: return "BrlECal"; break;
00077     case kP0DECal: return "P0DECal"; break;
00078     case kTPC1: return "TPC1"; break;
00079     case kTPC2: return "TPC2"; break;
00080     case kTPC3: return "TPC3"; break;
00081     case kMRD: return "MRD"; break;
00082     case kOffAxis: return "OffAxis"; break;
00083     case kINGRID: return "INGRID"; break;
00084     case kCavern: return "Cavern"; break;
00085     default: return "NONE";
00086   }
00087 }
00088 
00089 
00090 ND::ToaAnalysisUtils::EParticleCategory ND::ToaAnalysisUtils::PDGToCategory(const Int_t pdg) {
00091   TParticlePDG pdgInfo(pdg);
00092   return PDGInfoToCategory(&pdgInfo);
00093 }
00094 
00095 
00096 ND::ToaAnalysisUtils::EParticleCategory ND::ToaAnalysisUtils::PDGInfoToCategory(const TParticlePDG *pdgInfo) {
00097   if(pdgInfo) {
00098     Int_t pdg = pdgInfo->PdgCode();
00099     // rounding Double_t charge/3 to closest Int_t (ROOT returns a double in units of e/3!)
00100     Int_t charge = TMath::Nint(pdgInfo->Charge()/3.0) ;
00101     std::string particleClass = pdgInfo->ParticleClass();
00102     // Charged Particles
00103     if(charge != 0) {
00104       // Leptons
00105       if(TMath::Abs(pdg) == 11 || TMath::Abs(pdg) == 13 || TMath::Abs(pdg) == 15) {
00106         return kChargedLepton;
00107       }
00108       // Baryons
00109       if(particleClass.find("Baryon") != std::string::npos) {
00110         return kChargedBaryon;
00111       } else
00112       // Mesons
00113       if(particleClass.find("Meson") != std::string::npos) {
00114         return kChargedMeson;
00115       }
00116       // Other Charged
00117       else {
00118         return kOtherCharged;
00119       }
00120     } else
00121     // Photons
00122     if(pdg == 22) {
00123       return kPhoton;
00124     }
00125     // Other Neutral
00126     else {
00127       return kOtherNeutral;
00128     }
00129     ND280Warn("Problem!! PDGInfoToCategory: pdg is " << pdg
00130       << ", class is " << particleClass);
00131     // will never happen
00132     return kOther;
00133   }
00134   else {
00135     return kOther;
00136   }
00137 }
00138 
00139 
00140 void ND::ToaAnalysisUtils::UseCustomPDGTable() {
00141   gEnv->SetValue("Root.DatabasePDG", TString(gSystem->Getenv("OAANALYSISROOT")) + "/input/oaanalysis_pdg_table.txt");
00142 }
