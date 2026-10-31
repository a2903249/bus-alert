from apscheduler.schedulers.background import BackgroundScheduler

from app.services.poller import run_poll_once

scheduler = BackgroundScheduler()


def start_scheduler() -> None:
    scheduler.add_job(
        run_poll_once,
        "interval",
        seconds=60,
        id="poll_buses",
        max_instances=1,   # 上一輪還沒跑完，就不開新的一輪
        coalesce=True,
    )
    scheduler.start()


def stop_scheduler() -> None:
    scheduler.shutdown(wait=False)