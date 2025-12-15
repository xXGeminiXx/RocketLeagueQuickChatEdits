from __future__ import annotations

import argparse
import json
import os
import sys
import time
import unicodedata
from dataclasses import dataclass, field
from random import sample
from typing import Callable, Dict, List, Mapping, Optional, Sequence, Tuple

import pygame


def is_wsl() -> bool:
    try:
        return "microsoft" in os.uname().release.lower()
    except Exception:
        return False


# Create your own word variations and format them like this (see README for usage)
variations: Mapping[str, Sequence[str]] = {
    "Challenge": [
        "I dare you to score. Do it. I double-dog dare you.",
        "Try to beat that!",
        "Challenge accepted (I regret everything).",
        "Meet me in the midfield. We'll settle this with vibes.",
        "1v1 me behind the boost pad.",
        "Bold of you to challenge me while I'm holding drift.",
    ],
    "Confidence Boost": [
        "We are absolutely winning this (source: me).",
        "We're the main characters. The cutscene is loading.",
        "Trust the process (I have no idea what the process is).",
        "We're so back.",
        "If confidence was boost, we'd be supersonic.",
        "Calculated. (Not really.)",
        "We're about to peak. Probably. Maybe.",
        "Winners mentality: engaged. Mechanics: optional.",
        "I can feel the montage music starting.",
        "This lobby isn't ready for our nonsense.",
    ],
    "Encouraging Taunt": [
        "Is that all you've got? (I'm genuinely asking.)",
        "Nice try! That was almost a thing!",
        "You're getting warmer! Like, room temperature.",
        "Not bad! Now do it on purpose.",
        "You're almost there! (Where is 'there'? Nobody knows.)",
        "Getting better with every try. Statistically.",
        "You're on the right track; now let's find the ball.",
        "Impressive… but I'm still emotionally unprepared.",
        "Keep trying, you're almost unstoppable! Almost.",
        "You're a force to be reckoned with. In a different lobby.",
        "You can do better than that. I believe in future-you.",
        "That was a shot! Technically.",
    ],
    "Celebration": [
        "Great job, team! Nobody look at the replay.",
        "We're on fire! (Stop drop and rotate.)",
        "Calculated. (I own a calculator.)",
        "WINNING! (Narrator: he was not.)",
        "Peak Rocket League. Clip it. Send it to NASA.",
    ],
    "Apology": [
        "My bad, that was on me.",
        "Sorry about that. Brain buffering.",
        "Whoops. That was my controller. (It wasn't.)",
        "Apologies. I got jumpscared by the ball.",
        "Sorry! I saw a boost pad and blacked out.",
    ],
    "affirmation": [
        "...maybe",
        "...possibly",
        "...sometimes",
        "...probably",
        "...definitely",
        "...no doubt",
        "...on every alternate Tuesday.",
        "...unless it’s a full moon.",
        "...only if the WiFi signal is strong.",
        "...assuming I've had my coffee.",
        "...only in leap years.",
        "...give or take.",
        "...depending on the wind direction.",
        "...if planets align.",
        "...but don't quote me on that!",
        "...unless I forgot my socks",
        "...if it's not raining cats and dogs and whatnot.",
    ],
    "friend": [
        "ole Buddy.",
        "Pal.",
        "Mate.",
        "Champ.",
        "Comrade",
        "fellow gamer",
        "brother",
        "Bro!",
        "My Dude from another Latitude!",
        "My Partner in Digital-Crime!",
        "My Pixel Pal!",
        "home skillet",
        "Hey Chief!",
        "Mi Amigo!",
        "My Digital Sidekick!",
    ],
    "foe": [
        "Aggressive Rival.",
        "Mr. Challenger.",
        "Competitor.",
        "Primary Adversary.",
        "Nemesis.",
        "Antagonist.",
        "Digital Dance Partner.",
        "Keyboard Kombatant.",
        "Mysterious Stranger.",
        "Pixelated Enemy.",
        "you Digital Doppelganger.",
        "you Joystick Jouster.",
        "you Button Basher.",
        "Console Conqueror.",
    ],
    "compliment": [
        "Great!",
        "Awesome!",
        "Amazing!",
        "Fantastic!",
        "Impressive!",
        "Excellent!",
        "Outstanding!",
        "Stellar!",
        "Splendid!",
        "More legendary than a unicorn in a top hat!",
        "Cooler than a polar bear’s toenails!",
        "Shinier than a freshly waxed penguin!",
        "As epic as a double rainbow!",
        "Worthy of a mic drop!",
        "As dazzling as fireworks!",
        "As radiant as the morning sun!",
        "As electrifying as a thunderstorm!",
        "A true maestro!",
        "Nothing short of magic!",
        "That was illegal in at least 12 states.",
        "Your car has aura.",
    ],
    "cat fact": [
        "CAT FAX: Cats have 32 muscles in each ear. They still won't hear \"rotate.\"",
        "CAT FAX: A group of cats is a clowder. A group of teammates is a \"double commit.\"",
        "CAT FAX: Cats sleep 12–16 hours/day. Same as me after whiffing.",
        "CAT FAX: Cats purr at ~25 Hz. My car purrs at 0 boost.",
        "CAT FAX: Cats can’t taste sweetness. I can’t taste victory either (yet).",
        "CAT FAX: Cats have whiskers for spatial awareness. I have vibes.",
        "CAT FAX: The slow blink means trust. The fast flip means panic.",
        "CAT FAX: Cats always land on their feet. I land on the ceiling.",
        "CAT FAX: Cats knead to relax. I powerslide into the post to relax.",
        "CAT FAX: Cats can jump ~6x their height. I can jump 0x my rank.",
        "CAT FAX: A cat's nose print is unique. So is my ability to miss open nets.",
        "CAT FAX: Cats have retractable claws. I have retractable confidence.",
        "CAT FAX: Cats have a third eyelid. I have a third whiff.",
        "CAT FAX: Cats groom to remove scent. I demo to remove problems.",
        "CAT FAX: Cats are crepuscular (dawn/dusk). I'm carpuscular (all the time).",
        "CAT FAX: Cats can squeeze through tiny gaps. I can't squeeze through midfield.",
        "CAT FAX: Cats communicate with tails. I communicate with rapid backflips.",
        "CAT FAX: Cats dislike water. I dislike overtime.",
        "CAT FAX: Cats have great night vision. I still can't see the ball.",
        "CAT FAX: Cats have 18 toes. I have 0 mechanics.",
        "CAT FAX: Cats can rotate ears 180°. I can rotate my car 720° and still miss.",
        "CAT FAX: Cats were worshipped in ancient Egypt. I worship the small boost pad.",
        "CAT FAX: Cats have a collarbone that helps them fit places. I have a hitbox and regret.",
        "CAT FAX: Cats can run ~30 mph. I can drive 100 and still be late to the play.",
        "CAT FAX: Cats have an organ to \"taste\" smells. I have an organ to taste Ls.",
        "CAT FAX: Cats meow mostly at humans. I spam chat mostly at myself.",
        "CAT FAX: Cats make biscuits. I make own-goals.",
        "CAT FAX: Cats shed. I also shed rank points.",
        "CAT FAX: Cats love boxes. I love being boxed in the corner.",
        "CAT FAX: Cats chase lasers. I chase the ball like it's a laser pointer.",
        "CAT FAX: Cats have great balance. I have great excuses.",
        "CAT FAX: Cats nap to conserve energy. I conserve boost by never having any.",
        "CAT FAX: Cats can learn routines. I can learn kickoff. (Someday.)",
        "CAT FAX: Cats have excellent reflexes. I have excellent lag.",
        "CAT FAX: Cats knead with paws. I knead with D-pad inputs.",
    ],
}


