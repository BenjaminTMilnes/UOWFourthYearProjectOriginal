#include "TLorentzVector.h"
#include "/home/theory/phujce/FinalYearProject/Python/nd280/ND__GRooTrackerVtx.h"

namespace ND
{
	class GRooTrackerVtx;
}

void GRooTrackerHack()
{
    return;
}

TLorentzVector getRooTrackerMomentum(ND::GRooTrackerVtx* vertex, int i)
{
	return TLorentzVector(
		vertex->StdHepP4[i][0], // Px
		vertex->StdHepP4[i][1], // Py
		vertex->StdHepP4[i][2], // Pz
		vertex->StdHepP4[i][3]  // E
		);
}

TLorentzVector getRooTrackerPosition(ND::GRooTrackerVtx* vertex, int i)
{
	return TLorentzVector(
		vertex->StdHepX4[i][0], // X
		vertex->StdHepX4[i][1], // Y
		vertex->StdHepX4[i][2], // Z
		vertex->StdHepX4[i][3]  // E
		);
}

TLorentzVector getRooTrackerLocation(ND::GRooTrackerVtx* vertex)
{
	return TLorentzVector(
		vertex->EvtVtx[0], // X
		vertex->EvtVtx[1], // Y
		vertex->EvtVtx[2], // Z
		vertex->EvtVtx[3]  // E
		);
}

Int_t getRooTrackerNeutCode(ND::GRooTrackerVtx* vertex)
{
	return vertex->G2NeutEvtCode;
}
