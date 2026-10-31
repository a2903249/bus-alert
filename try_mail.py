from app.services.notifier import send_email, build_arrival_message

subject, body = build_arrival_message("105", "生產路口", 290)
send_email("ben1010105@gmail.com", subject, body)
print("寄出完成")