# DualSense/DS4-ish controller button mappings for pygame.
# Note: D-pad may be exposed as buttons OR as "hat 0". We support both.
BUTTONS: Mapping[str, int] = {
    "cross": 0,
    "circle": 1,
    "square": 2,
    "triangle": 3,
    "share": 4,
    "ps": 5,
    "options": 6,
    "L1": 9,
    "R1": 10,
    "up": 11,
    "down": 12,
    "left": 13,
    "right": 14,
}


DEFAULT_CHAT_KEYS: Mapping[str, str] = {
    "lobby": "t",
    "team": "y",
    "party": "u",
}


@dataclass(frozen=True)
class ChatSettings:
    chat_mode: str = "lobby"
    chat_keys: Mapping[str, str] = field(default_factory=lambda: dict(DEFAULT_CHAT_KEYS))
    chat_spam_interval_s: float = 0.2
    typing_interval_s: float = 0.001
    dry_run: bool = False


@dataclass
class RecentMessageCache:
    cooldown_s: float = 600.0
    max_entries: int = 200
    _entries: List[Tuple[str, float]] = field(default_factory=list)

    def seen_recently(self, message: str, now: float) -> bool:
        cutoff = now - self.cooldown_s
        self._entries = [(m, t) for (m, t) in self._entries if t >= cutoff]
        return any(m == message for (m, _) in self._entries)

    def add(self, message: str, now: float) -> None:
        self._entries.append((message, now))
        if len(self._entries) > self.max_entries:
            self._entries = self._entries[-self.max_entries :]


