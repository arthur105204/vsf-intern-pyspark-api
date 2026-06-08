# Weekly Work Plan: 05/06 - 12/06

Converted from the weekly Excel workbook to Markdown for easier mentor review.

Date values are displayed in dd/mm format based on the weekly planning period.

## Weekly Execution Plan

| Date | Day | Workstream | Task | Expected Output | Priority | Status | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 05/06 | Fri | Two-Tower | Commit stabilization/review gate | Clean repo checkpoint | High | Done | No more model features for now |
| 05/06 | Fri | Two-Tower | Read experiment summary, code walkthrough, mentor Q&A | Personal understanding notes | High | Done | Prepare to explain project |
| 05/06 | Fri | Planning | Finalize weekly Excel plan | Weekly plan ready | High | Done | Date-based plan |
| 05/06 | Fri | PySpark | Choose dataset and define problem | Dataset + target column selected | High | Done | Churn/propensity/classification |
| 05/06 | Fri | API | Define API mini scope | API endpoint/schema/test plan | High | Done | Prediction lookup by user_id |
| 05/06 | Fri | API | Draft API documentation | API_DOCS.md draft | High | Done | Mentor emphasized API docs; draft before implementation, finalize after code |
| 06/06 | Sat | PySpark | Do Pandas EDA | 5 charts + EDA notes | High | To Do | Quick data understanding |
| 06/06 | Sat | PySpark | Define cleaning and feature rules | Feature list + preprocessing plan | High | To Do | Prepare PySpark conversion |
| 06/06 | Sat | API | Generate 500k mock prediction rows | Mock prediction dataset | High | To Do | user_id, prediction_score |
| 06/06 | Sat | Docs | Write daily progress note | Daily summary | Medium | To Do | Track learning/output |
| 08/06 | Mon | PySpark | Convert preprocessing workflow to PySpark | PySpark preprocessing script | High | To Do | Pandas → PySpark |
| 08/06 | Mon | API | Build FastAPI lookup endpoint | /prediction/{user_id} works | High | To Do | Return prediction score |
| 08/06 | Mon | API | Add not-found handling and metadata | 404 response, trace_id, timestamp | High | To Do | Production-style response |
| 08/06 | Mon | PySpark | Train Logistic Regression model | Model metrics report | High | To Do | Accuracy/F1/AUC |
| 09/06 | Tue | API | Add in-memory cache | Cached lookup working | High | To Do | Compare cached vs non-cached |
| 09/06 | Tue | API | Finalize API docs after implementation | Updated API_DOCS.md | Medium | To Do | Endpoint, request, response |
| 09/06 | Tue | PySpark | Add second model if feasible | Model comparison table | Medium | To Do | RandomForest/XGBoost optional |
| 09/06 | Tue | API | Run load test | Load test report | High | To Do | Latency, throughput, error rate |
| 10/06 | Wed | API | Record performance metrics | P50/P95/P99, RPS, error rate | High | To Do | Performance test evidence |
| 10/06 | Wed | API | Run stress test | Stress test report | High | To Do | Find breaking point |
| 10/06 | Wed | API | Compare cache vs no-cache | Cache impact table | High | To Do | Show latency improvement |
| 10/06 | Wed | Privacy | Write PII/privacy notes | PII_PRIVACY_NOTES.md | Medium | To Do | Basic privacy awareness |
| 11/06 | Thu | PySpark | Finalize PySpark report | PYSPARK_REPORT.md | High | To Do | EDA + pipeline + model |
| 11/06 | Thu | API | Finalize API performance report | API_PERFORMANCE_REPORT.md | High | To Do | Load/stress/cache results |
| 11/06 | Thu | All | Reproducibility check | Commands verified | High | To Do | Run from clean instructions |
| 12/06 | Fri | All | Prepare mentor review package | Summary + links + questions | High | To Do | Ready for async review |
| 12/06 | Fri | All | Send weekly update | Mentor update message | High | To Do | Include blockers/questions |
| 12/06 | Fri | Buffer | Fix urgent issues | Bugfix/docs cleanup | Medium | To Do | Based on review/self-check |


## Milestones

