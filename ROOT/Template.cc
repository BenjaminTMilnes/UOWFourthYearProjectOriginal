// This template shows the syntax for creating c++ code to call root macros.

#define Sample_cxx
#include "Sample.h"
#include "TH2.h"
#include "TStyle.h"
#include "TCanvas.h"
#include "TMath.h"
#include <iostream>
using namespace std;

int main()
{
	Sample a;
	a.Loop();
	
	return 0;
}

void Sample::Loop()
{
//   In a Root session, you can do:
//      Root > .L Sample.C
//      Root > Sample t
//      Root > t.GetEntry(12); // Fill t data members with entry number 12
//      Root > t.Show();       // Show values of entry 12
//      Root > t.Show(16);     // Read and show values of entry 16
//      Root > t.Loop();       // Loop on all entries
//

//     This is the loop skeleton
//       To read only selected branches, Insert statements like:
// METHOD1:
//    fChain->SetBranchStatus("*",0);  // disable all branches
//    fChain->SetBranchStatus("branchname",1);  // activate branchname
// METHOD2: replace line
//    fChain->GetEntry(i);  // read all branches
//by  b_branchname->GetEntry(i); //read only this branch
   if (fChain == 0) return;

   // The Set-up code goes here.

   Long64_t nentries = (Long64_t) fChain->GetEntries();

   Long64_t nbytes = 0, nb = 0;
   for (Long64_t jentry=0; jentry<nentries;jentry++) {
      Long64_t ientry = LoadTree(jentry);
      nb = fChain->GetEntry(jentry);   nbytes += nb;
      // if (Cut(ientry) < 0) continue;

      // The Loop code goes here.

   }

   // The Wrap-up code goes here.

}
