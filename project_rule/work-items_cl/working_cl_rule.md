

## Rule 104: Full Rule Audit Report


## Rule 101: Todo Kickoff Bundle (Generic)
project_rule rule 101 00001



## Rule 102: Todo Execution From Issue Docs
project_rule rule 102 00001



## Rule 105: Validation Confirmation Update Pattern
project_rule rule 105 00001

#### Rule 200: Todo 현황 대시보드
root rule200
root rule200 --save

#### Rule 201: Batch Done Sweep (Rule 200 → 판정 → Rule 105)

root rule201 
api rule201 --dry-run
anal av rule201 --dry-run