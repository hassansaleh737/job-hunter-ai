import httpx
from job_hunter.sources.greenhouse import list_greenhouse_jobs,get_greenhouse_job
from job_hunter.sources import remotive
from job_hunter.sources.link_check import check_link


def test_greenhouse_adapter_normalizes_and_restricts_tokens():
    def handle(req):
        if req.url.path.endswith('/jobs'):
            return httpx.Response(200,json={'jobs':[{
                'id':7,'title':'Software Intern','absolute_url':'https://job-boards.greenhouse.io/ritual/jobs/7',
                'location':{'name':'Remote - US'},'content':'<p>Python &amp; FastAPI</p>',
                'first_published':'2026-10-25'}]})
        return httpx.Response(200,json={'questions':[{'label':'Eligible to work in US?'}],'pay_input_ranges':[]})
    with httpx.Client(transport=httpx.MockTransport(handle)) as c:
        jobs=list_greenhouse_jobs('ritual',client=c)
        detail=get_greenhouse_job('ritual',7,client=c)
    assert jobs[0].source=='Greenhouse'
    assert 'Python & FastAPI' in jobs[0].description
    assert detail['questions']==['Eligible to work in US?']


def test_remotive_adapter_parses_mock_feed(monkeypatch):
    remotive._cache.update({'payload':None,'at':0,'retrieved_at':''})
    def handle(req):
        return httpx.Response(200,json={'jobs':[{'id':1,'title':'Python Intern',
            'company_name':'Public Company','url':'https://remotive.com/remote-jobs/python-1',
            'description':'<p>Python developer role</p>','candidate_required_location':'Worldwide'}]})
    with httpx.Client(transport=httpx.MockTransport(handle)) as c:
        jobs,origin=remotive.search_remotive('python',client=c)
    assert len(jobs)==1
    assert jobs[0].location=='Worldwide'
    assert origin=='live fetch'
    remotive._cache.update({'payload':None,'at':0,'retrieved_at':''})


def test_link_checker_rejects_non_source_hosts_without_requests():
    assert check_link('http://127.0.0.1/private')=='unknown'
    assert check_link('https://169.254.169.254/latest/meta-data')=='unknown'
