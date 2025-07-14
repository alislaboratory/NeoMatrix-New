import time
import threading
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics

class MatrixController:
    def __init__(self):
        options = RGBMatrixOptions()
        options.rows = 16
        options.cols = 32
        options.chain_length = 1
        options.parallel = 1
        options.hardware_mapping = 'adafruit-hat'  # for Adafruit bonnet
        self.matrix = RGBMatrix(options=options)
        self.stop_event = threading.Event()
        self.worker = None

    def _run_in_thread(self, target, *args):
        # stop any existing demo
        if self.worker and self.worker.is_alive():
            self.stop_event.set()
            self.worker.join()
        self.stop_event.clear()
        self.worker = threading.Thread(target=target, args=args, daemon=True)
        self.worker.start()

    def clear(self):
        self.matrix.Clear()

    def show_text(self, text, color=(255,255,255), font_path="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size=12):
        def runner():
            self.clear()
            font = graphics.Font()
            font.LoadFont(font_path)
            text_color = graphics.Color(*color)
            pos = self.matrix.width
            while not self.stop_event.is_set():
                self.matrix.Clear()
                length = graphics.DrawText(self.matrix, font, pos, 12, text_color, text)
                pos -= 1
                if pos + length < 0:
                    pos = self.matrix.width
                time.sleep(0.05)
        self._run_in_thread(runner)

    def run_program(self, name):
        if name == 'rotating_square':
            self._run_in_thread(self._rotating_square)
        elif name == 'rainbow':
            self._run_in_thread(self._rainbow)
        else:
            self.clear()

    def _rotating_square(self):
        size = 10
        cx, cy = self.matrix.width//2, self.matrix.height//2
        angle = 0
        while not self.stop_event.is_set():
            self.clear()
            x0 = int(cx + size * 0.5 * (1 +  math.cos(angle)))
            y0 = int(cy + size * 0.5 * (1 +  math.sin(angle)))
            x1 = int(cx + size * 0.5 * (1 -  math.cos(angle)))
            y1 = int(cy + size * 0.5 * (1 -  math.sin(angle)))
            for x in range(min(x0,x1), max(x0,x1)):
                for y in range(min(y0,y1), max(y0,y1)):
                    self.matrix.SetPixel(x,y, 0,255,0)
            angle += 0.1
            time.sleep(0.1)

    def _rainbow(self):
        # cycle hue
        step = 0
        import colorsys
        while not self.stop_event.is_set():
            for x in range(self.matrix.width):
                for y in range(self.matrix.height):
                    hue = (x + step) / float(self.matrix.width)
                    r, g, b = [int(c*255) for c in colorsys.hsv_to_rgb(hue, 1.0, 1.0)]
                    self.matrix.SetPixel(x, y, r, g, b)
            step = (step + 1) % self.matrix.width
            time.sleep(0.05)

    def set_pixel(self, x, y, color):
        # immediately draw a single pixel
        self.stop_event.set()
        if self.worker:
            self.worker.join()
        self.matrix.SetPixel(x, y, *color)
