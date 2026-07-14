"""조회 API 수동 검증"""

import sys

import httpx

# sys.argv: 프로그램을 실행할 때 입력한 명령줄 인수를 담고 있는 리스트 ex) python test.py 570 5


def main() -> None:
    appid = int(sys.argv[1]) if len(sys.argv) > 1 else 570
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    base_url = sys.argv[3] if len(sys.argv) > 3 else "http://localhost:8000"

    url = f"{base_url}/reviews/{appid}"
    response = httpx.get(url, params={"limit": limit})
    response.raise_for_status()

    reviews = response.json()
    print(f"GET {response.url} → {response.status_code}")
    print(f"조회: appid={appid} {len(reviews)}개")
    for i, review in enumerate(reviews, start=1):
        preview = review["content"].replace("\n", " ")[:50]
        flag = "추천" if review["voted_up"] else "비추천"
        print(f"[{i}] {flag} {preview}")


if __name__ == "__main__":
    main()
