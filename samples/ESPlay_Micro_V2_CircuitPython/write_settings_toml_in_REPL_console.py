with open("settings.toml","w",encoding="utf8") as fout:
    fout.write('CIRCUITPY_WIFI_SSID = "canspy"\nCIRCUITPY_WIFI_PASSWORD = "canspycanspy"\nCIRCUITPY_WEB_API_PASSWORD = "mttiot"\nCIRCUITPY_WEB_API_PORT = 80\nMQTT_SUB = "/canspy/%/config"\nMQTT_PUP= "/canspy/%/data"\nMQTT_HOST = "10.42.0.1"\nMQTT_USER = ""\nMQTT_PASSWORD = ""')
    fout.close()