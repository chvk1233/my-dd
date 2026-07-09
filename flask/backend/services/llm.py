import config


def generate_report(event: dict, analysis: dict) -> str:
    if config.LLM_PROVIDER == "mock":
        return _mock_report(event, analysis)
    return _mock_report(event, analysis)


def generate_tasks(event: dict, analysis: dict) -> str:
    if config.LLM_PROVIDER == "mock":
        return _mock_tasks(event, analysis)
    return _mock_tasks(event, analysis)


def _mock_report(event: dict, analysis: dict) -> str:
    event_type = event.get("event_type", "unknown")
    severity = analysis.get("severity") or event.get("severity", "medium")
    message = event.get("message", "")
    predicted = analysis.get("predicted_type", event_type)

    return f"""[점장 보고서]

■ 사건 요약
- 사건 ID: {event.get('event_id')}
- 유형: {predicted} ({event_type})
- 내용: {message}

■ 심각도: {severity}

■ 고객 불만 원인
- {message}에 따른 고객 불편/문의가 접수되었습니다.

■ 권장 대응
- 고객에게 처리 현황을 즉시 안내하고, 예상 완료 시각을 공유합니다.
- 현장 직원에게 우선 처리를 지시합니다.

■ 재발 방지 포인트
- 유사 사건 재발 시 신속 대응 프로세스를 점검합니다.
- 관련 운영 매뉴얼을 팀 공유합니다.
"""


def _mock_tasks(event: dict, analysis: dict) -> str:
    severity = analysis.get("severity") or event.get("severity", "medium")
    message = event.get("message", "")

    return f"""[직원 체크리스트]

■ 즉시 확인할 항목
- 사건 내용 확인: {message}
- 현재 처리 상태 및 담당자 배정

■ 고객에게 안내할 내용
- 접수 완료 및 처리 진행 상황 안내
- 예상 처리 시간 공유 (심각도: {severity})

■ 점장에게 보고할 내용
- 사건 ID {event.get('event_id')} 처리 현황
- 추가 지원 필요 여부

■ 후속 처리
- 처리 완료 후 고객 만족도 확인
- 사건 기록 보관 및 유사 사건 예방 점검
"""