| Milestone ID | Date | Workstream | Milestone | Deliverable | Success Criteria | Status |
| --- | --- | --- | --- | --- | --- | --- |
| M1 | 05/06 | Two-Tower | Review package checkpoint | Summary, walkthrough, Q&A | Can explain project to mentor | Done |
| M2 | 05/06 | PySpark | Dataset selected | Dataset + problem statement | Target column and task are clear | Done |
| M3 | 05/06 | API | API scope finalized | API mini PRD | Endpoint/schema/cache/test plan defined | Done |
| M3A | 05/06 | API | API docs draft completed | API_DOCS.md draft | Endpoint/request/response/errors/cache/test plan documented | Done |
| M4 | 06/06 | PySpark | EDA completed | 5 charts + notes | Understand data and features | To Do |
| M5 | 06/06 | API | Mock data generated | 500k prediction rows | Data ready for API lookup | To Do |
| M6 | 08/06 | PySpark | PySpark preprocessing completed | PySpark script | Workflow runs in PySpark | To Do |
| M7 | 08/06 | API | API MVP completed | FastAPI endpoint | Lookup by user_id works | To Do |
| M8 | 08/06 | PySpark | Basic model trained | Logistic Regression metrics | Model trains/evaluates end-to-end | To Do |
| M9 | 09/06 | API | Cache added | Cached API | Repeated lookup faster or documented | To Do |
| M10 | 09/06 | API | Load test completed | Load test report | Latency/RPS/error rate recorded | To Do |
| M11 | 10/06 | API | Stress test completed | Stress test report | System limit identified | To Do |
| M12 | 10/06 | Privacy | PII notes completed | Privacy note | Basic PII risks documented | To Do |
| M13 | 11/06 | PySpark/API | Reports finalized | PySpark + API reports | Mentor-reviewable docs ready | To Do |
| M14 | 12/06 | All | Weekly package sent | Update message + links | Mentor can review asynchronously | To Do |


## Daily Output Checklist

| Date | Day | Must-Have Output | Nice-to-Have | Risk if Missed | Status |
| --- | --- | --- | --- | --- | --- |
| 05/06 | Fri | Two-Tower review checkpoint, PySpark dataset chosen, API scope + API docs draft defined | Clean commits | Next work becomes unclear | Done |
| 06/06 | Sat | PySpark EDA + mock prediction data | First API skeleton | PySpark/API delayed | To Do |
| 08/06 | Mon | PySpark preprocessing + FastAPI endpoint + Logistic Regression | Basic API tests | No working PySpark/API MVP | To Do |
| 09/06 | Tue | API cache + API docs + load test | Second PySpark model | Missing performance evidence | To Do |
| 10/06 | Wed | Stress test + cache comparison + PII notes | Charts/tables for report | Missing production-awareness evidence | To Do |
| 11/06 | Thu | Final PySpark/API reports | Full rerun commands | Review package incomplete | To Do |
| 12/06 | Fri | Mentor update sent | Fix feedback immediately | No review cycle | To Do |


## Risks  Blockers

| Date | Workstream | Risk / Blocker | Impact | Mitigation | Status |
| --- | --- | --- | --- | --- | --- |
| 05/06 | Two-Tower | Low personal understanding due to vibe coding | Hard to explain to mentor | Read walkthrough + Q&A before adding features | Open |
| 05/06 | Two-Tower | Popularity baseline still beats two-tower | Model result may look weak | Explain sparsity, cold users, baseline strength | Open |
| 05/06 | PySpark | Dataset choice takes too long | Delays MVP | Pick simple classification dataset quickly | Open |
| 06/06 | PySpark | PySpark setup issue | Blocks pipeline | Use local PySpark or fallback notebook environment | Open |
| 08/06 | API | API scope creep | Delays testing | Keep lookup API simple | Open |
| 09/06 | API | Cache overcomplication | Wastes time | Start with in-memory cache only | Open |
| 09/06 | API | Load test tool setup slow | Delays performance report | Use simplest available tool first | Open |
| 10/06 | Privacy | PII topic too broad | Too much theory | Keep to basic PII/access/logging notes | Open |


## Status Options

| Status |
| --- |
| To Do |
| In Progress |
| Blocked |
| Done |
| Deferred |


## Priority Options

| Priority |
| --- |
| High |
| Medium |
| Low |

