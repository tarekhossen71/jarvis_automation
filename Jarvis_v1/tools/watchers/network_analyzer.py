import ipaddress


class NetworkAnalyzer:

    # =========================================================
    # STANDARD PORTS
    # =========================================================

    SAFE_PORTS = {
        80: "Standard HTTP connection.",
        443: "Standard HTTPS connection.",
        53: "Standard DNS connection.",
        123: "Standard NTP time synchronization.",
        22: "Standard SSH connection.",
    }

    # =========================================================
    # ANALYZE CONNECTION
    # =========================================================

    @classmethod
    def analyze(cls, connection):

        remote_ip = (connection.get("remote_ip") or "").strip()
        remote_port = connection.get("remote_port")

        # =====================================================
        # MISSING REMOTE INFORMATION
        # =====================================================

        if not remote_ip:

            return {
                "risk": "MEDIUM",
                "reason": "Remote IP address could not be determined.",
            }

        # =====================================================
        # INVALID IP
        # =====================================================

        try:

            ip = ipaddress.ip_address(remote_ip)

        except ValueError:

            return {
                "risk": "MEDIUM",
                "reason": "Remote address is not a valid IP address.",
            }

        # =====================================================
        # PRIVATE / LOCAL NETWORK
        # =====================================================

        if ip.is_private or ip.is_loopback:

            return {
                "risk": "LOW",
                "reason": "Connection is to a private or local network address.",
            }

        # =====================================================
        # STANDARD PORT
        # =====================================================

        try:
            port = int(remote_port)
        except (TypeError, ValueError):
            port = None

        if port in cls.SAFE_PORTS:

            return {
                "risk": "LOW",
                "reason": cls.SAFE_PORTS[port],
            }

        # =====================================================
        # COMMON WEB PORTS
        # =====================================================

        if port in (8080, 8443):

            return {
                "risk": "LOW",
                "reason": "Common web application port.",
            }

        # =====================================================
        # UNKNOWN / UNUSUAL PORT
        # =====================================================

        return {
            "risk": "MEDIUM",
            "reason": "Connection uses a non-standard remote port.",
        }