class VariationPicker:
    def __init__(self, variations_map: Mapping[str, Sequence[str]]) -> None:
        self._variations = {k: list(v) for k, v in variations_map.items()}
        self._state: Dict[str, Dict[str, object]] = {}
        for key in self._variations:
            self._reshuffle(key, avoid_first=None)

    def _normalize_key(self, key: str) -> str:
        key = key.strip()
        if key in self._variations:
            return key

        alt = key.replace("_", " ")
        if alt in self._variations:
            return alt

        alt2 = key.replace(" ", "_")
        if alt2 in self._variations:
            return alt2

        key_lower = key.lower()
        alt_lower = alt.lower()
        alt2_lower = alt2.lower()
        for existing_key in self._variations.keys():
            existing_lower = existing_key.lower()
            if existing_lower in (key_lower, alt_lower, alt2_lower):
                return existing_key

        raise KeyError(f'Unknown variation key "{key}". Known keys: {sorted(self._variations)}')

    def _reshuffle(self, key: str, avoid_first: Optional[str]) -> None:
        words = self._variations[key]
        if not words:
            self._state[key] = {"randomized": [], "i": 0}
            return

        for _ in range(30):
            randomized = sample(words, len(words))
            if avoid_first is None or randomized[0] != avoid_first:
                self._state[key] = {"randomized": randomized, "i": 0}
                return

        self._state[key] = {"randomized": sample(words, len(words)), "i": 0}

    def pick(self, key: str) -> str:
        key = self._normalize_key(key)

        words = self._variations[key]
        if len(words) < 1:
            return ""
        if len(words) < 3:
            print(f'Warning: variation list "{key}" has <3 items; repeats are likely.')

        randomized = self._state[key]["randomized"]  # type: ignore[assignment]
        i = int(self._state[key]["i"])  # type: ignore[arg-type]
        if i >= len(randomized):
            avoid_first = randomized[-1] if randomized else None
            self._reshuffle(key, avoid_first=avoid_first)
            randomized = self._state[key]["randomized"]  # type: ignore[assignment]
            i = int(self._state[key]["i"])  # type: ignore[arg-type]

        self._state[key]["i"] = i + 1
        return str(randomized[i])


def apply_text_modifier(text: str, modifier: Optional[str]) -> str:
    if not modifier:
        return text
    modifier = modifier.strip().lower()
    if modifier == "lower":
        return text.lower()
    if modifier == "upper":
        return text.upper()
    if modifier == "capitalize":
        return text.capitalize()
    if modifier == "title":
        return text.title()
    raise ValueError(f"Unknown text modifier: {modifier}")


def render_template(template: str, pick_variation: Callable[[str], str]) -> str:
    # Minimal templating: "Hello {friend}" or "{compliment:lower}"
    out: List[str] = []
    i = 0
    while i < len(template):
        if template[i] != "{":
            out.append(template[i])
            i += 1
            continue

        end = template.find("}", i + 1)
        if end == -1:
            out.append(template[i:])
            break

        token = template[i + 1 : end].strip()
        if ":" in token:
            key, modifier = token.split(":", 1)
        else:
            key, modifier = token, None

        replacement = pick_variation(key.strip())
        out.append(apply_text_modifier(replacement, modifier))
        i = end + 1

    return "".join(out)


def normalize_ascii(text: str) -> str:
    table = str.maketrans(
        {
            "’": "'",
            "‘": "'",
            "“": '"',
            "”": '"',
            "–": "-",
            "—": "-",
            "…": "...",
            "\u00a0": " ",
        }
    )
    text = text.translate(table)
    text = unicodedata.normalize("NFKD", text)
    return text.encode("ascii", "ignore").decode("ascii")


def send_chat(message: str, settings: ChatSettings, spam_count: int = 1) -> None:
    if settings.chat_mode not in settings.chat_keys:
        raise KeyError(f'Unknown chat mode "{settings.chat_mode}". Known: {sorted(settings.chat_keys)}')

    for _ in range(spam_count):
        if settings.dry_run:
            print(f"[dry-run] {message}")
        else:
            import pyautogui

            pyautogui.press(settings.chat_keys[settings.chat_mode])
            pyautogui.write(message, interval=settings.typing_interval_s)
            pyautogui.press("enter")
        time.sleep(settings.chat_spam_interval_s)


