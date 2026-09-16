from tools.watchers.security_analyzer import (
    SecurityAnalyzer,
)


tests = [

    {
        "name": "svchost.exe",
        "path": r"C:\Windows\System32\svchost.exe",
    },

    {
        "name": "notepad.exe",
        "path": r"C:\Windows\System32\notepad.exe",
    },

    {
        "name": "unknown.exe",
        "path": r"C:\Users\Tarek\AppData\Local\Temp\unknown.exe",
    },

]


for process in tests:

    result = SecurityAnalyzer.analyze(
        process
    )

    print(
        f"\n🔍 {process['name']}"
    )

    print(
        f"📁 {process['path']}"
    )

    print(
        f"🛡️ Risk: {result['risk']}"
    )

    print(
        f"💬 Reason: {result['reason']}"
    )