import EventCodeDeconstructor
import sys
	
EventCodeDeconstructor1 = EventCodeDeconstructor.EventCodeDeconstructor()
EventCodeDeconstructor1.ReadCode("nu:14;tgt:1000010010;N:2212;proc:Weak[CC],QES;")
	
print EventCodeDeconstructor1.EventCode
print EventCodeDeconstructor1.WriteCode()
	
