"""
Invoke 태스크 모음 — 자주 쓰는 명령을 짧은 별칭으로.

실행: `invoke <태스크>` (예: invoke lint) 또는 축약 `inv lint`.
목록: `invoke --list`

핵심: 로컬에서 치는 명령과 CI(.github/workflows/ci.yml)가 부르는 명령을
      "이 파일 한 곳"으로 통일한다 → "내 PC에선 됐는데 CI에서 깨짐" 방지.
"""

from invoke import task  # @task 데코레이터: 함수를 CLI 태스크로 등록

SRC = "src tests"


@task
def lint(c):
    """Ruff 린트 검사"""
    c.run(f"ruff check {SRC}")


@task
def fmt(c):
    """Ruff 포매터로 코드 정렬·정돈"""
    c.run(f"ruff format {SRC}")


@task
def typecheck(c):
    """mypy 정적 타입 검사 (설정은 pyproject.toml)"""
    c.run(f"mypy {SRC}")


@task
def test(c):
    """pytest 실행 (test_s 로 시작하는 함수를 자동 수집해 돌림)"""
    c.run("pytest")


@task
def up(c):
    """인프라 컨테이너 기동 (Postgre 등) - background"""
    c.run("docker compose up -d")


@task
def down(c):
    """인프라 컨테이너 중지, 정리"""
    c.run("docker compose down")


@task
def check(c):
    """커밋 전 한방 검사: lint -> typecheck를 순서대로 실행"""
    print("check완료: lint -> typecheck 통과")
