"""바이크채널 인스타그램 캐러셀 자동 게시 스크립트.

깃허브 액션에서 실행합니다. 게시할 폴더(예: 2026-11-23-marquez-motogp-champion)에
카드 이미지(*.jpg, 파일 이름 순서대로 게시)와 caption.txt(게시글 멘트)를 두고,
publish.json 파일을 추가해 푸시하면 이 스크립트가 메타 공식 API로 게시합니다.

필요한 깃허브 비밀값(Settings > Secrets and variables > Actions):
  META_TOKEN  : 메타 시스템 사용자 액세스 토큰
                (권한: instagram_basic, instagram_content_publish,
                 pages_show_list, pages_read_engagement, business_management)
선택 비밀값:
  IG_USER_ID  : 인스타그램 비즈니스 계정 ID. 없으면 토큰으로 자동 조회합니다.
"""

import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

GRAPH = "https://graph.facebook.com/v21.0"
REPO = os.environ.get("GITHUB_REPOSITORY", "southjade1224/bikechannel-cardnews")
SHA = os.environ.get("GITHUB_SHA", "main")


def call(method, path, params):
    params = dict(params)
    params["access_token"] = os.environ["META_TOKEN"]
    data = urllib.parse.urlencode(params).encode()
    url = f"{GRAPH}/{path}"
    if method == "GET":
        req = urllib.request.Request(f"{url}?{data.decode()}")
    else:
        req = urllib.request.Request(url, data=data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        raise SystemExit(f"API 오류 {e.code} ({path}): {body}")


def find_ig_user_id():
    if os.environ.get("IG_USER_ID"):
        return os.environ["IG_USER_ID"]
    pages = call("GET", "me/accounts", {"fields": "name,instagram_business_account{id,username}"})
    for p in pages.get("data", []):
        ig = p.get("instagram_business_account")
        if ig:
            print(f"인스타그램 계정: @{ig.get('username')} ({ig['id']}) / 페이지: {p.get('name')}")
            return ig["id"]
    raise SystemExit("토큰으로 연결된 인스타그램 비즈니스 계정을 찾지 못했습니다.")


def wait_ready(container_id):
    for _ in range(30):
        st = call("GET", container_id, {"fields": "status_code,status"})
        code = st.get("status_code")
        if code == "FINISHED":
            return
        if code in ("ERROR", "EXPIRED"):
            raise SystemExit(f"미디어 처리 실패: {st}")
        time.sleep(5)
    raise SystemExit("미디어 처리 대기 시간 초과")


def publish(folder):
    if os.path.exists(os.path.join(folder, "published.json")):
        print(f"{folder}: 이미 게시된 폴더라 건너뜁니다.")
        return
    images = sorted(f for f in os.listdir(folder) if f.lower().endswith((".jpg", ".jpeg")))
    if not 2 <= len(images) <= 10:
        raise SystemExit(f"{folder}: 캐러셀은 이미지 2~10장이 필요합니다(현재 {len(images)}장).")
    with open(os.path.join(folder, "caption.txt"), encoding="utf-8") as f:
        caption = f.read().strip()

    ig = find_ig_user_id()
    children = []
    for name in images:
        url = f"https://raw.githubusercontent.com/{REPO}/{SHA}/{folder}/{urllib.parse.quote(name)}"
        c = call("POST", f"{ig}/media", {"image_url": url, "is_carousel_item": "true"})
        wait_ready(c["id"])
        children.append(c["id"])
        print(f"이미지 등록: {name}")

    carousel = call("POST", f"{ig}/media", {
        "media_type": "CAROUSEL",
        "children": ",".join(children),
        "caption": caption,
    })
    wait_ready(carousel["id"])
    result = call("POST", f"{ig}/media_publish", {"creation_id": carousel["id"]})
    media = call("GET", result["id"], {"fields": "permalink,timestamp"})
    print(f"게시 완료: {media.get('permalink')}")

    with open(os.path.join(folder, "published.json"), "w", encoding="utf-8") as f:
        json.dump({"media_id": result["id"], "permalink": media.get("permalink"),
                   "timestamp": media.get("timestamp")}, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    if sys.argv[1:2] == ["--check"]:
        find_ig_user_id()
        print("토큰 확인 완료: 게시 준비가 됐습니다.")
        raise SystemExit(0)
    folders = [a.strip().strip("/") for a in sys.argv[1:] if a.strip()]
    if not folders:
        raise SystemExit("게시할 폴더가 없습니다.")
    for folder in folders:
        publish(folder)
