import json
import sys
from pathlib import Path
from typing import Any, Dict

import cv2
import mss
import numpy as np


def load_config(config_path: Path) -> Dict[str, Any]:
    if config_path.exists():
        return json.loads(config_path.read_text(encoding="utf-8"))
    return {}


def save_config(config_path: Path, data: Dict[str, Any]) -> None:
    config_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def resolve_config_path() -> Path:
    # 打包后统一读写 exe 同目录配置；源码运行读写脚本同目录配置。
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().with_name("fishing_config.json")
    return Path(__file__).resolve().with_name("fishing_config.json")


class LiveRegionSelector:
    def __init__(self) -> None:
        self.dragging = False
        self.start = None
        self.end = None

    def on_mouse(self, event: int, x: int, y: int, _flags: int, _param: Any) -> None:
        if event == cv2.EVENT_LBUTTONDOWN:
            self.dragging = True
            self.start = (x, y)
            self.end = (x, y)
        elif event == cv2.EVENT_MOUSEMOVE and self.dragging:
            self.end = (x, y)
        elif event == cv2.EVENT_LBUTTONUP and self.dragging:
            self.dragging = False
            self.end = (x, y)

    def current_rect(self) -> Any:
        if self.start is None or self.end is None:
            return None
        x1, y1 = self.start
        x2, y2 = self.end
        left = min(x1, x2)
        top = min(y1, y2)
        right = max(x1, x2)
        bottom = max(y1, y2)
        return left, top, right, bottom


def select_region() -> Dict[str, int]:
    with mss.MSS() as sct:
        monitor = sct.monitors[1]
        selector = LiveRegionSelector()
        window_name = "Select Capture Region (Live)"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, int(monitor["width"]), int(monitor["height"]))
        cv2.moveWindow(window_name, int(monitor["left"]), int(monitor["top"]))
        cv2.setMouseCallback(window_name, selector.on_mouse)

        while True:
            shot = sct.grab(monitor)
            frame = np.array(shot)
            bgr = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
            view = bgr.copy()

            rect = selector.current_rect()
            if rect is not None:
                l, t, r, b = rect
                cv2.rectangle(view, (l, t), (r, b), (0, 255, 255), 2)
                w = max(0, r - l)
                h = max(0, b - t)
                cv2.putText(
                    view,
                    f"ROI: left={l} top={t} width={w} height={h}",
                    (20, 70),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 255),
                    2,
                )

            cv2.putText(
                view,
                "Live preview: drag with mouse | ENTER/SPACE confirm | C/ESC cancel",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 255),
                2,
            )
            cv2.imshow(window_name, view)

            key = cv2.waitKey(1) & 0xFF
            if key in (13, 32):  # Enter / Space
                rect = selector.current_rect()
                if rect is None:
                    continue
                l, t, r, b = rect
                x, y, w, h = l, t, r - l, b - t
                if w > 0 and h > 0:
                    break
            if key in (27, ord("c")):  # ESC / C
                cv2.destroyWindow(window_name)
                raise RuntimeError("未选择有效区域，已取消。")

        cv2.destroyWindow(window_name)

        return {
            "left": int(monitor["left"] + x),
            "top": int(monitor["top"] + y),
            "width": w,
            "height": h,
        }


def main() -> None:
    config_path = resolve_config_path()

    config = load_config(config_path)
    new_region = select_region()
    config["capture_region"] = new_region
    save_config(config_path, config)

    print("已更新 capture_region:")
    print(new_region)
    print(f"配置文件: {config_path}")


if __name__ == "__main__":
    main()
