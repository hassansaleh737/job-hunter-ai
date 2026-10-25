"""Conservative, deterministic eligibility; no model-based final labels."""
import re
from job_hunter.models import JobPosting, JobRequirementExtraction, Preferences, EligibilityCondition, Evidence, CandidateProfile
from job_hunter.analysis.experience import documented_experience_years

US_ONLY = re.compile(r"(?:\bremote\s*[-(]?\s*(?:u\.?s\.?a?\.?|united states)\s*\)?|\b(?:us|u\.s\.|usa|united states)\s*(?:only|based|residents?|candidates?)\b|\bmust (?:be|live|reside|work) in (?:the )?(?:us|u\.s\.|usa|united states)\b)", re.I)
UK_ONLY = re.compile(r"\b(?:uk\s*only|remote\s*[-(]?\s*(?:uk|united kingdom)\b)\b",re.I)
YEARS = re.compile(r"\b(?:at least|minimum(?: of)?|\+)?\s*(\d{1,2})\+?\s*(?:years?|yrs?)\s+(?:of )?(?:professional |relevant |work )?experience\b", re.I)
SENIOR = re.compile(r"\b(?:senior|staff|principal|lead)\b",re.I)


def evidence(job: JobPosting, field: str, excerpt: str, kind="explicit") -> list[Evidence]:
    if not excerpt: return []
    return [Evidence(field=field,excerpt=excerpt[:270],source_url=job.url,kind=kind)]


