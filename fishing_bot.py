import argparse
import json
import math
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional, Tuple

import cv2
import keyboard
import mss
import numpy as np
import pydirectinput


@dataclass
class Config:
    capture_region: dict
    fish_hsv_low: Tuple[int, int, int]
    fish_hsv_high: Tuple[int, int, int]
    line_hsv_low: Tuple[int, int, int]
    line_hsv_high: Tuple[int, int, int]
    bar_hsv_low: Tuple[int, int, int]
    bar_hsv_high: Tuple[int, int, int]
    left_key: str
    right_key: str
    ui_language: str
    input_backend: str
    auto_action_enabled: bool
    auto_action_key: str
    auto_action_interval_sec: float
    auto_action_hold_sec: float
    auto_action_idle_grace_sec: float
    prompt_detection_enabled: bool
    prompt_region: Optional[dict]
    prompt_detect_interval_sec: float
    prompt_cooldown_sec: float
    auto_click_enabled: bool
    auto_click_interval_sec: float
    auto_click_position: Optional[dict]
    recovery_escape_enabled: bool
    recovery_no_line_timeout_sec: float
    recovery_escape_cooldown_sec: float
    recovery_click_before_escape: bool
    recovery_click_attempts: int
    use_template_matching: bool
    fish_template_path: str
    template_match_threshold: float
    hold_control_enabled: bool
    fine_control_zone_px: int
    fine_tap_sec: float
    fine_tap_cooldown_sec: float
    gui_start_delay_sec: float
    dead_zone_px: int
    edge_margin_px: int
    min_blob_area: int
    min_col_pixels: int
    max_x_jump: int
    max_lost_frames: int
    mask_open_kernel: int
    mask_close_kernel: int
    enable_clahe: bool
    target_fps: int
    log_every_n_frames: int
    test_image_path: str
    debug_window_scale: float
    fullscreen_debug: bool
    debug_show_full_monitor: bool
    dry_run_default: bool
    show_mask_windows: bool


def save_config(path: Path, config: Config) -> None:
    raw = {
        "capture_region": config.capture_region,
        "fish_hsv_low": list(config.fish_hsv_low),
        "fish_hsv_high": list(config.fish_hsv_high),
        "line_hsv_low": list(config.line_hsv_low),
        "line_hsv_high": list(config.line_hsv_high),
        "bar_hsv_low": list(config.bar_hsv_low),
        "bar_hsv_high": list(config.bar_hsv_high),
        "left_key": config.left_key,
        "right_key": config.right_key,
        "ui_language": config.ui_language,
        "input_backend": config.input_backend,
        "auto_action_enabled": config.auto_action_enabled,
        "auto_action_key": config.auto_action_key,
        "auto_action_interval_sec": config.auto_action_interval_sec,
        "auto_action_hold_sec": config.auto_action_hold_sec,
        "auto_action_idle_grace_sec": config.auto_action_idle_grace_sec,
        "prompt_detection_enabled": config.prompt_detection_enabled,
        "prompt_region": config.prompt_region,
        "prompt_detect_interval_sec": config.prompt_detect_interval_sec,
        "prompt_cooldown_sec": config.prompt_cooldown_sec,
        "auto_click_enabled": config.auto_click_enabled,
        "auto_click_interval_sec": config.auto_click_interval_sec,
        "auto_click_position": config.auto_click_position,
        "recovery_escape_enabled": config.recovery_escape_enabled,
        "recovery_no_line_timeout_sec": config.recovery_no_line_timeout_sec,
        "recovery_escape_cooldown_sec": config.recovery_escape_cooldown_sec,
        "recovery_click_before_escape": config.recovery_click_before_escape,
        "recovery_click_attempts": config.recovery_click_attempts,
        "use_template_matching": config.use_template_matching,
        "fish_template_path": config.fish_template_path,
        "template_match_threshold": config.template_match_threshold,
        "hold_control_enabled": config.hold_control_enabled,
        "fine_control_zone_px": config.fine_control_zone_px,
        "fine_tap_sec": config.fine_tap_sec,
        "fine_tap_cooldown_sec": config.fine_tap_cooldown_sec,
        "gui_start_delay_sec": config.gui_start_delay_sec,
        "dead_zone_px": config.dead_zone_px,
        "edge_margin_px": config.edge_margin_px,
        "min_blob_area": config.min_blob_area,
        "min_col_pixels": config.min_col_pixels,
        "max_x_jump": config.max_x_jump,
        "max_lost_frames": config.max_lost_frames,
        "mask_open_kernel": config.mask_open_kernel,
        "mask_close_kernel": config.mask_close_kernel,
        "enable_clahe": config.enable_clahe,
        "target_fps": config.target_fps,
        "log_every_n_frames": config.log_every_n_frames,
        "test_image_path": config.test_image_path,
        "debug_window_scale": config.debug_window_scale,
        "fullscreen_debug": config.fullscreen_debug,
        "debug_show_full_monitor": config.debug_show_full_monitor,
        "dry_run_default": config.dry_run_default,
        "show_mask_windows": config.show_mask_windows,
    }
    path.write_text(json.dumps(raw, ensure_ascii=False, indent=2), encoding="utf-8")


