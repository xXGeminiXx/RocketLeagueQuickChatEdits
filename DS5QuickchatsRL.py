"""
DS5 Quickchats for Rocket League
================================

A DualSense/DS4 controller macro helper that sends funny, randomized quickchat
messages in Rocket League using D-pad combos.

HOW IT WORKS:
    1. The script listens for D-pad inputs on your controller via pygame
    2. When you press two D-pad directions in sequence (within ~1 second),
       it triggers a quickchat macro
    3. The macro picks a random message from a category and types it into
       Rocket League's chat using pyautogui

USAGE:
    python DS5QuickchatsRL.py [--dry-run] [--chat-mode lobby|team|party]

D-PAD COMBOS:
    UP + UP       = "I got it!" variations
    UP + DOWN     = Defending callouts
    DOWN + UP     = Greetings
    LEFT + UP     = Nice shot/pass compliments
    RIGHT + UP    = Centering callouts
    LEFT + RIGHT  = Thanks messages
    LEFT + DOWN   = Celebration
    LEFT + LEFT   = Quick compliment
    UP + RIGHT    = Confidence boost
    UP + LEFT     = Need boost callouts
    DOWN + RIGHT  = "No problem" (passive-aggressive)
    DOWN + LEFT   = Apologies
    RIGHT + LEFT  = Quick compliment (alt)
    RIGHT + RIGHT = Encouraging taunt
    RIGHT + DOWN  = Challenge
    DOWN + DOWN   = Random cat fact (the best feature)
    PS BUTTON     = Toggle macros on/off

REQUIREMENTS:
    - pygame (for controller input)
    - pyautogui (for typing into Rocket League)
    - A DualSense or DS4 controller
    - Rocket League running on Windows (not WSL!)

AUTHOR: David Ward
LICENSE: Do whatever you want with it, just have fun in ranked.
"""

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


# =============================================================================
# ENVIRONMENT DETECTION
# =============================================================================


def is_wsl() -> bool:
    """
    Detect if we're running under Windows Subsystem for Linux.

    This matters because pyautogui can't control Windows apps from WSL -
    you need to run this script with Windows Python directly.
    """
    try:
        return "microsoft" in os.uname().release.lower()
    except Exception:
        return False


# =============================================================================
# MESSAGE VARIATIONS
# =============================================================================
# Each category contains multiple variations of the same type of message.
# The system picks randomly from these, ensuring you don't repeat the same
# message twice in a row (or within a configurable cooldown window).
#
# TEMPLATE SYNTAX:
#   - Plain text is sent as-is
#   - {category_name} inserts a random pick from that category
#   - {category_name:modifier} applies a text transform:
#       :lower      = lowercase
#       :upper      = UPPERCASE
#       :capitalize = Capitalize first letter
#       :title      = Title Case Each Word
#
# TIPS FOR ADDING YOUR OWN:
#   - Keep messages under ~100 chars (Rocket League chat limit)
#   - More variations = less repetition = more fun
#   - Mix genuine callouts with jokes for maximum chaos
# =============================================================================

