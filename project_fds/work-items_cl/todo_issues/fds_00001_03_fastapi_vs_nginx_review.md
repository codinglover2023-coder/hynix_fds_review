# fds_00001 — 구현 방식 비교 검토: FastAPI vs Nginx

todo_idx: fds_00001
issue_idx: 03
생성일: 2026-03-04
최종 갱신일: 2026-03-04

---

## 목적

인가 통제 게이트웨이를 **FastAPI (현재 구현)** 방식과 **Nginx (리버스 프록시)** 방식으로 구현했을 때의 차이점을 비교 검토하여, 운영 아키텍처 결정 시 참고자료로 활용한다.

## 비교 요약

| 항목 | FastAPI (현재 구현) | Nginx |
|---|---|---|
| **역할** | 인가 통제 + 프록시 + Admin API | 리버스 프록시 + 정적 라우팅 |
| **인가 제어** | Python 코드 (DB 조회 → 동적 판단) | 설정 파일 기반 (정적 규칙) |
| **서비스 등록** | Admin API로 런타임 CRUD | nginx.conf 수정 + reload |
| **화이트리스트** | DB 기반 동적 관리 | location 블록 정적 정의 |
| **인가 헤더 주입** | auth_type별 Python 분기 로직 | proxy_set_header 정적 설정 |
| **DB 연동** | SQLAlchemy async (네이티브) | 불가 (Lua/njs 모듈 필요) |
| **동적 변경** | API 호출로 즉시 반영 | conf 수정 + `nginx -s reload` |
| **성능** | 중간 (Python async I/O) | 높음 (C 기반 event-driven) |
| **동시 접속** | uvicorn worker 수에 비례 | 수만 연결 처리 가능 |
| **개발 난이도** | 낮음 (Python 생태계) | 중간 (설정 문법 + Lua 확장) |
| **Swagger/문서** | 자동 생성 (`/docs`) | 별도 구성 필요 |
| **테스트** | pytest + httpx (단위/통합) | 수동 curl 또는 별도 도구 |

## 상세 비교

### 1. 인가 제어 (핵심 차이)

#### FastAPI 방식 (현재)
```python
# DB에서 서비스 조회 → 동적 인가 판단
service = await get_service_by_sub_prefix(db, sub_prefix)
if not service.is_active:
    raise HTTPException(403)

allowed = await path_allowed_for_service(db, service.id, path)
if not allowed:
    raise HTTPException(403)

headers.update(build_auth_header(service))  # 동적 헤더 주입
```
- 런타임에 DB 조회로 인가 결정
- Admin API로 서비스 추가/삭제 즉시 반영
- auth_type별 분기 로직 Python으로 자유롭게 확장

#### Nginx 방식
```nginx
# nginx.conf — 정적 설정
upstream confluence {
    server company.atlassian.net:443;
}

location /conf/ {
    proxy_pass https://confluence/;
    proxy_set_header Authorization "Bearer <static_token>";
    proxy_set_header Host company.atlassian.net;
}

location /jira/ {
    proxy_pass https://jira-upstream/;
    proxy_set_header Authorization "Basic <static_base64>";
}
```
- 서비스 추가마다 conf 수정 + reload 필요
- 인가 헤더는 정적 값 (동적 분기 어려움)
- DB 연동 없이 conf 파일이 곧 "레지스트리"

### 2. 화이트리스트 관리

| 관점 | FastAPI | Nginx |
|---|---|---|
| 저장소 | DB `uri_mappings` 테이블 | `location` 블록 |
| 추가/삭제 | Admin API (`POST /mappings`) | conf 편집 + reload |
| 패턴 매칭 | Python prefix 매칭 (Phase 2: regex) | regex 네이티브 지원 (`~`, `~*`) |
| 런타임 반영 | 즉시 | reload 필요 (`nginx -s reload`) |

### 3. 성능 특성

| 지표 | FastAPI | Nginx |
|---|---|---|
| 단순 프록시 처리량 | ~2,000-5,000 RPS (uvicorn) | ~50,000+ RPS |
| 메모리 사용 | 높음 (Python 프로세스) | 낮음 (C 기반 worker) |
| 레이턴시 추가분 | ~5-20ms (DB 조회 + Python) | ~0.5-2ms (설정 lookup) |
| Worker 모델 | async I/O (uvicorn workers) | event-driven (epoll/kqueue) |

> **참고**: FastAPI의 DB 조회 오버헤드는 Redis 캐시(Phase 2) 도입으로 크게 줄일 수 있음

### 4. 운영 관점

| 관점 | FastAPI | Nginx |
|---|---|---|
| 배포 | Docker + Python venv | Docker or OS 패키지 |
| 설정 변경 | API 호출 (무중단) | conf 수정 + reload (순단) |
| 모니터링 | Python logging + middleware | access.log + error.log |
| Health check | `GET /api/healthz` (내장) | `stub_status` 모듈 |
| TLS 종단 | uvicorn `--ssl-*` or 앞단 LB | 네이티브 지원 |
| 수평 확장 | 여러 uvicorn 인스턴스 + LB | 여러 Nginx 인스턴스 + LB |

### 5. 확장성

