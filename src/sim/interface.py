"""
Simulator <-> SNN arayuzu (muhendislik katmani, bkz. docs/yol_haritasi.md).

Kodlayici (LoomingEncoder): kamera goruntusu -> gorsel projeksiyon noronlarinin
  (LC4, LPLC2) Poisson girdi hizlari. Retina ve T4/T5 simule edilmez; nesnenin
  acisal buyuklugu ve buyume hizi klasik goruntu islemeyle hesaplanir.
    LC4   ~ acisal buyume hizi (dtheta/dt)   -- "ne kadar hizli yaklasiyor"
    LPLC2 ~ acisal buyukluk (theta), sadece buyurken  -- "ne kadar yakin"
  Sol/sag gorus alani ayri: goruntunun sol yarisi -> *_L, sag yarisi -> *_R.

Cozucu (MotorDecoder): inen noron (DN) hizlari -> rover hiz komutu.
  Sinekte DN'ler VNC'deki motor programlarini tetikler; program DN susunca hemen
  bitmez. Bunu taklit etmek icin her kanal aninda yukselir, persistence_s ile soner.
  Geri kacis: DNp02 + DNp04 + GF + MDN   (sinekte geri yonlu kacis/yurume)
  Ileri:      BPN tipleri                 (sinekte ileri yurume)
  Donus:      DNa01 + DNa02, sol - sag    (ayni taraf aktif -> o tarafa don)
"""
import numpy as np


class LoomingEncoder:
    def __init__(self, fovx_deg, lc4_gain=4.0, lc4_min_deg_s=8.0, lplc2_gain=2.0,
                 lplc2_min_deg=20.0, max_rate=100.0, window_s=0.1):
        self.fovx = fovx_deg
        self.lc4_gain = lc4_gain            # Hz per (deg/s)
        # LC4 sadece hizli genislemeye yanit verir; 8 deg/s, 0.4 m'lik top 1.2 m/s ile
        # gelirken ~2.3 m mesafeye karsilik gelir.
        self.lc4_min = lc4_min_deg_s
        self.lplc2_gain = lplc2_gain        # Hz per deg
        self.lplc2_min = lplc2_min_deg
        self.max_rate = max_rate
        self.window_s = window_s
        self._history = []     # (zaman, theta) -- buyume hizi bu pencereden hesaplanir
        self._t = 0.0
        self._rate = 0.0

    @staticmethod
    def threat_mask(img):
        # Tehdit kirmizi (aydinlik yuz ~187,26,26, golgeli yuz daha koyu); kizil Mars
        # zemini (~139,88,61) oranla elenir: r/g ~1.6 < 2.5
        img = img.astype(int)
        r, g, b = img[..., 0], img[..., 1], img[..., 2]
        return (r > 40) & (r > 2.5 * g) & (r > 2.5 * b)

    def encode(self, img, dt):
        """Doner: {'LC4_L': Hz, 'LC4_R': Hz, 'LPLC2_L': Hz, 'LPLC2_R': Hz}"""
        mask = self.threat_mask(img)
        w = mask.shape[1]
        # Pinhole kamera: goruntu merkezinde derece basina piksel
        px_per_deg = (w / 2) / np.tan(np.radians(self.fovx) / 2) * np.pi / 180
        # Kamera goruntusunde sol yari = rover'in sol tarafi
        halves = [mask[:, :w // 2], mask[:, w // 2:]]
        theta = np.array([2 * np.sqrt(h.sum() / np.pi) / px_per_deg for h in halves])  # derece
        total = 2 * np.sqrt(mask.sum() / np.pi) / px_per_deg
        share = theta / theta.sum() if theta.sum() > 0 else np.zeros(2)

        self._t += dt
        self._history.append((self._t, total))
        while self._history[0][0] < self._t - self.window_s - 1e-9:
            self._history.pop(0)
        t0, theta0 = self._history[0]
        self._rate = max((total - theta0) / (self._t - t0), 0.0) if self._t > t0 else 0.0  # deg/s

        lc4 = np.clip(self.lc4_gain * max(self._rate - self.lc4_min, 0) * share, 0, self.max_rate)
        lplc2 = np.clip(self.lplc2_gain * max(total - self.lplc2_min, 0) * share, 0, self.max_rate)
        if self._rate <= 0:
            lplc2[:] = 0
        return {'LC4_L': lc4[0], 'LC4_R': lc4[1], 'LPLC2_L': lplc2[0], 'LPLC2_R': lplc2[1]}


class MotorDecoder:
    BACKWARD = ['DNp02', 'DNp04', 'GF', 'MDN']
    FORWARD = ['BPN_T1', 'BPN_T2a', 'BPN_T2b', 'BPN_T3', 'BPN_T4']
    TURN = ['DNa01', 'DNa02']

    def __init__(self, back_gain=0.01, fwd_gain=0.01, turn_gain=0.02, max_speed=1.5, max_turn=2.0,
                 persistence_s=0.5):
        self.back_gain, self.fwd_gain, self.turn_gain = back_gain, fwd_gain, turn_gain
        self.max_speed, self.max_turn = max_speed, max_turn
        self.persistence_s = persistence_s
        self._state = {'back': 0.0, 'fwd': 0.0, 'left': 0.0, 'right': 0.0}

    def _persist(self, key, value, dt):
        decayed = self._state[key] * np.exp(-dt / self.persistence_s)
        self._state[key] = max(value, decayed)
        return self._state[key]

    @staticmethod
    def _sum(rates, types, sides='LR'):
        return sum(rates.get(f'{t}_{s}', 0.0) for t in types for s in sides)

    def decode(self, rates, dt):
        """rates: {dugum: Hz}, dt: s. Doner: (v_forward m/s, omega rad/s)."""
        back = self._persist('back', self._sum(rates, self.BACKWARD), dt)
        fwd = self._persist('fwd', self._sum(rates, self.FORWARD), dt)
        left = self._persist('left', self._sum(rates, self.TURN, 'L'), dt)
        right = self._persist('right', self._sum(rates, self.TURN, 'R'), dt)
        v = self.fwd_gain * fwd - self.back_gain * back
        omega = self.turn_gain * (left - right)
        return (float(np.clip(v, -self.max_speed, self.max_speed)),
                float(np.clip(omega, -self.max_turn, self.max_turn)))
