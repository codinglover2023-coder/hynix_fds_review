# TODO: work-items_cl_co 공유 작업 공간 운영 설계

todo_idx: rule_00002
상태: 실행완료 (사용자 검토 대기)
생성일: 2026-03-04
관련: rule_00001 (R&R 프레임워크)

---

## 배경

R&R(Rule 9000) 기반으로 Claude(커맨더)↔Codex(엑터) 간 협업 공간이 필요.
기존 `work-items_cl/`(Claude 전용), `work-items_co/`(Codex 전용)와 별도로
**양쪽이 공유하는 핸드오프 공간** `work-items_cl_co/`를 최상위에 신설.

---

## 운영 방안 검토

### 1. 용도 정의

| 기존 공간 | 담당 | 용도 |
|---|---|---|
| `work-items_cl/` | Claude 단독 | 분석, 설계, 검토 문서 |
| `work-items_co/` | Codex 단독 | 구현 실행, 테스트 기록 |
| **`work-items_cl_co/`** | **공유** | **커맨더→엑터 핸드오프, 검증 결과 교환** |

### 2. 핸드오프 흐름 (R&R 정렬 루프 기반)

```
사용자 요청
  ↓
Claude(커맨더): work-items_cl/ 에서 Todo/설계 작성
  ↓
Claude → Codex 핸드오프: work-items_cl_co/ 에 실행 스펙 배치
  ↓
Codex(엑터): work-items_co/ 에서 구현, 결과를 work-items_cl_co/ 에 리포트
  ↓
Claude(커맨더): work-items_cl_co/ 리포트 읽고 검증 → 사용자에게 최종 결과만 보고
```

### 3. 폴더 구조 (안)

```
work-items_cl_co/
├── handoff/          # Claude→Codex 실행 스펙
├── report/           # Codex→Claude 실행 결과
└── archive/y{YYYY}/m{MM}/  # 완료된 핸드오프/리포트 보관
```

### 4. 파일 네이밍

- 핸드오프: `handoff/{todo_idx}_spec.md`
- 리포트: `report/{todo_idx}_result.md`
- 네이밍 규칙은 기존 Rule 020 준수

### 5. 적용 범위

| 항목 | 결정 |
|------|------|
| 위치 | 최상위 `work-items_cl_co/` (크로스 프로젝트) |
| 하위 프로젝트별 생성 | 향후 필요 시 `{sub_project}/work-items_cl_co/` 허용 |
| 규칙 반영 | workflow_rules.md Rule 010 + Rule 9000에 추가 |
| CLAUDE.md 반영 | 최상위 `작업 공간 분리` 테이블에 행 추가 |

---

## 작업 항목

- [x] `work-items_cl_co/` 디렉터리 생성
- [x] 하위 폴더 구조(handoff/report/archive) 생성
- [x] workflow_rules.md Rule 010에 cl_co 행 추가 + Rule 9001 신설
- [x] CLAUDE.md 작업 공간 테이블에 cl_co 행 추가
- [ ] 사용자 검토 및 승인

---

## 완료 판정 기준

- [ ] 폴더 구조 생성 완료
- [ ] 규칙 문서 반영 완료
- [ ] 사용자 승인

---

## 의사결정 항목

| # | 항목 | 상태 | 결정 |
|---|------|------|------|
| 1 | 하위 폴더 구조 | 확정 | handoff/report/archive 3개 |
| 2 | 하위 프로젝트별 cl_co 생성 여부 | 확정 | 향후 필요 시 허용 |
| 3 | Rule 번호 | 확정 | Rule 9001 신설 |
