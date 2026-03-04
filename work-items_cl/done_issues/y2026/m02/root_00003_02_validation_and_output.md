# root_00003_02: Validation and Output

대상 todo: `root_00003_entrypoint_and_deployment_rules.md`

## 목적
- root_00003 완료 시 검증할 항목과 최종 산출물을 정의한다.

## 현재 결정사항

### 전 섹션 확정 완료
- 섹션 1~6 전체 사용자 결정 완료, todo 문서 반영 완료

### 최종 산출물
1. `render.yaml` — 최종 확정본 ✅ 검증 완료
2. `.env.template` — 모든 필요 환경 변수 키 포함 ✅ 검증 완료
3. root_00003 todo 문서 — 전체 체크박스 완료 상태 ✅

### 검증 체크리스트 (정적 분석 — rule102 수행)
- [x] `render.yaml`과 실물 코드의 entrypoint가 일치하는가 — **PASS**
  - `render_api/main.py`에 `app = fastapi_app` 변수 존재 확인
  - `render_cron/main.py`에 `if __name__ == "__main__": main()` 블록 존재 확인
  - `buildCommand`의 requirements 경로 정확
- [x] `render_api/requirements.txt`로 FastAPI+Flask 실행 가능한가 — **PASS**
  - fastapi>=0.115.0, uvicorn[standard]>=0.30.0, flask>=3.1.0, python-dotenv>=1.0.0 포함
  - 코드 import 대조 완료 (FastAPI, WSGIMiddleware, Flask, jsonify)
- [x] `render_cron/requirements.txt`로 cron 실행 가능한가 — **PASS**
  - schedule>=1.2.0 포함, 코드 import 대조 완료
- [x] `.env.template`의 키 목록이 `common_data/config.py`와 일치하는가 — **CONDITIONAL PASS**
  - ENV, DEBUG — 양쪽 일치
  - B2_KEY_ID, B2_APP_KEY, B2_ENDPOINT, B2_BUCKET_NAME — .env.template에만 존재 (미구현 placeholder, 기능 구현 시 config.py 추가 필요)
  - PORT — Render 자동 주입, uvicorn CLI 인자 → config.py 참조 불필요
- [x] `/api/healthz`와 `/web/healthz` 둘 다 응답하는가 — **PASS**
  - `/api/healthz`: render_api/app/routes.py @app.get("/api/healthz")
  - `/web/healthz`: render_web/app/routes.py @app.route("/healthz") + WSGIMiddleware "/web" 마운트
- [x] PYTHONPATH 없이 `common_data` import가 가능한가 — **PASS**
  - common_data/__init__.py 존재
  - 루트 실행 시 CWD가 sys.path에 포함 → 자동 인식

### 검증 방법
1. 로컬 스모크 테스트 (런타임 검증) — ✅ **실행 완료**:
   ```bash
   pip install -r render_api/requirements.txt   # ✅ 성공
   uvicorn render_api.main:app --port 8000       # ✅ 서버 기동
   curl http://localhost:8000/api/healthz         # ✅ {"ok":true,"via":"fastapi"}
   curl http://localhost:8000/web/healthz         # ✅ {"ok":true,"via":"flask"}
   curl http://localhost:8000/                    # ✅ {"project":"CycleStack","status":"running"}
   ```
   - 실행 환경: Python 3.12.10, Windows 10
   - 패키지: fastapi 0.134.0, uvicorn 0.41.0, flask 3.1.3
2. render.yaml 정합성: `render.yaml`의 buildCommand/startCommand 확인 — ✅ 정적 분석 완료
3. 환경 변수 대조: `.env.template` 키 vs `config.py` 참조 키 — ✅ 정적 분석 완료

## 남은 작업
- [x] render.yaml 정합성 확인 — 정적 분석 완료
- [x] 환경 변수 대조 — 정적 분석 완료
- [x] 로컬 스모크 테스트 실행 — ✅ 3개 endpoint 모두 응답 확인

## 다음 액션
1. `root rule105 root_00003` → 완료 처리
