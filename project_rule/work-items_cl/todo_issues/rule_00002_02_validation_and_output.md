# rule_00002 — Validation & Output: 검증 기준

todo_idx: rule_00002
issue_idx: 02
생성일: 2026-03-04

---

## 목적

`work-items_cl_co/` 운영 설계의 검증 기준과 완료 조건 정리.

---

## 현재 결정사항

### 검증 항목

| # | 검증 | 방법 | 상태 |
|---|------|------|------|
| 1 | 폴더 구조 존재 확인 | `ls work-items_cl_co/{handoff,report,archive}` | 미수행 |
| 2 | Rule 010 테이블에 cl_co 행 존재 | workflow_rules.md grep | 미수행 |
| 3 | Rule 9000 핸드오프 정책 존재 | workflow_rules.md grep | 미수행 |
| 4 | CLAUDE.md 작업 공간 테이블에 cl_co 행 존재 | CLAUDE.md grep | 미수행 |

### 완료 조건

- 검증 4건 모두 통과
- 사용자 승인

---

## 남은 작업

- [ ] rule 102 실행 후 검증 수행

---

## 다음 액션

1. rule 102 실행 대기
