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
APPROVED_EMOJI = "👍"
ACCEPT_EMOJI = "✅"
DENY_EMOJI = "⛔"
UPDATE_EMOJI = "🔄"
UNKNOWN_EMOJI = "🧐"
TRASH_EMOJI = "🗑️"
CREATE_EMOJI = "🌱"
RUNNING_EMOJI = "⌛"
RELEASE_EMOJI = "🎉"


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
    repo_url = payload['project']['web_url']
    merge_object = payload['object_attributes']

    # merge 정보
    action = merge_object.get('action')
    source_branch = merge_object.get('source_branch')
    target_branch = merge_object.get('target_branch')
    title = merge_object.get('title')
    description = merge_object.get('description')
    merge_id = merge_object.get('iid')
    merge_url = merge_object.get('url')

    source_url = repo_url + '/-/tree/' + source_branch
    target_url = repo_url + '/-/tree/' + target_branch

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
    elif action == "approved":
        color = ORANGE_COLOR
        emoji = APPROVED_EMOJI
        action_text = "approved a Merge Request"
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


async def handle_pipeline(payload: dict):
    repo_name = payload['project']['name']
    user_name = payload['user']['name']
    repo_url = payload['project']['web_url']
    pipeline = payload['object_attributes']

    status = pipeline['status']
    ref = pipeline['ref']
    pipeline_id = pipeline['id']
    pipeline_url = pipeline['url']

    color = GRAY_COLOR
    emoji = UNKNOWN_EMOJI
    status_text = "Pipeline status unknown"

    if status == "running":
        color = BLUE_COLOR
        emoji = RUNNING_EMOJI
        status_text = "started a Pipeline"
    elif status == "success":
        color = GREEN_COLOR
        emoji = ACCEPT_EMOJI
        status_text = "pipeline Succeeded"
    elif status == "failed":
        color = RED_COLOR
        emoji = DENY_EMOJI
        status_text = "pipeline Failed"
    else:
        return

    pipeline_text = (f"**Pipeline ID:** [`{pipeline_id}`]({pipeline_url})\n"
                     f"**Branch:** [`{ref}`]({repo_url}/-/tree/{ref})")

    message = {
        "username": "GitLab Bot",
        "icon_url": "https://about.gitlab.com/images/press/logo/png/gitlab-icon-rgb.png",
        "attachments": [
            {
                "color": color,
                "pretext": f"{GITLAB_EMOJI} GitLab Pipeline Notification for `{repo_name}`",
                "title": f"{emoji} {user_name} {status_text}",
                "title_link": pipeline_url,
                "text": pipeline_text,
                "footer": "GitLab Bot By IT DICE"
            }
        ]
    }

    async with httpx.AsyncClient() as client:
        await client.post(MATTERMOST_LINK, json=message)


async def handle_release(payload: dict):
    action = payload.get('action')
    if action != 'create':
        return

    repo_name = payload['project']['name']
    author_name = (
            payload.get('author', {}).get('name') or
            payload.get('user', {}).get('name') or
            payload.get('commit', {}).get('author', {}).get('name') or "Unknown"
    )
    repo_url = payload['project']['web_url']
    release_name = payload['name']
    tag = payload['tag']
    release_url = payload['url']
    description = payload.get('description', '')

    color = GREEN_COLOR
    emoji = RELEASE_EMOJI
    title_text = f"released `{release_name}`"

    release_text = (
        f"**Tag:** [`{tag}`]({repo_url}/-/tags/{tag})\n"
        f"{description}"
    )

    message = {
        "username": "GitLab Bot",
        "icon_url": "https://about.gitlab.com/images/press/logo/png/gitlab-icon-rgb.png",
        "attachments": [
            {
                "color": color,
                "pretext": f"{GITLAB_EMOJI} GitLab Release Notification for `{repo_name}`",
                "title": f"{emoji} {author_name} {title_text}",
                "title_link": release_url,
                "text": release_text,
                "footer": "GitLab Bot By IT DICE"
            }
        ]
    }

    async with httpx.AsyncClient() as client:
        await client.post(MATTERMOST_LINK, json=message)