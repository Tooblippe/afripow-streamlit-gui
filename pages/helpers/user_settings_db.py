import json
import os
from addict import Dict
from streamlit_local_storage import LocalStorage


def who_is_working():
    localS = LocalStorage()
    return localS.getItem("who_is_working")


def save_user_setting(d):
    with open("user_settings.json", "w") as f:
        f.write(json.dumps(d.to_dict(), indent=4))


def create_settings_db():
    if not os.path.exists("user_settings.json"):
        d = Dict()
        d["description"] = "User settings"
        save_user_setting(d)


def load_user_settings():
    with open("user_settings.json", "r") as f:
        d = Dict(json.loads(f.read()))
    return d


def get_setting(user, setting):
    d = load_user_settings()
    return d[user].get(setting, None)


def get_setting_for_current_user(setting):
    return get_setting(who_is_working(), setting)


def set_setting(user, setting, value):
    d = load_user_settings()
    d[user][setting] = value
    save_user_setting(d)


def set_setting_for_current_user(setting, value):
    set_setting(who_is_working(), setting, value)