def hat_to_dpad_action(value: Tuple[int, int]) -> Optional[str]:
    x, y = value
    if x == 0 and y == 0:
        return None
    if y == 1:
        return "up"
    if y == -1:
        return "down"
    if x == -1:
        return "left"
    if x == 1:
        return "right"
    return None


@dataclass(frozen=True)
class MacroSettings:
    macro_window_s: float = 1.1
    macro_min_gap_s: float = 0.05


class MacroEngine:
    def __init__(
        self,
        variation_picker: VariationPicker,
        chat_settings: ChatSettings,
        macro_settings: MacroSettings,
        message_cooldown_s: float,
        ascii_only: bool,
        persist_path: Optional[str],
    ) -> None:
        self._variation_picker = variation_picker
        self._chat_settings = chat_settings
        self._macro_settings = macro_settings
        self._recent = RecentMessageCache(cooldown_s=message_cooldown_s)
        self._ascii_only = ascii_only
        self._persist_path = persist_path
        self._macros_enabled = True

        self._last_action: Optional[str] = None
        self._last_action_time: float = 0.0
        self._last_sent_message: str = ""
        self._last_toggle_time: float = 0.0

        self._macros: Dict[Tuple[str, str], str] = {
            ("up", "up"): "I got it{affirmation}",
            ("up", "down"): "Defending... emotionally and physically{affirmation}",
            ("down", "up"): "OH SNAP! Hello, {friend}",
            ("left", "up"): "Nice one! Shot? Pass? Vibes? {compliment:lower}",
            ("right", "up"): "Centering! (Narrator: he was not.) {foe:lower}",
            ("left", "right"): "Thanks! Totally intentional. Definitely. My {friend}",
            ("left", "down"): "HA! {Celebration:lower}",
            ("left", "left"): "{compliment:capitalize}",
            ("up", "right"): "{Confidence Boost:capitalize}",
            ("up", "left"): "Need boost! I'm running on hopes and fumes, {friend}",
            ("down", "right"): "No problem. (It was absolutely your fault,) {foe:lower}",
            ("down", "left"): "{Apology:capitalize}",
            ("right", "left"): "{compliment:capitalize}",
            ("right", "right"): "{Encouraging Taunt:capitalize}",
            ("right", "down"): "{Challenge:lower}",
            ("down", "down"): "{cat fact:capitalize}",
        }

        self._load_persisted_state()

    def _load_persisted_state(self) -> None:
        if not self._persist_path:
            return
        try:
            with open(self._persist_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            last_sent = data.get("last_sent_message")
            if isinstance(last_sent, str):
                self._last_sent_message = last_sent
            entries = data.get("recent_messages")
            if isinstance(entries, list):
                parsed: List[Tuple[str, float]] = []
                for item in entries:
                    if (
                        isinstance(item, list)
                        and len(item) == 2
                        and isinstance(item[0], str)
                        and isinstance(item[1], (int, float))
                    ):
                        parsed.append((item[0], float(item[1])))
                self._recent._entries = parsed[-self._recent.max_entries :]
        except FileNotFoundError:
            return
        except Exception as e:
            print(f"Warning: failed to load persisted state from {self._persist_path!r}: {e}")

    def save_persisted_state(self) -> None:
        if not self._persist_path:
            return
        try:
            os.makedirs(os.path.dirname(self._persist_path) or ".", exist_ok=True)
            payload = {
                "last_sent_message": self._last_sent_message,
                "recent_messages": [[m, t] for (m, t) in self._recent._entries],
            }
            with open(self._persist_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: failed to save persisted state to {self._persist_path!r}: {e}")

    def toggle(self) -> None:
        now = time.time()
        if now - self._last_toggle_time < 0.25:
            return
        self._last_toggle_time = now
        self._macros_enabled = not self._macros_enabled
        state = "on" if self._macros_enabled else "off"
        print(f"----- quickchat macros toggled {state} -----")

    def handle_action(self, action: str) -> None:
        if action == "ps":
            self.toggle()
            return
        if not self._macros_enabled:
            return
        if action not in ("up", "down", "left", "right"):
            return

        now = time.time()
        if self._last_action is None:
            self._last_action = action
            self._last_action_time = now
            return

        elapsed = now - self._last_action_time
        if elapsed > self._macro_settings.macro_window_s:
            self._last_action = action
            self._last_action_time = now
            return
        if elapsed < self._macro_settings.macro_min_gap_s:
            return

        seq = (self._last_action, action)
        self._last_action = None
        self._last_action_time = 0.0

        template = self._macros.get(seq)
        if not template:
            return

        self._send_template(template)

    def _send_template(self, template: str) -> None:
        now = time.time()

        def pick(key: str) -> str:
            return self._variation_picker.pick(key)

        for _ in range(8):
            message = render_template(template, pick).strip()
            if self._ascii_only:
                message = normalize_ascii(message)
            if not message:
                return
            if message == self._last_sent_message:
                continue
            if self._recent.seen_recently(message, now):
                continue
            send_chat(message, self._chat_settings)
            print(f"Sent quick chat: {message}")
            self._last_sent_message = message
            self._recent.add(message, now)
            return

        message = render_template(template, pick).strip()
        if self._ascii_only:
            message = normalize_ascii(message)
        if message:
            send_chat(message, self._chat_settings)
            print(f"Sent quick chat: {message}")
            self._last_sent_message = message
            self._recent.add(message, now)


def list_controllers() -> List[pygame.joystick.Joystick]:
    pygame.joystick.init()
    controllers: List[pygame.joystick.Joystick] = []
    for i in range(pygame.joystick.get_count()):
        js = pygame.joystick.Joystick(i)
        js.init()
        controllers.append(js)
    return controllers


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="DualSense/DS4 Rocket League quickchat macro helper.")
    parser.add_argument("--chat-mode", default="lobby", choices=sorted(DEFAULT_CHAT_KEYS.keys()))
    parser.add_argument("--macro-window", type=float, default=1.1, help="Max seconds between 1st and 2nd input.")
    parser.add_argument("--spam-interval", type=float, default=0.2, help="Delay between repeated sends.")
    parser.add_argument("--cooldown", type=float, default=600.0, help="Seconds before identical message can repeat.")
    parser.add_argument("--ascii", action="store_true", help="Force ASCII-only output (replace smart punctuation).")
    parser.add_argument(
        "--persist",
        default="",
        help="Optional path to persist cooldown history across restarts (JSON file).",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print messages instead of typing them.")
    parser.add_argument("--list-devices", action="store_true", help="List detected controllers and exit.")
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)

    if sys.platform.startswith("linux") and is_wsl():
        print(
            "Warning: running under WSL. PyAutoGUI cannot control Windows apps from WSL.\n"
            "Run this with Windows Python (PowerShell/CMD) instead if Rocket League is on Windows."
        )

    pygame.init()
    pygame.joystick.init()

    if args.list_devices:
        controllers = list_controllers()
        if not controllers:
            print("No controllers detected.")
        for js in controllers:
            print(
                f"- #{js.get_id()}: {js.get_name()} "
                f"(buttons={js.get_numbuttons()}, hats={js.get_numhats()}, axes={js.get_numaxes()})"
            )
        return 0

    controllers = list_controllers()
    if not controllers:
        print("No controllers detected. Connect your controller, then rerun.")
        return 2

    print("Detected controllers:")
    for js in controllers:
        print(f"- #{js.get_id()}: {js.get_name()}")
    print("Waiting for quickchat inputs... (press PS to toggle macros, Ctrl+C to quit)")

    variation_picker = VariationPicker(variations)
    chat_settings = ChatSettings(
        chat_mode=args.chat_mode,
        chat_spam_interval_s=float(args.spam_interval),
        dry_run=bool(args.dry_run),
    )
    macro_settings = MacroSettings(macro_window_s=float(args.macro_window))
    engine = MacroEngine(
        variation_picker=variation_picker,
        chat_settings=chat_settings,
        macro_settings=macro_settings,
        message_cooldown_s=float(args.cooldown),
        ascii_only=bool(args.ascii),
        persist_path=(str(args.persist).strip() or None),
    )

    button_to_action = {v: k for k, v in BUTTONS.items()}

    try:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.JOYBUTTONDOWN:
                    action = button_to_action.get(int(event.button))
                    if action:
                        engine.handle_action(action)

                elif event.type == pygame.JOYHATMOTION:
                    action = hat_to_dpad_action(tuple(event.value))
                    if action:
                        engine.handle_action(action)

                elif event.type == pygame.JOYDEVICEADDED:
                    try:
                        js = pygame.joystick.Joystick(event.device_index)
                        js.init()
                        print(f"Controller added: #{js.get_id()}: {js.get_name()}")
                    except Exception:
                        pass

                elif event.type == pygame.JOYDEVICEREMOVED:
                    print(f"Controller removed: instance_id={event.instance_id}")

            time.sleep(0.005)
    except KeyboardInterrupt:
        print("\nExiting...")
        return 0
    finally:
        engine.save_persisted_state()
        pygame.quit()


if __name__ == "__main__":
    raise SystemExit(main())
