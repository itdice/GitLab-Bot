# GitLab Notification Bot for Mattermost

이 프로젝트는 **GitLab Webhook 이벤트를 Mattermost 채널에 알림으로 전송**해주는 간단한 봇입니다.  
FastAPI 기반으로 구현되었으며, Docker를 이용해 손쉽게 배포할 수 있습니다.


## ✨ 지원 기능

GitLab에서 다음과 같은 이벤트 발생 시, 해당 내용을 Mattermost 채널로 알림을 전송합니다:

- 🌱 새로운 Branch 생성
- 🗑️ 기존 Branch 삭제
- 🚀 새로운 Commits 추가
- 📣 Merge Request 열기
- 🔄 Merge Request 정보 변경
- ✅ Merge Request 승인
- ⛔ Merge Request 닫기


## 📦 알림 예시

### ✅ Push 알림

> 누군가 브랜치에 커밋을 푸시했을 때:

```
🚀 user_name pushed 3 commit(s) to feature/login

- Fix login redirect bug ([`a1b2c3d`](https://gitlab.com/...))
- Add login form validation ([`d4e5f6g`](https://gitlab.com/...))
- Update README ([`h7i8j9k`](https://gitlab.com/...))
```


### 🌱 Branch 생성 / 삭제

```
🌱 user_name created feature/new-feature
🗑️ user_name deleted hotfix/temp-fix
```


### 📣 Merge Request 관련

```
📣 user_name opened a new Merge Request
**Add OAuth2 Login** ([`!23`](https://gitlab.com/...))
[`feature/oauth`] → [`develop`]

Implements login using Google OAuth2
```

---

## 🚀 설치 방법 (Docker 사용)

### 1. `.env` 파일 생성

루트 디렉토리에 `.env` 파일을 만들고 다음 내용을 추가하세요:

```env
GITLAB_WEBHOOK_SECRET=your_secret_token
MATTERMOST_LINK=https://your-mattermost.com/hooks/your-webhook-url
```

> `GITLAB_WEBHOOK_SECRET`은 GitLab Webhook에서 설정한 Token과 일치해야 합니다.  
> `MATTERMOST_LINK`는 Mattermost의 Incoming Webhook URL입니다.


### 2. Docker 빌드 및 실행

```bash
docker compose up --build -d
```

FastAPI 서버는 기본적으로 `http://localhost:4180` 포트에서 실행됩니다.


### 3. GitLab Webhook 설정

GitLab 프로젝트 설정 > Webhooks 메뉴에서 다음과 같이 등록하세요:

- **URL**: `http://your-server-address:4180/gitlab-link`
- **Secret Token**: `.env`에서 설정한 `GITLAB_WEBHOOK_SECRET`과 동일하게 입력
- **Trigger**: `Push events`, `Merge request events` 체크


## 🛠 기술 스택

- Python 3.11.9 +
- FastAPI
- httpx
- dotenv
- Docker / Docker Compose


## 👤 제작자

IT DICE — internal GitLab notification bot

