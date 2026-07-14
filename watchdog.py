# -*- coding: utf-8 -*-
"""
watchdog.py -- 进程自愈守护

常驻监控本地 8765 端口。若服务进程崩溃 / 端口无监听，
自动重新拉起 `python server.py` 并跟踪其子进程 PID。

设计要点（P8 闭环，考虑边界 case）：
- 端口被"别人"占用时不抢、不杀，仅记录（避免误杀真实服务）。
- 只在端口"无人监听"时才启动，天然规避僵尸端口冲突。
- 子进程以无窗口 + 日志重定向方式启动，崩溃输出落盘 server_runtime.log。
- 优雅停止：同目录放 watchdog.stop 文件即退出（服务子进程保留运行）。
- 自带 PID 文件 watchdog.pid，便于排查。

启动入口：守护进程.bat
"""
import os
import sys
import time
import socket
import subprocess

DIR = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(DIR, "watchdog.log")
SERVER_LOG = os.path.join(DIR, "server_runtime.log")
PID_FILE = os.path.join(DIR, "watchdog.pid")
STOP_FILE = os.path.join(DIR, "watchdog.stop")
PORT = 8765
CHECK_INTERVAL = 10  # 秒
PY = sys.executable

# Windows 无窗口标志；非 Windows 忽略
CREATE_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)


def log(msg):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = "[%s] %s" % (ts, msg)
    print(line, flush=True)
    try:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def port_open():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    try:
        return s.connect_ex(("127.0.0.1", PORT)) == 0
    finally:
        s.close()


def is_alive(pid):
    if not pid:
        return False
    try:
        os.kill(pid, 0)
        return True
    except Exception:
        return False


def start_server():
    """拉起 server.py，返回子进程 PID；失败返回 None。"""
    try:
        with open(SERVER_LOG, "a", encoding="utf-8") as sl:
            sl.write("\n%s [watchdog] launching server.py\n" % time.strftime("%Y-%m-%d %H:%M:%S"))
            proc = subprocess.Popen(
                [PY, "server.py"],
                cwd=DIR,
                stdout=sl,
                stderr=subprocess.STDOUT,
                creationflags=CREATE_NO_WINDOW,
            )
        return proc.pid
    except Exception as e:
        log("[watchdog] FAILED to start server: %s" % e)
        return None


def main():
    try:
        with open(PID_FILE, "w", encoding="utf-8") as f:
            f.write(str(os.getpid()))
    except Exception:
        pass

    log("watchdog started, monitoring port %d (pid=%d)" % (PORT, os.getpid()))
    restart_count = 0
    child_pid = None

    while True:
        # 优雅停止信号
        if os.path.exists(STOP_FILE):
            try:
                os.remove(STOP_FILE)
            except Exception:
                pass
            log("stop file detected -> exiting (server child pid=%s left running)" % child_pid)
            break

        if not port_open():
            log("port %d NOT listening -> evaluating restart" % PORT)
            if child_pid and not is_alive(child_pid):
                log("previous child pid %s is dead, clearing" % child_pid)
                child_pid = None
            if child_pid is None:
                new_pid = start_server()
                if new_pid:
                    child_pid = new_pid
                    restart_count += 1
                    log("started server.py, child pid=%s (restart #%d)" % (child_pid, restart_count))
            else:
                log("child pid %s alive but port closed? waiting next cycle" % child_pid)
        else:
            # 端口正常；若我们跟踪的子进程已死，说明服务被外部接管，重置跟踪
            if child_pid and not is_alive(child_pid):
                log("port open but our child %s died (service now externally managed)" % child_pid)
                child_pid = None

        time.sleep(CHECK_INTERVAL)

    try:
        os.remove(PID_FILE)
    except Exception:
        pass
    log("watchdog exited (restart_count=%d)" % restart_count)


if __name__ == "__main__":
    main()
