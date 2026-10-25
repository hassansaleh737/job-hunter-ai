"""Bounded agent: model plans REAL tool calls; deterministic evaluation owns decisions."""
from __future__ import annotations
import re
import threading
from collections import OrderedDict
from job_hunter.models import CandidateProfile, Preferences, JobPosting, JobAssessment, JobRequirementExtraction, Evidence
from job_hunter.inference.client import HFGateway
from job_hunter.sources.remotive import search_remotive,SourceError
from job_hunter.sources.greenhouse import list_greenhouse_jobs,get_greenhouse_job
from job_hunter.sources.link_check import check_link
from job_hunter.config import GREENHOUSE_BOARDS
from job_hunter.analysis.skills import assess_skills
from job_hunter.analysis.eligibility import evaluate_eligibility
from job_hunter.analysis.ranking import rank
from job_hunter.snapshots.loader import load_snapshot, load_prepared_requirements, job_fingerprint

# Smaller live shortlist limits sequential external inference while preserving
# both source types. All source discovery/verification still uses real APIs.
MAX_SHORTLIST = 6

# Public posting facts only. NO CVs, profiles, or candidate-dependent analyses.
_PUBLIC_REQ_CACHE: OrderedDict[str, JobRequirementExtraction] = OrderedDict()
_PUBLIC_REQ_LOCK = threading.Lock()
_PUBLIC_CACHE_LIMIT = 128


def _ground_requirements(job: JobPosting, req: JobRequirementExtraction) -> JobRequirementExtraction:
    """Remove ungrounded model facts; cached records are verified the same way."""
    grounded = req.model_copy(deep=True)
    source_blob = (job.title + " " + job.description + " " + job.location + " " +
                   " ".join(job.questions)).casefold()
    for field in ("experience_requirement", "geography", "work_authorization",
                  "remote_policy", "employment_type", "pay_evidence"):
        value = getattr(grounded, field)
        if value and value.casefold() not in source_blob:
            setattr(grounded, field, "")
    for field in ("required_skills", "preferred_skills", "mandatory_skills"):
        setattr(grounded, field, [v for v in getattr(grounded, field)
                                  if v and v.casefold() in source_blob])
    grounded.evidence_quotes = [q for q in grounded.evidence_quotes
                                if q and q.casefold() in source_blob]
    if not grounded.evidence_quotes and not grounded.required_skills and not grounded.experience_requirement:
        return JobRequirementExtraction(required_skills=[], preferred_skills=[], mandatory_skills=[],
            experience_requirement="", geography="", work_authorization="", remote_policy="",
            employment_type="", pay_evidence="", evidence_quotes=[])
    return grounded


def _public_requirements(job: JobPosting, gateway, prepared: dict[str, JobRequirementExtraction]):
    fingerprint = job_fingerprint(job)
    if fingerprint in prepared:
        return _ground_requirements(job, prepared[fingerprint]), "prepared snapshot"
    model_cfg = getattr(gateway, "cfg", None)
    model_identity = f"{getattr(model_cfg, 'model', '')}:{getattr(model_cfg, 'provider', '')}"
    key = model_identity + ":" + fingerprint
    with _PUBLIC_REQ_LOCK:
        cached = _PUBLIC_REQ_CACHE.get(key)
        if cached is not None:
            _PUBLIC_REQ_CACHE.move_to_end(key)
            return cached.model_copy(deep=True), "in-memory posting cache"
    # No lock while calling a remote model. Never cache failed or ungrounded output.
    req = _ground_requirements(job, gateway.requirements(
        job.title, job.description, job.location, job.questions))
    with _PUBLIC_REQ_LOCK:
        _PUBLIC_REQ_CACHE[key] = req.model_copy(deep=True)
        _PUBLIC_REQ_CACHE.move_to_end(key)
        if len(_PUBLIC_REQ_CACHE) > _PUBLIC_CACHE_LIMIT:
            _PUBLIC_REQ_CACHE.popitem(last=False)
    return req, "live model analysis"


def shortlist(jobs: list[JobPosting], pref: Preferences) -> list[JobPosting]:
    terms={w.casefold() for role in pref.roles for w in re.findall(r"[A-Za-z+#.]{3,}",role)}
    early=re.compile(r"intern|junior|entry.level|graduate|new grad|python|backend|software|ai|machine learning|developer",re.I)
    scored=[]
    seen=set()
    for j in jobs:
        key=(j.source,j.source_id)
        if key in seen or not j.url.startswith("https://"): continue
        seen.add(key)
        title=j.title.casefold()
        relevance=sum(w in title for w in terms)
        if not early.search(title) and relevance==0: continue
        scored.append((relevance, int(bool(re.search(r"intern|junior|entry.level|graduate", title))),j))
    scored.sort(key=lambda x:(-x[0],-x[1]))
    # Keep both approved source types represented when matching records exist.
    greenhouse=[j for _,__,j in scored if j.source=="Greenhouse"]
    remotive=[j for _,__,j in scored if j.source=="Remotive"]
    # Ensure we don't accidentally use every slot on Greenhouse first.
    chosen=greenhouse[:4]+remotive[:2]
    if len(chosen)<MAX_SHORTLIST:
        ids={(j.source,j.source_id) for j in chosen}
        chosen.extend(j for _,__,j in scored if (j.source,j.source_id) not in ids)
    return chosen[:MAX_SHORTLIST]