variations: Mapping[str, Sequence[str]] = {

    # =========================================================================
    # "I GOT IT" - Calling the ball (with varying confidence levels)
    # Triggered by: UP + UP
    # =========================================================================
    "I Got It": [
        "I got it... maybe.",
        "I got it... probably.",
        "I got it... definitely. (Don't quote me.)",
        "I got it! (Narrator: He did not.)",
        "I got it! Trust the process!",
        "I got it... assuming my boost cooperates.",
        "I got it! Clear the area, genius at work!",
        "Mine! Or not. We'll see.",
        "I got this. I've been training for this moment. (I haven't.)",
        "Going for it! Pray for me.",
        "I got it! (Said with the confidence of someone who doesn't.)",
        "On it like a bonnet!",
        "I'm going! Cover my emotional baggage!",
        "Taking it! Results may vary.",
        "My ball! My rules! My whiff!",
        "I got it... on alternate Tuesdays.",
        "Going! If I miss, we never speak of this.",
    ],

    # =========================================================================
    # DEFENDING - When you're back on D (emotionally and physically)
    # Triggered by: UP + DOWN
    # =========================================================================
    "Defending": [
        "Defending... emotionally and physically.",
        "I'm back! Guarding the net like my life depends on it. (It does.)",
        "Defending! Nothing gets past me. Except most shots.",
        "Back on D! D stands for 'definitely panicking.'",
        "Goalie mode: ACTIVATED. Confidence: QUESTIONABLE.",
        "Defending! I am the wall. A very porous wall.",
        "I'm last back! Everyone stay calm! STAY CALM!",
        "Guarding goal. Send positive vibes.",
        "Defending with the fury of a thousand bronze players!",
        "I'm back! The net is safe-ish.",
        "On defense! (Mentally preparing for the replay.)",
        "Defending! I watched a tutorial once.",
        "I'm the goalie now. Pray.",
        "Back in net! Accepting tips and therapy recommendations.",
        "Defending! Bold of them to shoot while I'm awake.",
    ],

    # =========================================================================
    # GREETINGS - When you need to say hi to your fellow car soccer enthusiasts
    # Triggered by: DOWN + UP
    # =========================================================================
    "Greeting": [
        "OH SNAP! Hello there, fellow car enthusiast!",
        "Greetings, traveler! Welcome to the thunderdome!",
        "Hello! I come in peace. My shots? Not so much.",
        "Ahoy, boost pirates!",
        "What's up, fellow ball chasers!",
        "Hey hey! Let's make some bad decisions together!",
        "Salutations! May your demos be swift and your whiffs be hidden!",
        "Hello friends! And future friends who don't know it yet!",
        "Yo! Ready to question our life choices?",
        "Greetings from someone who peaked in Season 3!",
        "Hey! I brought snacks. (The snacks are goals.)",
        "Hello! I'm here to kick ball and chew boost. And I'm all out of boost.",
        "Sup! Let's get this bread. The bread is the ball. Don't ask.",
        "Hey there! Nice cars! This is gonna hurt!",
        "Hola! Prepare for calculated chaos!",
    ],

    # =========================================================================
    # NICE ONE - Complimenting good plays (or any plays, really)
    # Triggered by: LEFT + UP
    # =========================================================================
    "Nice One": [
        "Nice shot! Was that intentional? Either way, WOW!",
        "Nice one! That was cleaner than my room!",
        "Great pass! Telepathy confirmed!",
        "What a play! That was beautiful and I'm emotional now.",
        "Nice shot! That was illegal in at least 12 states.",
        "Beautiful! Chef's kiss! Five stars!",
        "Nice one! Clip it! Send it! Frame it!",
        "Great shot! I believed in you the whole time. (I didn't.)",
        "Nice pass! We're basically telepathic now.",
        "Wow! That was smoother than butter on a hot pan!",
        "Nice one! Your car has AURA.",
        "What a shot! The physics engine is SHOOK.",
        "Great play! I'd clap but I'm holding a controller.",
        "Nice! That was more calculated than my taxes!",
        "What a save! Flexed on them, you did.",
        "Nice shot! That was straight out of RLCS!",
        "Beautiful pass! We're in sync like a boyband!",
        "Nice one! Someone call Psyonix, that was art!",
        "Great shot! I'm not crying, you're crying!",
        "What a play! I need a moment.",
    ],

    # =========================================================================
    # CENTERING - When you're trying to set up plays (key word: trying)
    # Triggered by: RIGHT + UP
    # =========================================================================
    "Centering": [
        "Centering! (Narrator: He was not centering.)",
        "Centering! Ball incoming! Probably!",
        "Setting you up! Don't leave me hanging!",
        "Passing! Do the thing! Score the goal!",
        "Centering! I'm like a waiter serving goals!",
        "Cross incoming! (Results not guaranteed.)",
        "Centering! I believe in you even if the ball doesn't!",
        "Passing! The rest is your problem!",
        "Setting up shop! Come get your free goals!",
        "Centering! This is a team effort! I did my part!",
        "Cross! Inbound! Hopefully!",
        "Passing mid! I'm basically an assist machine!",
        "Centering! It's not a whiff if you meant to pass!",
        "Setting you up for glory! (Or pain. 50/50.)",
        "Incoming pass! I BELIEVE!",
    ],

    # =========================================================================
    # THANKS - Expressing gratitude (sincerely or otherwise)
    # Triggered by: LEFT + RIGHT
    # =========================================================================
    "Thanks": [
        "Thanks! That was definitely intentional! (It wasn't.)",
        "Thank you, kind teammate! You're a real one!",
        "Thanks! We're basically a championship duo now!",
        "Appreciate it! My therapist was right about teamwork!",
        "Thanks! I owe you a boost pad!",
        "Thank you! That was smoother than my aerial attempts!",
        "Thanks! You're my favorite random!",
        "Appreciate the setup! I almost felt useful!",
        "Thanks! We're vibing on another level!",
        "Thank you! This is the teamwork I dreamed of!",
        "Thanks! You're carrying and I appreciate it!",
        "Gracias! Merci! Danke! All the thanks!",
        "Thanks! I'll name my next aerial after you!",
        "Appreciate it! We're in sync like a playlist!",
        "Thanks! You're the assist to my... attempt!",
    ],

    # =========================================================================
    # CELEBRATION - When the team does something right
    # Triggered by: LEFT + DOWN
    # =========================================================================
    "Celebration": [
        "Great job, team! Nobody look at the replay!",
        "We're on fire! (Stop drop and rotate!)",
        "Calculated! (I own a calculator!)",
        "WINNING! (Narrator: He was not... wait, he was!)",
        "Peak Rocket League! Clip it! Send it to NASA!",
        "LET'S GOOO! That's what I'm talking about!",
        "WE DID IT! Group hug! Virtual group hug!",
        "BEAUTIFUL! I'm getting emotional!",
        "That's how it's done! Someone screenshot this!",
        "WE'RE GAMING NOW! This is the good stuff!",
        "GOLAZO! (I've been waiting to use that.)",
        "WHAT A GOAL! I was definitely helpful somehow!",
        "YES! This is our championship moment!",
        "INCREDIBLE! We're basically pros now!",
        "POGGERS! (Do people still say that?)",
    ],

    # =========================================================================
    # APOLOGY - For when you inevitably mess up
    # Triggered by: DOWN + LEFT
    # =========================================================================
    "Apology": [
        "My bad, that was on me.",
        "Sorry about that. Brain buffering.",
        "Whoops. That was my controller. (It wasn't.)",
        "Apologies. I got jumpscared by the ball.",
        "Sorry! I saw a boost pad and blacked out.",
        "My bad! The vibes were off on that one.",
        "Sorry! Gravity works differently for me apparently.",
        "Oops! That was... that was something.",
        "My bad! I panicked and chose violence. Against myself.",
        "Sorry! I'm still learning. (After 2000 hours.)",
        "Apologies! The ball is faster than my brain.",
        "My bad! I'll hit the next one. (No guarantees.)",
        "Sorry! I trusted the physics and the physics lied.",
        "Oops! Let's never speak of this again.",
        "My bad! I blame the server. (It was me.)",
    ],

    # =========================================================================
    # NEED BOOST - The eternal struggle
    # Triggered by: UP + LEFT
    # =========================================================================
    "Need Boost": [
        "Need boost! I'm running on hopes and fumes!",
        "No boost! I'm basically a very slow brick right now!",
        "Need boost! My tank is drier than my humor!",
        "Zero boost! I'm coasting on prayers!",
        "Boost please! My car is sad and empty!",
        "Running on empty! Send help! Send boost!",
        "No boost! I'm just vibes and bad decisions!",
        "Need boost! Currently operating on pure spite!",
        "Boost-less! I'm a sitting duck! A car duck!",
        "Empty tank! I'm decorative right now!",
        "No boost! My car is questioning its life choices!",
        "Need boost! I'm held together by hope and momentum!",
        "Zero fuel! I'm running on audacity alone!",
        "Boost starved! Someone adopt me!",
        "No boost! I'm basically a paper weight!",
    ],

    # =========================================================================
    # NO PROBLEM - Passive-aggressive forgiveness
    # Triggered by: DOWN + RIGHT
    # =========================================================================
    "No Problem": [
        "No problem! (It was absolutely your fault.)",
        "All good! We'll get 'em next time! (We won't.)",
        "No worries! I've made worse decisions! (Have I?)",
        "It's fine! Everything is fine! THIS IS FINE!",
        "No problem! Pain is temporary, vibes are eternal!",
        "All good! We're still learning! (Allegedly.)",
        "No worries! That's just extra spicy gameplay!",
        "It's okay! Mistakes build character!",
        "No problem! I didn't see anything! (I saw everything.)",
        "All good! The important thing is friendship!",
        "No worries! We'll pretend that didn't happen!",
        "It's fine! I've seen worse! (I haven't.)",
        "No problem! Growth mindset! Learning experience!",
        "All good! At least we're having fun! (Are we?)",
        "No worries! I still believe in us! (Barely.)",
    ],

    # =========================================================================
    # CHALLENGE - Throwing down the gauntlet
    # Triggered by: RIGHT + DOWN
    # =========================================================================
    "Challenge": [
        "I dare you to score. Do it. I double-dog dare you.",
        "Try to beat that!",
        "Challenge accepted! (I regret everything.)",
        "Meet me in the midfield. We'll settle this with vibes.",
        "1v1 me behind the boost pad.",
        "Bold of you to challenge me while I'm holding drift.",
        "You dare challenge ME? In MY ranked lobby?",
        "Is that a challenge? Because I'm already nervous!",
        "Fight me in the air! (I'll probably miss but STILL!)",
        "Challenge mode activated! (Panic mode also activated!)",
        "You want some of this? THIS IS ROCKET LEAGUE!",
        "Square up! My aerials are ready! (They're not.)",
        "Challenge accepted! May the best whiffer win!",
        "You vs me! Let's see what happens!",
        "I challenge you to a duel! (Of bad decisions!)",
    ],

    # =========================================================================
    # CONFIDENCE BOOST - Self-affirmation for the team
    # Triggered by: UP + RIGHT
    # =========================================================================
    "Confidence Boost": [
        "We are absolutely winning this! (Source: me.)",
        "We're the main characters. Act like it!",
        "Trust the process! (I have no idea what the process is.)",
        "We're so back.",
        "If confidence was boost, we'd be supersonic!",
        "Calculated! (Not really, but BELIEVE!)",
        "We're about to peak. Probably. Maybe.",
        "Winner's mentality: ENGAGED. Mechanics: Optional.",
        "I can feel the montage music starting!",
        "This lobby isn't ready for our nonsense!",
        "We've got this! Statistically, we have to win eventually!",
        "Champions in the making! Future legends right here!",
        "We're different! We're special! We're slightly above average!",
        "Believe in the me that believes in you!",
        "We're gonna be unstoppable! (One day!)",
    ],

    # =========================================================================
    # ENCOURAGING TAUNT - Being supportive... kind of
    # Triggered by: RIGHT + RIGHT
    # =========================================================================
    "Encouraging Taunt": [
        "Is that all you've got? (I'm genuinely asking.)",
        "Nice try! That was almost a thing!",
        "You're getting warmer! Like, room temperature.",
        "Not bad! Now do it on purpose!",
        "You're almost there! (Where is 'there'? Nobody knows.)",
        "Getting better with every try! Statistically.",
        "You're on the right track! Now let's find the ball!",
        "Impressive... but I'm still emotionally unprepared.",
        "Keep trying! You're almost unstoppable! Almost.",
        "You're a force to be reckoned with! In a different lobby.",
        "You can do better than that! I believe in future-you!",
        "That was a shot! Technically speaking.",
        "So close! In a metaphysical sense!",
        "Nice attempt! Have you tried practicing? (Same.)",
        "Good effort! The ball respects your hustle!",
    ],

    # =========================================================================
    # COMPLIMENTS - Quick one-liners for good plays
    # Triggered by: LEFT + LEFT or RIGHT + LEFT
    # =========================================================================
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
        "Magnificent!",
        "Brilliant!",
        "Glorious!",
        "Legendary!",
        "Epic!",
        "Phenomenal!",
        "Incredible!",
        "Spectacular!",
        "Marvelous!",
        "Perfection!",
        "Chef's kiss!",
        "More legendary than a unicorn in a top hat!",
        "Cooler than a polar bear's toenails!",
        "Shinier than a freshly waxed penguin!",
        "As epic as a double rainbow!",
        "Worthy of a mic drop!",
        "As dazzling as fireworks!",
        "That was illegal in at least 12 states!",
        "Your car has aura!",
    ],

    # =========================================================================
    # CAT FACTS - The most important feature (DOWN + DOWN)
    # Because what's Rocket League without random cat facts?
    # =========================================================================
    "cat fact": [
        "CAT FAX: Cats have 32 muscles in each ear. They still won't hear 'rotate.'",
        "CAT FAX: A group of cats is a clowder. A group of teammates is a 'double commit.'",
        "CAT FAX: Cats sleep 12-16 hours/day. Same as me after whiffing.",
        "CAT FAX: Cats purr at ~25 Hz. My car purrs at 0 boost.",
        "CAT FAX: Cats can't taste sweetness. I can't taste victory either. (Yet.)",
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
        "CAT FAX: Cats can rotate ears 180 degrees. I can rotate my car 720 and still miss.",
        "CAT FAX: Cats were worshipped in ancient Egypt. I worship the small boost pad.",
        "CAT FAX: Cats have a collarbone that helps them fit places. I have a hitbox and regret.",
        "CAT FAX: Cats can run ~30 mph. I can drive 100 and still be late to the play.",
        "CAT FAX: Cats have an organ to 'taste' smells. I have an organ to taste Ls.",
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


# =============================================================================
# CONTROLLER BUTTON MAPPINGS
# =============================================================================
# DualSense/DS4-ish controller button mappings for pygame.
# Note: D-pad may be exposed as buttons OR as "hat 0" depending on the
# controller and driver. We support both via the event loop.
#
# If your controller has different button numbers, adjust these values.
# Use --list-devices to see what pygame detects for your controller.
# =============================================================================

BUTTONS: Mapping[str, int] = {
    "cross": 0,       # X button (bottom face button)
    "circle": 1,      # O button (right face button)
    "square": 2,      # Square button (left face button)
    "triangle": 3,    # Triangle button (top face button)
    "share": 4,       # Share/Create button
    "ps": 5,          # PS button (home button) - used to toggle macros
    "options": 6,     # Options button
    "L1": 9,          # Left bumper
    "R1": 10,         # Right bumper
    "up": 11,         # D-pad up (when exposed as button)
    "down": 12,       # D-pad down
    "left": 13,       # D-pad left
    "right": 14,      # D-pad right
}


# =============================================================================
# CHAT KEY CONFIGURATION
# =============================================================================
# These are the keyboard keys that open different chat modes in Rocket League.
# Adjust these if you've rebound your chat keys in-game.
#
# - lobby: All-chat (everyone in the match can see)
# - team: Team-only chat
# - party: Party chat (only your premade group)
# =============================================================================

DEFAULT_CHAT_KEYS: Mapping[str, str] = {
    "lobby": "t",    # All-chat (default: T)
    "team": "y",     # Team chat (default: Y)
    "party": "u",    # Party chat (default: U)
}


# =============================================================================
# CONFIGURATION CLASSES
# =============================================================================


@dataclass(frozen=True)
class ChatSettings:
    """
    Configuration for how chat messages are sent.

    Attributes:
        chat_mode: Which chat to use ("lobby", "team", or "party")
        chat_keys: Mapping of chat modes to keyboard keys
        chat_spam_interval_s: Delay between message sends (for spam protection)
        typing_interval_s: Delay between keystrokes (pyautogui setting)
        dry_run: If True, print messages instead of actually typing them
    """
    chat_mode: str = "lobby"
    chat_keys: Mapping[str, str] = field(default_factory=lambda: dict(DEFAULT_CHAT_KEYS))
    chat_spam_interval_s: float = 0.2
    typing_interval_s: float = 0.001
    dry_run: bool = False


@dataclass
class RecentMessageCache:
    """
    Tracks recently sent messages to avoid repetition.

    This prevents the same message from being sent twice within the cooldown
    window, even if the random picker happens to select it again.

    Attributes:
        cooldown_s: How long (in seconds) before a message can be repeated
        max_entries: Maximum number of messages to track (older ones are pruned)
    """
    cooldown_s: float = 600.0   # 10 minutes default cooldown
    max_entries: int = 200      # Keep track of up to 200 recent messages
    _entries: List[Tuple[str, float]] = field(default_factory=list)

    def seen_recently(self, message: str, now: float) -> bool:
        """Check if we've sent this exact message recently."""
        cutoff = now - self.cooldown_s
        # Prune old entries while we're at it
        self._entries = [(m, t) for (m, t) in self._entries if t >= cutoff]
        return any(m == message for (m, _) in self._entries)

    def add(self, message: str, now: float) -> None:
        """Record that we sent this message at this time."""
        self._entries.append((message, now))
        # Cap the list size to prevent unbounded memory growth
        if len(self._entries) > self.max_entries:
            self._entries = self._entries[-self.max_entries:]


# =============================================================================
# VARIATION PICKER
# =============================================================================
# This class handles random selection from variation lists while ensuring
# we don't repeat the same item twice in a row. It shuffles each category
# and walks through the shuffled list, reshuffling when we reach the end.
# =============================================================================


class VariationPicker:
    """
    Picks random variations from categories without immediate repetition.

    Uses a "shuffle bag" approach: each category's items are shuffled,
    then dealt out one by one. When the bag is empty, it's reshuffled
    (making sure the last item of the old bag isn't the first of the new).

    This gives better perceived randomness than pure random selection,
    which can feel "streaky" and repeat items unexpectedly.
    """

    def __init__(self, variations_map: Mapping[str, Sequence[str]]) -> None:
        self._variations = {k: list(v) for k, v in variations_map.items()}
        self._state: Dict[str, Dict[str, object]] = {}
        # Initialize shuffle state for each category
        for key in self._variations:
            self._reshuffle(key, avoid_first=None)

    def _normalize_key(self, key: str) -> str:
        """
        Handle key lookup with flexible matching.

        Supports:
        - Exact match
        - Underscore/space equivalence (e.g., "cat_fact" = "cat fact")
        - Case-insensitive matching
        """
        key = key.strip()
        if key in self._variations:
            return key

        # Try with underscores replaced by spaces
        alt = key.replace("_", " ")
        if alt in self._variations:
            return alt

        # Try with spaces replaced by underscores
        alt2 = key.replace(" ", "_")
        if alt2 in self._variations:
            return alt2

        # Case-insensitive fallback
        key_lower = key.lower()
        alt_lower = alt.lower()
        alt2_lower = alt2.lower()
        for existing_key in self._variations.keys():
            existing_lower = existing_key.lower()
            if existing_lower in (key_lower, alt_lower, alt2_lower):
                return existing_key

        raise KeyError(f'Unknown variation key "{key}". Known keys: {sorted(self._variations)}')

    def _reshuffle(self, key: str, avoid_first: Optional[str]) -> None:
        """
        Reshuffle a category's items.

        Args:
            key: The category to reshuffle
            avoid_first: If set, try to avoid this item being first
                        (prevents back-to-back repeats across reshuffles)
        """
        words = self._variations[key]
        if not words:
            self._state[key] = {"randomized": [], "i": 0}
            return

        # Try up to 30 times to get a shuffle that doesn't start with avoid_first
        for _ in range(30):
            randomized = sample(words, len(words))
            if avoid_first is None or randomized[0] != avoid_first:
                self._state[key] = {"randomized": randomized, "i": 0}
                return

        # Give up and accept whatever shuffle we get
        self._state[key] = {"randomized": sample(words, len(words)), "i": 0}

    def pick(self, key: str) -> str:
        """
        Pick the next random item from a category.

        Returns:
            A string from the category, guaranteed not to be the same as
            the previous pick (unless the category has only 1-2 items).
        """
        key = self._normalize_key(key)

        words = self._variations[key]
        if len(words) < 1:
            return ""
        if len(words) < 3:
            print(f'Warning: variation list "{key}" has <3 items; repeats are likely.')

        randomized = self._state[key]["randomized"]  # type: ignore[assignment]
        i = int(self._state[key]["i"])  # type: ignore[arg-type]

        # If we've used all items, reshuffle
        if i >= len(randomized):
            avoid_first = randomized[-1] if randomized else None
            self._reshuffle(key, avoid_first=avoid_first)
            randomized = self._state[key]["randomized"]  # type: ignore[assignment]
            i = int(self._state[key]["i"])  # type: ignore[arg-type]

        self._state[key]["i"] = i + 1
        return str(randomized[i])


# =============================================================================
# TEXT PROCESSING
# =============================================================================


def apply_text_modifier(text: str, modifier: Optional[str]) -> str:
    """
    Apply a text transformation (used in template syntax like {key:lower}).

    Supported modifiers:
        - lower: lowercase everything
        - upper: UPPERCASE EVERYTHING
        - capitalize: Capitalize first letter only
        - title: Title Case Every Word
    """
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
    """
    Render a template string by substituting {category} placeholders.

    Examples:
        "Hello {friend}" -> "Hello ole Buddy."
        "{compliment:lower}" -> "great!"
        "Nice one, {friend:upper}" -> "Nice one, OLE BUDDY."

    Args:
        template: The template string with {placeholders}
        pick_variation: Function that returns a random item for a category

    Returns:
        The fully rendered string with all placeholders replaced
    """
    out: List[str] = []
    i = 0
    while i < len(template):
        if template[i] != "{":
            out.append(template[i])
            i += 1
            continue

        end = template.find("}", i + 1)
        if end == -1:
            # Unclosed brace, just output the rest as-is
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
    """
    Convert text to ASCII-only by replacing/removing special characters.

    This is useful because some terminal/chat systems don't handle Unicode
    well. Smart quotes become regular quotes, em-dashes become hyphens, etc.
    """
    # First, replace common "smart" characters with ASCII equivalents
    table = str.maketrans(
        {
            "'": "'",      # Smart single quote (left)
            "'": "'",      # Smart single quote (right)
            """: '"',      # Smart double quote (left)
            """: '"',      # Smart double quote (right)
            "–": "-",      # En-dash
            "—": "-",      # Em-dash
            "…": "...",    # Ellipsis
            "\u00a0": " ", # Non-breaking space
        }
    )
    text = text.translate(table)

    # Then normalize Unicode and strip anything that's still not ASCII
    text = unicodedata.normalize("NFKD", text)
    return text.encode("ascii", "ignore").decode("ascii")


# =============================================================================
# CHAT SENDING
# =============================================================================


def send_chat(message: str, settings: ChatSettings, spam_count: int = 1) -> None:
    """
    Send a chat message in Rocket League via simulated keyboard input.

    This opens chat with the appropriate key, types the message, and hits enter.

    Args:
        message: The message to send
        settings: Chat configuration (mode, keys, timing)
        spam_count: How many times to send the message (default 1)
    """
    if settings.chat_mode not in settings.chat_keys:
        raise KeyError(f'Unknown chat mode "{settings.chat_mode}". Known: {sorted(settings.chat_keys)}')

    for _ in range(spam_count):
        if settings.dry_run:
            # Just print instead of actually sending
            print(f"[dry-run] {message}")
        else:
            import pyautogui

            # Open chat with the appropriate key
            pyautogui.press(settings.chat_keys[settings.chat_mode])
            # Type the message
            pyautogui.write(message, interval=settings.typing_interval_s)
            # Send it
            pyautogui.press("enter")
        time.sleep(settings.chat_spam_interval_s)


# =============================================================================
# D-PAD HANDLING
# =============================================================================


def hat_to_dpad_action(value: Tuple[int, int]) -> Optional[str]:
    """
    Convert a "hat" (D-pad) value from pygame to a direction string.

    Pygame represents D-pad as a tuple of (x, y) where:
        - x: -1 = left, 0 = center, 1 = right
        - y: -1 = down, 0 = center, 1 = up

    Returns:
        "up", "down", "left", "right", or None if centered
    """
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


# =============================================================================
# MACRO ENGINE
# =============================================================================


@dataclass(frozen=True)
class MacroSettings:
    """
    Configuration for the macro input detection.

    Attributes:
        macro_window_s: Maximum time between first and second D-pad press
                       to register as a combo (default 1.1 seconds)
        macro_min_gap_s: Minimum time between presses (filters out bouncing)
    """
    macro_window_s: float = 1.1
    macro_min_gap_s: float = 0.05


class MacroEngine:
    """
    The main engine that processes D-pad inputs and triggers quickchats.

    Listens for D-pad direction sequences (e.g., UP + UP, LEFT + RIGHT)
    and sends the corresponding quickchat message when a combo is detected.

    Features:
        - Two-input combo detection with configurable timing window
        - Automatic message variation to avoid repetition
        - Cooldown system to prevent spam of identical messages
        - Persistent state across restarts (optional)
        - Toggle on/off with PS button
    """

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

        # Input tracking state
        self._last_action: Optional[str] = None
        self._last_action_time: float = 0.0
        self._last_sent_message: str = ""
        self._last_toggle_time: float = 0.0

        # =====================================================================
        # MACRO DEFINITIONS
        # =====================================================================
        # Each tuple (direction1, direction2) maps to a template string.
        # Templates can be plain text or include {category} placeholders.
        # =====================================================================

        self._macros: Dict[Tuple[str, str], str] = {
            # Callouts
            ("up", "up"):       "{I Got It}",           # I got it!
            ("up", "down"):     "{Defending}",          # Defending...
            ("up", "left"):     "{Need Boost}",         # Need boost!
            ("right", "up"):    "{Centering}",          # Centering!

            # Positive reactions
            ("left", "up"):     "{Nice One}",           # Nice shot/pass!
            ("left", "right"):  "{Thanks}",             # Thanks!
            ("left", "down"):   "{Celebration}",        # Let's go!
            ("left", "left"):   "{compliment}",         # Quick compliment
            ("right", "left"):  "{compliment}",         # Quick compliment (alt)

            # Morale
            ("up", "right"):    "{Confidence Boost}",   # We got this!
            ("down", "up"):     "{Greeting}",           # Hello!

            # Responses
            ("down", "right"):  "{No Problem}",         # No problem (sarcastic)
            ("down", "left"):   "{Apology}",            # Sorry!

            # Taunts & Challenges
            ("right", "right"): "{Encouraging Taunt}",  # Nice try!
            ("right", "down"):  "{Challenge}",          # Fight me!

            # The best feature
            ("down", "down"):   "{cat fact}",           # CAT FAX!
        }

        # Try to restore state from previous session
        self._load_persisted_state()

    def _load_persisted_state(self) -> None:
        """
        Load previously saved state (cooldown history, last message).

        This allows the cooldown system to work across restarts -
        you won't immediately repeat a message you just sent before
        restarting the script.
        """
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
                self._recent._entries = parsed[-self._recent.max_entries:]
        except FileNotFoundError:
            return
        except Exception as e:
            print(f"Warning: failed to load persisted state from {self._persist_path!r}: {e}")

    def save_persisted_state(self) -> None:
        """
        Save current state to disk for restoration after restart.

        Called automatically when the script exits cleanly.
        """
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
        """Toggle macros on/off (called when PS button is pressed)."""
        now = time.time()
        # Debounce to prevent rapid toggling
        if now - self._last_toggle_time < 0.25:
            return
        self._last_toggle_time = now
        self._macros_enabled = not self._macros_enabled
        state = "on" if self._macros_enabled else "off"
        print(f"----- quickchat macros toggled {state} -----")

    def handle_action(self, action: str) -> None:
        """
        Process a D-pad or button action.

        For D-pad directions, this builds up two-input combos and triggers
        the corresponding macro when a valid combo is detected.

        For the PS button, this toggles macros on/off.
        """
        # PS button toggles macros
        if action == "ps":
            self.toggle()
            return

        # If macros are disabled, ignore D-pad inputs
        if not self._macros_enabled:
            return

        # Only process D-pad directions
        if action not in ("up", "down", "left", "right"):
            return

        now = time.time()

        # First input of potential combo
        if self._last_action is None:
            self._last_action = action
            self._last_action_time = now
            return

        elapsed = now - self._last_action_time

        # Too slow? Reset and start a new potential combo
        if elapsed > self._macro_settings.macro_window_s:
            self._last_action = action
            self._last_action_time = now
            return

        # Too fast? Ignore (probably button bounce)
        if elapsed < self._macro_settings.macro_min_gap_s:
            return

        # We have a valid two-input combo!
        seq = (self._last_action, action)
        self._last_action = None
        self._last_action_time = 0.0

        # Look up the macro template
        template = self._macros.get(seq)
        if not template:
            return

        self._send_template(template)

    def _send_template(self, template: str) -> None:
        """
        Render a template and send it as a chat message.

        Tries multiple times to get a unique message (one we haven't
        sent recently). If all attempts result in duplicates, sends
        anyway to avoid infinite loops.
        """
        now = time.time()

        def pick(key: str) -> str:
            return self._variation_picker.pick(key)

        # Try up to 8 times to get a non-duplicate message
        for _ in range(8):
            message = render_template(template, pick).strip()
            if self._ascii_only:
                message = normalize_ascii(message)
            if not message:
                return
            # Skip if same as last message or seen recently
            if message == self._last_sent_message:
                continue
            if self._recent.seen_recently(message, now):
                continue
            # Found a good one!
            send_chat(message, self._chat_settings)
            print(f"Sent quick chat: {message}")
            self._last_sent_message = message
            self._recent.add(message, now)
            return

        # Fallback: just send whatever we have
        message = render_template(template, pick).strip()
        if self._ascii_only:
            message = normalize_ascii(message)
        if message:
            send_chat(message, self._chat_settings)
            print(f"Sent quick chat: {message}")
            self._last_sent_message = message
            self._recent.add(message, now)


# =============================================================================
# CONTROLLER DETECTION
# =============================================================================


def list_controllers() -> List[pygame.joystick.Joystick]:
    """
    Detect and initialize all connected game controllers.

    Returns:
        List of pygame Joystick objects for each detected controller
    """
    pygame.joystick.init()
    controllers: List[pygame.joystick.Joystick] = []
    for i in range(pygame.joystick.get_count()):
        js = pygame.joystick.Joystick(i)
        js.init()
        controllers.append(js)
    return controllers


# =============================================================================
# COMMAND LINE INTERFACE
# =============================================================================


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="DualSense/DS4 Rocket League quickchat macro helper.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python DS5QuickchatsRL.py                    # Run with defaults (lobby chat)
  python DS5QuickchatsRL.py --chat-mode team   # Use team chat instead
  python DS5QuickchatsRL.py --dry-run          # Print messages without sending
  python DS5QuickchatsRL.py --list-devices     # Show detected controllers

D-pad combos:
  UP+UP       I got it!          LEFT+UP      Nice shot!
  UP+DOWN     Defending          LEFT+RIGHT   Thanks!
  UP+LEFT     Need boost         LEFT+DOWN    Celebration
  DOWN+DOWN   Cat facts!         RIGHT+RIGHT  Encouraging taunt
  ...and more! See source code for full list.
        """
    )
    parser.add_argument(
        "--chat-mode",
        default="lobby",
        choices=sorted(DEFAULT_CHAT_KEYS.keys()),
        help="Which chat to use: lobby (all), team, or party"
    )
    parser.add_argument(
        "--macro-window",
        type=float,
        default=1.1,
        help="Max seconds between 1st and 2nd D-pad input (default: 1.1)"
    )
    parser.add_argument(
        "--spam-interval",
        type=float,
        default=0.2,
        help="Delay between repeated sends in seconds (default: 0.2)"
    )
    parser.add_argument(
        "--cooldown",
        type=float,
        default=600.0,
        help="Seconds before identical message can repeat (default: 600)"
    )
    parser.add_argument(
        "--ascii",
        action="store_true",
        help="Force ASCII-only output (converts smart quotes, etc.)"
    )
    parser.add_argument(
        "--persist",
        default="",
        help="Path to save/load message history (JSON file) for cross-session cooldowns"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print messages instead of typing them (for testing)"
    )
    parser.add_argument(
        "--list-devices",
        action="store_true",
        help="List detected controllers and exit"
    )
    return parser.parse_args(argv)


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================


def main(argv: Optional[Sequence[str]] = None) -> int:
    """
    Main entry point for the quickchat macro script.

    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    args = parse_args(argv)

    # Warn if running under WSL (won't work for Windows games)
    if sys.platform.startswith("linux") and is_wsl():
        print(
            "Warning: running under WSL. PyAutoGUI cannot control Windows apps from WSL.\n"
            "Run this with Windows Python (PowerShell/CMD) instead if Rocket League is on Windows."
        )

    # Initialize pygame for controller input
    pygame.init()
    pygame.joystick.init()

    # Handle --list-devices flag
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

    # Detect controllers
    controllers = list_controllers()
    if not controllers:
        print("No controllers detected. Connect your controller, then rerun.")
        return 2

    print("Detected controllers:")
    for js in controllers:
        print(f"  - #{js.get_id()}: {js.get_name()}")
    print()
    print("Quickchat macros are ACTIVE!")
    print("  - Use D-pad combos to send messages")
    print("  - Press PS button to toggle macros on/off")
    print("  - Press Ctrl+C to quit")
    print()

    # Set up the macro engine
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

    # Reverse lookup: button number -> action name
    button_to_action = {v: k for k, v in BUTTONS.items()}

    # Main event loop
    try:
        while True:
            for event in pygame.event.get():
                # Handle button presses (for controllers that expose D-pad as buttons)
                if event.type == pygame.JOYBUTTONDOWN:
                    action = button_to_action.get(int(event.button))
                    if action:
                        engine.handle_action(action)

                # Handle hat motion (for controllers that expose D-pad as a hat)
                elif event.type == pygame.JOYHATMOTION:
                    action = hat_to_dpad_action(tuple(event.value))
                    if action:
                        engine.handle_action(action)

                # Handle controller connect/disconnect
                elif event.type == pygame.JOYDEVICEADDED:
                    try:
                        js = pygame.joystick.Joystick(event.device_index)
                        js.init()
                        print(f"Controller added: #{js.get_id()}: {js.get_name()}")
                    except Exception:
                        pass

                elif event.type == pygame.JOYDEVICEREMOVED:
                    print(f"Controller removed: instance_id={event.instance_id}")

            # Small sleep to avoid busy-waiting
            time.sleep(0.005)

    except KeyboardInterrupt:
        print("\nExiting...")
        return 0
    finally:
        # Save state for next session and clean up
        engine.save_persisted_state()
        pygame.quit()


# =============================================================================
# SCRIPT EXECUTION
# =============================================================================

if __name__ == "__main__":
    raise SystemExit(main())
