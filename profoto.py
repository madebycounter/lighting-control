import subprocess
import threading


class Strobe:
    def __init__(self, device, strobe):
        self.device = device
        self.strobe = strobe
        self.offset = 730 * strobe
        self.model_light = False

        self.slider_start = 183
        self.slider_end = 1035

        if (
            self.device.get_screen_size() != (1080, 2340)
            or self.device.get_screen_density() != 300
        ):
            self.device.set_screen_size((1080, 2340), 300)

    def slider_position(self, value):
        return self.slider_start + (self.slider_end - self.slider_start) * value / 100

    def model_temp(self, temperature):
        self.device.send_tap((self.slider_position(temperature), 652 + self.offset))

    def model_intensity(self, intensity):
        self.device.send_tap((self.slider_position(intensity), 740 + self.offset))

    def model_light_on(self):
        if not self.model_light:
            self.toggle_model_light()

    def model_light_off(self):
        if self.model_light:
            self.toggle_model_light()

    def toggle_model_light(self):
        self.device.send_tap((980, 459 + self.offset))
        self.model_light = not self.model_light

    def flash(self):
        self.device.send_tap((118, 683 + self.offset))


class Bulb:
    def __init__(self, ip):
        self.ip = ip

    def command(self, *command):
        def threaded():
            proc = subprocess.Popen(
                ["kasa", "--type", "bulb", "--host", self.ip, *command],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            stdout, stderr = proc.communicate()

        threading.Thread(target=threaded).start()

    def set_hsv(self, h, s, v):
        self.command("hsv", str(h), str(s), str(v))

    def turn_on(self):
        self.command("on")

    def turn_off(self):
        self.command("off")
