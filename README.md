# bikechannel-cardnews

바이크채널 카드뉴스 이미지 저장소입니다. 날짜-주제 폴더(예: `2026-11-23-marquez-motogp-champion`)마다 카드 이미지를 보관합니다.

## 인스타그램 자동 게시

메타 공식 API로 캐러셀을 게시합니다. 인스타그램 웹은 외부 이미지를 막기 때문에, 메타 서버가 이 저장소의 이미지를 직접 가져가는 방식입니다.

1. 폴더에 카드 이미지(`*.jpg`, 파일 이름 순서대로 게시, 2~10장)와 `caption.txt`(게시글 멘트)를 넣습니다.
2. 같은 폴더에 `publish.json`(내용은 `{}`이면 충분)을 추가해 `main`에 푸시합니다.
3. 깃허브 액션 '인스타그램 카드뉴스 게시'가 실행돼 게시하고, 결과를 `published.json`에 남깁니다. `published.json`이 있는 폴더는 다시 게시하지 않습니다.

필요한 비밀값(Settings > Secrets and variables > Actions):

- `META_TOKEN`: 메타 시스템 사용자 액세스 토큰(만료 없음). 권한은 `instagram_basic`, `instagram_content_publish`, `pages_show_list`, `pages_read_engagement`, `business_management`입니다.
- `IG_USER_ID`(선택): 인스타그램 비즈니스 계정 ID입니다. 없으면 토큰으로 자동 조회합니다.

설정 확인은 Actions 탭의 '인스타그램 연결 확인'을 실행하면 됩니다. 이 작업은 게시하지 않고 토큰과 계정만 확인합니다.