def load_config(path: Path) -> Config:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return Config(
        capture_region=raw["capture_region"],
        fish_hsv_low=tuple(raw["fish_hsv_low"]),
        fish_hsv_high=tuple(raw["fish_hsv_high"]),
        line_hsv_low=tuple(raw["line_hsv_low"]),
        line_hsv_high=tuple(raw["line_hsv_high"]),
        bar_hsv_low=tuple(raw["bar_hsv_low"]),
        bar_hsv_high=tuple(raw["bar_hsv_high"]),
        left_key=raw.get("left_key", "a"),
        right_key=raw.get("right_key", "d"),
        ui_language=str(raw.get("ui_language", "ru")),
        input_backend=str(raw.get("input_backend", "pydirectinput")),
        auto_action_enabled=bool(raw.get("auto_action_enabled", True)),
        auto_action_key=str(raw.get("auto_action_key", "f")),
        auto_action_interval_sec=float(raw.get("auto_action_interval_sec", 0.6)),
        auto_action_hold_sec=float(raw.get("auto_action_hold_sec", 0.05)),
        auto_action_idle_grace_sec=float(raw.get("auto_action_idle_grace_sec", 0.7)),
        prompt_detection_enabled=bool(raw.get("prompt_detection_enabled", True)),
        prompt_region=raw.get("prompt_region"),
        prompt_detect_interval_sec=float(raw.get("prompt_detect_interval_sec", 0.08)),
        prompt_cooldown_sec=float(raw.get("prompt_cooldown_sec", 0.35)),
        auto_click_enabled=bool(raw.get("auto_click_enabled", True)),
        auto_click_interval_sec=float(raw.get("auto_click_interval_sec", 0.6)),
        auto_click_position=raw.get("auto_click_position"),
        recovery_escape_enabled=bool(raw.get("recovery_escape_enabled", True)),
        recovery_no_line_timeout_sec=float(raw.get("recovery_no_line_timeout_sec", 3.0)),
        recovery_escape_cooldown_sec=float(raw.get("recovery_escape_cooldown_sec", 10.0)),
        recovery_click_before_escape=bool(raw.get("recovery_click_before_escape", True)),
        recovery_click_attempts=int(raw.get("recovery_click_attempts", 2)),
        use_template_matching=bool(raw.get("use_template_matching", True)),
        fish_template_path=str(raw.get("fish_template_path", "fish_reference.png")),
        template_match_threshold=float(raw.get("template_match_threshold", 0.62)),
        hold_control_enabled=bool(raw.get("hold_control_enabled", True)),
        fine_control_zone_px=int(raw.get("fine_control_zone_px", 22)),
        fine_tap_sec=float(raw.get("fine_tap_sec", 0.012)),
        fine_tap_cooldown_sec=float(raw.get("fine_tap_cooldown_sec", 0.015)),
        gui_start_delay_sec=float(raw.get("gui_start_delay_sec", 3.0)),
        dead_zone_px=int(raw.get("dead_zone_px", 6)),
        edge_margin_px=int(raw.get("edge_margin_px", 8)),
        min_blob_area=int(raw.get("min_blob_area", 35)),
        min_col_pixels=int(raw.get("min_col_pixels", 2)),
        max_x_jump=int(raw.get("max_x_jump", 35)),
        max_lost_frames=int(raw.get("max_lost_frames", 6)),
        mask_open_kernel=int(raw.get("mask_open_kernel", 3)),
        mask_close_kernel=int(raw.get("mask_close_kernel", 5)),
        enable_clahe=bool(raw.get("enable_clahe", True)),
        target_fps=int(raw.get("target_fps", 30)),
        log_every_n_frames=int(raw.get("log_every_n_frames", 1)),
        test_image_path=str(raw.get("test_image_path", "")),
        debug_window_scale=float(raw.get("debug_window_scale", 1.0)),
        fullscreen_debug=bool(raw.get("fullscreen_debug", True)),
        debug_show_full_monitor=bool(raw.get("debug_show_full_monitor", True)),
        dry_run_default=bool(raw.get("dry_run_default", False)),
        show_mask_windows=bool(raw.get("show_mask_windows", False)),
    )


def resolve_config_path() -> Path:
    # 打包后统一使用 exe 同目录配置；源码运行使用脚本同目录配置。
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().with_name("fishing_config.json")
    return Path(__file__).resolve().with_name("fishing_config.json")


def resolve_asset_path(config_path: Path, raw_path: str) -> Path:
    path = Path(raw_path)
    if path.is_absolute():
        return path
    return config_path.resolve().parent / path


def enhance_hsv(hsv: np.ndarray, enable_clahe: bool) -> np.ndarray:
    if not enable_clahe:
        return hsv
    h, s, v = cv2.split(hsv)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    v = clahe.apply(v)
    return cv2.merge((h, s, v))


def make_mask(
    hsv: np.ndarray,
    low: Tuple[int, int, int],
    high: Tuple[int, int, int],
    open_kernel_size: int,
    close_kernel_size: int,
) -> np.ndarray:
    mask = cv2.inRange(hsv, np.array(low, dtype=np.uint8), np.array(high, dtype=np.uint8))
    open_kernel_size = max(1, open_kernel_size | 1)
    close_kernel_size = max(1, close_kernel_size | 1)
    open_kernel = np.ones((open_kernel_size, open_kernel_size), np.uint8)
    close_kernel = np.ones((close_kernel_size, close_kernel_size), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, open_kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, close_kernel)
    return mask


def make_relaxed_range(
    low: Tuple[int, int, int],
    high: Tuple[int, int, int],
    h_pad: int = 10,
    sv_pad_low: int = 25,
    sv_pad_high: int = 10,
) -> Tuple[Tuple[int, int, int], Tuple[int, int, int]]:
    low_h = max(0, int(low[0]) - h_pad)
    low_s = max(0, int(low[1]) - sv_pad_low)
    low_v = max(0, int(low[2]) - sv_pad_low)
    high_h = min(179, int(high[0]) + h_pad)
    high_s = min(255, int(high[1]) + sv_pad_high)
    high_v = min(255, int(high[2]) + sv_pad_high)
    return (low_h, low_s, low_v), (high_h, high_s, high_v)


def yellow_line_candidate_mask(bgr: np.ndarray, hsv: np.ndarray, tolerance: int = 10) -> np.ndarray:
    tolerance = max(1, int(tolerance))
    b = bgr[:, :, 0].astype(np.int16)
    g = bgr[:, :, 1].astype(np.int16)
    r = bgr[:, :, 2].astype(np.int16)
    h = hsv[:, :, 0].astype(np.int16)
    s = hsv[:, :, 1].astype(np.int16)
    v = hsv[:, :, 2].astype(np.int16)

    r_min = max(125, 190 - tolerance * 4)
    g_min = max(90, 145 - tolerance * 3)
    rb_min = max(8, 36 - tolerance)
    gb_min = max(0, 18 - tolerance)
    h_low = max(0, 16 - tolerance)
    h_high = min(60, 38 + tolerance)
    s_min = max(20, 115 - tolerance * 5)
    v_min = max(90, 160 - tolerance * 4)

    warm_rgb = (r >= r_min) & (g >= g_min) & (r >= b + rb_min) & (g >= b + gb_min)
    warm_hsv = (h >= h_low) & (h <= h_high) & (s >= s_min) & (v >= v_min)
    pale_core = (
        (r >= max(200, 245 - tolerance * 3))
        & (g >= max(170, 215 - tolerance * 3))
        & (b <= min(245, 205 + tolerance * 3))
        & (r >= b + max(5, 25 - tolerance))
        & (g >= b + max(0, 12 - tolerance))
    )
    orange_glow = (
        (r >= max(145, 185 - tolerance * 3))
        & (g >= max(70, 105 - tolerance * 2))
        & (r >= g + max(8, 28 - tolerance))
        & (r >= b + max(35, 70 - tolerance * 2))
    )

    mask = ((warm_rgb & warm_hsv) | pale_core | orange_glow).astype(np.uint8) * 255
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((3, 2), np.uint8))
    return mask


