import threading
from profoto import Strobe, Bulb
from android import Device
import vlc
import re
import time


def parse_command(string):
    cmd = string.split()

    if len(cmd) == 0:
        return None

    if cmd[0] == "BULB":
        if cmd[2] == "OFF":
            return {
                "type": "BULB_OFF",
                "bulb": cmd[1],
            }

        if cmd[2] == "ON":
            return {
                "type": "BULB_ON",
                "bulb": cmd[1],
            }

        return {
            "type": "BULB",
            "bulb": cmd[1],
            "hsv": (int(cmd[2]), int(cmd[3]), int(cmd[4])),
        }

    if cmd[0] == "STROBE":
        if cmd[2] == "FLASH":
            return {
                "type": "FLASH",
                "strobe": cmd[1],
            }
        else:
            if cmd[2] == "OFF":
                return {
                    "type": "STROBE",
                    "strobe": cmd[1],
                    "intensity": 0,
                }
            else:
                return {
                    "type": "STROBE",
                    "strobe": cmd[1],
                    "intensity": int(cmd[2]),
                }


def parse_scene(file):
    defines = {}
    actions = []
    current_ts = 0

    def add_action(ts, cmd):
        actions.append({"timestamp": ts, "command": cmd})

    with open(file, "r") as f:
        for line in f.read().split("\n"):
            if not line:
                continue

            line = line.split()
            line = [word if word not in defines else defines[word] for word in line]
            line = " ".join(line).upper()

            if line.startswith("!DEFINE"):
                defines[line.split()[1]] = " ".join(line.split()[2:])

            elif line.startswith("[+"):
                delta = re.match(r"\[\+([\d.]*)\]", line).group(1)
                current_ts += float(delta)

            elif line.startswith("["):
                timestamp = re.match(r"\[([\d.]*)\]", line).group(1)
                current_ts = float(timestamp)

            elif line.startswith("REPEAT"):
                matches = re.match(r"REPEAT\((.*)\) (.*)", line)
                args = matches.group(1).split()
                cmd = parse_command(matches.group(2))
                repeat = int(args[0])
                interval = float(args[1])

                if not cmd:
                    continue

                for i in range(repeat):
                    add_action(current_ts + i * interval, cmd)

            else:
                cmd = parse_command(line)
                if cmd:
                    add_action(current_ts, cmd)

    groups = {}

    for action in actions:
        ts = action["timestamp"]
        cmd = action["command"]

        if ts not in groups:
            groups[ts] = []

        groups[ts].append(cmd)

    return groups


def execute_actions(actions, variables):
    timestamps = sorted(actions.keys())

    for idx, ts in enumerate(timestamps):
        start_time = time.time()

        cmds = actions[ts]

        for cmd in cmds:
            if cmd["type"] == "BULB":
                bulb = variables[cmd["bulb"]]
                bulb.set_hsv(*cmd["hsv"])

            if cmd["type"] == "BULB_ON":
                bulb = variables[cmd["bulb"]]
                bulb.turn_on()

            if cmd["type"] == "BULB_OFF":
                bulb = variables[cmd["bulb"]]
                bulb.turn_off()

            if cmd["type"] == "STROBE":
                strobe = variables[cmd["strobe"]]
                strobe.model_intensity(cmd["intensity"])

                if cmd["intensity"] > 0:
                    strobe.model_light_on()

                if cmd["intensity"] == 0:
                    strobe.model_light_off()

            if cmd["type"] == "FLASH":
                strobe = variables[cmd["strobe"]]
                strobe.flash()

        if idx < len(timestamps) - 1:
            time_delta = time.time() - start_time
            delay = timestamps[idx + 1] - timestamps[idx] - time_delta
            time.sleep(delay)

        for var in variables.values():
            if type(var) == Strobe:
                var.model_light_off()


vlc_instance = vlc.Instance()
player = vlc_instance.media_player_new()

pixel = Device("09241JEC235813")
lights = {
    "CEILING_1": Bulb("192.168.1.2"),
    "CEILING_2": Bulb("192.168.1.3"),
    "CEILING_3": Bulb("192.168.1.4"),
    "CEILING_4": Bulb("192.168.1.5"),
    "DESKTOP": Strobe(pixel, 1),
    "HALLWAY": Strobe(pixel, 0),
}

domestic_terror = vlc_instance.media_new(
    "audio/domesticterror_projection_vignette1.mp4"
)
diosa_mutt = vlc_instance.media_new("audio/diosa mutt projection_v1.mp4")
tech_capital = vlc_instance.media_new("audio/tech capital.mp4")
iron_prison = vlc_instance.media_new("audio/black iron.mp4")

domestic_terror_scene = parse_scene("examples/domestic_terror.scene")
diosa_mutt_scene = parse_scene("examples/diosa_mutt.scene")
tech_capital_scene = parse_scene("examples/tech_capital.scene")

player.set_media(domestic_terror)
player.play()
player.set_pause(1)

input("FULLSCREEN READY ")

player.toggle_fullscreen()

input("DOMESTIC TERROR READY ")

player.play()

execute_actions(
    domestic_terror_scene,
    lights,
)

player.set_media(diosa_mutt)
player.play()
player.set_pause(1)


input("DIOSA MUTT READY ")

player.play()

execute_actions(
    diosa_mutt_scene,
    lights,
)

player.set_media(tech_capital)
player.play()
player.set_pause(1)

input("TECH CAPITAL READY ")

player.play()

execute_actions(
    tech_capital_scene,
    lights,
)

player.set_media(iron_prison)
player.play()
player.set_pause(1)

input("IRON PRISON READY ")

player.play()

while True:
    pass
