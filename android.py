import subprocess
import threading

ADB_PATH = ".\\platform-tools\\adb.exe"


class Device:
    def __init__(self, id):
        self.id = id
        self.original_size = self.get_screen_size()
        self.original_density = self.get_screen_density()

    def reset_screen(self):
        self.set_screen_size(self.original_size, self.original_density)

    def command(self, *command):
        def threaded():
            subprocess.Popen(
                [ADB_PATH, "-s", self.id, "shell", *command],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

        threading.Thread(target=threaded).start()

    def send_tap(self, position):
        self.command("input", "tap", *map(str, position))

    def set_screen_size(self, size, density):
        self.command("wm", "size", "x".join(map(str, size)))
        self.command("wm", "density", str(density))

    def get_screen_size(self):
        process = subprocess.Popen(
            [ADB_PATH, "-s", self.id, "shell", "wm", "size"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, stderr = process.communicate()

        if stderr:
            raise Exception(stderr.decode("utf-8"))

        return tuple(map(int, stdout.decode("utf-8").split(":")[1].strip().split("x")))

    def get_screen_density(self):
        process = subprocess.Popen(
            [ADB_PATH, "-s", self.id, "shell", "wm", "density"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, stderr = process.communicate()

        if stderr:
            raise Exception(stderr.decode("utf-8"))

        return int(stdout.decode("utf-8").split(":")[1].split("\r\n")[0].strip())