def evaluate_eligibility(job: JobPosting, req: JobRequirementExtraction, pref: Preferences, profile: CandidateProfile | None = None) -> tuple[str,list[EligibilityCondition]]:
    conditions=[]
    def put(name, state, reason, field="", excerpt=""):
        conditions.append(EligibilityCondition(name=name,state=state,explanation=reason,
             evidence=evidence(job,field or name,excerpt)))
    if job.active:
        put("Posting status","confirmed","Listed in the job-source response during this run; the employer accepting applications is not independently confirmed.","source record",job.source_id)
    else:
        put("Posting status","unknown","Current posting activity has not been verified (including historical snapshot results).")
    if job.link_status == "unavailable":
        put("Original link","unknown","The original URL could not be opened.")
    elif job.link_status == "active":
        put("Original link","confirmed","The original job URL responded successfully when checked; this does not confirm applications are open.","URL",job.url)
    else:
        put("Original link","unknown","The original URL has not been independently verified.")

    loc=job.location.strip(); geo=(req.geography or "").strip(); combined=" ".join([loc,geo]).replace("—","-").replace("–","-")
    country=pref.country.casefold().strip()
    if country == "egypt" and (US_ONLY.search(combined) or UK_ONLY.search(combined)):
        put("Geography","conflict",f"This position explicitly restricts its hiring geography outside {pref.country}.","location",loc or geo)
    elif country == "egypt" and re.search(r"\b(?:egypt|worldwide|anywhere in the world|globally)\b",combined,re.I):
        put("Geography","confirmed","The posting's stated geographic scope includes Egypt or Worldwide (not a legal authorization guarantee).","location",loc or geo)
    elif loc and country in loc.casefold():
        put("Geography","confirmed",f"The stated geographic scope includes {pref.country}.","location",loc)
    else:
        put("Geography","unknown",f"No explicit evidence confirms hiring eligibility from {pref.country}.")

    auth=(req.work_authorization or "").strip()
    if country=="egypt" and US_ONLY.search(auth):
        put("Work authorization","conflict","The stated work-authorization rule is US-restricted.","authorization",auth)
    elif re.search(r"\b(?:no (?:visa )?sponsorship|must be authorized)\b",auth,re.I):
        put("Work authorization","unknown","An authorization requirement exists; candidate authorization is not established.","authorization",auth)
    elif re.search(r"\b(?:all countries eligible|no work authorization required)\b",auth,re.I):
        put("Work authorization","confirmed","The posting explicitly states broad authorization acceptance.","authorization",auth)
    else:
        put("Work authorization","unknown","Employer work-authorization and payroll eligibility are not confirmed.")

    # The user's target level is a SEARCH PREFERENCE, not evidence of their
    # actual experience. Never reject someone solely for choosing Junior/Both.
    # CV silence does not establish a conflict. Only a documented lower bound
    # can positively support a specific minimum; we never sum overlapping roles.
    years = [int(m.group(1)) for m in YEARS.finditer(
        " ".join([job.description[:8000], req.experience_requirement]))]
    minimum = max(years) if years else None
    demonstrated = documented_experience_years(profile) if profile else None
    if minimum is not None:
        excerpt = req.experience_requirement or f"{minimum} years of experience"
        if demonstrated is not None and demonstrated >= minimum:
            put("Experience level", "confirmed",
                f"The reviewed profile documents at least {demonstrated:g} years in one role, "
                f"meeting the stated {minimum}-year minimum. Verify role relevance with the employer.",
                "experience", excerpt)
        else:
            message = ("The reviewed profile does not document enough relevant experience "
                       "to confirm this minimum; missing CV detail is not proof of ineligibility.")
            put("Experience level", "unknown",
                f"Employer asks for {minimum}+ years. {message}", "experience", excerpt)
    elif SENIOR.search(job.title):
        put("Experience level", "unknown",
            "This is advertised as a senior-level role; the candidate's fit is not confirmed "
            "by the title or selected experience preference alone.", "title", job.title)
    elif re.search(r"\b(?:intern|entry.level|junior|graduate|new grad|early career)\b",
                   job.title + " " + req.experience_requirement, re.I):
        put("Experience level", "confirmed",
            "The posting explicitly advertises an early-career role.", "title", job.title)
    else:
        put("Experience level", "unknown",
            "The posting does not establish a verifiable experience-level match.")

    jobtype=" ".join([job.employment_type,req.employment_type]).casefold().replace("_","-")
    chosen=[x.casefold() for x in pref.employment_types]
    if not chosen:
        put("Employment type","not_applicable","No employment-type restriction selected.")
    elif any(x in jobtype for x in chosen):
        put("Employment type","confirmed","Advertised employment type matches a selected type.","employment type",jobtype[:200])
    elif any(x in jobtype for x in ["full-time","part-time","internship","freelance","contract"]):
        put("Employment type","conflict","Advertised employment type conflicts with the selected types.","employment type",jobtype[:200])
    else:
        put("Employment type","unknown","Employment type is not clear enough to verify.")

    pay=job.salary.strip()+" "+req.pay_evidence.strip()
    if not pref.paid_only:
        put("Paid only","not_applicable","Paid-only preference is off.")
    elif re.search(r"\b(?:unpaid|volunteer|without compensation)\b",pay,re.I):
        put("Paid only","conflict","The posting explicitly indicates unpaid work.","pay",pay.strip())
    elif re.search(r"(?:\$|€|£)\s*\d|\b(?:paid|compensated|salary|hourly rate)\b",pay,re.I):
        put("Paid only","confirmed","The posting explicitly describes compensation.","pay",pay.strip())
    else:
        put("Paid only","unknown","Paid status is not verified.")

    remote=(job.location+" "+req.remote_policy+" "+job.description[:2000]).casefold()
    if re.search(r"\b(?:on.site only|onsite only|not remote)\b",remote):
        put("Remote work","conflict","The employer explicitly disallows remote work.","remote",job.location or req.remote_policy)
    elif job.source=="Remotive" or re.search(r"\b(?:remote|work from home|wfh)\b",remote):
        put("Remote work","confirmed","The source or employer explicitly advertises remote work.","remote",job.location or req.remote_policy or "Remotive remote listing")
    else:
        put("Remote work","unknown","Remote work is not expressly confirmed.")

    states={c.state for c in conditions}
    overall="Not Eligible" if "conflict" in states else "Unknown" if "unknown" in states else "Eligible"
    return overall,conditions
