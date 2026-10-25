import time
from job_hunter.agent.run_controller import RunController
from job_hunter.models import CandidateProfile,Preferences

def profile():
    return CandidateProfile(skills=['Python'],education=[],experience=[],projects=[],confirmed=True)
def pref():return Preferences(roles=['Python'],level='Both',country='Egypt')

def test_cancel_discards_late_results():
    def delayed(profile,pref,mode,emit,cancelled):
        time.sleep(.03)
        return ['late'],{},''
    run=RunController(profile(),pref(),'snapshot',0,pipeline=delayed)
    run.cancel()
    run.future.result(timeout=3)
    run.poll()
    assert run.result==[]
    assert run.state=='Cancelled'
