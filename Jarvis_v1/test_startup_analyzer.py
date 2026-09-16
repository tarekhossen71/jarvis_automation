from tools.watchers.startup_analyzer import StartupAnalyzer


test_items = [

    {
        "location": "USER_STARTUP_FOLDER",
        "name": "Chrome.lnk",
        "value": r"C:\Users\Tarek\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\Chrome.lnk",
    },

    {
        "location": "USER_STARTUP_FOLDER",
        "name": "script.bat",
        "value": r"C:\Users\Tarek\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\script.bat",
    },

    {
        "location": "USER_STARTUP_FOLDER",
        "name": "unknown.exe",
        "value": r"C:\Users\Tarek\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\unknown.exe",
    },

    {
        "location": "HKCU_RUN",
        "name": "MyApp",
        "value": r"C:\Users\Tarek\AppData\Local\MyApp\app.exe",
    },

]


for item in test_items:

    result = StartupAnalyzer.analyze(item)

    print("\nStartup Item:")
    print(item)

    print("Analysis:")
    print(result)