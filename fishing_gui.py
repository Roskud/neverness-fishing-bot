import copy
import queue
import threading
import time
import tkinter as tk
import webbrowser
from pathlib import Path
from tkinter import messagebox, ttk
from typing import Optional

import cv2
import mss
import numpy as np

from fishing_bot import (
    Config,
    click_at,
    default_action_click_point,
    enhance_hsv,
    load_config,
    resolve_asset_path,
    run_bot,
    save_config,
    select_capture_region,
    select_capture_strip,
    tap,
    vertical_line_center_x_from_mask,
    vertical_line_component_mask,
)


LANGUAGE_OPTIONS = {
    "ru": "Русский",
    "zh": "中文",
    "en": "English",
}

LANGUAGE_CODES_BY_LABEL = {label: code for code, label in LANGUAGE_OPTIONS.items()}

TRANSLATIONS = {
    "ru": {
        "app_title": "Neverness Fishing Bot",
        "ready_status": "Готово. Нажми Старт, когда окно игры активно.",
        "launch": "Запуск",
        "language": "Язык",
        "simple_mode_hint": "Обычный запуск: выбери Полоса, при необходимости открой Калибровка, потом Старт.",
        "show_advanced": "Показать расширенные настройки",
        "hotkeys_hint": "Горячие клавиши во время работы: F8 старт/продолжить | F9 пауза | ESC остановить",
        "start": "Старт",
        "stop": "Стоп",
        "test_f": "Тест F",
        "save": "Сохранить",
        "dry_run": "Тестовый режим без нажатий",
        "start_delay": "Задержка старта, сек",
        "sponsor_text": "Быстрый VPN для игр, Telegram и повседневного интернета.",
        "telegram_bot": "Telegram-бот @boxvolt_bot",
        "telegram_channel": "Канал BoxVoltVPN",
        "auto_frame": "Автонажатие кнопки ловли",
        "auto_enable": "Включить авто-кнопку",
        "prompt_enable": "Искать подсказку F на экране",
        "key": "Кнопка",
        "interval_sec": "Интервал, сек",
        "hold_sec": "Удержание, сек",
        "idle_grace": "Пауза после мини-игры, сек",
        "prompt_cooldown": "Повтор F-подсказки, сек",
        "input_method": "Метод ввода",
        "auto_click": "Кликать мышью по F/меню",
        "click_interval": "Интервал клика, сек",
        "recovery_enable": "Автозакрытие зависания",
        "recovery_timeout": "Нет линии, сек",
        "tuning": "Выравнивание",
        "left": "Лево",
        "right": "Право",
        "dead_zone": "Мертвая зона px",
        "fast_hold": "Быстрое удержание A/D",
        "target_frame": "Цель выравнивания",
        "template_enable": "Искать по картинкам-референсам",
        "template_threshold": "Порог совпадения",
        "pipette": "Пипетка цвета",
        "color_from_ref": "Цвет из референса",
        "view_ref": "Посмотреть референс",
        "refresh": "Обновить",
        "disable_ref": "Отключить референс",
        "capture_region": "Область захвата",
        "choose": "Выбрать",
        "choose_strip": "Полоса",
        "click_position": "Позиция автоклика",
        "reset": "Сброс",
        "test_click": "Тест клик",
        "status": "Статус",
        "config_saved": "Конфиг сохранен.",
        "settings_error": "Ошибка настроек",
        "bot_running_title": "Бот запущен",
        "bot_already_running": "Бот уже запущен.",
        "started_status": "Бот запущен. Верни фокус в игру.",
        "started_log": "Старт: авто-режим включен.",
        "test_key_log": "Тест: через 3 секунды нажму {key}. Переключись в игру.",
        "test_key_status": "Тест {key}: нажму через {remaining}...",
        "test_key_success": "Тест: нажал {key} методом {backend}.",
        "test_key_error": "Не смог нажать {key}: {error}",
        "start_countdown": "Старт через {delay:.1f} сек. Переключись в игру.",
        "stopped": "Бот остановлен.",
        "stopping": "Останавливаю...",
        "stop_requested": "Стоп запрошен.",
        "choose_region_running": "Сначала останови бота, потом выбери область.",
        "calibrate": "Калибровка",
        "calibration_title": "Живая калибровка области",
        "calibration_hint": "Подгони область так, чтобы в яркой рамке была только горизонтальная полоска мини-игры.",
        "region_left_label": "Left",
        "region_top_label": "Top",
        "region_width_label": "Width",
        "region_height_label": "Height",
        "preview_loading": "Загрузка preview...",
        "preview_invalid": "Неверная область",
        "preview_detection": "Цель: {fish} | Линия: {line}",
        "calibration_picker": "Выбор цвета по preview",
        "calibration_pick_hint": "Сделай снимок, выбери линию или цель, кликни пипеткой по цвету и двигай допуск. Красная маска показывает, что будет найдено.",
        "yellow": "Жёлтая линия",
        "green": "Бирюзовая цель",
        "yellow_tolerance": "Допуск линии",
        "green_tolerance": "Допуск цели",
        "test_match": "Проверить",
        "recapture": "Снимок",
        "sample_waiting": "Кликни по цвету на снимке",
        "sample_info": "RGB={rgb} HSV={hsv}",
        "range_info": "HSV {low}-{high}",
        "mask_info": "{target}: маска {pixels} px, центр {center}",
        "snapshot_saved": "Снимок калибровки обновлён: {region}.",
        "color_pick_saved": "{target}: цвет сохранён HSV={median}, диапазон {low}-{high}.",
        "apply_region": "Сохранить область",
        "calibration_saved": "Калибровка сохранена: {region}",
        "close": "Закрыть",
        "choose_click_running": "Сначала останови бота, потом выбери позицию клика.",
        "region_updated": "Область захвата обновлена.",
        "strip_region_updated": "Полоса захвата обновлена.",
        "click_updated": "Позиция автоклика обновлена.",
        "click_reset": "Позиция автоклика сброшена: будет использоваться центр области F или низ справа.",
        "reference": "Референс",
        "file_missing": "Файл не найден: {path}",
        "open_failed": "Не смог открыть: {path}",
        "ref_opened": "Открыл референс: {name}.",
        "pipette_running": "Сначала останови бота, потом используй пипетку.",
        "pipette_title": "Пипетка",
        "pipette_source": "Пипетка",
        "reference_source": "Референс",
        "color_applied": "{source}: HSV={median}, диапазон {low}-{high}. Референс отключен.",
        "ref_disabled": "Референс отключен, бот будет искать цель по цвету/форме.",
        "templates_refreshed": "Статус эталонов обновлен.",
        "test_click_log": "Тест: через 3 секунды кликну {x},{y}. Переключись в игру.",
        "test_click_status": "Тест клика: кликну через {remaining}...",
        "test_click_success": "Тест: кликнул {x},{y}.",
        "test_click_error": "Не смог кликнуть: {error}",
        "error_status": "Ошибка.",
        "error_prefix": "Ошибка: {message}",
        "need_number": "нужно число.",
        "need_integer": "нужно целое число.",
        "minimum": "минимум {minimum}.",
        "auto_click_auto": "Авто: центр области F, иначе низ справа",
        "template_exists": "есть",
        "template_missing": "нет",
        "template_status": "Бирюзовая цель: {status} ({path})",
        "fish_hsv_status": "Цвет цели HSV: low={low} high={high}",
        "language_changed": "Язык интерфейса изменен: {language}.",
    },
    "en": {
        "app_title": "Neverness Fishing Bot",
        "ready_status": "Ready. Press Start while the game window is active.",
        "launch": "Launch",
        "language": "Language",
        "simple_mode_hint": "Normal setup: choose Stripe, calibrate if needed, then Start.",
        "show_advanced": "Show advanced settings",
        "hotkeys_hint": "Hotkeys while running: F8 start/resume | F9 pause | ESC stop",
        "start": "Start",
        "stop": "Stop",
        "test_f": "Test F",
        "save": "Save",
        "dry_run": "Test mode without inputs",
        "start_delay": "Start delay, sec",
        "sponsor_text": "Fast VPN for games, Telegram, and everyday internet.",
        "telegram_bot": "Telegram bot @boxvolt_bot",
        "telegram_channel": "BoxVoltVPN channel",
        "auto_frame": "Auto Fishing Key",
        "auto_enable": "Enable auto key",
        "prompt_enable": "Detect F prompt on screen",
        "key": "Key",
        "interval_sec": "Interval, sec",
        "hold_sec": "Hold, sec",
        "idle_grace": "Pause after mini-game, sec",
        "prompt_cooldown": "F prompt repeat, sec",
        "input_method": "Input method",
        "auto_click": "Mouse click F/menu",
        "click_interval": "Click interval, sec",
        "recovery_enable": "Auto close stuck screen",
        "recovery_timeout": "No line, sec",
        "tuning": "Alignment",
        "left": "Left",
        "right": "Right",
        "dead_zone": "Dead zone px",
        "fast_hold": "Fast A/D hold",
        "target_frame": "Alignment Target",
        "template_enable": "Use reference images",
        "template_threshold": "Match threshold",
        "pipette": "Color pipette",
        "color_from_ref": "Color from reference",
        "view_ref": "View reference",
        "refresh": "Refresh",
        "disable_ref": "Disable reference",
        "capture_region": "Capture Region",
        "choose": "Choose",
        "choose_strip": "Stripe",
        "click_position": "Auto Click Position",
        "reset": "Reset",
        "test_click": "Test click",
        "status": "Status",
        "config_saved": "Config saved.",
        "settings_error": "Settings error",
        "bot_running_title": "Bot is running",
        "bot_already_running": "Bot is already running.",
        "started_status": "Bot started. Return focus to the game.",
        "started_log": "Start: auto mode enabled.",
        "test_key_log": "Test: I will press {key} in 3 seconds. Switch to the game.",
        "test_key_status": "Test {key}: pressing in {remaining}...",
        "test_key_success": "Test: pressed {key} with {backend}.",
        "test_key_error": "Could not press {key}: {error}",
        "start_countdown": "Starting in {delay:.1f} sec. Switch to the game.",
        "stopped": "Bot stopped.",
        "stopping": "Stopping...",
        "stop_requested": "Stop requested.",
        "choose_region_running": "Stop the bot first, then choose the region.",
        "calibrate": "Calibrate",
        "calibration_title": "Live Region Calibration",
        "calibration_hint": "Adjust the region so only the horizontal mini-game bar is inside the bright frame.",
        "region_left_label": "Left",
        "region_top_label": "Top",
        "region_width_label": "Width",
        "region_height_label": "Height",
        "preview_loading": "Loading preview...",
        "preview_invalid": "Invalid region",
        "preview_detection": "Target: {fish} | Line: {line}",
        "calibration_picker": "Pick Color From Preview",
        "calibration_pick_hint": "Capture a still image, choose line or target, click the color, then tune tolerance. The red mask shows what will be matched.",
        "yellow": "Yellow",
        "green": "Green",
        "yellow_tolerance": "Yellow tolerance",
        "green_tolerance": "Green tolerance",
        "test_match": "Test match",
        "recapture": "Recapture",
        "sample_waiting": "Click a color on the snapshot",
        "sample_info": "RGB={rgb} HSV={hsv}",
        "range_info": "HSV {low}-{high}",
        "mask_info": "{target}: mask {pixels} px, center {center}",
        "snapshot_saved": "Calibration snapshot updated: {region}.",
        "color_pick_saved": "{target}: color saved HSV={median}, range {low}-{high}.",
        "apply_region": "Save region",
        "calibration_saved": "Calibration saved: {region}",
        "close": "Close",
        "choose_click_running": "Stop the bot first, then choose the click position.",
        "region_updated": "Capture region updated.",
        "strip_region_updated": "Capture stripe updated.",
        "click_updated": "Auto click position updated.",
        "click_reset": "Auto click position reset: using F area center or lower-right default.",
        "reference": "Reference",
        "file_missing": "File not found: {path}",
        "open_failed": "Could not open: {path}",
        "ref_opened": "Opened reference: {name}.",
        "pipette_running": "Stop the bot first, then use the pipette.",
        "pipette_title": "Pipette",
        "pipette_source": "Pipette",
        "reference_source": "Reference",
        "color_applied": "{source}: HSV={median}, range {low}-{high}. Reference disabled.",
        "ref_disabled": "Reference disabled; the bot will find the target by color/shape.",
        "templates_refreshed": "Reference status refreshed.",
        "test_click_log": "Test: I will click {x},{y} in 3 seconds. Switch to the game.",
        "test_click_status": "Click test: clicking in {remaining}...",
        "test_click_success": "Test: clicked {x},{y}.",
        "test_click_error": "Could not click: {error}",
        "error_status": "Error.",
        "error_prefix": "Error: {message}",
        "need_number": "must be a number.",
        "need_integer": "must be an integer.",
        "minimum": "minimum {minimum}.",
        "auto_click_auto": "Auto: F area center, otherwise lower-right",
        "template_exists": "found",
        "template_missing": "missing",
        "template_status": "Turquoise target: {status} ({path})",
        "fish_hsv_status": "Target HSV color: low={low} high={high}",
        "language_changed": "Interface language changed: {language}.",
    },
    "zh": {
        "app_title": "Neverness 钓鱼助手",
        "ready_status": "准备好了。游戏窗口激活后点击开始。",
        "launch": "启动",
        "language": "语言",
        "simple_mode_hint": "普通设置：选择条带，必要时校准，然后开始。",
        "show_advanced": "显示高级设置",
        "hotkeys_hint": "运行快捷键：F8 开始/继续 | F9 暂停 | ESC 停止",
        "start": "开始",
        "stop": "停止",
        "test_f": "测试 F",
        "save": "保存",
        "dry_run": "测试模式，不发送按键",
        "start_delay": "启动延迟，秒",
        "sponsor_text": "适合游戏、Telegram 和日常上网的快速 VPN。",
        "telegram_bot": "Telegram 机器人 @boxvolt_bot",
        "telegram_channel": "BoxVoltVPN 频道",
        "auto_frame": "自动钓鱼按键",
        "auto_enable": "启用自动按键",
        "prompt_enable": "检测屏幕上的 F 提示",
        "key": "按键",
        "interval_sec": "间隔，秒",
        "hold_sec": "按住，秒",
        "idle_grace": "小游戏后暂停，秒",
        "prompt_cooldown": "F 提示重复，秒",
        "input_method": "输入方式",
        "auto_click": "鼠标点击 F/菜单",
        "click_interval": "点击间隔，秒",
        "recovery_enable": "自动关闭卡住界面",
        "recovery_timeout": "无线条，秒",
        "tuning": "对齐",
        "left": "左",
        "right": "右",
        "dead_zone": "死区 px",
        "fast_hold": "快速按住 A/D",
        "target_frame": "对齐目标",
        "template_enable": "使用参考图片",
        "template_threshold": "匹配阈值",
        "pipette": "颜色吸管",
        "color_from_ref": "从参考取色",
        "view_ref": "查看参考",
        "refresh": "刷新",
        "disable_ref": "禁用参考",
        "capture_region": "截图区域",
        "choose": "选择",
        "choose_strip": "条带",
        "click_position": "自动点击位置",
        "reset": "重置",
        "test_click": "测试点击",
        "status": "状态",
        "config_saved": "配置已保存。",
        "settings_error": "设置错误",
        "bot_running_title": "机器人正在运行",
        "bot_already_running": "机器人已经在运行。",
        "started_status": "机器人已启动。请把焦点切回游戏。",
        "started_log": "开始：自动模式已启用。",
        "test_key_log": "测试：3 秒后按 {key}。请切回游戏。",
        "test_key_status": "测试 {key}：{remaining} 秒后按下...",
        "test_key_success": "测试：已用 {backend} 按下 {key}。",
        "test_key_error": "无法按下 {key}: {error}",
        "start_countdown": "{delay:.1f} 秒后开始。请切回游戏。",
        "stopped": "机器人已停止。",
        "stopping": "正在停止...",
        "stop_requested": "已请求停止。",
        "choose_region_running": "请先停止机器人，再选择区域。",
        "calibrate": "校准",
        "calibration_title": "实时区域校准",
        "calibration_hint": "调整区域，让亮框内只包含小游戏的水平条。",
        "region_left_label": "Left",
        "region_top_label": "Top",
        "region_width_label": "Width",
        "region_height_label": "Height",
        "preview_loading": "正在加载预览...",
        "preview_invalid": "区域无效",
        "preview_detection": "目标：{fish} | 线：{line}",
        "calibration_picker": "从预览取色",
        "calibration_pick_hint": "先截图，再选择黄线或目标，点击颜色并调整容差。红色遮罩显示会匹配到的区域。",
        "yellow": "黄线",
        "green": "青色目标",
        "yellow_tolerance": "黄线容差",
        "green_tolerance": "目标容差",
        "test_match": "测试匹配",
        "recapture": "重新截图",
        "sample_waiting": "在截图上点击颜色",
        "sample_info": "RGB={rgb} HSV={hsv}",
        "range_info": "HSV {low}-{high}",
        "mask_info": "{target}: 遮罩 {pixels} px，中心 {center}",
        "snapshot_saved": "校准截图已更新：{region}。",
        "color_pick_saved": "{target}: 颜色已保存 HSV={median}, 范围 {low}-{high}。",
        "apply_region": "保存区域",
        "calibration_saved": "校准已保存：{region}",
        "close": "关闭",
        "choose_click_running": "请先停止机器人，再选择点击位置。",
        "region_updated": "截图区域已更新。",
        "strip_region_updated": "截图条带已更新。",
        "click_updated": "自动点击位置已更新。",
        "click_reset": "自动点击位置已重置：使用 F 区域中心或右下默认点。",
        "reference": "参考",
        "file_missing": "找不到文件：{path}",
        "open_failed": "无法打开：{path}",
        "ref_opened": "已打开参考：{name}。",
        "pipette_running": "请先停止机器人，再使用吸管。",
        "pipette_title": "吸管",
        "pipette_source": "吸管",
        "reference_source": "参考",
        "color_applied": "{source}: HSV={median}, 范围 {low}-{high}。参考已禁用。",
        "ref_disabled": "参考已禁用，机器人将按颜色/形状寻找目标。",
        "templates_refreshed": "参考状态已刷新。",
        "test_click_log": "测试：3 秒后点击 {x},{y}。请切回游戏。",
        "test_click_status": "点击测试：{remaining} 秒后点击...",
        "test_click_success": "测试：已点击 {x},{y}。",
        "test_click_error": "无法点击：{error}",
        "error_status": "错误。",
        "error_prefix": "错误：{message}",
        "need_number": "必须是数字。",
        "need_integer": "必须是整数。",
        "minimum": "最小值 {minimum}。",
        "auto_click_auto": "自动：F 区域中心，否则右下",
        "template_exists": "存在",
        "template_missing": "缺失",
        "template_status": "青绿色目标：{status} ({path})",
        "fish_hsv_status": "目标 HSV 颜色：low={low} high={high}",
        "language_changed": "界面语言已切换：{language}。",
    },
}


