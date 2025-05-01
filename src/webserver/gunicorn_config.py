import multiprocessing

# 核心数 × 2 + 1
workers = multiprocessing.cpu_count() * 2 + 1
# 每个 worker 的线程数
threads = 2
# 请求超时时间（秒）
timeout = 120
# 保持连接
keepalive = 5
# 最大请求数后重启 worker
max_requests = 1000
# 错误日志
errorlog = "log/error.log"
# 访问日志
accesslog = "log/access.log"
# 预加载应用
preload_app = True