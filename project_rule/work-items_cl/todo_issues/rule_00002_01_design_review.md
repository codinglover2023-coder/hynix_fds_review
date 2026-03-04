# rule_00002 — Design Review: 폴더 구조 + 규칙 반영 설계

todo_idx: rule_00002
issue_idx: 01
생성일: 2026-03-04

---

## 목적

`work-items_cl_co/` 폴더 구조와 workflow_rules.md / CLAUDE.md 반영 방안 확정.

---

## 현재 결정사항

### A. 폴더 구조

```
work-items_cl_co/
├── handoff/                    # Claude→Codex 실행 스펙
├── report/                     # Codex→Claude 실행 결과
└── archive/y{YYYY}/m{MM}/     # 완료 건 보관
```

- **handoff/**: `{todo_idx}_spec.md` — 커맨더가 엑터에게 넘기는 구현 스펙
- **report/**: `{todo_idx}_result.md` — 엑터가 커맨더에게 돌려주는 결과
- **archive/**: Done 처리 시 handoff + report 쌍을 이동

### B. workflow_rules.md 반영

**Rule 010 작업 공간 테이블에 행 추가:**

```markdown
- 5폴더 구조 (기존 4폴더 + cl_co):
  - `todo/` — 진행 중 작업
  - `todo_issues/` — 진행 중 작업의 쟁점
  - `done/y{YYYY}/m{MM}/` — 완료된 작업
  - `done_issues/y{YYYY}/m{MM}/` — 완료된 쟁점
- 크로스 작업 공간:
  - `work-items_cl_co/` — Claude↔Codex 공유 핸드오프 공간 (최상위만)
```

**Rule 9000에 핸드오프 정책 추가:**

```markdown
#### 핸드오프 정책 (work-items_cl_co/)
- 커맨더(Claude)가 `handoff/{todo_idx}_spec.md`에 실행 스펙 작성
- 엑터(Codex)가 구현 후 `report/{todo_idx}_result.md`에 결과 작성
- 커맨더가 report 검증 후 사용자에게 최종 결과만 보고
- Done 처리 시 handoff + report 쌍을 `archive/y{YYYY}/m{MM}/`로 이동
```

### C. CLAUDE.md 반영

작업 공간 분리 테이블에 행 추가:

```markdown
| `work-items_cl_co/` | Claude↔Codex 공유 | 핸드오프 스펙/리포트 교환 (최상위만) |
```

---

## 남은 작업

- [ ] 사용자 폴더 구조 승인
- [ ] 실제 폴더 생성 + 규칙 편집

---

## 다음 액션

1. 사용자 승인 → rule 102로 실행
