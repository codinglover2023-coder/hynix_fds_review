# rule_00001 — Kickoff Scope: R&R 프레임워크 기반 규칙 업데이트

todo_idx: rule_00001
issue_idx: 00
생성일: 2026-03-04

---

## 목적

프롬프트 글의 R&R 구조(평가자/커맨더/엑터)를 프로젝트 워크플로우에 매핑하고,
`workflow_rules.md`와 `CLAUDE.md` 업데이트 방안을 도출한다.

---

## 현재 결정사항

### 1. R&R 역할 매핑 확정 (사용자 원안)

```
평가자 : 사용자 (최종 승인 전담)
커맨더 : 사용자(요청) → Claude(정) → Codex(부)
엑터   : Codex(정, 구현) → Claude(부, 검증/보조)
```

### 2. 프롬프트 개념 → 프로젝트 매핑

정렬 순환 루프를 워크플로우에 대응시킴:

```
Real Self (방향 감각)     → 사용자의 프로젝트 비전/요구
  ↓
Meta Self-ego (운영체계)  → CLAUDE.md + Todo 설계 (Claude 커맨더)
  ↓
Ego (Actor)               → 코드 구현 (Codex 엑터)
  ↓
롤모델 Ego (해석/피드백)  → Done 이력 + 검증 패턴 (Claude 검증)
  ↓
글로벌 맵 (기준 좌표)     → workflow_rules.md (Base Rules)
  ↓ (루프 복귀)
Real Self ...
```

### 3. 기존 규칙과의 관계

현재 `workflow_rules.md`에는 R&R 관련 규칙이 **없음**.
- Rule 030 (실행 커뮤니케이션 규칙)이 가장 가까운 위치이나, **내부 룰 9000번대**로 분리 배치 확정
- Rule 010 (작업 흐름)에 `work-items_cl/` (Claude) vs `work-items_co/` (Codex) 구분은 있으나 역할 정의는 없음
- 내부 룰 범위: 9000~9999 (일반 워크플로우와 분리된 운영 정책)

---

## 남은 작업

- [x] R&R 규칙 위치 결정 → **Rule 9000번대 내부 룰로 확정** (9000~9999 범위)
- [x] workflow_rules.md 업데이트 → Rule 9000 추가 완료
- [x] CLAUDE.md 업데이트 → 최상위 합의사항 6번 추가 완료
- [x] 하위 CLAUDE.md 반영 범위 결정 → 참조 1줄 방식, 8개 전체 완료

---

## 다음 액션

1. **design_review 이슈 작성** — 구체적 업데이트 초안 설계