| 확장 항목 | FastAPI | Nginx |
|---|---|---|
| 사용자별 토큰 위임 | Python 코드 추가 | Lua/njs 스크립트 필요 |
| Rate limit | Python middleware | `limit_req` 모듈 (네이티브) |
| 감사 로깅 | DB 저장 (proxy_logs) | access.log 파싱 |
| OAuth/SSO 연동 | Python 라이브러리 활용 | auth_request + 외부 서비스 |
| A/B 테스트/Canary | Python 로직으로 자유 분기 | `split_clients` or 외부 연동 |

## 각 방식의 장점

### FastAPI 장점
1. **동적 서비스 관리**: Admin API로 런타임 서비스 추가/삭제 (서버 재시작 불필요)
2. **DB 기반 인가 제어**: 복잡한 인가 정책을 Python 코드로 유연하게 구현
3. **Swagger 자동 생성**: API 문서 + 테스트 UI 자동 제공
4. **테스트 용이성**: pytest로 단위/통합 테스트 자동화
5. **확장 자유도**: Phase 2 기능(사용자 위임, OAuth, 감사 로깅)을 Python으로 직접 구현

### Nginx 장점
1. **고성능**: C 기반으로 단순 프록시 처리량이 10x 이상
2. **검증된 안정성**: 프록시/리버스 프록시 전문 도구 (수십 년 실전 검증)
3. **TLS/SSL 네이티브**: 인증서 관리 + TLS 종단 내장
4. **Rate limit 내장**: `limit_req`, `limit_conn` 네이티브 모듈
5. **정적 라우팅 최적화**: 경로 패턴이 고정적일 때 오버헤드 최소

## 각 방식의 한계

### FastAPI 한계
1. **성능 천장**: Python GIL + async I/O 한계로 대용량 트래픽에 불리
2. **프록시 전문 도구 아님**: 프록시 특화 기능 (TLS 종단, 압축, 캐시) 직접 구현 필요
3. **연결 관리**: httpx AsyncClient 풀 크기 제한
4. **인프라 복잡도**: 운영 시 gunicorn + uvicorn worker 튜닝 필요

### Nginx 한계
1. **동적 제어 불가**: 서비스 추가마다 conf 수정 + reload 필요
2. **DB 연동 어려움**: 네이티브 DB 접근 불가 (OpenResty Lua 또는 njs 필요)
3. **복잡한 비즈니스 로직 부적합**: 인가 분기, 토큰 관리 등 conf로 표현 한계
4. **Admin API 없음**: 관리 인터페이스 별도 개발 필요
5. **테스트 자동화 어려움**: 단위 테스트 프레임워크 부재

## 하이브리드 아키텍처 (권장)

운영 환경에서는 **두 방식을 결합한 하이브리드 구조**가 최적:

```
Client
   ↓
Nginx (Edge Layer)
   ├── TLS 종단
   ├── Rate limit (limit_req)
   ├── 정적 자산 서빙
   ├── 기본 접근 제어
   └── proxy_pass ──→ FastAPI (FDS Gateway)
                          ├── 동적 인가 제어 (DB 기반)
                          ├── Admin API (서비스 관리)
                          ├── 인가 헤더 주입
                          └── httpx ──→ 외부 서비스
                                          (Confluence/Jira/...)
```

### 역할 분담

| 계층 | 역할 | 도구 |
|---|---|---|
| **Edge (앞단)** | TLS 종단, Rate limit, 정적 자산, 기본 보안 | Nginx |
| **Gateway (뒷단)** | 동적 인가 제어, DB 관리, Admin API, 헤더 주입 | FastAPI |

### 하이브리드 장점
1. Nginx가 TLS/Rate limit/정적 자산 처리 → FastAPI 부하 경감
2. FastAPI가 동적 인가/DB 제어 전담 → 비즈니스 로직 유연성 유지
3. Nginx 캐시로 반복 요청 가속 가능
4. 각 계층 독립 스케일링 가능

## 현재 구현 (FastAPI) 선택 근거

| 판단 기준 | 평가 |
|---|---|
| **MVP 속도** | FastAPI로 빠르게 프로토타입 + 검증 완료 (28/28 PASS) |
| **동적 관리 필수** | 서비스 등록/삭제가 Admin API로 런타임 제어 → Nginx conf 방식 부적합 |
| **DB 기반 화이트리스트** | 고객 요구사항 핵심 → Nginx 단독 불가 |
| **인가 헤더 분기** | auth_type별 동적 주입 → Python 코드 필수 |
| **Phase 2 확장** | 사용자 위임, OAuth, 감사 로깅 → Python 구현이 자연스러움 |
| **성능 요구** | MVP 단계에서 대용량 트래픽 없음 → FastAPI 충분 |

## 결론

1. **MVP 단계**: FastAPI 단독 구현이 적합 (현재 완료)
2. **운영 전환 시**: Nginx(Edge) + FastAPI(Gateway) 하이브리드 권장
3. **Nginx 단독은 부적합**: DB 기반 동적 인가 제어 요구사항에 맞지 않음

## 다음 액션

1. 운영 전환 시 Nginx Edge Layer 구성 검토 (Phase 2 이후)
2. FastAPI 성능 병목 발생 시 Redis 캐시 도입 우선 검토
