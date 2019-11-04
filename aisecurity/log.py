"""

"aisecurity.log"

MySQL logging handling.

"""

import time
import warnings

import mysql.connector

from aisecurity.extras.paths import HOME, CONFIG_HOME


warnings.warn("logging with MySQL is deprecated and will be removed in later versions", DeprecationWarning)

# SETUP
THRESHOLDS = {
    "num_recognized": 5,
    "num_unknown": 5,
    "percent_diff": 0.1,
    "cooldown": 10.,
    "missed_frames": 10
}

num_recognized = 0
num_unknown = 0

last_logged = time.time() - THRESHOLDS["cooldown"] + 0.1  # don't log for first 0.1s- it's just warming up then
unk_last_logged = time.time() - THRESHOLDS["cooldown"] + 0.1

current_log = {}

try:
    database = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="Blast314" if "ryan" in HOME else "KittyCat123",
        database="LOG"
    )
    cursor = database.cursor()

except (mysql.connector.errors.DatabaseError, mysql.connector.errors.InterfaceError):
    warnings.warn("Database credentials missing or incorrect")


# LOGGING INIT AND HELPERS
def init(flush=False, thresholds=None):
    cursor.execute("USE LOG;")
    database.commit()

    if flush:
        instructions = open(CONFIG_HOME + "/bin/drop.sql")
        for cmd in instructions:
            if not cmd.startswith(" ") and not cmd.startswith("*/") and not cmd.startswith("/*"):
                cursor.execute(cmd)
                database.commit()

    if thresholds:
        global THRESHOLDS
        THRESHOLDS = {**THRESHOLDS, **thresholds}  # combining and overwriting THRESHOLDS with thresholds param


def get_now(seconds):
    date_and_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(seconds))
    return date_and_time.split(" ")


def get_id(name):
    # will be filled in later
    return "00000"


def get_percent_diff(best_match):
    return 1. - (len(current_log[best_match]) / len([item for sublist in current_log.values() for item in sublist]))


def update_current_logs(is_recognized, best_match):
    global current_log, num_recognized, num_unknown

    if is_recognized:
        now = time.time()

        if best_match not in current_log:
            current_log[best_match] = [now]
        else:
            current_log[best_match].append(now)

        if len(current_log[best_match]) == 1 or get_percent_diff(best_match) <= THRESHOLDS["percent_diff"]:
            num_recognized += 1
            num_unknown = 0

    else:
        num_unknown += 1
        num_recognized = 0


# LOGGING FUNCTIONS
def log_person(student_name, times):
    add = "INSERT INTO Activity (student_id, student_name, date, time) VALUES ({}, '{}', '{}', '{}');".format(
        get_id(student_name), student_name.replace("_", " ").title(), *get_now(sum(times) / len(times)))
    cursor.execute(add)
    database.commit()

    global last_logged
    last_logged = time.time()

    flush_current(regular_activity=True)


def log_unknown(path_to_img):
    add = "INSERT INTO Unknown (path_to_img, date, time) VALUES ('{}', '{}', '{}');".format(
        path_to_img, *get_now(time.time()))
    cursor.execute(add)
    database.commit()

    global unk_last_logged
    unk_last_logged = time.time()

    flush_current(regular_activity=False)


def flush_current(regular_activity=True):
    global current_log, num_recognized, num_unknown
    if regular_activity:
        current_log = {}
        num_recognized = 0
    else:
        num_unknown = 0