def run_pipeline(profile: CandidateProfile,pref: Preferences, mode: str,
                 emit, cancelled, gateway=None) -> tuple[list[JobAssessment],dict,str]:
    """Executed in worker thread. Never touches Streamlit's session_state."""
    def guard():
        if cancelled(): raise InterruptedError("Cancelled")
    def stage(msg, status="Running"):
        guard();emit("stage",{"name":msg,"status":status})
    outcomes={"Remotive":"Pending","Greenhouse":"Pending"}
    gateway=gateway or HFGateway()
    stage("Preparing search based on your profile")
    jobs=[]; collected=""; prepared={}
    if mode=="snapshot":
        date,jobs=load_snapshot();collected=date
        prepared=load_prepared_requirements(date)
        emit("info", {"message": f"Prepared public job facts loaded: {len(prepared)}. Skills and eligibility will still be calculated from your reviewed CV."})
        for historical_job in jobs:
            historical_job.active=False  # Historical collection does NOT confirm current availability.
            historical_job.link_status="unchecked"
        emit("info",{"message":f"Dated Snapshot collected {date}. No source requests were made."})
        for src in outcomes: outcomes[src]="Snapshot"
        stage("Preparing search based on your profile","Completed")
        for name in ("Searching Remotive","Searching Greenhouse"):
            stage(name,"Skipped")  # No source tools are called during a snapshot.
    else:
        calls=gateway.plan_tool_calls(pref.roles)
        stage("Preparing search based on your profile","Completed")
        rem_queries=[args for name,args in calls if name=="search_remotive"]
        args=rem_queries[0] if rem_queries else {"query":pref.roles[0],"limit":15,"category":"software-dev"}
        stage("Searching Remotive")
        try:
            guard()
            rem, origin=search_remotive(**args)
            jobs.extend(rem);outcomes["Remotive"]="Completed"
            emit("info",{"message":f"Remotive: {len(rem)} relevant jobs ({origin})."})
        except SourceError:
            outcomes["Remotive"]="Failed";emit("info",{"message":"Remotive unavailable; checking Greenhouse."})
        stage("Searching Remotive",outcomes["Remotive"])
        stage("Searching Greenhouse")
        success=0
        for token in GREENHOUSE_BOARDS:
            guard()
            try:
                found=list_greenhouse_jobs(token)
                jobs.extend(found);success+=1
                emit("info",{"message":f"Greenhouse / {token}: {len(found)} jobs."})
            except SourceError:
                emit("info",{"message":f"Greenhouse / {token}: unavailable."})
        outcomes["Greenhouse"]="Completed" if success==len(GREENHOUSE_BOARDS) else "Partial" if success else "Failed"
        stage("Searching Greenhouse","Completed" if success else "Failed")
        if outcomes["Remotive"]=="Failed" and success==0:
            raise SourceError("Both job sources failed. Please retry.")
    guard()
    selected=shortlist(jobs,pref)
    stage("Verifying job details and restrictions")
    assessments=[]
    for job in selected:
        guard()
        if mode=="live" and job.source=="Greenhouse":
            try:
                detail=get_greenhouse_job(job.board,int(job.source_id))
                job.questions=detail["questions"]
                if detail["pay"]:job.salary=detail["pay"]
                if detail["description"]:job.description=detail["description"]
            except (SourceError,ValueError):
                emit("info",{"message":f"Details unavailable for one {job.company} posting."})
        # Only approved URLs are checked, and failed HTTP validation cannot create evidence.
        if mode=="live": job.link_status=check_link(job.url)
    stage("Verifying job details and restrictions","Completed")
    stage("Evaluating skills match and eligibility")
    for job in selected:
        guard()
        req, provenance = _public_requirements(job, gateway, prepared)
        if mode == "snapshot" and provenance == "prepared snapshot":
            emit("info", {"message": f"Reused prepared public requirements for {job.source} job {job.source_id}."})
        skills=assess_skills(profile,req,job.title)
        eligibility,conditions=evaluate_eligibility(job,req,pref,profile)
        quotes = [Evidence(field="Employer job description", excerpt=quote[:270],
                           source_url=job.url) for quote in req.evidence_quotes[:10]]
        assessments.append(JobAssessment(job=job,skills=skills,eligibility=eligibility,
                 conditions=conditions,evidence=quotes,
                 freshness=job.posted_at or job.retrieved_at))
        emit("count",{"checked":len(assessments),"total":len(selected)})
    stage("Evaluating skills match and eligibility","Completed")
    stage("Preparing results")
    output=rank(assessments)
    stage("Preparing results","Completed")
    return output,outcomes,collected
