from tasks import get_access_token, get_tasks
from messaging import send_message

def daily_update():
    token = get_access_token()
    tasks = get_tasks(token)
    message = "Here are your tasks for today:\n"
    for task in tasks:
        message += f"- {task['title']}\n"
    send_message("YOUR_CHAT_ID", message)

if __name__ == "__main__":
    daily_update()
