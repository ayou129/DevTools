import psutil
import platform
import socket
import time

# 全局变量用于存储先前的网络流量和时间戳
prev_net_io_stats = None
prev_timestamp = None

# 获取操作系统信息
def get_system_info():
    system_info = {
        "系统": platform.system(),
        "版本": platform.version(),
        "机器": platform.machine(),
        "处理器": platform.processor()
    }
    return system_info

# 获取CPU信息
def get_cpu_info():
    cpu_info = {
        "CPU核心数": psutil.cpu_count(logical=True),
    }
    try:
        # 尝试获取 CPU 频率
        cpu_freq = psutil.cpu_freq()
        cpu_info["CPU频率"] = f"{cpu_freq.current:.2f} MHz"
    except Exception as e:
        # 如果无法获取 CPU 频率，设置为无法获取
        cpu_info["CPU频率"] = "无法获取 CPU 频率"

    # 获取 CPU 使用率
    cpu_info["CPU负载"] = f"{psutil.cpu_percent(interval=1)}%"
    
    return cpu_info

# 获取内存信息
def get_memory_info():
    memory_info = psutil.virtual_memory()
    mem_info = {
        "总内存": f"{memory_info.total / (1024**3):.2f} GB",  # 转换为GB
        "已使用内存": f"{memory_info.used / (1024**3):.2f} GB",
        "空闲内存": f"{memory_info.free / (1024**3):.2f} GB",
        "内存使用率": f"{memory_info.percent}%"
    }
    return mem_info

# 获取交换机信息
def get_swap_info():
    swap_info = psutil.swap_memory()
    swap_mem_info = {
        "交换区总容量": f"{swap_info.total / (1024**3):.2f} GB",
        "已使用交换区": f"{swap_info.used / (1024**3):.2f} GB",
        "空闲交换区": f"{swap_info.free / (1024**3):.2f} GB",
        "交换区使用率": f"{swap_info.percent}%"
    }
    return swap_mem_info

# 格式化系统信息为文本
def format_system_info():
    system_info = get_system_info()
    cpu_info = get_cpu_info()
    memory_info = get_memory_info()
    swap_info = get_swap_info()

    # info_text = f"系统: {system_info['系统']} {system_info['版本']}\n"
    # info_text += f"机器: {system_info['机器']}\n"
    info_text = f"处理器: {system_info['处理器']}\n"
    info_text += f"\nCPU信息：\n"
    info_text += f"CPU核心数: {cpu_info['CPU核心数']}\n"
    info_text += f"CPU频率: {cpu_info['CPU频率']}\n"
    info_text += f"CPU负载: {cpu_info['CPU负载']}%\n"
    info_text += f"\n内存信息：\n"
    info_text += f"总内存: {memory_info['总内存']}\n"
    info_text += f"已使用内存: {memory_info['已使用内存']}\n"
    info_text += f"空闲内存: {memory_info['空闲内存']}\n"
    info_text += f"内存使用率: {memory_info['内存使用率']}%\n"
    info_text += f"\n交换机信息：\n"
    info_text += f"交换区总容量: {swap_info['交换区总容量']}\n"
    info_text += f"已使用交换区: {swap_info['已使用交换区']}\n"
    info_text += f"空闲交换区: {swap_info['空闲交换区']}\n"
    info_text += f"交换区使用率: {swap_info['交换区使用率']}%\n"

    return info_text

# 获取本地IP地址
def get_ip_address():
    # 遍历网络接口
    for interface, addrs in psutil.net_if_addrs().items():
        # 检查每个地址
        for addr in addrs:
            # 使用 socket.AF_INET 来判断 IPv4 地址
            if addr.family == socket.AF_INET:
                # 找到 IPv4 地址
                return addr.address
    return "无法获取 IP 地址"



def get_network_info():
    global prev_net_io_stats, prev_timestamp
    
    # 获取当前时间戳和网络IO统计数据
    current_timestamp = time.time()
    current_net_io_stats = psutil.net_io_counters()
    
    if prev_net_io_stats is not None:
        # 计算时间差异（以秒为单位）
        time_diff = current_timestamp - prev_timestamp
        
        # 计算数据量差异
        upload_diff = current_net_io_stats.bytes_sent - prev_net_io_stats.bytes_sent
        download_diff = current_net_io_stats.bytes_recv - prev_net_io_stats.bytes_recv
        
        # 计算上传速率和下载速率
        upload_rate = (upload_diff / (1024 ** 2)) / time_diff  # 转换为 MB/s
        download_rate = (download_diff / (1024 ** 2)) / time_diff  # 转换为 MB/s
        
        # 将速率转换为 MB/min
        upload_rate_mb_per_min = upload_rate * 60
        download_rate_mb_per_min = download_rate * 60
        
        # 更新网络信息
        net_info = {
            "上传": f"{current_net_io_stats.bytes_sent / (1024 ** 2):.2f} MB",  # 转换为 MB
            "下载": f"{current_net_io_stats.bytes_recv / (1024 ** 2):.2f} MB",  # 转换为 MB
            "上传速率": f"{upload_rate_mb_per_min:.2f} MB/min",
            "下载速率": f"{download_rate_mb_per_min:.2f} MB/min"
        }
    else:
        # 如果这是第一次调用或没有先前的数据，则初始化网络信息
        net_info = {
            "上传": f"{current_net_io_stats.bytes_sent / (1024 ** 2):.2f} MB",  # 转换为 MB
            "下载": f"{current_net_io_stats.bytes_recv / (1024 ** 2):.2f} MB",  # 转换为 MB
            "上传速率": "0.00 MB/min",
            "下载速率": "0.00 MB/min"
        }
    
    # 更新先前的网络流量和时间戳
    prev_net_io_stats = current_net_io_stats
    prev_timestamp = current_timestamp
    
    return net_info

# 格式化网络信息为文本
def format_network_info():
    network_info = get_network_info()
    info_text = f"上传: {network_info['上传']}\n"
    info_text += f"下载: {network_info['下载']}\n"
    info_text += f"上传速率: {network_info['上传速率']}\n"
    info_text += f"下载速率: {network_info['下载速率']}\n"
    
    return info_text

def format_network_ip():
    return get_ip_address()
