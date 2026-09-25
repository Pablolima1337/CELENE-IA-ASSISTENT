import os
import shutil
import time

import psutil


class SystemMonitor:
    def __init__(self):
        # Primeira leitura de CPU costuma ser imprecisa,
        # então fazemos uma leitura inicial.
        psutil.cpu_percent(interval=None)

    def get_cpu(self):
        return {
            "usage": psutil.cpu_percent(
                interval=0.15
            ),
            "cores_physical": psutil.cpu_count(
                logical=False
            ),
            "cores_logical": psutil.cpu_count(
                logical=True
            ),
            "frequency": self._get_cpu_frequency()
        }

    def _get_cpu_frequency(self):
        try:
            frequency = psutil.cpu_freq()

            if not frequency:
                return None

            return round(
                frequency.current,
                0
            )

        except Exception:
            return None

    def get_memory(self):
        memory = psutil.virtual_memory()

        return {
            "usage": memory.percent,

            "total_gb": round(
                memory.total
                / (1024 ** 3),
                2
            ),

            "used_gb": round(
                memory.used
                / (1024 ** 3),
                2
            ),

            "available_gb": round(
                memory.available
                / (1024 ** 3),
                2
            )
        }

    def get_disks(self):
        disks = []

        partitions = psutil.disk_partitions(
            all=False
        )

        seen = set()

        for partition in partitions:
            device = partition.device

            if device in seen:
                continue

            seen.add(device)

            try:
                usage = psutil.disk_usage(
                    partition.mountpoint
                )

                disks.append({
                    "device": device,

                    "mountpoint":
                        partition.mountpoint,

                    "filesystem":
                        partition.fstype,

                    "usage":
                        usage.percent,

                    "total_gb": round(
                        usage.total
                        / (1024 ** 3),
                        2
                    ),

                    "used_gb": round(
                        usage.used
                        / (1024 ** 3),
                        2
                    ),

                    "free_gb": round(
                        usage.free
                        / (1024 ** 3),
                        2
                    )
                })

            except (
                PermissionError,
                OSError
            ):
                continue

        return disks

    def get_gpu(self):
        """
        Tenta obter utilização da GPU no Windows
        usando contadores de desempenho do sistema.

        Caso não consiga, retorna dados básicos.
        """

        if os.name != "nt":
            return {
                "name": None,
                "usage": None,
                "memory_usage": None
            }

        try:
            return self._get_windows_gpu()

        except Exception as error:
            print(
                "[SYSTEM] GPU monitor error:",
                error
            )

            return {
                "name": "GPU",
                "usage": None,
                "memory_usage": None
            }

    def _get_windows_gpu(self):
        try:
            import subprocess

            command = [
                "powershell",
                "-NoProfile",
                "-Command",
                (
                    "Get-Counter "
                    "'\\GPU Engine(*)\\Utilization Percentage' "
                    "| Select-Object "
                    "-ExpandProperty CounterSamples "
                    "| Measure-Object "
                    "-Property CookedValue "
                    "-Sum "
                    "| Select-Object "
                    "-ExpandProperty Sum"
                )
            ]

            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=4
            )

            raw = result.stdout.strip()

            if not raw:
                usage = None

            else:
                raw = raw.replace(
                    ",",
                    "."
                )

                usage = float(raw)

                usage = min(
                    100,
                    round(
                        usage,
                        1
                    )
                )

        except Exception:
            usage = None

        name = self._get_gpu_name()

        return {
            "name": name,
            "usage": usage,
            "memory_usage": None
        }

    def _get_gpu_name(self):
        try:
            import subprocess

            command = [
                "powershell",
                "-NoProfile",
                "-Command",
                (
                    "Get-CimInstance Win32_VideoController "
                    "| Select-Object "
                    "-ExpandProperty Name "
                    "| Select-Object -First 1"
                )
            ]

            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=4
            )

            name = result.stdout.strip()

            if name:
                return name

        except Exception:
            pass

        return "GPU"

    def get_uptime(self):
        boot_time = psutil.boot_time()

        seconds = int(
            time.time()
            - boot_time
        )

        days, remainder = divmod(
            seconds,
            86400
        )

        hours, remainder = divmod(
            remainder,
            3600
        )

        minutes, _ = divmod(
            remainder,
            60
        )

        return {
            "days": days,
            "hours": hours,
            "minutes": minutes,

            "formatted": (
                f"{days}d "
                f"{hours:02d}h "
                f"{minutes:02d}m"
            )
        }

    def get_all(self):
        return {
            "cpu": self.get_cpu(),
            "gpu": self.get_gpu(),
            "memory": self.get_memory(),
            "disks": self.get_disks(),
            "uptime": self.get_uptime()
        }