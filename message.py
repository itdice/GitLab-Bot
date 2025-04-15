import os
import httpx
from dotenv import load_dotenv

# Environments 불러오기
load_dotenv()
MATTERMOST_LINK = os.getenv("MATTERMOST_LINK")

# Bar 색상 설정
BLUE_COLOR = "#27b8d9"
GREEN_COLOR = "#21b838"
YELLOW_COLOR = "#f7f020"
ORANGE_COLOR = "#ed5e0c"
RED_COLOR = "#d90707"
GRAY_COLOR = "#919191"

# Emoji 설정
GITLAB_EMOJI = ":gitlab:"
BOX_EMOJI = "📦"
PUSH_EMOJI = "🚀"
COMPARE_EMOJI = "🔍"
REQUEST_EMOJI = "📣"
ACCEPT_EMOJI = "✅"
DENY_EMOJI = "⛔"
UPDATE_EMOJI = "🔄"
UNKNOWN_EMOJI = "🧐"
TRASH_EMOJI = "🗑️"
CREATE_EMOJI = "🌱"


async def handle_pushes(payload: dict):
    repo_name = payload['repository']['name']
    user_name = payload['user_name']
    branch_raw = payload['ref']
    commits = payload.get('commits', [])
    commit_count = payload.get('total_commits_count', 0)
    reop_url = payload['project']['web_url']
    before = payload.get('before')
    after = payload.get('after')

    # branch 이름 자르기
    branch = branch_raw
    branch_url = reop_url
    if branch_raw.startswith('refs/heads/'):
        branch = branch_raw[len('refs/heads/'):]
        branch_url = reop_url + '/-/tree/' + branch

    # commit 정보 생성
    color = GRAY_COLOR
    emoji = UNKNOWN_EMOJI
    action_text = "Unknown Action"
    commit_text = f"{BOX_EMOJI} No commits in this push."

    if commit_count == 0 and after == "0" * 40:  # branch 삭제
        color = GRAY_COLOR
        emoji = TRASH_EMOJI
        action_text = f"{user_name} deleted {branch}"
    elif commit_count >= 0 and before == "0" * 40:  # branch 생성
        color = GREEN_COLOR
        emoji = CREATE_EMOJI
        action_text = f"{user_name} created {branch}"
        if commit_count > 0:
            commit_text = f"- {commits[-1]['message'].strip()} ([`{commits[-1]['id'][:7]}`]({commits[-1]['url']}))"
    else:  # 기존 branch에 commit 추가
        color = BLUE_COLOR
        emoji = PUSH_EMOJI
        action_text = f"{user_name} pushed {commit_count} commit(s) to {branch}"
        commit_text = "\n".join([
            f"- {commit['message'].strip()} ([`{commit['id'][:7]}`]({commit['url']}))"
            for commit in commits
        ])

    if commit_count == 0 and after == "0" * 40:  # branch 삭제는 링크가 없어야하므로 따로 관리
        message = {
            "username": "GitLab Bot",
            "icon_url": "https://about.gitlab.com/images/press/logo/png/gitlab-icon-rgb.png",
            "attachments": [
                {
                    "color": color,
                    "pretext": f"{GITLAB_EMOJI} GitLab Push Notification for `{repo_name}`",
                    "title": f"{emoji} {action_text}",
                    "footer": "GitLab Bot By IT DICE"
                }
            ]
        }
    else:
        message = {
            "username": "GitLab Bot",
            "icon_url": "https://about.gitlab.com/images/press/logo/png/gitlab-icon-rgb.png",
            "attachments": [
                {
                    "color": color,
                    "pretext": f"{GITLAB_EMOJI} GitLab Push Notification for `{repo_name}`",
                    "title": f"{emoji} {action_text}",
                    "title_link": branch_url,
                    "text": commit_text,
                    "footer": "GitLab Bot By IT DICE"
                }
            ]
        }

    async with httpx.AsyncClient() as client:
        await client.post(MATTERMOST_LINK, json=message)


async def handle_merge_request(payload: dict):
    repo_name = payload['project']['name']
    user_name = payload['user']['name']
    reop_url = payload['project']['web_url']
    merge_object = payload['object_attributes']

    # merge 정보
    action = merge_object.get('action')
    source_branch = merge_object.get('source_branch')
    target_branch = merge_object.get('target_branch')
    title = merge_object.get('title')
    description = merge_object.get('description')
    merge_id = merge_object.get('iid')
    merge_url = merge_object.get('url')

    source_url = reop_url + '/-/tree/' + source_branch
    target_url = reop_url + '/-/tree/' + target_branch

    color = GRAY_COLOR
    emoji = UNKNOWN_EMOJI
    action_text = "Unknown Action"

    if action == "open" or action == "reopen":
        color = YELLOW_COLOR
        emoji = REQUEST_EMOJI
        action_text = "opened a new Merge Request"
    elif action == "update":
        color = BLUE_COLOR
        emoji = UPDATE_EMOJI
        action_text = "updated a Merge Request"
    elif action == "merge":
        color = GREEN_COLOR
        emoji = ACCEPT_EMOJI
        action_text = "merged a Merge Request"
    elif action == "close":
        color = RED_COLOR
        emoji = DENY_EMOJI
        action_text = "closed a Merge Request"

    # merge 요약 정보 생성
    merge_text = (f"**{title}** ([`{merge_id}`]({merge_url}))\n"
                  f"[`{source_branch}`]({source_url}) → [`{target_branch}`]({target_url})\n"
                  f"{description}\n")

    # 최종 message 생성
    message = {
        "username": "GitLab Bot",
        "icon_url": "https://about.gitlab.com/images/press/logo/png/gitlab-icon-rgb.png",
        "attachments": [
            {
                "color": color,
                "pretext": f"{GITLAB_EMOJI} GitLab Merge Request Notification for `{repo_name}` ",
                "title": f"{emoji} {user_name} {action_text}",
                "title_link": merge_url,
                "text": merge_text,
                "footer": "GitLab Bot By IT DICE"
            }
        ]
    }

    async with httpx.AsyncClient() as client:
        await client.post(MATTERMOST_LINK, json=message)
