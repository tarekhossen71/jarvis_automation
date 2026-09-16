import psutil

from core.watcher import Watcher
from tools.watchers.network_analyzer import NetworkAnalyzer

class NetworkWatcher(Watcher):

    def __init__(self, callback=None):

        super().__init__(
            name="network_watcher",
            interval=5,
            callback=callback,
        )

        self.known_connections = set()

        self._load_existing_connections()

    # =========================================================
    # LOCAL ADDRESS CHECK
    # =========================================================

    @staticmethod
    def _is_local_address(ip):

        if not ip:
            return True

        return ip in (
            "127.0.0.1",
            "::1",
            "0.0.0.0",
            "::",
        )

    # =========================================================
    # CONNECTION KEY
    # =========================================================

    def _connection_key(self, connection):

        try:

            pid = connection.pid
            status = connection.status

            # Ignore PID 0
            if not pid:
                return None

            local_address = connection.laddr
            remote_address = connection.raddr

            if not remote_address:
                return None

            local_ip = ""
            local_port = 0

            remote_ip = ""
            remote_port = 0

            if local_address:

                local_ip = local_address.ip
                local_port = local_address.port

            if remote_address:

                remote_ip = remote_address.ip
                remote_port = remote_address.port

            # Ignore loopback connections
            if self._is_local_address(remote_ip):
                return None

            # Ignore TIME_WAIT
            if status == psutil.CONN_TIME_WAIT:
                return None

            return (
                pid,
                local_ip,
                local_port,
                remote_ip,
                remote_port,
                status,
            )

        except Exception:
            return None

    # =========================================================
    # LOAD EXISTING CONNECTIONS
    # =========================================================

    def _load_existing_connections(self):

        try:

            connections = psutil.net_connections(
                kind="inet"
            )

        except Exception:
            return

        for connection in connections:

            key = self._connection_key(connection)

            if key:
                self.known_connections.add(key)

    # =========================================================
    # PROCESS NAME
    # =========================================================

    def _get_process_name(self, pid):

        if not pid:
            return "unknown"

        try:

            process = psutil.Process(pid)

            return process.name()

        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied,
        ):

            return "unknown"

    # =========================================================
    # CHECK
    # =========================================================

    def check(self):

        events = []

        current_connections = set()

        try:

            connections = psutil.net_connections(
                kind="inet"
            )

        except Exception as e:

            return {
                "events": [{
                    "type": "NETWORK_WATCHER_ERROR",
                    "error": str(e),
                }],
                "count": 1,
            }

        for connection in connections:

            key = self._connection_key(connection)

            if not key:
                continue

            current_connections.add(key)

            # =================================================
            # NEW CONNECTION
            # =================================================

            if key not in self.known_connections:

                (
                    pid,
                    local_ip,
                    local_port,
                    remote_ip,
                    remote_port,
                    status,
                ) = key

                process_name = self._get_process_name(pid)

                connection_data = {
                    "type": "SECURITY_NETWORK_CONNECTION",
                    "pid": pid,
                    "process": process_name,
                    "local_ip": local_ip,
                    "local_port": local_port,
                    "remote_ip": remote_ip,
                    "remote_port": remote_port,
                    "status": status,
                }

                # =========================================================
                # NETWORK ANALYSIS
                # =========================================================

                analysis = NetworkAnalyzer.analyze(
                    connection_data
                )

                connection_data["risk"] = analysis["risk"]
                connection_data["reason"] = analysis["reason"]

                events.append(connection_data)

        self.known_connections = current_connections

        if not events:
            return None

        return {
            "events": events,
            "count": len(events),
        }