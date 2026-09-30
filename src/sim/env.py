"""MuJoCo rover ortami: teker komutu al, fizik adimla, kamera goruntusu ver."""
import os

import mujoco
import numpy as np

SCENE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rover.xml')
WHEEL_RADIUS = 0.1
TRACK_WIDTH = 0.5     # sol-sag teker arasi (m)
THREAT_RADIUS = 0.4
ROVER_HALF_LENGTH = 0.3


class RoverEnv:
    def __init__(self, threat_start=(6.0, 0.0), threat_speed=1.0, eye_size=(96, 192)):
        # from_xml_path ASCII olmayan yollari (orn. 'MSİ') acamiyor; metin olarak veriyoruz
        with open(SCENE, encoding='utf-8') as f:
            self.model = mujoco.MjModel.from_xml_string(f.read())
        self.data = mujoco.MjData(self.model)
        self.threat_speed = threat_speed
        self.threat_mocap = self.model.body('threat').mocapid[0]
        self.data.mocap_pos[self.threat_mocap][:2] = threat_start
        self._threat_dir = -np.array([*threat_start]) / np.linalg.norm(threat_start)
        mujoco.mj_forward(self.model, self.data)
        self.eye = mujoco.Renderer(self.model, *eye_size)
        self._chase = None

    @property
    def rover_xy(self):
        return self.data.body('rover').xpos[:2].copy()

    @property
    def threat_xy(self):
        return self.data.mocap_pos[self.threat_mocap][:2].copy()

    def threat_distance(self):
        """Top ile rover govdesi arasindaki bosluk (m); <= 0 carpisma."""
        return float(np.linalg.norm(self.threat_xy - self.rover_xy) - THREAT_RADIUS - ROVER_HALF_LENGTH)

    def step(self, v_forward, omega, duration_s=0.02):
        """v_forward: m/s (+ ileri), omega: rad/s (+ sola donus). Skid-steer kinematigi."""
        v_left = (v_forward - omega * TRACK_WIDTH / 2) / WHEEL_RADIUS
        v_right = (v_forward + omega * TRACK_WIDTH / 2) / WHEEL_RADIUS
        self.data.ctrl[:] = [v_left, v_left, v_right, v_right]
        for _ in range(int(round(duration_s / self.model.opt.timestep))):
            self.data.mocap_pos[self.threat_mocap][:2] += (
                self._threat_dir * self.threat_speed * self.model.opt.timestep)
            mujoco.mj_step(self.model, self.data)

    def eye_image(self):
        self.eye.update_scene(self.data, camera='eye')
        return self.eye.render()

    def chase_image(self, size=(270, 360)):
        if self._chase is None:
            self._chase = mujoco.Renderer(self.model, *size)
        self._chase.update_scene(self.data, camera='chase')
        return self._chase.render()

    @property
    def eye_fovx_deg(self):
        fovy = self.model.cam('eye').fovy[0]
        h, w = self.eye.height, self.eye.width
        return float(np.degrees(2 * np.arctan(np.tan(np.radians(fovy) / 2) * w / h)))

    def close(self):
        for r in (self.eye, self._chase):
            if r is not None:
                r.close()
