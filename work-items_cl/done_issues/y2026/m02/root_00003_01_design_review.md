# root_00003_01: Design Review

대상 todo: `root_00003_entrypoint_and_deployment_rules.md`

## 목적
- Entrypoint, 배포, 로컬 개발 규칙의 설계를 검토한다.

## 현재 결정사항

### Render 서비스 ↔ 하위 프로젝트 매핑 ✅ 확정

| 서비스 | 타입 | 프로젝트 | Entrypoint | 배포 |
|---|---|---|---|---|
| cyclestack-api | Web | render_api + render_web | `uvicorn render_api.main:app --host 0.0.0.0 --port $PORT` | Render |
| cyclestack-cron | Cron | render_cron | `python -m render_cron.main` | Render |
| (없음) | 로컬 | render_anal | Jupyter 실행 | 로컬 전용 |
| (없음) | clasp | project_gas | `clasp push` | Google 직접 |
| (없음) | 없음 | common_data | import 전용 | 배포 없음 |
| (없음) | 없음 | project_arch | 설계 문서 | 배포 없음 |

### FastAPI + Flask 마운트 설계 ✅ 확정

```
Request → FastAPI (ASGI host)
  ├── /api/*     → FastAPI 라우터 (직접 처리)
  ├── /web/*     → WSGIMiddleware → Flask 앱
  └── /          → FastAPI root (금지 또는 /web/ 리다이렉트)
```

- **경로 규약**: `/api/*` = FastAPI, `/web/*` = Flask
- **새 라우트 추가 체크리스트** (필수):
  1. `/api/` 또는 `/web/` prefix 준수
  2. 동일 경로 중복 여부 확인
  3. `/api/healthz` + `/web/healthz` 스모크 통과
- **재시작 정책**: 운영=재배포 필요, 로컬=`--reload` 자동 반영
- **WSGIMiddleware 제약**:
  - WebSocket 불가 (Flask 측), streaming 버퍼링 가능
  - 단일 프로세스 공유 → 장애/부하 상호 영향
  - 고성능/대용량 시 분리 서비스 고려 (향후)

### 환경 변수 SSOT ✅ 확정
- 키의 SSOT = `.env.template`
- 값의 SSOT: Render(운영) / `.env`(로컬) 분리
- 3종 동기화: `.env.template` → `config.py` → `render.yaml`/Render UI

### 로컬 개발 ↔ Render 차이점 ✅ 확정

| 항목 | 로컬 | Render |
|---|---|---|
| 환경 변수 | `.env` → `load_dotenv` | Dashboard/render.yaml |
| 포트 | `--port 8000` | `$PORT` (자동) |
| 리로드 | `--reload` 사용 | 사용 안 함 |
| PYTHONPATH | 루트 실행으로 자동 보장 | 루트에서 실행되므로 자동 |
| 실행 위치 | `CycleStack/` 루트 고정 | 루트 기준 |

### render.yaml 변경 게이트 ✅ 확정
- 3종 동기화 + 스모크 필수
- Python 버전: 로컬 스모크 → requirements 재빌드 → render.yaml 갱신 → healthz 확인

## 남은 작업
- [x] ~~WSGIMiddleware 제약 사항~~ → todo에 기록 완료
- [x] ~~로컬 개발 PYTHONPATH 해결~~ → 루트 실행 표준으로 확정 (수동 설정 금지)
- [x] ~~render.yaml 변경 시 체크리스트~~ → 3종 동기화 + 스모크 확정
- [x] ~~Render↔.env 동기화 규칙~~ → .env.template SSOT + 3종 동기화 확정

## 다음 액션
1. **전체 설계 확정 완료** ✅
2. **검증 체크리스트 완료** — 정적 분석 6항목 (5 PASS + 1 CONDITIONAL PASS)
3. `root rule105 root_00003` → 완료 처리
