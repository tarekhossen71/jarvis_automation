import socket
import time

import speedtest


# =========================================================
# INTERNET CONNECTION
# =========================================================

def check_internet_connection():
    """
    Check whether the computer currently has
    internet connectivity.
    """

    test_hosts = [
        ("8.8.8.8", 53),
        ("1.1.1.1", 53),
        ("google.com", 80),
    ]

    for host, port in test_hosts:
        try:
            socket.create_connection(
                (host, port),
                timeout=3
            )

            return {
                "success": True,
                "connected": True,
                "message": "Internet connection is available.",
            }

        except OSError:
            continue

    return {
        "success": True,
        "connected": False,
        "message": "No internet connection detected.",
    }


# =========================================================
# ISP / SERVER INFORMATION
# =========================================================

def get_internet_info():
    """
    Get ISP and speed-test server information.
    """

    try:
        tester = speedtest.Speedtest()

        tester.get_best_server()

        server = tester.results.server

        return {
            "success": True,
            "isp": tester.config.get(
                "client",
                {}
            ).get(
                "isp",
                "Unknown"
            ),
            "ip": tester.config.get(
                "client",
                {}
            ).get(
                "ip",
                "Unknown"
            ),
            "server": server.get(
                "name",
                "Unknown"
            ),
            "server_country": server.get(
                "country",
                "Unknown"
            ),
            "server_sponsor": server.get(
                "sponsor",
                "Unknown"
            ),
            "latency_ms": round(
                tester.results.ping,
                2
            ),
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


# =========================================================
# FULL SPEED TEST
# =========================================================

def run_internet_speed_test():
    """
    Perform a complete internet speed test.

    Measures:
    - Download speed
    - Upload speed
    - Ping
    - ISP
    - Public IP
    - Test server
    """

    try:

        print("🌐 Preparing internet speed test...")

        tester = speedtest.Speedtest()

        # -------------------------------------------------
        # Find best server
        # -------------------------------------------------

        print("🌐 Finding best speed-test server...")

        tester.get_best_server()

        server = tester.results.server

        # -------------------------------------------------
        # Ping
        # -------------------------------------------------

        ping = tester.results.ping

        print(
            f"📡 Ping: {ping:.2f} ms"
        )

        # -------------------------------------------------
        # Download
        # -------------------------------------------------

        print(
            "⬇️ Testing download speed..."
        )

        start_time = time.time()

        download_bits = tester.download(
            threads=None
        )

        download_time = time.time() - start_time

        download_mbps = (
            download_bits
            / 1_000_000
        )

        # -------------------------------------------------
        # Upload
        # -------------------------------------------------

        print(
            "⬆️ Testing upload speed..."
        )

        start_time = time.time()

        upload_bits = tester.upload(
            threads=None
        )

        upload_time = time.time() - start_time

        upload_mbps = (
            upload_bits
            / 1_000_000
        )

        # -------------------------------------------------
        # Results
        # -------------------------------------------------

        results = tester.results

        return {
            "success": True,

            "download_mbps": round(
                download_mbps,
                2
            ),

            "upload_mbps": round(
                upload_mbps,
                2
            ),

            "ping_ms": round(
                ping,
                2
            ),

            "isp": tester.config.get(
                "client",
                {}
            ).get(
                "isp",
                "Unknown"
            ),

            "public_ip": tester.config.get(
                "client",
                {}
            ).get(
                "ip",
                "Unknown"
            ),

            "server": server.get(
                "name",
                "Unknown"
            ),

            "server_country": server.get(
                "country",
                "Unknown"
            ),

            "server_sponsor": server.get(
                "sponsor",
                "Unknown"
            ),

            "download_test_seconds": round(
                download_time,
                2
            ),

            "upload_test_seconds": round(
                upload_time,
                2
            ),

            "message": (
                "Internet speed test completed successfully."
            ),
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e),
            "message": (
                "Internet speed test failed."
            ),
        }


# =========================================================
# SIMPLE DOWNLOAD TEST
# =========================================================

def test_download_speed():
    """
    Test only download speed.
    """

    try:

        tester = speedtest.Speedtest()

        tester.get_best_server()

        download_bits = tester.download(
            threads=None
        )

        download_mbps = (
            download_bits
            / 1_000_000
        )

        return {
            "success": True,
            "download_mbps": round(
                download_mbps,
                2
            ),
            "message": (
                f"Download speed is "
                f"{download_mbps:.2f} Mbps."
            ),
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e),
        }


# =========================================================
# SIMPLE UPLOAD TEST
# =========================================================

def test_upload_speed():
    """
    Test only upload speed.
    """

    try:

        tester = speedtest.Speedtest()

        tester.get_best_server()

        upload_bits = tester.upload(
            threads=None
        )

        upload_mbps = (
            upload_bits
            / 1_000_000
        )

        return {
            "success": True,
            "upload_mbps": round(
                upload_mbps,
                2
            ),
            "message": (
                f"Upload speed is "
                f"{upload_mbps:.2f} Mbps."
            ),
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e),
        }


# =========================================================
# PING TEST
# =========================================================

def test_ping():
    """
    Test internet latency.
    """

    try:

        tester = speedtest.Speedtest()

        tester.get_best_server()

        ping = tester.results.ping

        return {
            "success": True,
            "ping_ms": round(
                ping,
                2
            ),
            "message": (
                f"Ping is "
                f"{ping:.2f} ms."
            ),
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e),
        }