"""Capture only isolated generated lab TCP traffic at both endpoints."""
import hashlib
import os
from pathlib import Path
import re
import signal
import subprocess
import time
from vfw_research.packet_observation import packets, compare_endpoints


class EndpointCapture:
    def __init__(self, output: Path):
        self.output = output.resolve()
        self.processes = []
        self.features = {}

    def start(self):
        try:
            for node in ("client", "server"):
                prefix = ["ip", "netns", "exec", "vfwlab3-" + node]
                subprocess.run([*prefix, "ethtool", "-K", "eth0", "gro", "off", "gso", "off", "tso", "off"],
                               check=True, capture_output=True, timeout=5)
                self.features[node] = subprocess.run([*prefix, "ethtool", "-k", "eth0"], check=True,
                                                     capture_output=True, text=True, timeout=5).stdout
                for feature in ("generic-receive-offload", "generic-segmentation-offload", "tcp-segmentation-offload"):
                    if not re.search(rf"^{feature}: off", self.features[node], re.MULTILINE):
                        raise RuntimeError("required offload setting not verified")
                path = self.output / f"{node}.pcap"
                log = self.output / f"{node}-capture.log"
                with log.open("x", encoding="utf-8") as handle:
                    proc = subprocess.Popen([*prefix, "tcpdump", "--immediate-mode", "-n", "-U", "-s", "0", "-i", "eth0",
                        "-B", "4096", "-Z", "root", "-w", str(path),
                        "tcp and port 9000 and host 10.50.0.2 and host 10.50.5.2"],
                        stdout=subprocess.DEVNULL, stderr=handle, env={**os.environ, "LC_ALL": "C"})
                self.processes.append((node, proc, log))
                deadline = time.monotonic() + 5
                while "listening on" not in log.read_text():
                    if proc.poll() is not None or time.monotonic() >= deadline:
                        raise RuntimeError("capture failed to become ready")
                    time.sleep(.05)
        except Exception:
            self.stop()
            raise

    def stop(self):
        for _, proc, _ in self.processes:
            if proc.poll() is None:
                proc.send_signal(signal.SIGINT)
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=5)

    def analyze(self):
        drops = 0
        logs = {}
        for node, proc, log in self.processes:
            content = log.read_text()
            matches = re.findall(r"(\d+) packets dropped by kernel", content)
            if proc.returncode != 0 or len(matches) != 1:
                raise ValueError("capture did not close with known statistics")
            drops += int(matches[0])
            logs[node] = content
        if len(logs) != 2:
            raise ValueError("two ready captures required")
        result = compare_endpoints(packets(self.output / "client.pcap"), packets(self.output / "server.pcap"),
                                   capture_drops=drops)
        result.update(logs=logs, offload_features=self.features,
                      capture_sha256={node: hashlib.sha256((self.output / f"{node}.pcap").read_bytes()).hexdigest()
                                      for node in ("client", "server")})
        return result
