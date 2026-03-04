

## Rule 104: Full Rule Audit Report


## Rule 101: Todo Kickoff Bundle (Generic)
root rule 101 00003

api rule 101 api_00001
arch rule 101 arch_00001
cron rule 101 00005


## Rule 102: Todo Execution From Issue Docs
root rule 102 00005

api rule 102 00006

cron rule 102 00006



## Rule 103: Jupyter Validation Notebook For Todo Index
root rule 103 037
root rule 103 037 done


## Rule 105: Validation Confirmation Update Pattern
root rule 105 021 --skip-notebooks-check
root rule 105 00003

#### Rule 200: Todo 현황 대시보드
root rule200
root rule200 --save

#### Rule 201: Batch Done Sweep (Rule 200 → 판정 → Rule 105)

root rule201 
api rule201 --dry-run
anal av rule201 --dry-run