import tkinter as tk
from tkinter import messagebox, font
import random
from enum import Enum
from collections import Counter

class Suit(Enum):
    HEARTS = "♥"
    DIAMONDS = "♦"
    CLUBS = "♣"
    SPADES = "♠"

class Rank(Enum):
    TWO = (2, "2")
    THREE = (3, "3")
    FOUR = (4, "4")
    FIVE = (5, "5")
    SIX = (6, "6")
    SEVEN = (7, "7")
    EIGHT = (8, "8")
    NINE = (9, "9")
    TEN = (10, "10")
    JACK = (11, "J")
    QUEEN = (12, "Q")
    KING = (13, "K")
    ACE = (14, "A")

    @property
    def numeric_value(self):
        return self.value[0]

    @property
    def symbol(self):
        return self.value[1]

class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank

    def __str__(self):
        return f"{self.rank.symbol}{self.suit.value}"

    def __repr__(self):
        return self.__str__()

class Deck:
    def __init__(self):
        self.cards = []
        self.reset()

    def reset(self):
        self.cards = [Card(suit, rank) for suit in Suit for rank in Rank]
        self.shuffle()

    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self):
        if not self.cards:
            return None
        return self.cards.pop()

class HandRank(Enum):
    HIGH_CARD = (1, "High Card")
    PAIR = (2, "Pair")
    TWO_PAIR = (3, "Two Pair")
    THREE_OF_A_KIND = (4, "Three of a Kind")
    STRAIGHT = (5, "Straight")
    FLUSH = (6, "Flush")
    FULL_HOUSE = (7, "Full House")
    FOUR_OF_A_KIND = (8, "Four of a Kind")
    STRAIGHT_FLUSH = (9, "Straight Flush")
    ROYAL_FLUSH = (10, "Royal Flush")

    @property
    def numeric_value(self):
        return self.value[0]

    @property
    def display_name(self):
        return self.value[1]

class HandEvaluator:
    @staticmethod
    def evaluate(cards):
        if not cards or len(cards) < 5:
            return (HandRank.HIGH_CARD, [])

        all_combinations = HandEvaluator._get_combinations(cards, 5)
        best_hand = (HandRank.HIGH_CARD, [], [])

        for combo in all_combinations:
            hand_rank, tiebreakers = HandEvaluator._evaluate_five_cards(combo)
            if hand_rank.numeric_value > best_hand[0].numeric_value:
                best_hand = (hand_rank, tiebreakers, combo)
            elif hand_rank.numeric_value == best_hand[0].numeric_value:
                if tiebreakers > best_hand[1]:
                    best_hand = (hand_rank, tiebreakers, combo)

        return best_hand[0], best_hand[2]

    @staticmethod
    def _get_combinations(cards, r):
        from itertools import combinations
        return list(combinations(cards, r))

    @staticmethod
    def _evaluate_five_cards(cards):
        ranks = sorted([c.rank.numeric_value for c in cards], reverse=True)
        suits = [c.suit for c in cards]
        rank_counts = Counter(ranks)
        suit_counts = Counter(suits)

        is_flush = len(suit_counts) == 1
        is_straight = HandEvaluator._is_straight(ranks)

        if is_flush and is_straight:
            if ranks == [14, 13, 12, 11, 10]:
                return (HandRank.ROYAL_FLUSH, [14])
            return (HandRank.STRAIGHT_FLUSH, [max(ranks)])

        if 4 in rank_counts.values():
            quad_rank = [r for r, c in rank_counts.items() if c == 4][0]
            kicker = [r for r in ranks if r != quad_rank][0]
            return (HandRank.FOUR_OF_A_KIND, [quad_rank, kicker])

        if 3 in rank_counts.values() and 2 in rank_counts.values():
            trip_rank = [r for r, c in rank_counts.items() if c == 3][0]
            pair_rank = [r for r, c in rank_counts.items() if c == 2][0]
            return (HandRank.FULL_HOUSE, [trip_rank, pair_rank])

        if is_flush:
            return (HandRank.FLUSH, ranks)

        if is_straight:
            return (HandRank.STRAIGHT, [max(ranks)])

        if 3 in rank_counts.values():
            trip_rank = [r for r, c in rank_counts.items() if c == 3][0]
            kickers = sorted([r for r in ranks if r != trip_rank], reverse=True)
            return (HandRank.THREE_OF_A_KIND, [trip_rank] + kickers)

        pairs = [r for r, c in rank_counts.items() if c == 2]
        if len(pairs) == 2:
            pairs_sorted = sorted(pairs, reverse=True)
            kicker = [r for r in ranks if r not in pairs][0]
            return (HandRank.TWO_PAIR, pairs_sorted + [kicker])

        if len(pairs) == 1:
            pair_rank = pairs[0]
            kickers = sorted([r for r in ranks if r != pair_rank], reverse=True)
            return (HandRank.PAIR, [pair_rank] + kickers)

        return (HandRank.HIGH_CARD, ranks)

    @staticmethod
    def _is_straight(ranks):
        sorted_ranks = sorted(ranks)
        if sorted_ranks == list(range(sorted_ranks[0], sorted_ranks[0] + 5)):
            return True
        if sorted_ranks == [2, 3, 4, 5, 14]:
            return True
        return False

class PokerGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Texas Hold'em Poker")
        self.root.geometry("1000x700")
        self.root.configure(bg="#1a1a2e")

        self.deck = Deck()
        self.player_hand = []
        self.dealer_hand = []
        self.community_cards = []
        self.player_chips = 1000
        self.dealer_chips = 1000
        self.pot = 0
        self.current_bet = 0
        self.game_phase = "preflop"

        self.setup_ui()
        self.start_new_round()

    def setup_ui(self):
        self.title_font = font.Font(family="Arial", size=24, weight="bold")
        self.card_font = font.Font(family="Arial", size=18, weight="bold")
        self.normal_font = font.Font(family="Arial", size=12)

        self.info_frame = tk.Frame(self.root, bg="#1a1a2e")
        self.info_frame.pack(pady=10)

        self.pot_label = tk.Label(self.info_frame, text="Pot: $0", font=self.title_font, 
                                  fg="#ffd700", bg="#1a1a2e")
        self.pot_label.pack()

        self.dealer_frame = tk.Frame(self.root, bg="#1a1a2e")
        self.dealer_frame.pack(pady=20)

        tk.Label(self.dealer_frame, text="DEALER", font=self.normal_font, 
                 fg="#e94560", bg="#1a1a2e").pack()

        self.dealer_chips_label = tk.Label(self.dealer_frame, text="Chips: $1000", 
                                           font=self.normal_font, fg="#ffd700", bg="#1a1a2e")
        self.dealer_chips_label.pack()

        self.dealer_cards_frame = tk.Frame(self.dealer_frame, bg="#1a1a2e")
        self.dealer_cards_frame.pack(pady=10)

        self.community_frame = tk.Frame(self.root, bg="#1a1a2e")
        self.community_frame.pack(pady=20)

        tk.Label(self.community_frame, text="COMMUNITY CARDS", font=self.normal_font,
                 fg="#0f3460", bg="#1a1a2e").pack()

        self.community_cards_frame = tk.Frame(self.community_frame, bg="#1a1a2e")
        self.community_cards_frame.pack(pady=10)

        self.player_frame = tk.Frame(self.root, bg="#1a1a2e")
        self.player_frame.pack(pady=20)

        tk.Label(self.player_frame, text="YOUR HAND", font=self.normal_font,
                 fg="#16213e", bg="#1a1a2e").pack()

        self.player_chips_label = tk.Label(self.player_frame, text="Chips: $1000",
                                           font=self.normal_font, fg="#ffd700", bg="#1a1a2e")
        self.player_chips_label.pack()

        self.player_cards_frame = tk.Frame(self.player_frame, bg="#1a1a2e")
        self.player_cards_frame.pack(pady=10)

        self.bet_frame = tk.Frame(self.root, bg="#1a1a2e")
        self.bet_frame.pack(pady=20)

        self.bet_entry = tk.Entry(self.bet_frame, font=self.normal_font, width=10)
        self.bet_entry.pack(side=tk.LEFT, padx=5)

        self.bet_button = tk.Button(self.bet_frame, text="Bet", font=self.normal_font,
                                     bg="#e94560", fg="white", command=self.player_bet,
                                     width=10)
        self.bet_button.pack(side=tk.LEFT, padx=5)

        self.call_button = tk.Button(self.bet_frame, text="Call", font=self.normal_font,
                                      bg="#0f3460", fg="white", command=self.player_call,
                                      width=10)
        self.call_button.pack(side=tk.LEFT, padx=5)

        self.fold_button = tk.Button(self.bet_frame, text="Fold", font=self.normal_font,
                                     bg="#16213e", fg="white", command=self.player_fold,
                                     width=10)
        self.fold_button.pack(side=tk.LEFT, padx=5)

        self.check_button = tk.Button(self.bet_frame, text="Check", font=self.normal_font,
                                      bg="#1a1a2e", fg="white", command=self.player_check,
                                      width=10)
        self.check_button.pack(side=tk.LEFT, padx=5)

        self.phase_label = tk.Label(self.root, text="Phase: Pre-Flop", font=self.normal_font,
                                    fg="#ffffff", bg="#1a1a2e")
        self.phase_label.pack(pady=10)

        self.message_label = tk.Label(self.root, text="Place your bet!", font=self.normal_font,
                                      fg="#00ff88", bg="#1a1a2e")
        self.message_label.pack(pady=5)

    def create_card_widget(self, card, hidden=False):
        card_frame = tk.Frame(self.root, bg="white", width=70, height=100, relief="raised", bd=2)
        card_frame.pack_propagate(False)

        if hidden:
            tk.Label(card_frame, text="🂠", font=("Segoe UI Symbol", 40), bg="#1a1a2e", fg="#e94560").pack(expand=True)
            card_frame.configure(bg="#1a1a2e")
        else:
            color = "#e94560" if card.suit in [Suit.HEARTS, Suit.DIAMONDS] else "#16213e"
            tk.Label(card_frame, text=card.rank.symbol, font=self.card_font, 
                     fg=color, bg="white").pack(pady=2)
            tk.Label(card_frame, text=card.suit.value, font=("Segoe UI Symbol", 30),
                     fg=color, bg="white").pack(expand=True)

        return card_frame

    def update_display(self):
        for widget in self.dealer_cards_frame.winfo_children():
            widget.destroy()
        for widget in self.community_cards_frame.winfo_children():
            widget.destroy()
        for widget in self.player_cards_frame.winfo_children():
            widget.destroy()

        show_dealer_cards = self.game_phase == "showdown"

        for card in self.dealer_hand:
            card_widget = self.create_card_widget(card, hidden=not show_dealer_cards)
            card_widget.pack(side=tk.LEFT, padx=5)

        for card in self.community_cards:
            card_widget = self.create_card_widget(card)
            card_widget.pack(side=tk.LEFT, padx=5)

        for card in self.player_hand:
            card_widget = self.create_card_widget(card)
            card_widget.pack(side=tk.LEFT, padx=5)

        self.pot_label.config(text=f"Pot: ${self.pot}")
        self.player_chips_label.config(text=f"Chips: ${self.player_chips}")
        self.dealer_chips_label.config(text=f"Chips: ${self.dealer_chips}")
        self.phase_label.config(text=f"Phase: {self.game_phase.replace('_', ' ').title()}")

    def start_new_round(self):
        if self.player_chips <= 0:
            messagebox.showinfo("Game Over", "You're out of chips! Game Over.")
            self.root.quit()
            return
        if self.dealer_chips <= 0:
            messagebox.showinfo("Congratulations", "You won! The dealer is out of chips!")
            self.root.quit()
            return

        self.deck.reset()
        self.player_hand = [self.deck.deal(), self.deck.deal()]
        self.dealer_hand = [self.deck.deal(), self.deck.deal()]
        self.community_cards = []
        self.pot = 0
        self.current_bet = 0
        self.game_phase = "preflop"

        blind = 10
        self.player_chips -= blind
        self.dealer_chips -= blind
        self.pot = blind * 2

        self.update_display()
        self.message_label.config(text="Place your bet or check!")

    def player_bet(self):
        try:
            bet_amount = int(self.bet_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number")
            return

        if bet_amount <= 0:
            messagebox.showerror("Error", "Bet must be positive")
            return
        if bet_amount > self.player_chips:
            messagebox.showerror("Error", "Not enough chips")
            return

        self.player_chips -= bet_amount
        self.pot += bet_amount
        self.current_bet = bet_amount
        self.update_display()
        self.dealer_action()

    def player_call(self):
        call_amount = self.current_bet
        if call_amount > self.player_chips:
            messagebox.showerror("Error", "Not enough chips to call")
            return

        self.player_chips -= call_amount
        self.pot += call_amount
        self.update_display()
        self.advance_phase()

    def player_fold(self):
        self.message_label.config(text="You folded. Dealer wins!")
        self.dealer_chips += self.pot
        self.pot = 0
        self.update_display()
        self.root.after(2000, self.start_new_round)

    def player_check(self):
        if self.current_bet > 0:
            messagebox.showerror("Error", "Cannot check when there's a bet")
            return
        self.update_display()
        self.dealer_action()

    def dealer_action(self):
        dealer_cards = self.dealer_hand + self.community_cards
        hand_rank, _ = HandEvaluator.evaluate(dealer_cards)

        strength = hand_rank.numeric_value

        if strength >= 4:
            action = "raise"
        elif strength >= 2:
            action = "call" if self.current_bet > 0 else "check"
        else:
            if self.current_bet > 50:
                action = "fold"
            elif self.current_bet > 0:
                action = "call"
            else:
                action = "check"

        if action == "raise":
            raise_amount = min(self.current_bet + random.randint(20, 100), self.dealer_chips)
            self.dealer_chips -= raise_amount
            self.pot += raise_amount
            self.current_bet = raise_amount
            self.message_label.config(text=f"Dealer raises ${raise_amount}!")
        elif action == "call":
            call_amount = min(self.current_bet, self.dealer_chips)
            self.dealer_chips -= call_amount
            self.pot += call_amount
            self.message_label.config(text=f"Dealer calls ${call_amount}!")
        elif action == "check":
            self.message_label.config(text="Dealer checks.")
        elif action == "fold":
            self.message_label.config(text="Dealer folds! You win!")
            self.player_chips += self.pot
            self.pot = 0
            self.update_display()
            self.root.after(2000, self.start_new_round)
            return

        self.update_display()
        self.advance_phase()

    def advance_phase(self):
        phases = ["preflop", "flop", "turn", "river", "showdown"]
        current_index = phases.index(self.game_phase)

        if self.game_phase == "preflop":
            self.community_cards = [self.deck.deal() for _ in range(3)]
            self.game_phase = "flop"
        elif self.game_phase == "flop":
            self.community_cards.append(self.deck.deal())
            self.game_phase = "turn"
        elif self.game_phase == "turn":
            self.community_cards.append(self.deck.deal())
            self.game_phase = "river"
        elif self.game_phase == "river":
            self.game_phase = "showdown"
            self.determine_winner()
            return

        self.current_bet = 0
        self.update_display()
        self.message_label.config(text="Your turn!")

    def determine_winner(self):
        player_cards = self.player_hand + self.community_cards
        dealer_cards = self.dealer_hand + self.community_cards

        player_rank, player_best = HandEvaluator.evaluate(player_cards)
        dealer_rank, dealer_best = HandEvaluator.evaluate(dealer_cards)

        self.update_display()

        if player_rank.numeric_value > dealer_rank.numeric_value:
            winner = "player"
            self.message_label.config(text=f"You win with {player_rank.display_name}!")
            self.player_chips += self.pot
        elif dealer_rank.numeric_value > player_rank.numeric_value:
            winner = "dealer"
            self.message_label.config(text=f"Dealer wins with {dealer_rank.display_name}!")
            self.dealer_chips += self.pot
        else:
            self.message_label.config(text="It's a tie! Pot split.")
            self.player_chips += self.pot // 2
            self.dealer_chips += self.pot // 2

        self.pot = 0
        self.update_display()
        self.root.after(3000, self.start_new_round)

if __name__ == "__main__":
    root = tk.Tk()
    game = PokerGame(root)
    root.mainloop()