class FishingBotGUI(tk.Tk):
    def __init__(self, config_path: Path) -> None:
        super().__init__()
        self.config_path = config_path
        self.config = load_config(config_path)
        self.stop_event: Optional[threading.Event] = None
        self.worker: Optional[threading.Thread] = None
        self.calibration_window: Optional[tk.Toplevel] = None
        self.calibration_preview_image: Optional[tk.PhotoImage] = None
        self.log_queue: queue.Queue = queue.Queue()
        self.root_frame: Optional[ttk.Frame] = None

        if self.config.ui_language not in TRANSLATIONS:
            self.config.ui_language = "ru"

        self.title(self.text("app_title"))
        self.geometry("760x900")
        self.minsize(700, 820)

        self.language_var = tk.StringVar(value=LANGUAGE_OPTIONS[self.config.ui_language])
        self.input_backend_var = tk.StringVar(value=self.config.input_backend)
        self.auto_enabled_var = tk.BooleanVar(value=self.config.auto_action_enabled)
        self.auto_key_var = tk.StringVar(value=self.config.auto_action_key)
        self.auto_interval_var = tk.StringVar(value=str(self.config.auto_action_interval_sec))
        self.auto_hold_var = tk.StringVar(value=str(self.config.auto_action_hold_sec))
        self.auto_idle_var = tk.StringVar(value=str(self.config.auto_action_idle_grace_sec))
        self.prompt_enabled_var = tk.BooleanVar(value=self.config.prompt_detection_enabled)
        self.prompt_cooldown_var = tk.StringVar(value=str(self.config.prompt_cooldown_sec))
        self.auto_click_enabled_var = tk.BooleanVar(value=self.config.auto_click_enabled)
        self.auto_click_interval_var = tk.StringVar(value=str(self.config.auto_click_interval_sec))
        self.recovery_escape_var = tk.BooleanVar(value=self.config.recovery_escape_enabled)
        self.recovery_timeout_var = tk.StringVar(value=str(self.config.recovery_no_line_timeout_sec))
        self.template_enabled_var = tk.BooleanVar(value=self.config.use_template_matching)
        self.template_threshold_var = tk.StringVar(value=str(self.config.template_match_threshold))
        self.hold_control_var = tk.BooleanVar(value=self.config.hold_control_enabled)
        self.start_delay_var = tk.StringVar(value=str(self.config.gui_start_delay_sec))
        self.left_key_var = tk.StringVar(value=self.config.left_key)
        self.right_key_var = tk.StringVar(value=self.config.right_key)
        self.dead_zone_var = tk.StringVar(value=str(self.config.dead_zone_px))
        self.target_fps_var = tk.StringVar(value=str(self.config.target_fps))
        self.dry_run_var = tk.BooleanVar(value=self.config.dry_run_default)
        self.advanced_visible_var = tk.BooleanVar(value=False)
        self.status_var = tk.StringVar(value=self.text("ready_status"))
        self.region_var = tk.StringVar(value=self.format_region(self.config.capture_region))
        self.click_position_var = tk.StringVar(value=self.format_click_position(self.config.auto_click_position))
        self.template_status_var = tk.StringVar(value=self.format_template_status())
        self.fish_hsv_var = tk.StringVar(value=self.format_fish_hsv())

        self.build_ui()
        self.after(100, self.poll_log_queue)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def text(self, key: str) -> str:
        language = self.config.ui_language if self.config.ui_language in TRANSLATIONS else "ru"
        return TRANSLATIONS[language].get(key, TRANSLATIONS["ru"].get(key, key))

    def language_code_from_label(self, label: str) -> str:
        return LANGUAGE_CODES_BY_LABEL.get(label, self.config.ui_language if self.config.ui_language in TRANSLATIONS else "ru")

    def on_language_changed(self, _event: object = None) -> None:
        try:
            self.apply_form_to_config()
        except ValueError:
            pass
        self.config.ui_language = self.language_code_from_label(self.language_var.get())
        save_config(self.config_path, self.config)
        self.title(self.text("app_title"))
        self.status_var.set(self.text("ready_status"))
        self.click_position_var.set(self.format_click_position(self.config.auto_click_position))
        self.template_status_var.set(self.format_template_status())
        self.fish_hsv_var.set(self.format_fish_hsv())
        self.build_ui()
        self.append_log(self.text("language_changed").format(language=LANGUAGE_OPTIONS[self.config.ui_language]))

    def build_ui(self) -> None:
        if self.root_frame is not None:
            self.root_frame.destroy()
        root = ttk.Frame(self, padding=14)
        self.root_frame = root
        root.pack(fill=tk.BOTH, expand=True)

        controls = ttk.LabelFrame(root, text=self.text("launch"), padding=10)
        controls.pack(fill=tk.X)

        ttk.Label(controls, text=self.text("simple_mode_hint")).grid(
            row=0, column=0, columnspan=4, sticky="w", pady=(0, 8)
        )
        ttk.Button(controls, text=self.text("start"), command=self.start_bot).grid(
            row=1, column=0, padx=(0, 8), sticky="ew"
        )
        ttk.Button(controls, text=self.text("stop"), command=self.stop_bot).grid(
            row=1, column=1, padx=(0, 8), sticky="ew"
        )
        ttk.Button(controls, text=self.text("test_f"), command=self.test_action_key).grid(
            row=1, column=2, padx=(0, 8), sticky="ew"
        )
        ttk.Button(controls, text=self.text("save"), command=self.on_save_clicked).grid(
            row=1, column=3, sticky="ew"
        )
        controls.columnconfigure((0, 1, 2, 3), weight=1)

        ttk.Label(controls, text=self.text("language")).grid(row=2, column=0, padx=(0, 8), pady=(10, 0), sticky="w")
        language_combo = ttk.Combobox(
            controls,
            textvariable=self.language_var,
            values=tuple(LANGUAGE_OPTIONS.values()),
            state="readonly",
            width=14,
        )
        language_combo.grid(row=2, column=1, padx=(0, 18), pady=(10, 0), sticky="ew")
        language_combo.bind("<<ComboboxSelected>>", self.on_language_changed)
        ttk.Checkbutton(
            controls,
            text=self.text("show_advanced"),
            variable=self.advanced_visible_var,
            command=self.build_ui,
        ).grid(row=2, column=2, columnspan=2, pady=(10, 0), sticky="w")

        if self.advanced_visible_var.get():
            ttk.Label(controls, text=self.text("hotkeys_hint")).grid(
                row=3, column=0, columnspan=4, sticky="w", pady=(8, 0)
            )
            ttk.Checkbutton(
                controls,
                text=self.text("dry_run"),
                variable=self.dry_run_var,
            ).grid(row=4, column=0, columnspan=2, pady=(8, 0), sticky="w")
            self.add_entry(controls, 4, 2, self.text("start_delay"), self.start_delay_var, 8)

        sponsor_frame = ttk.LabelFrame(root, text="BoxVolt VPN", padding=10)
        sponsor_frame.pack(fill=tk.X, pady=(12, 0))
        ttk.Label(
            sponsor_frame,
            text=self.text("sponsor_text"),
        ).grid(row=0, column=0, columnspan=2, sticky="w")
        ttk.Button(
            sponsor_frame,
            text=self.text("telegram_bot"),
            command=lambda: webbrowser.open("https://t.me/boxvolt_bot"),
        ).grid(row=1, column=0, padx=(0, 8), pady=(8, 0), sticky="ew")
        ttk.Button(
            sponsor_frame,
            text=self.text("telegram_channel"),
            command=lambda: webbrowser.open("https://t.me/BoxVoltVPN"),
        ).grid(row=1, column=1, pady=(8, 0), sticky="ew")
        sponsor_frame.columnconfigure((0, 1), weight=1)

        auto_frame = ttk.LabelFrame(root, text=self.text("auto_frame"), padding=10)
        auto_frame.pack(fill=tk.X, pady=(12, 0))
        ttk.Checkbutton(auto_frame, text=self.text("auto_enable"), variable=self.auto_enabled_var).grid(
            row=0, column=0, columnspan=2, sticky="w"
        )
        ttk.Checkbutton(auto_frame, text=self.text("prompt_enable"), variable=self.prompt_enabled_var).grid(
            row=0, column=2, columnspan=2, sticky="w"
        )
        self.add_entry(auto_frame, 1, 0, self.text("key"), self.auto_key_var, 8)
        self.add_entry(auto_frame, 1, 2, self.text("interval_sec"), self.auto_interval_var, 8)
        self.add_entry(auto_frame, 2, 0, self.text("hold_sec"), self.auto_hold_var, 8)
        self.add_entry(auto_frame, 2, 2, self.text("idle_grace"), self.auto_idle_var, 8)
        self.add_entry(auto_frame, 3, 0, self.text("prompt_cooldown"), self.prompt_cooldown_var, 8)
        ttk.Label(auto_frame, text=self.text("input_method")).grid(
            row=3, column=2, padx=(0, 8), pady=(8, 0), sticky="w"
        )
        ttk.Combobox(
            auto_frame,
            textvariable=self.input_backend_var,
            values=("pydirectinput", "keyboard", "auto"),
            state="readonly",
            width=14,
        ).grid(row=3, column=3, padx=(0, 18), pady=(8, 0), sticky="ew")
        ttk.Checkbutton(auto_frame, text=self.text("auto_click"), variable=self.auto_click_enabled_var).grid(
            row=4, column=0, columnspan=2, sticky="w", pady=(8, 0)
        )
        self.add_entry(auto_frame, 4, 2, self.text("click_interval"), self.auto_click_interval_var, 8)
        ttk.Checkbutton(auto_frame, text=self.text("recovery_enable"), variable=self.recovery_escape_var).grid(
            row=5, column=0, columnspan=2, sticky="w", pady=(8, 0)
        )
        self.add_entry(auto_frame, 5, 2, self.text("recovery_timeout"), self.recovery_timeout_var, 8)
        auto_frame.columnconfigure(1, weight=1)
        auto_frame.columnconfigure(3, weight=1)
        if not self.advanced_visible_var.get():
            auto_frame.pack_forget()

        tuning_frame = ttk.LabelFrame(root, text=self.text("tuning"), padding=10)
        tuning_frame.pack(fill=tk.X, pady=(12, 0))
        self.add_entry(tuning_frame, 0, 0, self.text("left"), self.left_key_var, 8)
        self.add_entry(tuning_frame, 0, 2, self.text("right"), self.right_key_var, 8)
        self.add_entry(tuning_frame, 1, 0, self.text("dead_zone"), self.dead_zone_var, 8)
        self.add_entry(tuning_frame, 1, 2, "FPS", self.target_fps_var, 8)
        ttk.Checkbutton(tuning_frame, text=self.text("fast_hold"), variable=self.hold_control_var).grid(
            row=2, column=0, columnspan=4, pady=(8, 0), sticky="w"
        )
        tuning_frame.columnconfigure(1, weight=1)
        tuning_frame.columnconfigure(3, weight=1)
        if not self.advanced_visible_var.get():
            tuning_frame.pack_forget()

        template_frame = ttk.LabelFrame(root, text=self.text("target_frame"), padding=10)
        template_frame.pack(fill=tk.X, pady=(12, 0))
        ttk.Checkbutton(template_frame, text=self.text("template_enable"), variable=self.template_enabled_var).grid(
            row=0, column=0, columnspan=2, sticky="w"
        )
        self.add_entry(template_frame, 0, 2, self.text("template_threshold"), self.template_threshold_var, 8)
        ttk.Label(template_frame, textvariable=self.template_status_var).grid(
            row=1, column=0, columnspan=4, pady=(8, 0), sticky="w"
        )
        ttk.Label(template_frame, textvariable=self.fish_hsv_var).grid(
            row=2, column=0, columnspan=4, pady=(8, 0), sticky="w"
        )
        ttk.Button(template_frame, text=self.text("pipette"), command=self.pick_fish_color).grid(
            row=3, column=0, padx=(0, 8), pady=(8, 0), sticky="ew"
        )
        ttk.Button(template_frame, text=self.text("color_from_ref"), command=self.pick_fish_color_from_reference).grid(
            row=3, column=1, padx=(0, 8), pady=(8, 0), sticky="ew"
        )
        ttk.Button(template_frame, text=self.text("view_ref"), command=self.view_fish_reference).grid(
            row=3, column=2, padx=(0, 8), pady=(8, 0), sticky="ew"
        )
        ttk.Button(template_frame, text=self.text("refresh"), command=self.refresh_template_status).grid(
            row=4, column=0, padx=(0, 8), pady=(8, 0), sticky="ew"
        )
        ttk.Button(template_frame, text=self.text("disable_ref"), command=self.disable_template_matching).grid(
            row=3, column=3, padx=(0, 8), pady=(8, 0), sticky="ew"
        )
        template_frame.columnconfigure((0, 1, 2, 3), weight=1)
        if not self.advanced_visible_var.get():
            template_frame.pack_forget()

        region_frame = ttk.LabelFrame(root, text=self.text("capture_region"), padding=10)
        region_frame.pack(fill=tk.X, pady=(12, 0))
        ttk.Label(region_frame, textvariable=self.region_var).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(region_frame, text=self.text("calibrate"), command=self.open_calibration_window).pack(
            side=tk.RIGHT, padx=(10, 0)
        )
        ttk.Button(region_frame, text=self.text("choose_strip"), command=self.choose_strip).pack(
            side=tk.RIGHT, padx=(10, 0)
        )
        ttk.Button(region_frame, text=self.text("choose"), command=self.choose_region).pack(
            side=tk.RIGHT, padx=(10, 0)
        )

        click_frame = ttk.LabelFrame(root, text=self.text("click_position"), padding=10)
        click_frame.pack(fill=tk.X, pady=(12, 0))
        ttk.Label(click_frame, textvariable=self.click_position_var).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(click_frame, text=self.text("reset"), command=self.reset_click_position).pack(
            side=tk.RIGHT, padx=(10, 0)
        )
        ttk.Button(click_frame, text=self.text("test_click"), command=self.test_click_position).pack(
            side=tk.RIGHT, padx=(10, 0)
        )
        ttk.Button(click_frame, text=self.text("choose"), command=self.choose_click_position).pack(side=tk.RIGHT)

        status_frame = ttk.LabelFrame(root, text=self.text("status"), padding=10)
        status_frame.pack(fill=tk.BOTH, expand=True, pady=(12, 0))
        ttk.Label(status_frame, textvariable=self.status_var, wraplength=560).pack(fill=tk.X)
        self.log_text = tk.Text(status_frame, height=10, wrap="word", state="disabled")
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=(8, 0))

    def add_entry(
        self,
        parent: ttk.LabelFrame,
        row: int,
        column: int,
        label: str,
        variable: tk.StringVar,
        width: int,
    ) -> None:
        ttk.Label(parent, text=label).grid(row=row, column=column, padx=(0, 8), pady=(8, 0), sticky="w")
        ttk.Entry(parent, textvariable=variable, width=width).grid(
            row=row, column=column + 1, padx=(0, 18), pady=(8, 0), sticky="ew"
        )

    def save_current_config(self) -> Config:
        try:
            self.apply_form_to_config()
            save_config(self.config_path, self.config)
            self.region_var.set(self.format_region(self.config.capture_region))
            self.click_position_var.set(self.format_click_position(self.config.auto_click_position))
            self.template_status_var.set(self.format_template_status())
            self.fish_hsv_var.set(self.format_fish_hsv())
            self.append_log(self.text("config_saved"))
            return self.config
        except ValueError as exc:
            messagebox.showerror(self.text("settings_error"), str(exc))
            raise

    def on_save_clicked(self) -> None:
        try:
            self.save_current_config()
        except ValueError:
            return

    def apply_form_to_config(self) -> None:
        self.config.ui_language = self.language_code_from_label(self.language_var.get())
        self.config.input_backend = self.input_backend_var.get()
        self.config.auto_action_enabled = self.auto_enabled_var.get()
        self.config.auto_action_key = self.clean_key(self.auto_key_var.get(), "f")
        self.config.auto_action_interval_sec = self.parse_float(self.auto_interval_var.get(), self.text("interval_sec"), 0.1)
        self.config.auto_action_hold_sec = self.parse_float(self.auto_hold_var.get(), self.text("hold_sec"), 0.01)
        self.config.auto_action_idle_grace_sec = self.parse_float(self.auto_idle_var.get(), self.text("idle_grace"), 0.0)
        self.config.prompt_detection_enabled = self.prompt_enabled_var.get()
        self.config.prompt_cooldown_sec = self.parse_float(self.prompt_cooldown_var.get(), self.text("prompt_cooldown"), 0.1)
        self.config.auto_click_enabled = self.auto_click_enabled_var.get()
        self.config.auto_click_interval_sec = self.parse_float(self.auto_click_interval_var.get(), self.text("click_interval"), 0.1)
        self.config.recovery_escape_enabled = self.recovery_escape_var.get()
        self.config.recovery_no_line_timeout_sec = self.parse_float(self.recovery_timeout_var.get(), self.text("recovery_timeout"), 0.5)
        self.config.use_template_matching = self.template_enabled_var.get()
        self.config.template_match_threshold = self.parse_float(self.template_threshold_var.get(), self.text("template_threshold"), 0.1)
        self.config.template_match_threshold = min(0.99, self.config.template_match_threshold)
        self.config.hold_control_enabled = self.hold_control_var.get()
        self.config.gui_start_delay_sec = self.parse_float(self.start_delay_var.get(), self.text("start_delay"), 0.0)
        self.config.left_key = self.clean_key(self.left_key_var.get(), "a")
        self.config.right_key = self.clean_key(self.right_key_var.get(), "d")
        self.config.dead_zone_px = self.parse_int(self.dead_zone_var.get(), self.text("dead_zone"), 0)
        self.config.target_fps = self.parse_int(self.target_fps_var.get(), "FPS", 1)
        self.config.dry_run_default = self.dry_run_var.get()

    def start_bot(self) -> None:
        if self.worker is not None and self.worker.is_alive():
            self.append_log(self.text("bot_already_running"))
            return
        try:
            config = copy.deepcopy(self.save_current_config())
        except ValueError:
            return

        self.stop_event = threading.Event()
        self.worker = threading.Thread(target=self.run_worker, args=(config, self.stop_event), daemon=True)
        self.worker.start()
        self.status_var.set(self.text("started_status"))
        self.append_log(self.text("started_log"))

    def test_action_key(self) -> None:
        try:
            self.apply_form_to_config()
        except ValueError as exc:
            messagebox.showerror(self.text("settings_error"), str(exc))
            return

        key = self.config.auto_action_key
        hold = self.config.auto_action_hold_sec
        backend = self.config.input_backend
        self.append_log(self.text("test_key_log").format(key=key.upper()))
        threading.Thread(target=self.test_action_key_worker, args=(key, hold, backend), daemon=True).start()

    def test_action_key_worker(self, key: str, hold: float, backend: str) -> None:
        for remaining in (3, 2, 1):
            self.log_queue.put(("status", self.text("test_key_status").format(key=key.upper(), remaining=remaining)))
            time.sleep(1.0)
        try:
            tap(key, hold, backend)
            self.log_queue.put(("log", self.text("test_key_success").format(key=key.upper(), backend=backend)))
        except Exception as exc:
            self.log_queue.put(("error", self.text("test_key_error").format(key=key.upper(), error=exc)))

    def run_worker(self, config: Config, stop_event: threading.Event) -> None:
        last_emit = 0.0

        def on_status(line: str) -> None:
            nonlocal last_emit
            now = time.perf_counter()
            if now - last_emit >= 0.25:
                self.log_queue.put(("status", line))
                last_emit = now

        try:
            delay = max(0.0, config.gui_start_delay_sec)
            while delay > 0:
                if stop_event.is_set():
                    return
                self.log_queue.put(("status", self.text("start_countdown").format(delay=delay)))
                sleep_for = min(0.5, delay)
                time.sleep(sleep_for)
                delay -= sleep_for

            run_bot(
                config,
                self.config_path,
                start_running=True,
                stop_event=stop_event,
                status_callback=on_status,
                allow_hotkeys=True,
            )
        except Exception as exc:
            self.log_queue.put(("error", str(exc)))
        finally:
            self.log_queue.put(("stopped", self.text("stopped")))

    def stop_bot(self) -> None:
        if self.stop_event is not None:
            self.stop_event.set()
            self.status_var.set(self.text("stopping"))
            self.append_log(self.text("stop_requested"))

    def choose_region(self) -> None:
        if self.worker is not None and self.worker.is_alive():
            messagebox.showinfo(self.text("bot_running_title"), self.text("choose_region_running"))
            return
        try:
            with mss.MSS() as sct:
                region = select_capture_region(sct, self.config.capture_region)
        except Exception as exc:
            messagebox.showerror(self.text("capture_region"), str(exc))
            return
        if region is None:
            return
        self.config.capture_region = region
        self.region_var.set(self.format_region(region))
        save_config(self.config_path, self.config)
        self.append_log(self.text("region_updated"))

    def choose_strip(self) -> None:
        if self.worker is not None and self.worker.is_alive():
            messagebox.showinfo(self.text("bot_running_title"), self.text("choose_region_running"))
            return
        try:
            with mss.MSS() as sct:
                region = select_capture_strip(sct, self.config.capture_region)
        except Exception as exc:
            messagebox.showerror(self.text("capture_region"), str(exc))
            return
        if region is None:
            return
        self.config.capture_region = region
        self.region_var.set(self.format_region(region))
        save_config(self.config_path, self.config)
        self.append_log(self.text("strip_region_updated"))

    def open_calibration_window(self) -> None:
        if self.worker is not None and self.worker.is_alive():
            messagebox.showinfo(self.text("bot_running_title"), self.text("choose_region_running"))
            return
        if self.calibration_window is not None and self.calibration_window.winfo_exists():
            self.calibration_window.lift()
            return

        sct = mss.MSS()
        monitor = sct.monitors[1]
        mon_left = int(monitor["left"])
        mon_top = int(monitor["top"])
        mon_right = mon_left + int(monitor["width"])
        mon_bottom = mon_top + int(monitor["height"])
        region = self.clamp_region(self.config.capture_region, monitor)

        window = tk.Toplevel(self)
        self.calibration_window = window
        window.title(self.text("calibration_title"))
        window.geometry("980x660")
        window.minsize(820, 560)
        window.transient(self)
        window.attributes("-topmost", True)

        frame = ttk.Frame(window, padding=12)
        frame.pack(fill=tk.BOTH, expand=True)
        ttk.Label(frame, text=self.text("calibration_hint"), wraplength=690).pack(fill=tk.X)

        vars_by_key = {
            "left": tk.IntVar(value=region["left"]),
            "top": tk.IntVar(value=region["top"]),
            "width": tk.IntVar(value=region["width"]),
            "height": tk.IntVar(value=region["height"]),
        }
        limits = {
            "left": (mon_left, mon_right - 2),
            "top": (mon_top, mon_bottom - 2),
            "width": (4, int(monitor["width"])),
            "height": (4, min(int(monitor["height"]), 420)),
        }
        labels = {
            "left": self.text("region_left_label"),
            "top": self.text("region_top_label"),
            "width": self.text("region_width_label"),
            "height": self.text("region_height_label"),
        }

        sliders = ttk.LabelFrame(frame, text=self.text("capture_region"), padding=8)
        sliders.pack(fill=tk.X, pady=(10, 0))
        for row, key in enumerate(("left", "top", "width", "height")):
            ttk.Label(sliders, text=labels[key], width=8).grid(row=row, column=0, sticky="w", pady=2)
            scale = tk.Scale(
                sliders,
                from_=limits[key][0],
                to=limits[key][1],
                orient=tk.HORIZONTAL,
                showvalue=False,
                variable=vars_by_key[key],
                resolution=1,
            )
            scale.grid(row=row, column=1, sticky="ew", padx=(6, 8), pady=2)
            tk.Spinbox(
                sliders,
                from_=limits[key][0],
                to=limits[key][1],
                textvariable=vars_by_key[key],
                width=8,
            ).grid(row=row, column=2, sticky="e", pady=2)
        sliders.columnconfigure(1, weight=1)

        body = ttk.Frame(frame)
        body.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        body.columnconfigure(0, weight=1)
        body.rowconfigure(0, weight=1)

        preview_area = ttk.Frame(body)
        preview_area.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        preview_area.rowconfigure(0, weight=1)
        preview_area.columnconfigure(0, weight=1)
        preview_label = ttk.Label(preview_area, text=self.text("preview_loading"), anchor="center")
        preview_label.grid(row=0, column=0, sticky="nsew")
        detection_var = tk.StringVar(value=self.text("preview_detection").format(fish="-", line="-"))
        ttk.Label(preview_area, textvariable=detection_var).grid(row=1, column=0, sticky="ew", pady=(6, 0))
        preview_state = {
            "canvas_rgb": None,
            "strip_rgb": None,
            "strip_bgr": None,
            "strip_hsv": None,
            "strip_y1": 0,
            "strip_y2": 0,
            "source_w": 1,
            "source_h": 1,
            "photo_w": 1,
            "photo_h": 1,
            "line_median": None,
            "line_rgb": None,
            "fish_median": None,
            "fish_rgb": None,
        }

        picker = ttk.LabelFrame(body, text=self.text("calibration_picker"), padding=8)
        picker.grid(row=0, column=1, sticky="ns")
        ttk.Label(picker, text=self.text("calibration_pick_hint"), wraplength=260).grid(
            row=0, column=0, columnspan=3, sticky="w"
        )
        active_pick_var = tk.StringVar(value="line")
        line_h_span = (int(self.config.line_hsv_high[0]) - int(self.config.line_hsv_low[0])) // 2
        fish_h_span = (int(self.config.fish_hsv_high[0]) - int(self.config.fish_hsv_low[0])) // 2
        yellow_tol_var = tk.IntVar(value=max(4, min(50, line_h_span or 18)))
        green_tol_var = tk.IntVar(value=max(4, min(60, fish_h_span or 29)))
        capture_info_var = tk.StringVar(value="")
        yellow_info_var = tk.StringVar(value=self.text("sample_waiting"))
        green_info_var = tk.StringVar(value=self.text("sample_waiting"))

        ttk.Button(picker, text=self.text("recapture"), command=lambda: capture_snapshot(log=True)).grid(
            row=1, column=2, sticky="e", pady=(8, 8)
        )
        ttk.Label(picker, textvariable=capture_info_var).grid(row=1, column=0, columnspan=2, sticky="w", pady=(8, 8))

        yellow_chip = tk.Label(picker, width=3, height=1, background="#f2d65b")
        yellow_chip.grid(row=2, column=0, sticky="w", pady=(8, 0))
        ttk.Radiobutton(
            picker,
            text=self.text("yellow"),
            variable=active_pick_var,
            value="line",
            command=lambda: render_snapshot(),
        ).grid(row=2, column=1, columnspan=2, sticky="w", pady=(8, 0))
        ttk.Label(picker, textvariable=yellow_info_var).grid(row=3, column=0, columnspan=3, sticky="w", pady=(2, 0))
        ttk.Label(picker, text=self.text("yellow_tolerance")).grid(row=4, column=0, columnspan=3, sticky="w", pady=(6, 0))
        yellow_scale = tk.Scale(
            picker,
            from_=4,
            to=50,
            orient=tk.HORIZONTAL,
            showvalue=True,
            variable=yellow_tol_var,
            resolution=1,
        )
        yellow_scale.grid(row=5, column=0, columnspan=3, sticky="ew", pady=(0, 8))

        green_chip = tk.Label(picker, width=3, height=1, background="#36ddbd")
        green_chip.grid(row=6, column=0, sticky="w", pady=(8, 0))
        ttk.Radiobutton(
            picker,
            text=self.text("green"),
            variable=active_pick_var,
            value="fish",
            command=lambda: render_snapshot(),
        ).grid(row=6, column=1, columnspan=2, sticky="w", pady=(8, 0))
        ttk.Label(picker, textvariable=green_info_var).grid(row=7, column=0, columnspan=3, sticky="w", pady=(2, 0))
        ttk.Label(picker, text=self.text("green_tolerance")).grid(row=8, column=0, columnspan=3, sticky="w", pady=(6, 0))
        green_scale = tk.Scale(
            picker,
            from_=4,
            to=100,
            orient=tk.HORIZONTAL,
            showvalue=True,
            variable=green_tol_var,
            resolution=1,
        )
        green_scale.grid(row=9, column=0, columnspan=3, sticky="ew", pady=(0, 8))
        ttk.Button(picker, text=self.text("test_match"), command=lambda: render_snapshot()).grid(
            row=10, column=0, columnspan=3, sticky="ew", pady=(8, 0)
        )
        picker.columnconfigure(1, weight=1)
        picker.columnconfigure(2, weight=1)

        buttons = ttk.Frame(frame)
        buttons.pack(fill=tk.X, pady=(10, 0))

        def current_region() -> dict:
            raw_region = {
                "left": int(vars_by_key["left"].get()),
                "top": int(vars_by_key["top"].get()),
                "width": int(vars_by_key["width"].get()),
                "height": int(vars_by_key["height"].get()),
            }
            return self.clamp_region(raw_region, monitor)

        def apply_region(log: bool = True) -> dict:
            selected = current_region()
            for key, value in selected.items():
                vars_by_key[key].set(value)
            self.config.capture_region = selected
            self.region_var.set(self.format_region(selected))
            save_config(self.config_path, self.config)
            if log:
                self.append_log(self.text("calibration_saved").format(region=self.format_region(selected)))
            return selected

        def close_window() -> None:
            try:
                sct.close()
            except Exception:
                pass
            self.calibration_window = None
            window.destroy()

        def current_range(target: str) -> tuple:
            if target == "line":
                return self.config.line_hsv_low, self.config.line_hsv_high
            return self.config.fish_hsv_low, self.config.fish_hsv_high

        def set_target_range(target: str, low: tuple, high: tuple) -> None:
            if target == "line":
                self.config.line_hsv_low = low
                self.config.line_hsv_high = high
            else:
                self.config.fish_hsv_low = low
                self.config.fish_hsv_high = high
                self.config.use_template_matching = False
                self.template_enabled_var.set(False)

        def mask_center_x(mask: np.ndarray) -> Optional[int]:
            ys, xs = np.where(mask > 0)
            if xs.size == 0:
                return None
            return int(round(float(xs.mean())))

        def rgb_hex(rgb: tuple) -> str:
            return "#{:02x}{:02x}{:02x}".format(*(max(0, min(255, int(value))) for value in rgb))

        def update_sample_labels() -> None:
            for target, info_var, chip in (
                ("line", yellow_info_var, yellow_chip),
                ("fish", green_info_var, green_chip),
            ):
                low, high = current_range(target)
                rgb = preview_state.get(f"{target}_rgb")
                median = preview_state.get(f"{target}_median")
                if rgb is not None and median is not None:
                    info_var.set(self.text("sample_info").format(rgb=rgb, hsv=median))
                    chip.configure(background=rgb_hex(rgb))
                else:
                    info_var.set(self.text("range_info").format(low=low, high=high))

        def update_range_from_tolerance(target: str, save: bool = True) -> None:
            median = preview_state.get(f"{target}_median")
            if median is None:
                return
            tolerance = yellow_tol_var.get() if target == "line" else green_tol_var.get()
            if target == "line":
                low, high = self.hsv_yellow_range_from_median(median, tolerance)
            else:
                low, high = self.hsv_range_from_median(median, tolerance)
            set_target_range(target, low, high)
            if save:
                save_config(self.config_path, self.config)
            self.fish_hsv_var.set(self.format_fish_hsv())
            update_sample_labels()

        def render_snapshot() -> None:
            canvas = preview_state.get("canvas_rgb")
            strip_bgr = preview_state.get("strip_bgr")
            strip_hsv = preview_state.get("strip_hsv")
            if canvas is None or strip_bgr is None or strip_hsv is None:
                preview_label.configure(image="", text=self.text("preview_loading"))
                detection_var.set(self.text("preview_detection").format(fish="-", line="-"))
                return

            display = canvas.copy()
            y1 = int(preview_state["strip_y1"])
            y2 = int(preview_state["strip_y2"])
            active = active_pick_var.get()
            preferred_line_x = preview_state.get("line_click_x")
            line_edge_margin = max(8, strip_hsv.shape[0] // 2)
            if active == "line":
                low, high = current_range(active)
                raw_mask = cv2.inRange(strip_hsv, np.array(low, dtype=np.uint8), np.array(high, dtype=np.uint8))
                raw_mask = cv2.morphologyEx(raw_mask, cv2.MORPH_CLOSE, np.ones((2, 2), np.uint8))
                mask = vertical_line_component_mask(
                    raw_mask,
                    min_area=self.config.min_blob_area,
                    bgr=strip_bgr,
                    preferred_x=preferred_line_x,
                    edge_margin=line_edge_margin,
                )
            else:
                low, high = current_range(active)
                mask = cv2.inRange(strip_hsv, np.array(low, dtype=np.uint8), np.array(high, dtype=np.uint8))
            pixels = int(np.count_nonzero(mask))
            center = mask_center_x(mask)
            if pixels:
                strip_view = display[y1:y2, :, :]
                overlay_pixels = mask > 0
                red = np.array((255, 0, 0), dtype=np.float32)
                strip_view[overlay_pixels] = (
                    strip_view[overlay_pixels].astype(np.float32) * 0.28 + red * 0.72
                ).astype(np.uint8)
                display[y1:y2, :, :] = strip_view

            fish_mask = cv2.inRange(
                strip_hsv,
                np.array(self.config.fish_hsv_low, dtype=np.uint8),
                np.array(self.config.fish_hsv_high, dtype=np.uint8),
            )
            line_mask = cv2.inRange(
                strip_hsv,
                np.array(self.config.line_hsv_low, dtype=np.uint8),
                np.array(self.config.line_hsv_high, dtype=np.uint8),
            )
            line_mask = cv2.morphologyEx(line_mask, cv2.MORPH_CLOSE, np.ones((2, 2), np.uint8))
            line_mask = vertical_line_component_mask(
                line_mask,
                min_area=self.config.min_blob_area,
                bgr=strip_bgr,
                preferred_x=preferred_line_x,
                edge_margin=line_edge_margin,
            )
            line_x = vertical_line_center_x_from_mask(
                line_mask,
                self.config.min_blob_area,
                bgr=strip_bgr,
                preferred_x=preferred_line_x,
                edge_margin=line_edge_margin,
            )
            fish_x = mask_center_x(fish_mask)
            cv2.rectangle(display, (0, y1), (display.shape[1] - 1, y2 - 1), (110, 110, 110), 1)

            self.calibration_preview_image = self.rgb_to_photo(display, max_width=680, max_height=320)
            preview_state["source_w"] = display.shape[1]
            preview_state["source_h"] = display.shape[0]
            preview_state["photo_w"] = self.calibration_preview_image.width()
            preview_state["photo_h"] = self.calibration_preview_image.height()
            preview_label.configure(image=self.calibration_preview_image, text="")
            detection_var.set(
                self.text("preview_detection").format(
                    fish="-" if fish_x is None else int(fish_x),
                    line="-" if line_x is None else int(line_x),
                )
                + " | "
                + self.text("mask_info").format(
                    target=self.text("yellow") if active == "line" else self.text("green"),
                    pixels=pixels,
                    center="-" if center is None else int(center),
                )
            )

        def capture_snapshot(log: bool = False) -> None:
            try:
                selected = apply_region(log=False)
                shot = np.array(sct.grab(selected))
                strip_rgb = cv2.cvtColor(shot, cv2.COLOR_BGRA2RGB)
                strip_bgr = cv2.cvtColor(strip_rgb, cv2.COLOR_RGB2BGR)
                strip_hsv = cv2.cvtColor(strip_bgr, cv2.COLOR_BGR2HSV)
                strip_hsv = enhance_hsv(strip_hsv, self.config.enable_clahe)
                strip_h, strip_w = strip_rgb.shape[:2]
                canvas_h = max(180, min(360, strip_h + 140))
                canvas = np.zeros((canvas_h, strip_w, 3), dtype=np.uint8)
                y1 = max(0, (canvas_h - strip_h) // 2)
                y2 = y1 + strip_h
                canvas[y1:y2, :, :] = strip_rgb
                preview_state["canvas_rgb"] = canvas
                preview_state["strip_rgb"] = strip_rgb
                preview_state["strip_bgr"] = strip_bgr
                preview_state["strip_hsv"] = strip_hsv
                preview_state["strip_y1"] = y1
                preview_state["strip_y2"] = y2
                preview_state.pop("line_click_x", None)
                capture_info_var.set(f"{selected['left']},{selected['top']}  {selected['width']}x{selected['height']}")
                update_sample_labels()
                render_snapshot()
                if log:
                    self.append_log(self.text("snapshot_saved").format(region=self.format_region(selected)))
            except Exception:
                preview_label.configure(image="", text=self.text("preview_invalid"))
                detection_var.set(self.text("preview_detection").format(fish="-", line="-"))

        def on_tolerance_changed(target: str) -> None:
            update_range_from_tolerance(target)
            render_snapshot()

        ttk.Button(buttons, text=self.text("apply_region"), command=apply_region).pack(side=tk.RIGHT, padx=(0, 8))
        ttk.Button(buttons, text=self.text("recapture"), command=lambda: capture_snapshot(log=True)).pack(
            side=tk.RIGHT, padx=(0, 8)
        )
        ttk.Button(buttons, text=self.text("close"), command=close_window).pack(side=tk.RIGHT, padx=(0, 8))

        def pick_color_from_preview(event: tk.Event) -> None:
            strip_hsv = preview_state.get("strip_hsv")
            strip_rgb = preview_state.get("strip_rgb")
            if strip_hsv is None or strip_rgb is None:
                return
            photo_w = max(1, int(preview_state["photo_w"]))
            photo_h = max(1, int(preview_state["photo_h"]))
            label_w = max(photo_w, preview_label.winfo_width())
            label_h = max(photo_h, preview_label.winfo_height())
            offset_x = max(0, (label_w - photo_w) // 2)
            offset_y = max(0, (label_h - photo_h) // 2)
            px = event.x - offset_x
            py = event.y - offset_y
            if px < 0 or py < 0 or px >= photo_w or py >= photo_h:
                return
            source_x = int(round(px * int(preview_state["source_w"]) / photo_w))
            source_y = int(round(py * int(preview_state["source_h"]) / photo_h))
            source_x = max(0, min(strip_hsv.shape[1] - 1, source_x))
            strip_y = source_y - int(preview_state["strip_y1"])
            if strip_y < 0 or strip_y >= strip_hsv.shape[0]:
                return
            strip_y = max(0, min(strip_hsv.shape[0] - 1, strip_y))

            is_line = active_pick_var.get() == "line"
            target_key = "line" if is_line else "fish"
            tolerance = yellow_tol_var.get() if is_line else green_tol_var.get()
            if is_line:
                sample = self.hsv_range_from_yellow_line_point(strip_hsv, source_x, strip_y, tolerance=tolerance)
            else:
                sample = self.hsv_range_from_point(strip_hsv, source_x, strip_y, radius=4, tolerance=tolerance)
            if sample is None:
                return
            low, high, median = sample
            rgb = tuple(int(value) for value in strip_rgb[strip_y, source_x])
            preview_state[f"{target_key}_median"] = median
            preview_state[f"{target_key}_rgb"] = rgb
            if is_line:
                preview_state["line_click_x"] = source_x
                low, high = self.hsv_yellow_range_from_median(median, tolerance)
            set_target_range(target_key, low, high)
            target = self.text("yellow") if is_line else self.text("green")
            save_config(self.config_path, self.config)
            self.fish_hsv_var.set(self.format_fish_hsv())
            update_sample_labels()
            self.append_log(self.text("color_pick_saved").format(target=target, median=median, low=low, high=high))
            render_snapshot()

        preview_label.bind("<Button-1>", pick_color_from_preview)
        yellow_scale.configure(command=lambda _value: on_tolerance_changed("line"))
        green_scale.configure(command=lambda _value: on_tolerance_changed("fish"))

        window.protocol("WM_DELETE_WINDOW", close_window)
        capture_snapshot(log=False)

    def choose_click_position(self) -> None:
        if self.worker is not None and self.worker.is_alive():
            messagebox.showinfo(self.text("bot_running_title"), self.text("choose_click_running"))
            return
        try:
            point = select_click_point()
        except Exception as exc:
            messagebox.showerror(self.text("click_position"), str(exc))
            return
        if point is None:
            return
        self.config.auto_click_position = point
        self.click_position_var.set(self.format_click_position(point))
        save_config(self.config_path, self.config)
        self.append_log(self.text("click_updated"))

    def reset_click_position(self) -> None:
        self.config.auto_click_position = None
        self.click_position_var.set(self.format_click_position(None))
        save_config(self.config_path, self.config)
        self.append_log(self.text("click_reset"))

    def view_fish_reference(self) -> None:
        path = resolve_asset_path(self.config_path, self.config.fish_template_path)
        if not path.exists():
            messagebox.showinfo(self.text("reference"), self.text("file_missing").format(path=path))
            return
        image = cv2.imread(str(path), cv2.IMREAD_COLOR)
        if image is None:
            messagebox.showerror(self.text("reference"), self.text("open_failed").format(path=path))
            return
        cv2.imshow("fish_reference.png", image)
        cv2.waitKey(1)
        self.append_log(self.text("ref_opened").format(name=path.name))

    def pick_fish_color(self) -> None:
        if self.worker is not None and self.worker.is_alive():
            messagebox.showinfo(self.text("bot_running_title"), self.text("pipette_running"))
            return
        try:
            sample = select_hsv_color_sample()
        except Exception as exc:
            messagebox.showerror(self.text("pipette_title"), str(exc))
            return
        if sample is None:
            return

        low, high, median = sample
        self.apply_fish_color_sample(low, high, median, self.text("pipette_source"))

    def pick_fish_color_from_reference(self) -> None:
        path = resolve_asset_path(self.config_path, self.config.fish_template_path)
        if not path.exists():
            messagebox.showinfo(self.text("reference"), self.text("file_missing").format(path=path))
            return
        image = cv2.imread(str(path), cv2.IMREAD_COLOR)
        if image is None:
            messagebox.showerror(self.text("reference"), self.text("open_failed").format(path=path))
            return
        h, w = image.shape[:2]
        sample = hsv_range_from_patch(image, w // 2, h // 2, radius=max(2, min(w, h) // 8))
        low, high, median = sample
        self.apply_fish_color_sample(low, high, median, self.text("reference_source"))

    def apply_fish_color_sample(self, low: tuple, high: tuple, median: tuple, source: str) -> None:
        self.config.fish_hsv_low = low
        self.config.fish_hsv_high = high
        self.config.use_template_matching = False
        self.template_enabled_var.set(False)
        self.fish_hsv_var.set(self.format_fish_hsv())
        save_config(self.config_path, self.config)
        self.append_log(self.text("color_applied").format(source=source, median=median, low=low, high=high))

    def disable_template_matching(self) -> None:
        self.config.use_template_matching = False
        self.template_enabled_var.set(False)
        save_config(self.config_path, self.config)
        self.append_log(self.text("ref_disabled"))

    def refresh_template_status(self) -> None:
        self.template_status_var.set(self.format_template_status())
        self.fish_hsv_var.set(self.format_fish_hsv())
        self.append_log(self.text("templates_refreshed"))

    def test_click_position(self) -> None:
        try:
            self.apply_form_to_config()
        except ValueError as exc:
            messagebox.showerror(self.text("settings_error"), str(exc))
            return

        point = self.resolve_preview_click_point()
        self.append_log(self.text("test_click_log").format(x=point["x"], y=point["y"]))
        threading.Thread(target=self.test_click_worker, args=(point,), daemon=True).start()

    def test_click_worker(self, point: dict) -> None:
        for remaining in (3, 2, 1):
            self.log_queue.put(("status", self.text("test_click_status").format(remaining=remaining)))
            time.sleep(1.0)
        try:
            click_at(point["x"], point["y"])
            self.log_queue.put(("log", self.text("test_click_success").format(x=point["x"], y=point["y"])))
        except Exception as exc:
            self.log_queue.put(("error", self.text("test_click_error").format(error=exc)))

    def resolve_preview_click_point(self) -> dict:
        if self.config.auto_click_position is not None:
            return self.config.auto_click_position
        if self.config.prompt_region is not None:
            return {
                "x": int(self.config.prompt_region["left"] + self.config.prompt_region["width"] / 2),
                "y": int(self.config.prompt_region["top"] + self.config.prompt_region["height"] / 2),
            }
        with mss.MSS() as sct:
            x, y = default_action_click_point(sct.monitors[1])
        return {"x": x, "y": y}

    def poll_log_queue(self) -> None:
        try:
            while True:
                kind, message = self.log_queue.get_nowait()
                if kind == "status":
                    self.status_var.set(message)
                elif kind == "log":
                    self.append_log(message)
                elif kind == "error":
                    self.status_var.set(self.text("error_status"))
                    self.append_log(self.text("error_prefix").format(message=message))
                elif kind == "stopped":
                    self.status_var.set(message)
                    self.append_log(message)
        except queue.Empty:
            pass
        self.after(100, self.poll_log_queue)

    def append_log(self, message: str) -> None:
        self.log_text.configure(state="normal")
        self.log_text.insert(tk.END, f"{time.strftime('%H:%M:%S')}  {message}\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state="disabled")

    def on_close(self) -> None:
        if self.stop_event is not None:
            self.stop_event.set()
        self.after(150, self.destroy)

    @staticmethod
    def clean_key(value: str, default: str) -> str:
        value = value.strip().lower()
        return value or default

    def parse_float(self, value: str, label: str, minimum: float) -> float:
        try:
            parsed = float(value.replace(",", "."))
        except ValueError as exc:
            raise ValueError(f"{label}: {self.text('need_number')}") from exc
        if parsed < minimum:
            raise ValueError(f"{label}: {self.text('minimum').format(minimum=minimum)}")
        return parsed

    def parse_int(self, value: str, label: str, minimum: int) -> int:
        try:
            parsed = int(value)
        except ValueError as exc:
            raise ValueError(f"{label}: {self.text('need_integer')}") from exc
        if parsed < minimum:
            raise ValueError(f"{label}: {self.text('minimum').format(minimum=minimum)}")
        return parsed

    @staticmethod
    def clamp_region(region: dict, monitor: dict) -> dict:
        mon_left = int(monitor["left"])
        mon_top = int(monitor["top"])
        mon_width = int(monitor["width"])
        mon_height = int(monitor["height"])
        mon_right = mon_left + mon_width
        mon_bottom = mon_top + mon_height

        left = max(mon_left, min(int(region["left"]), mon_right - 2))
        top = max(mon_top, min(int(region["top"]), mon_bottom - 2))
        width = max(4, min(int(region["width"]), mon_right - left))
        height = max(4, min(int(region["height"]), mon_bottom - top))
        return {"left": left, "top": top, "width": width, "height": height}

    @staticmethod
    def hsv_range_from_median(median: tuple, tolerance: int) -> tuple:
        h_med, s_med, v_med = [int(round(value)) for value in median]
        tolerance = max(1, int(tolerance))
        h_pad = max(4, min(35, tolerance))
        s_pad = max(25, min(170, tolerance * 4))
        v_pad = max(25, min(180, tolerance * 4))
        low = (
            max(0, h_med - h_pad),
            max(0, s_med - s_pad),
            max(0, v_med - v_pad),
        )
        high = (
            min(179, h_med + h_pad),
            min(255, s_med + s_pad),
            min(255, v_med + v_pad),
        )
        return low, high

    @staticmethod
    def hsv_yellow_range_from_median(median: tuple, tolerance: int) -> tuple:
        h_med, s_med, v_med = [int(round(value)) for value in median]
        tolerance = max(1, int(tolerance))
        h_pad = max(10, min(40, tolerance * 2 + 6))
        s_low_pad = max(55, min(180, tolerance * 7 + 45))
        s_high_pad = max(90, min(210, tolerance * 8 + 70))
        v_low_pad = max(70, min(190, tolerance * 8 + 55))
        low = (
            max(0, h_med - h_pad),
            max(0, s_med - s_low_pad),
            max(0, v_med - v_low_pad),
        )
        high = (
            min(179, h_med + h_pad),
            min(255, s_med + s_high_pad),
            255,
        )
        return low, high

    @staticmethod
    def hsv_range_from_point(
        hsv: np.ndarray,
        x: int,
        y: int,
        radius: int,
        tolerance: int,
    ) -> Optional[tuple]:
        h, w = hsv.shape[:2]
        x1 = max(0, x - radius)
        x2 = min(w, x + radius + 1)
        y1 = max(0, y - radius)
        y2 = min(h, y + radius + 1)
        patch = hsv[y1:y2, x1:x2].reshape(-1, 3)
        if patch.size == 0:
            return None

        vivid = patch[(patch[:, 1] >= 35) & (patch[:, 2] >= 35)]
        if vivid.size >= 9:
            patch = vivid

        median = np.median(patch, axis=0)
        spread = np.std(patch, axis=0)
        h_med, s_med, v_med = [int(round(value)) for value in median]
        h_pad = max(4, min(35, int(tolerance)))
        s_pad = max(25, min(170, int(tolerance) * 4 + int(round(spread[1]))))
        v_pad = max(25, min(180, int(tolerance) * 4 + int(round(spread[2]))))
        low = (
            max(0, h_med - h_pad),
            max(0, s_med - s_pad),
            max(0, v_med - v_pad),
        )
        high = (
            min(179, h_med + h_pad),
            min(255, s_med + s_pad),
            min(255, v_med + v_pad),
        )
        return low, high, (h_med, s_med, v_med)

    @staticmethod
    def hsv_range_from_yellow_line_point(
        hsv: np.ndarray,
        x: int,
        y: int,
        tolerance: int,
    ) -> Optional[tuple]:
        h, w = hsv.shape[:2]
        x1 = max(0, x - 10)
        x2 = min(w, x + 11)
        y1 = max(0, y - 18)
        y2 = min(h, y + 19)
        patch = hsv[y1:y2, x1:x2].reshape(-1, 3)
        if patch.size == 0:
            return None

        yellow = patch[
            (patch[:, 0] >= 12)
            & (patch[:, 0] <= 50)
            & (patch[:, 1] >= 70)
            & (patch[:, 2] >= 105)
        ]
        if yellow.size < 9:
            yellow = patch[(patch[:, 1] >= 105) & (patch[:, 2] >= 130)]
        if yellow.size < 9:
            return FishingBotGUI.hsv_range_from_point(hsv, x, y, radius=6, tolerance=tolerance)

        median = np.median(yellow, axis=0)
        h_med, s_med, v_med = [int(round(value)) for value in median]
        tolerance = max(1, int(tolerance))
        low, high = FishingBotGUI.hsv_yellow_range_from_median((h_med, s_med, v_med), tolerance)
        return low, high, (h_med, s_med, v_med)

    @staticmethod
    def rgb_to_photo(rgb: np.ndarray, max_width: int, max_height: int) -> tk.PhotoImage:
        h, w = rgb.shape[:2]
        if h <= 0 or w <= 0:
            raise ValueError("empty image")
        scale = min(max_width / w, max_height / h)
        target_w = max(1, int(round(w * scale)))
        target_h = max(1, int(round(h * scale)))
        if target_w != w or target_h != h:
            interpolation = cv2.INTER_NEAREST if scale >= 1 else cv2.INTER_AREA
            rgb = cv2.resize(rgb, (target_w, target_h), interpolation=interpolation)
        rgb = np.ascontiguousarray(rgb)
        header = f"P6\n{target_w} {target_h}\n255\n".encode("ascii")
        return tk.PhotoImage(data=header + rgb.tobytes(), format="PPM")

    @staticmethod
    def format_region(region: dict) -> str:
        return (
            f"left={region['left']} top={region['top']} "
            f"width={region['width']} height={region['height']}"
        )

    def format_click_position(self, point: Optional[dict]) -> str:
        if point is None:
            return self.text("auto_click_auto")
        return f"x={point['x']} y={point['y']}"

    def format_template_status(self) -> str:
        fish_path = resolve_asset_path(self.config_path, self.config.fish_template_path)
        fish_status = self.text("template_exists") if fish_path.exists() else self.text("template_missing")
        return self.text("template_status").format(status=fish_status, path=self.config.fish_template_path)

    def format_fish_hsv(self) -> str:
        return self.text("fish_hsv_status").format(
            low=self.config.fish_hsv_low,
            high=self.config.fish_hsv_high,
        )


def launch_gui(config_path: Path) -> None:
    app = FishingBotGUI(config_path)
    app.mainloop()


def hsv_range_from_patch(bgr: np.ndarray, x: int, y: int, radius: int = 3) -> tuple:
    h, w = bgr.shape[:2]
    x1 = max(0, x - radius)
    x2 = min(w, x + radius + 1)
    y1 = max(0, y - radius)
    y2 = min(h, y + radius + 1)
    patch = bgr[y1:y2, x1:x2]
    hsv_patch = cv2.cvtColor(patch, cv2.COLOR_BGR2HSV).reshape(-1, 3)
    vivid = hsv_patch[(hsv_patch[:, 1] >= 45) & (hsv_patch[:, 2] >= 45)]
    if vivid.size >= 9:
        hsv_patch = vivid

    median = np.median(hsv_patch, axis=0)
    spread = np.std(hsv_patch, axis=0)
    h_med, s_med, v_med = [int(round(value)) for value in median]
    h_pad = min(18, max(8, int(round(spread[0] * 1.5)) + 5))
    s_low_pad = min(95, max(45, int(round(spread[1] * 1.5)) + 35))
    s_high_pad = min(85, max(35, int(round(spread[1] * 1.3)) + 30))
    v_low_pad = min(110, max(55, int(round(spread[2] * 1.5)) + 40))
    v_high_pad = min(95, max(45, int(round(spread[2] * 1.3)) + 35))

    low = (
        max(0, h_med - h_pad),
        max(0, s_med - s_low_pad),
        max(0, v_med - v_low_pad),
    )
    high = (
        min(179, h_med + h_pad),
        min(255, s_med + s_high_pad),
        min(255, v_med + v_high_pad),
    )
    return low, high, (h_med, s_med, v_med)


def select_hsv_color_sample() -> Optional[tuple]:
    with mss.MSS() as sct:
        monitor = sct.monitors[1]
        shot = sct.grab(monitor)
        frame = np.array(shot)
        bgr = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
        selected = {"point": None, "sample": None}
        window_name = "Pick Turquoise Color"

        def on_mouse(event: int, x: int, y: int, _flags: int, _param: object) -> None:
            if event == cv2.EVENT_LBUTTONDOWN:
                selected["point"] = (x, y)
                selected["sample"] = hsv_range_from_patch(bgr, x, y)

        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, min(int(monitor["width"]), 1280), min(int(monitor["height"]), 800))
        cv2.setMouseCallback(window_name, on_mouse)

        while True:
            view = bgr.copy()
            point = selected["point"]
            sample = selected["sample"]
            if point is not None:
                cv2.circle(view, point, 10, (0, 255, 255), 2)
                cv2.line(view, (point[0] - 16, point[1]), (point[0] + 16, point[1]), (0, 255, 255), 2)
                cv2.line(view, (point[0], point[1] - 16), (point[0], point[1] + 16), (0, 255, 255), 2)
            text = "Click turquoise target color | ENTER/SPACE confirm | C/ESC cancel"
            cv2.putText(view, text, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 255), 2)
            if sample is not None:
                low, high, median = sample
                cv2.putText(
                    view,
                    f"HSV={median} range={low}-{high}",
                    (20, 75),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.65,
                    (0, 255, 255),
                    2,
                )
            cv2.imshow(window_name, view)
            key = cv2.waitKey(20) & 0xFF
            if key in (13, 32) and sample is not None:
                cv2.destroyWindow(window_name)
                return sample
            if key in (27, ord("c")):
                cv2.destroyWindow(window_name)
                return None


def select_click_point() -> Optional[dict]:
    with mss.MSS() as sct:
        monitor = sct.monitors[1]
        shot = sct.grab(monitor)
        frame = np.array(shot)
        bgr = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
        selected = {"point": None}
        window_name = "Select Auto Click Point"

        def on_mouse(event: int, x: int, y: int, _flags: int, _param: object) -> None:
            if event == cv2.EVENT_LBUTTONDOWN:
                selected["point"] = (x, y)

        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, min(int(monitor["width"]), 1280), min(int(monitor["height"]), 800))
        cv2.setMouseCallback(window_name, on_mouse)

        while True:
            view = bgr.copy()
            point = selected["point"]
            if point is not None:
                cv2.circle(view, point, 12, (0, 255, 255), 2)
                cv2.line(view, (point[0] - 18, point[1]), (point[0] + 18, point[1]), (0, 255, 255), 2)
                cv2.line(view, (point[0], point[1] - 18), (point[0], point[1] + 18), (0, 255, 255), 2)

            cv2.putText(
                view,
                "Click target point | ENTER/SPACE confirm | C/ESC cancel",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 255),
                2,
            )
            cv2.imshow(window_name, view)
            key = cv2.waitKey(20) & 0xFF
            if key in (13, 32) and point is not None:
                cv2.destroyWindow(window_name)
                return {
                    "x": int(monitor["left"] + point[0]),
                    "y": int(monitor["top"] + point[1]),
                }
            if key in (27, ord("c")):
                cv2.destroyWindow(window_name)
                return None


if __name__ == "__main__":
    from fishing_bot import resolve_config_path

    launch_gui(resolve_config_path())