def vertical_line_component_mask(mask: np.ndarray, min_area: int) -> np.ndarray:
    frame_height, frame_width = mask.shape[:2]
    col_counts = np.count_nonzero(mask, axis=0)
    min_col_pixels = max(5, min(frame_height - 1, frame_height // 4))
    active_cols = np.where(col_counts >= min_col_pixels)[0]
    result = np.zeros_like(mask)
    if active_cols.size == 0:
        return result

    max_width = max(8, min(22, frame_height))
    best = None
    best_score = 0.0
    start = int(active_cols[0])
    prev = int(active_cols[0])
    spans = []
    for col in active_cols[1:]:
        col = int(col)
        if col <= prev + 2:
            prev = col
            continue
        spans.append((start, prev))
        start = col
        prev = col
    spans.append((start, prev))

    for start, end in spans:
        width = end - start + 1
        if width > max_width:
            continue
        x1 = max(0, start - 2)
        x2 = min(frame_width, end + 3)
        component = mask[:, x1:x2]
        ys, xs = np.where(component > 0)
        if xs.size < max(5, min_area // 8):
            continue
        height = int(ys.max() - ys.min() + 1)
        comp_width = int(xs.max() - xs.min() + 1)
        if height < max(6, frame_height // 4):
            continue
        if comp_width > max_width:
            continue
        if height >= frame_height - 1 and comp_width > 6:
            continue
        area = int(xs.size)
        score = area * (height / max(1, comp_width)) * min(2.0, height / max(1, frame_height * 0.45))
        if score > best_score:
            best_score = score
            best = (x1, x2)

    if best is None:
        return result
    x1, x2 = best
    result[:, x1:x2] = mask[:, x1:x2]
    result = cv2.morphologyEx(result, cv2.MORPH_CLOSE, np.ones((2, 2), np.uint8))
    return result


def yellow_line_component_mask(
    bgr: np.ndarray,
    hsv: np.ndarray,
    tolerance: int = 10,
    min_area: int = 35,
) -> np.ndarray:
    raw_mask = yellow_line_candidate_mask(bgr, hsv, tolerance=tolerance)
    return vertical_line_component_mask(raw_mask, min_area=min_area)


def largest_blob_center_x(mask: np.ndarray, min_area: int) -> Optional[int]:
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    best = None
    best_area = 0.0
    for contour in contours:
        area = cv2.contourArea(contour)
        if area < min_area or area <= best_area:
            continue
        x, y, w, h = cv2.boundingRect(contour)
        best = x + w // 2
        best_area = area
    return best


def tracked_blob_center_x(
    mask: np.ndarray,
    min_area: int,
    prev_x: Optional[int],
    max_x_jump: int,
    min_width: int = 0,
) -> Optional[int]:
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    candidates = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area < min_area:
            continue
        x, y, w, h = cv2.boundingRect(contour)
        if w < min_width:
            continue
        cx = x + w // 2
        candidates.append((cx, area))
    if not candidates:
        return None
    if prev_x is None:
        return int(max(candidates, key=lambda item: item[1])[0])
    near = [item for item in candidates if abs(item[0] - prev_x) <= max_x_jump]
    if near:
        return int(max(near, key=lambda item: item[1])[0])
    return int(max(candidates, key=lambda item: item[1])[0])


def dominant_span(mask: np.ndarray, min_area: int) -> Optional[Tuple[int, int]]:
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    best = None
    best_area = 0.0
    for contour in contours:
        area = cv2.contourArea(contour)
        if area < min_area or area <= best_area:
            continue
        x, y, w, h = cv2.boundingRect(contour)
        best = (x, x + w)
        best_area = area
    return best


def center_x_by_projection(mask: np.ndarray, min_col_pixels: int = 2) -> Optional[int]:
    col_counts = np.count_nonzero(mask, axis=0)
    active = np.where(col_counts >= min_col_pixels)[0]
    if active.size == 0:
        return None
    return int(active.mean())


def longest_span_from_counts(counts: np.ndarray, min_col_pixels: int, min_width: int = 2) -> Optional[Tuple[int, int]]:
    active = np.where(counts >= min_col_pixels)[0]
    if active.size == 0:
        return None
    best = None
    start = int(active[0])
    prev = int(active[0])
    for idx in active[1:]:
        idx = int(idx)
        if idx == prev + 1:
            prev = idx
            continue
        if prev - start + 1 >= min_width:
            if best is None or (prev - start) > (best[1] - best[0]):
                best = (start, prev)
        start = idx
        prev = idx
    if prev - start + 1 >= min_width:
        if best is None or (prev - start) > (best[1] - best[0]):
            best = (start, prev)
    return best


def peak_x_from_counts(
    counts: np.ndarray, min_col_pixels: int, prev_x: Optional[int], max_x_jump: int
) -> Optional[int]:
    candidates = np.where(counts >= min_col_pixels)[0]
    if candidates.size == 0:
        return None
    if prev_x is None:
        return int(candidates[np.argmax(counts[candidates])])
    nearby = [int(x) for x in candidates if abs(int(x) - prev_x) <= max_x_jump]
    if nearby:
        return int(max(nearby, key=lambda x: int(counts[x])))
    return int(candidates[np.argmax(counts[candidates])])


def span_by_projection(mask: np.ndarray, min_col_pixels: int = 2) -> Optional[Tuple[int, int]]:
    col_counts = np.count_nonzero(mask, axis=0)
    active = np.where(col_counts >= min_col_pixels)[0]
    if active.size == 0:
        return None
    return int(active[0]), int(active[-1])


def motion_center_x(prev_gray: Optional[np.ndarray], gray: np.ndarray, min_col_pixels: int) -> Optional[int]:
    if prev_gray is None:
        return None
    diff = cv2.absdiff(gray, prev_gray)
    _, motion = cv2.threshold(diff, 18, 255, cv2.THRESH_BINARY)
    motion = cv2.medianBlur(motion, 3)
    return center_x_by_projection(motion, min_col_pixels=max(2, min_col_pixels))


def load_template_image(config_path: Path, raw_path: str) -> Optional[np.ndarray]:
    if not raw_path:
        return None
    path = resolve_asset_path(config_path, raw_path)
    if not path.exists():
        return None
    image = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if image is None or image.shape[0] < 3 or image.shape[1] < 3:
        return None
    return image


def template_center_x(
    bgr: np.ndarray,
    template: Optional[np.ndarray],
    threshold: float,
) -> Optional[Tuple[int, float]]:
    if template is None:
        return None
    th, tw = template.shape[:2]
    fh, fw = bgr.shape[:2]
    if th > fh or tw > fw:
        return None

    frame_gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    if float(np.std(template_gray)) < 3.0:
        return None

    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(4, 4))
    frame_eq = clahe.apply(frame_gray)
    template_eq = clahe.apply(template_gray)
    frame_edge = cv2.Canny(frame_eq, 45, 130)
    template_edge = cv2.Canny(template_eq, 45, 130)

    candidates = []
    for frame_variant, template_variant, weight in (
        (frame_gray, template_gray, 1.00),
        (frame_eq, template_eq, 1.05),
        (frame_edge, template_edge, 0.92),
    ):
        if float(np.std(template_variant)) < 3.0:
            continue
        result = cv2.matchTemplate(frame_variant, template_variant, cv2.TM_CCOEFF_NORMED)
        _, score, _, location = cv2.minMaxLoc(result)
        candidates.append((float(score) * weight, location))

    if not candidates:
        return None
    score, location = max(candidates, key=lambda item: item[0])
    if score < threshold:
        return None
    return int(location[0] + tw // 2), float(score)


def turquoise_indicator_center_x(
    hsv: np.ndarray,
    min_area: int,
    low: Tuple[int, int, int],
    high: Tuple[int, int, int],
) -> Optional[int]:
    mask = cv2.inRange(hsv, np.array(low, dtype=np.uint8), np.array(high, dtype=np.uint8))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((7, 5), np.uint8))
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    best = None
    best_score = 0.0
    for contour in contours:
        area = cv2.contourArea(contour)
        if area < max(min_area, 80):
            continue
        x, _y, w, h = cv2.boundingRect(contour)
        if w < 30 or h < 5:
            continue
        aspect = w / max(1, h)
        if aspect < 2.0:
            continue
        score = area * min(6.0, aspect)
        if score > best_score:
            best_score = score
            best = x + w // 2
    return best


def yellow_line_center_x(hsv: np.ndarray, min_area: int, bgr: Optional[np.ndarray] = None) -> Optional[int]:
    if bgr is not None:
        mask = yellow_line_component_mask(bgr, hsv, tolerance=12, min_area=min_area)
    else:
        mask = cv2.inRange(hsv, np.array((14, 55, 105), dtype=np.uint8), np.array((48, 255, 255), dtype=np.uint8))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
        mask = vertical_line_component_mask(mask, min_area=min_area)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    best = None
    best_score = 0.0
    frame_height = hsv.shape[0]
    for contour in contours:
        area = cv2.contourArea(contour)
        if area < max(4, min_area // 10):
            continue
        x, _y, w, h = cv2.boundingRect(contour)
        if h < max(5, frame_height // 4):
            continue
        if w > max(18, frame_height):
            continue
        if h >= frame_height - 1:
            continue
        score = area * (h / max(1, w)) * min(2.0, h / max(1, frame_height * 0.45))
        if score > best_score:
            best_score = score
            best = x + w // 2
    return best


def detect_action_prompt(bgr: np.ndarray) -> Optional[Tuple[int, int]]:
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)

    dark_mask = cv2.inRange(hsv, np.array((0, 0, 8), dtype=np.uint8), np.array((179, 120, 95), dtype=np.uint8))
    dark_mask = cv2.morphologyEx(dark_mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    dark_mask = cv2.morphologyEx(dark_mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))

    contours, _ = cv2.findContours(dark_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    best_score = 0.0
    best_center = None

    for contour in contours:
        area = cv2.contourArea(contour)
        if area < 120 or area > 2600:
            continue

        x, y, w, h = cv2.boundingRect(contour)
        if w < 16 or h < 16 or w > 72 or h > 72:
            continue

        aspect = w / max(1, h)
        if aspect < 0.65 or aspect > 1.35:
            continue

        perimeter = cv2.arcLength(contour, True)
        if perimeter <= 0:
            continue

        circularity = 4.0 * math.pi * area / (perimeter * perimeter)
        if circularity < 0.45:
            continue

        roi_gray = gray[y : y + h, x : x + w]
        roi_hsv = hsv[y : y + h, x : x + w]
        bright_mask = cv2.inRange(
            roi_hsv,
            np.array((0, 0, 120), dtype=np.uint8),
            np.array((179, 95, 255), dtype=np.uint8),
        )
        bright_mask = cv2.bitwise_or(bright_mask, cv2.inRange(roi_gray, 135, 255))
        bright_pixels = int(np.count_nonzero(bright_mask))
        bright_ratio = bright_pixels / max(1, w * h)
        if bright_pixels < 8 or bright_ratio > 0.35:
            continue

        score = circularity * area * min(1.0, bright_pixels / 55.0)
        if score > best_score:
            best_score = score
            best_center = (x + w // 2, y + h // 2)

    return best_center


def key_down(key: str, backend: str) -> None:
    backend = (backend or "pydirectinput").lower()
    if backend in ("pydirectinput", "auto"):
        try:
            pydirectinput.keyDown(key)
        except Exception:
            if backend != "auto":
                raise
    if backend in ("keyboard", "auto"):
        try:
            keyboard.press(key)
        except Exception:
            if backend != "auto":
                raise


def key_up(key: str, backend: str) -> None:
    backend = (backend or "pydirectinput").lower()
    if backend in ("keyboard", "auto"):
        try:
            keyboard.release(key)
        except Exception:
            if backend != "auto":
                raise
    if backend in ("pydirectinput", "auto"):
        try:
            pydirectinput.keyUp(key)
        except Exception:
            if backend != "auto":
                raise


def release_keys(left_key: str, right_key: str, backend: str = "pydirectinput") -> None:
    key_up(left_key, backend)
    key_up(right_key, backend)


def tap(key: str, duration: float, backend: str = "pydirectinput") -> None:
    key_down(key, backend)
    time.sleep(duration)
    key_up(key, backend)


def click_at(x: int, y: int) -> None:
    pydirectinput.moveTo(int(x), int(y))
    pydirectinput.click()


def default_action_click_point(monitor: dict) -> Tuple[int, int]:
    return (
        int(monitor["left"] + monitor["width"] * 0.925),
        int(monitor["top"] + monitor["height"] * 0.91),
    )


def default_recovery_click_point(monitor: dict) -> Tuple[int, int]:
    return (
        int(monitor["left"] + monitor["width"] * 0.25),
        int(monitor["top"] + monitor["height"] * 0.78),
    )


def default_prompt_scan_region(monitor: dict) -> dict:
    width = int(monitor["width"] * 0.42)
    height = int(monitor["height"] * 0.42)
    return {
        "left": int(monitor["left"] + monitor["width"] - width),
        "top": int(monitor["top"] + monitor["height"] - height),
        "width": width,
        "height": height,
    }


def resolve_auto_click_point(
    config: Config,
    monitor: dict,
    last_prompt_point: Optional[Tuple[int, int]],
) -> Tuple[int, int]:
    if config.auto_click_position is not None:
        return int(config.auto_click_position["x"]), int(config.auto_click_position["y"])
    if last_prompt_point is not None:
        return last_prompt_point
    if config.prompt_region is not None:
        return (
            int(config.prompt_region["left"] + config.prompt_region["width"] / 2),
            int(config.prompt_region["top"] + config.prompt_region["height"] / 2),
        )
    return default_action_click_point(monitor)


def is_stop_requested(stop_event: Optional[object]) -> bool:
    return bool(stop_event is not None and getattr(stop_event, "is_set")())


def select_capture_region(sct: mss.MSS, fallback_region: dict) -> Optional[dict]:
    monitor = sct.monitors[1]
    shot = sct.grab(monitor)
    frame = np.array(shot)
    bgr = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
    preview = bgr.copy()

    fr = fallback_region
    l = int(fr["left"] - monitor["left"])
    t = int(fr["top"] - monitor["top"])
    w = int(fr["width"])
    h = int(fr["height"])
    cv2.rectangle(preview, (l, t), (l + w, t + h), (0, 255, 255), 2)
    cv2.putText(
        preview,
        "Select ROI and press ENTER / SPACE, or C to cancel",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 255),
        2,
    )
    roi = cv2.selectROI("Select Fishing Region", preview, showCrosshair=True, fromCenter=False)
    cv2.destroyWindow("Select Fishing Region")
    x, y, rw, rh = [int(v) for v in roi]
    if rw <= 0 or rh <= 0:
        return None
    return {
        "left": monitor["left"] + x,
        "top": monitor["top"] + y,
        "width": rw,
        "height": rh,
    }


def run_bot(
    config: Config,
    config_path: Path,
    start_running: bool = False,
    stop_event: Optional[object] = None,
    status_callback: Optional[Callable[[str], None]] = None,
    allow_hotkeys: bool = True,
    dry_run_override: Optional[bool] = None,
) -> None:
    pydirectinput.PAUSE = 0.0
    pydirectinput.FAILSAFE = False

    running = start_running
    dry_run = config.dry_run_default if dry_run_override is None else dry_run_override
    frame_interval = 1.0 / max(1, config.target_fps)
    pulse_min = 0.01
    pulse_max = 0.05
    input_backend = (config.input_backend or "pydirectinput").strip().lower()
    auto_key = config.auto_action_key.strip().lower()
    auto_interval = max(0.1, config.auto_action_interval_sec)
    auto_hold = max(0.01, config.auto_action_hold_sec)
    auto_idle_grace = max(0.0, config.auto_action_idle_grace_sec)
    prompt_scan_interval = max(0.03, config.prompt_detect_interval_sec)
    prompt_cooldown = max(0.1, config.prompt_cooldown_sec)
    auto_click_interval = max(0.1, config.auto_click_interval_sec)
    recovery_timeout = max(0.5, config.recovery_no_line_timeout_sec)
    recovery_cooldown = max(1.0, config.recovery_escape_cooldown_sec)
    recovery_click_attempts_max = max(0, config.recovery_click_attempts)
    recovery_click_interval = min(1.2, max(0.7, recovery_timeout * 0.35))
    fine_zone_px = max(config.dead_zone_px + 1, config.fine_control_zone_px)
    fine_tap_sec = max(0.006, config.fine_tap_sec)
    fine_tap_cooldown = max(0.0, config.fine_tap_cooldown_sec)
    last_auto_action_at = -auto_interval
    last_prompt_action_at = -prompt_cooldown
    last_prompt_seen_at = 0.0
    last_auto_click_at = -auto_click_interval
    last_recovery_escape_at = -recovery_cooldown
    last_recovery_click_at = -recovery_click_interval
    last_fine_tap_at = -fine_tap_cooldown
    next_prompt_scan_at = 0.0
    prompt_detected = False
    prompt_point: Optional[Tuple[int, int]] = None
    last_prompt_point: Optional[Tuple[int, int]] = None
    last_active_game_at = 0.0
    has_seen_active_game = False
    recovery_clicks_done = 0
    held_control_key: Optional[str] = None
    _ = config_path  # 纯日志模式下不再使用弹窗选区

    def release_control_keys() -> None:
        nonlocal held_control_key
        release_keys(config.left_key, config.right_key, input_backend)
        held_control_key = None

    def apply_control_key(key: Optional[str]) -> None:
        nonlocal held_control_key
        if dry_run:
            held_control_key = key
            return
        if key is None:
            release_control_keys()
            return
        if held_control_key == key:
            return
        if held_control_key is not None:
            key_up(held_control_key, input_backend)
        other_key = config.left_key if key == config.right_key else config.right_key
        key_up(other_key, input_backend)
        key_down(key, input_backend)
        held_control_key = key

    if allow_hotkeys:
        print("F8: start automation")
        print("F9: pause automation")
        print("F6: toggle test mode (no key presses)")
        print("ESC: exit")
    print(f"Control keys: left={config.left_key}, right={config.right_key}, backend={input_backend}")
    print(f"Mode: {'TEST(no key presses)' if dry_run else 'LIVE(will press keys)'}")
    print(f"capture_region: {config.capture_region}")
    if not allow_hotkeys:
        print("GUI mode: hotkeys disabled, use the window buttons.")
    print(
        "Auto action: "
        f"{'ON' if config.auto_action_enabled else 'OFF'} key={auto_key or '-'} "
        f"interval={auto_interval:.2f}s idle_grace={auto_idle_grace:.2f}s"
    )
    print(
        "Auto click: "
        f"{'ON' if config.auto_click_enabled else 'OFF'} interval={auto_click_interval:.2f}s "
        f"position={config.auto_click_position or 'auto'}"
    )
    print("Status: mode run fish_x line_x bar_span error action hit% lost")
    if config.test_image_path:
        print(f"静态图测试: {config.test_image_path}")

    fish_template = None
    if config.use_template_matching:
        fish_template = load_template_image(config_path, config.fish_template_path)
        print(
            "Template matching: "
            f"fish={'ON' if fish_template is not None else 'missing'} "
            f"threshold={config.template_match_threshold:.2f}"
        )

    with mss.MSS() as sct:
        static_bgr = None
        if config.test_image_path:
            img_path = Path(config.test_image_path)
            if img_path.exists():
                static_bgr = cv2.imread(str(img_path))
                if static_bgr is None:
                    print("警告: test_image_path 读取失败，改为屏幕抓取模式")
            else:
                print("警告: test_image_path 不存在，改为屏幕抓取模式")
        frame_id = 0
        last_line_len = 0
        prev_fish_x: Optional[int] = None
        prev_line_x: Optional[int] = None
        prev_bar_span: Optional[Tuple[int, int]] = None
        prev_gray: Optional[np.ndarray] = None
        fish_lost = 0
        line_lost = 0
        bar_lost = 0
        while True:
            loop_start = time.perf_counter()

            if is_stop_requested(stop_event):
                break

            if allow_hotkeys and keyboard.is_pressed("f8"):
                running = True
                last_auto_action_at = -auto_interval
                time.sleep(0.2)
            if allow_hotkeys and keyboard.is_pressed("f9"):
                running = False
                release_control_keys()
                time.sleep(0.2)
            if allow_hotkeys and keyboard.is_pressed("f6"):
                dry_run = not dry_run
                release_control_keys()
                print(f"\nMode changed: {'TEST(no key presses)' if dry_run else 'LIVE(will press keys)'}")
                time.sleep(0.2)
            if allow_hotkeys and keyboard.is_pressed("esc"):
                break

            if static_bgr is not None:
                bgr = static_bgr.copy()
            else:
                shot = sct.grab(config.capture_region)
                frame = np.array(shot)
                bgr = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
            hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
            hsv = enhance_hsv(hsv, config.enable_clahe)
            gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)

            fish_mask = make_mask(
                hsv, config.fish_hsv_low, config.fish_hsv_high, config.mask_open_kernel, config.mask_close_kernel
            )
            line_mask_hsv = make_mask(
                hsv, config.line_hsv_low, config.line_hsv_high, config.mask_open_kernel, config.mask_close_kernel
            )
            line_mask_shape = yellow_line_component_mask(bgr, hsv, tolerance=12, min_area=config.min_blob_area)
            line_mask_hsv = vertical_line_component_mask(line_mask_hsv, min_area=config.min_blob_area)
            line_mask = cv2.bitwise_or(line_mask_hsv, line_mask_shape)
            bar_mask = make_mask(
                hsv, config.bar_hsv_low, config.bar_hsv_high, config.mask_open_kernel, config.mask_close_kernel
            )
            total_px = fish_mask.size
            fish_ratio = float(np.count_nonzero(fish_mask)) / total_px
            line_ratio = float(np.count_nonzero(line_mask)) / total_px
            bar_ratio = float(np.count_nonzero(bar_mask)) / total_px

            fish_col_counts = np.count_nonzero(fish_mask, axis=0)
            line_col_counts = np.count_nonzero(line_mask, axis=0)
            bar_col_counts = np.count_nonzero(bar_mask, axis=0)

            fish_x = None
            line_x = None
            bar_span = None
            fish_source = "none"
            min_target_width = max(24, bgr.shape[1] // 35)

            fish_template_match = template_center_x(bgr, fish_template, config.template_match_threshold)
            if fish_template_match is not None:
                fish_x = fish_template_match[0]
                fish_source = "template"

            if fish_x is None:
                shaped_fish_x = turquoise_indicator_center_x(
                    hsv,
                    config.min_blob_area,
                    config.fish_hsv_low,
                    config.fish_hsv_high,
                )
                if shaped_fish_x is not None:
                    fish_x = shaped_fish_x
                    fish_source = "shape"

            if line_x is None:
                line_x = yellow_line_center_x(hsv, config.min_blob_area, bgr)

            # 优先按列信号识别（对横向条形UI更稳定）。
            if fish_x is None:
                fish_seg = longest_span_from_counts(fish_col_counts, config.min_col_pixels, min_width=min_target_width)
                if fish_seg is not None:
                    fish_x = (fish_seg[0] + fish_seg[1]) // 2
                    fish_source = "colspan"

            if line_x is None:
                line_x = peak_x_from_counts(line_col_counts, config.min_col_pixels, prev_line_x, config.max_x_jump)
            bar_span = longest_span_from_counts(bar_col_counts, config.min_col_pixels, min_width=max(8, bgr.shape[1] // 6))

            # 条形边界有重叠时，改用联合掩膜估算边界。
            if bar_span is None:
                merged_for_bar = cv2.bitwise_or(bar_mask, fish_mask)
                merged_for_bar = cv2.bitwise_or(merged_for_bar, line_mask)
                merged_counts = np.count_nonzero(merged_for_bar, axis=0)
                bar_span = longest_span_from_counts(
                    merged_counts, config.min_col_pixels, min_width=max(8, bgr.shape[1] // 6)
                )

            # 轮廓法对细线和断裂目标容易丢失，失败时用投影兜底。
            if fish_x is None:
                fish_span = longest_span_from_counts(fish_col_counts, config.min_col_pixels, min_width=min_target_width)
                if fish_span is not None:
                    fish_source = "proj"
                    fish_x = (fish_span[0] + fish_span[1]) // 2
            if line_x is None:
                line_x = center_x_by_projection(line_mask, min_col_pixels=config.min_col_pixels)
            if bar_span is None:
                bar_span = span_by_projection(bar_mask, min_col_pixels=config.min_col_pixels)

            # fish 常见问题: 色相稍偏就会全部丢失，做一次宽松阈值二次检测。
            if fish_x is None:
                relaxed_low, relaxed_high = make_relaxed_range(config.fish_hsv_low, config.fish_hsv_high)
                fish_mask_relaxed = make_mask(
                    hsv, relaxed_low, relaxed_high, config.mask_open_kernel, config.mask_close_kernel
                )
                fish_x = tracked_blob_center_x(
                    fish_mask_relaxed,
                    config.min_blob_area,
                    prev_fish_x,
                    config.max_x_jump,
                    min_width=min_target_width,
                )
                if fish_x is None:
                    relaxed_counts = np.count_nonzero(fish_mask_relaxed, axis=0)
                    relaxed_span = longest_span_from_counts(
                        relaxed_counts,
                        config.min_col_pixels,
                        min_width=min_target_width,
                    )
                    if relaxed_span is not None:
                        fish_x = (relaxed_span[0] + relaxed_span[1]) // 2
                if fish_x is not None:
                    fish_source = "relaxed"

            # 如果 bar 受 line/fish 重合影响，使用联合掩膜求跨度兜底。
            if bar_span is None or (bar_span[1] - bar_span[0]) < max(20, bgr.shape[1] // 5):
                merged_mask = cv2.bitwise_or(bar_mask, fish_mask)
                merged_mask = cv2.bitwise_or(merged_mask, line_mask)
                merged_span = span_by_projection(merged_mask, min_col_pixels=config.min_col_pixels)
                if merged_span is not None:
                    bar_span = merged_span

            # 最后兜底: motion 估计 fish，大幅减少 fish_x=NONE。
            if fish_x is None:
                motion_x = motion_center_x(prev_gray, gray, config.min_col_pixels)
                if motion_x is not None:
                    fish_x = motion_x
                    fish_source = "motion"

            if fish_x is None:
                fish_lost += 1
                if prev_fish_x is not None and fish_lost <= config.max_lost_frames:
                    fish_x = prev_fish_x
                    fish_source = "history"
            else:
                fish_lost = 0
                prev_fish_x = fish_x

            if line_x is None:
                line_lost += 1
                if prev_line_x is not None and line_lost <= config.max_lost_frames:
                    line_x = prev_line_x
            else:
                line_lost = 0
                prev_line_x = line_x

            if bar_span is None:
                bar_lost += 1
                if prev_bar_span is not None and bar_lost <= config.max_lost_frames:
                    bar_span = prev_bar_span
            else:
                bar_lost = 0
                prev_bar_span = bar_span

            action = "HOLD"
            error = None
            key_echo = "-"
            auto_key_echo = "-"
            click_echo = "-"
            active_game = fish_x is not None and line_x is not None
            now = time.perf_counter()
            if active_game:
                last_active_game_at = now
                has_seen_active_game = True
                recovery_clicks_done = 0

            prompt_detected = False
            prompt_point = None
            if running and config.auto_action_enabled and config.prompt_detection_enabled and now >= next_prompt_scan_at:
                next_prompt_scan_at = now + prompt_scan_interval
                prompt_region = config.prompt_region or default_prompt_scan_region(sct.monitors[1])
                prompt_shot = sct.grab(prompt_region)
                prompt_frame = np.array(prompt_shot)
                prompt_bgr = cv2.cvtColor(prompt_frame, cv2.COLOR_BGRA2BGR)
                prompt_local_point = detect_action_prompt(prompt_bgr)
                if prompt_local_point is not None:
                    prompt_detected = True
                    last_prompt_seen_at = now
                    prompt_point = (
                        int(prompt_region["left"] + prompt_local_point[0]),
                        int(prompt_region["top"] + prompt_local_point[1]),
                    )
                    last_prompt_point = prompt_point

            if running and fish_x is not None and line_x is not None:
                left_bound = 0
                right_bound = bgr.shape[1] - 1
                if bar_span is not None:
                    left_bound = bar_span[0] + config.edge_margin_px
                    right_bound = bar_span[1] - config.edge_margin_px

                error = fish_x - line_x

                if line_x <= left_bound:
                    action = "RIGHT_EDGE_RECOVER"
                    key_echo = config.right_key.upper()
                    if config.hold_control_enabled:
                        apply_control_key(config.right_key)
                    elif not dry_run:
                        tap(config.right_key, pulse_min, input_backend)
                elif line_x >= right_bound:
                    action = "LEFT_EDGE_RECOVER"
                    key_echo = config.left_key.upper()
                    if config.hold_control_enabled:
                        apply_control_key(config.left_key)
                    elif not dry_run:
                        tap(config.left_key, pulse_min, input_backend)
                elif error > config.dead_zone_px:
                    action = "MOVE_RIGHT"
                    key_echo = config.right_key.upper()
                    if config.hold_control_enabled and abs(error) > fine_zone_px:
                        apply_control_key(config.right_key)
                    else:
                        apply_control_key(None)
                        if not dry_run and now - last_fine_tap_at >= fine_tap_cooldown:
                            tap(config.right_key, fine_tap_sec, input_backend)
                            last_fine_tap_at = now
                elif error < -config.dead_zone_px:
                    action = "MOVE_LEFT"
                    key_echo = config.left_key.upper()
                    if config.hold_control_enabled and abs(error) > fine_zone_px:
                        apply_control_key(config.left_key)
                    else:
                        apply_control_key(None)
                        if not dry_run and now - last_fine_tap_at >= fine_tap_cooldown:
                            tap(config.left_key, fine_tap_sec, input_backend)
                            last_fine_tap_at = now
                else:
                    action = "DEAD_ZONE_HOLD"
                    apply_control_key(None)
            else:
                release_control_keys()
                if not running:
                    action = "PAUSED"
                elif fish_x is None and line_x is None:
                    action = "NO_FISH_NO_LINE"
                elif fish_x is None:
                    action = "NO_FISH"
                elif line_x is None:
                    action = "NO_LINE"

            if (
                running
                and config.auto_action_enabled
                and auto_key
                and prompt_detected
                and now - last_prompt_action_at >= prompt_cooldown
            ):
                release_control_keys()
                if not dry_run:
                    tap(auto_key, auto_hold, input_backend)
                last_prompt_action_at = now
                auto_key_echo = auto_key.upper()
                action = f"{action}+PROMPT_{auto_key_echo}"
            elif (
                running
                and config.auto_action_enabled
                and auto_key
                and not active_game
                and now - last_active_game_at >= auto_idle_grace
                and now - last_auto_action_at >= auto_interval
            ):
                release_control_keys()
                if not dry_run:
                    tap(auto_key, auto_hold, input_backend)
                last_auto_action_at = now
                auto_key_echo = auto_key.upper()
                action = f"{action}+AUTO_{auto_key_echo}"

            if (
                running
                and config.auto_click_enabled
                and not dry_run
                and (
                    (prompt_detected and now - last_auto_click_at >= prompt_cooldown)
                    or (not active_game and now - last_auto_click_at >= auto_click_interval)
                )
            ):
                click_x, click_y = resolve_auto_click_point(config, sct.monitors[1], prompt_point or last_prompt_point)
                click_at(click_x, click_y)
                last_auto_click_at = now
                click_echo = f"{click_x},{click_y}"
                action = f"{action}+CLICK"

            if (
                running
                and config.recovery_escape_enabled
                and has_seen_active_game
                and line_x is None
                and not prompt_detected
                and now - last_prompt_seen_at >= recovery_timeout
                and now - last_active_game_at >= recovery_timeout
            ):
                release_control_keys()
                should_click_blank = (
                    config.recovery_click_before_escape
                    and recovery_clicks_done < recovery_click_attempts_max
                    and now - last_recovery_click_at >= recovery_click_interval
                )
                should_press_escape = (
                    not should_click_blank
                    and (not config.recovery_click_before_escape or recovery_clicks_done >= recovery_click_attempts_max)
                    and now - last_recovery_click_at >= recovery_timeout
                    and now - last_recovery_escape_at >= recovery_cooldown
                )
                if should_click_blank:
                    click_x, click_y = default_recovery_click_point(sct.monitors[1])
                    if not dry_run:
                        click_at(click_x, click_y)
                    last_recovery_click_at = now
                    last_auto_click_at = now
                    recovery_clicks_done += 1
                    click_echo = f"{click_x},{click_y}"
                    action = f"{action}+RECOVER_CLICK"
                elif should_press_escape:
                    if not dry_run:
                        tap("esc", 0.05, input_backend)
                    last_recovery_escape_at = now
                    last_prompt_seen_at = now
                    last_active_game_at = now
                    has_seen_active_game = False
                    recovery_clicks_done = 0
                    prev_fish_x = None
                    prev_line_x = None
                    prev_bar_span = None
                    fish_lost = 0
                    line_lost = 0
                    bar_lost = 0
                    auto_key_echo = "ESC"
                    action = f"{action}+RECOVER_ESC"

            frame_id += 1
            mode_label = "TEST" if dry_run else "LIVE"
            if frame_id % max(1, config.log_every_n_frames) == 0:
                bar_text = "None" if bar_span is None else f"{bar_span[0]}-{bar_span[1]}"
                err_text = "None" if error is None else f"{error:+d}"
                line = (
                    f"F{frame_id:06d} {mode_label[0]}{int(running)} "
                    f"fx:{str(fish_x):>4} lx:{str(line_x):>4} b:{bar_text:<9} "
                    f"e:{err_text:>5} s:{fish_source[:1]} a:{action:<14} "
                    f"k:{key_echo:<2} f:{auto_key_echo:<2} c:{click_echo:<9} p:{int(prompt_detected)} "
                    f"h:{fish_ratio * 100:4.1f}/{line_ratio * 100:4.1f}/{bar_ratio * 100:4.1f} "
                    f"l:{fish_lost}/{line_lost}/{bar_lost}"
                )
                # 先覆盖旧内容，再写新内容，避免残留字符。
                padded = line.ljust(max(last_line_len, len(line)))
                print(f"\r{padded}", end="", flush=True)
                if status_callback is not None:
                    status_callback(line)
                last_line_len = len(line)

            prev_gray = gray

            elapsed = time.perf_counter() - loop_start
            to_sleep = frame_interval - elapsed
            if to_sleep > 0:
                time.sleep(to_sleep)

    release_control_keys()
    print()


def main() -> None:
    parser = argparse.ArgumentParser(description="Fishing bot")
    parser.add_argument("--gui", action="store_true", help="open the GUI")
    parser.add_argument("--start", action="store_true", help="start automation immediately")
    parser.add_argument("--no-hotkeys", action="store_true", help="disable F8/F9/F6/ESC hotkeys")
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument("--dry-run", action="store_true", help="test mode: do not press keys")
    mode_group.add_argument("--live", action="store_true", help="live mode: press keys")
    args = parser.parse_args()

    config_path = resolve_config_path()
    if not config_path.exists():
        raise FileNotFoundError(f"找不到配置文件: {config_path}")
    print(f"读取配置: {config_path}")
    if args.gui:
        from fishing_gui import launch_gui

        launch_gui(config_path)
        return

    config = load_config(config_path)
    dry_override = True if args.dry_run else False if args.live else None
    run_bot(
        config,
        config_path,
        start_running=args.start,
        allow_hotkeys=not args.no_hotkeys,
        dry_run_override=dry_override,
    )


if __name__ == "__main__":
    main()
