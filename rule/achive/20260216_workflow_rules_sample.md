# Workflow Rules

## Rule 000: Rule Reload Trigger
- 사용자가 `rule 000` 형식으로 호출하면, 현재 `rule/` 문서 내용을 다시 읽고 작업 설정에 재반영한다.
- 이 호출은 "룰 재로딩/재적용" 명령으로 해석한다.

## Rule 001: Mutable Rules Policy
- 룰은 언제나 변경될 수 있다.
- 룰이 복잡해지거나 실제 작업 흐름과 어긋나면 즉시 수정 가능하다.
- 최신 문서 상태를 단일 기준(Source of Truth)으로 사용한다.
