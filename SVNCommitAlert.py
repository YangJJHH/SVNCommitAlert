import subprocess
import time
from plyer import notification
from datetime import datetime

def get_latest_revision(repo_path):
    result = subprocess.run(["svn", "info", "-r", "HEAD", "--show-item", "revision", repo_path], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"SVN 명령어 실행 중 오류 발생: {result.stderr}")
        return None
    return int(result.stdout.strip())

def get_commit_message(repo_path, revision):
    result = subprocess.run(["svn", "log", "-r", str(revision), repo_path], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"SVN 명령어 실행 중 오류 발생: {result.stderr}")
        return None
    
    log_lines = result.stdout.strip().split('\n')
    if len(log_lines) < 2:
        return None

    # 리비전, 작성자, 메시지를 파싱
    rev_author_info = log_lines[1].split('|')
    if len(rev_author_info) < 2:
        return None
    
    revision = rev_author_info[0].strip()
    author = rev_author_info[1].strip()
    message = log_lines[3].strip() if len(log_lines) > 3 else "No commit message."

    return f"리비전: {revision}\n작성자: {author}\n메시지: {message}"

def show_notification(revision, message = "Message : "):
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    notification_message = f"메시지: {message}\n현재 시각: {current_time}"

    print(f"알림 메시지: {notification_message}")  # 디버깅 출력

    notification.notify(
        title="SVN Commit Notice!",
        message=notification_message,
        app_name="Commit Alert",
        timeout=10
    )

def read_repo_path(file_path):
    try:
        with open(file_path, 'r') as file:
            repo_path = file.readline().strip()
            return repo_path
    except FileNotFoundError:
        print(f"파일을 찾을 수 없습니다: {file_path}")
        return None
    except Exception as e:
        print(f"파일을 읽는 중 오류가 발생했습니다: {e}")
        return None

def monitor_svn(repo_path, interval=60):
    latest_revision = get_latest_revision(repo_path)
    if latest_revision is None:
        print("초기 리비전을 가져오는 데 실패했습니다.")
        return
    print("SVN 연결성공. 대기중...")
    while True:
        new_revision = get_latest_revision(repo_path)
        print(f"최신 리비전 : {new_revision}")
        if new_revision is None:
            continue

        if new_revision > latest_revision:
            commit_message = get_commit_message(repo_path, new_revision)
            if commit_message:
                show_notification(new_revision, commit_message)
            else:
                show_notification(new_revision)
            latest_revision = new_revision
        
        time.sleep(interval)

if __name__ == "__main__":
    try:
        repo_path_file = "repo_path.txt"  # 여기서 텍스트 파일 경로를 설정하세요
        repo_path = read_repo_path(repo_path_file)
        if repo_path:
            monitor_svn(repo_path,10)
        else:
            print("저장소 경로를 읽는 데 실패했습니다.")
    except Exception as e:
        print(f"프로그램 실행 중 오류가 발생했습니다: {e}")
        input("오류가 발생했습니다. 종료하려면 Enter 키를 누르세요...")

# pip로 설치한 패키지 모든 종속성 포함한 실행파일 추출
# pyinstaller --onefile --hidden-import=plyer.platforms.win.notification --hidden-import=plyer.platforms.win --hidden-import=plyer.platforms CommitAlert.py