# rule_00002 — Kickoff Scope: work-items_cl_co 공유 작업 공간

todo_idx: rule_00002
issue_idx: 00
생성일: 2026-03-04

---

## 목적

R&R(Rule 9000) 기반 Claude(커맨더)↔Codex(엑터) 핸드오프 공간 `work-items_cl_co/` 운영 설계.

---

## 현재 결정사항

1. 최상위 `work-items_cl_co/` 디렉터리 생성 완료
2. 용도: Claude→Codex 실행 스펙 전달 + Codex→Claude 결과 리포트 교환
3. 기존 `_cl/`, `_co/`는 각자 단독 공간으로 유지 — `_cl_co/`는 교차점만 담당

### 즉시 수행 가능 항목

| # | 작업 | 수행 가능 여부 |
|---|------|---------------|
| 1 | 하위 폴더(handoff/report/archive) 생성 | 가능 — 사용자 폴더 구조 승인 후 |
| 2 | workflow_rules.md Rule 010 테이블 행 추가 | 가능 |
| 3 | workflow_rules.md Rule 9000 핸드오프 정책 추가 | 가능 |
| 4 | CLAUDE.md 작업 공간 테이블 행 추가 | 가능 |

---

## 남은 작업

- [ ] 폴더 구조 확정 (handoff/report/archive 3개 vs 더 단순화)
- [ ] Rule 반영 범위 확정 (Rule 9000 확장 vs Rule 9001 신설)
- [ ] 실제 파일 편집

---

## 다음 액션

1. **design_review(01)** — 폴더 구조 + 규칙 반영 구체안 설계
2. **validation_and_output(02)** — 검증 기준 정리
