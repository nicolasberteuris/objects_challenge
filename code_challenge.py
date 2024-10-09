import re
import uuid

class UsernameException(Exception):
    pass

class PaymentException(Exception):
    pass

class CreditCardException(Exception):
    pass

class Payment:
    def __init__(self, amount, actor, target, note):
        self.id = str(uuid.uuid4())
        self.amount = float(amount)
        self.actor = actor
        self.target = target
        self.note = note
        print(f"Payment created: {actor.username} paid {target.username} ${amount:.2f} for {note}")

class User:
    def __init__(self, username):
        self.credit_card_number = None
        self.balance = 0.0
        self.friends = []

        if self._is_valid_username(username):
            self.username = username
            print(f"User created: {username}")
        else:
            raise UsernameException('Username not valid.')

    def retrieve_feed(self):
        print(f"Retrieving feed for {self.username}")
        for payment in MiniVenmo.feed:
            print(f"este es mi payment {payment.note}")
        payments_feed = [
            f"{payment.actor.username} paid {payment.target.username} ${payment.amount:.2f} for {payment.note}"
            for payment in MiniVenmo.feed if payment.actor == self or payment.target == self
        ]
        friends_feed = [f"{self.username} and {friend.username} are now friends." for friend in self.friends]
        return payments_feed + friends_feed

    def add_friend(self, new_friend):
        if new_friend not in self.friends and new_friend != self:
            self.friends.append(new_friend)
            MiniVenmo.feed.append(f"{self.username} and {new_friend.username} are now friends.")
            print(f"{self.username} and {new_friend.username} are now friends.")
        else:
            print(f"Cannot add the same friend twice or yourself: {new_friend.username}")
            raise Exception('Cannot add the same friend twice or yourself.')

    def add_to_balance(self, amount):
        self.balance += float(amount)
        print(f"Added ${amount:.2f} to {self.username}'s balance. New balance: ${self.balance:.2f}")

    def add_credit_card(self, credit_card_number):
        if self.credit_card_number is not None:
            raise CreditCardException('Only one credit card per user!')

        if self._is_valid_credit_card(credit_card_number):
            self.credit_card_number = credit_card_number
            print(f"Credit card added for {self.username}")
        else:
            raise CreditCardException('Invalid credit card number.')

    def pay(self, target, amount, note):
        print(f"{self.username} is attempting to pay {target.username} ${amount:.2f} for {note}")
        amount = float(amount)

        if self.username == target.username:
            raise PaymentException('User cannot pay themselves.')

        elif amount <= 0.0:
            raise PaymentException('Amount must be a positive number.')

        if self.balance >= amount:
            payment = self.pay_with_balance(target, amount, note)
        else:
            payment = self.pay_with_card(target, amount, note)

        MiniVenmo.feed.append(payment)
        return payment

    def pay_with_card(self, target, amount, note):
        amount = float(amount)

        if self.credit_card_number is None:
            raise PaymentException('Must have a credit card to make a payment.')

        self._charge_credit_card(self.credit_card_number)
        print(f"{self.username}'s credit card was charged ${amount:.2f}")
        payment = Payment(amount, self, target, note)
        target.add_to_balance(amount)
        return payment

    def pay_with_balance(self, target, amount, note):
        self.balance -= amount
        print(f"{self.username}'s balance decreased by ${amount:.2f}. New balance: ${self.balance:.2f}")
        payment = Payment(amount, self, target, note)
        target.add_to_balance(amount)
        return payment

    def _is_valid_credit_card(self, credit_card_number):
        return credit_card_number in ["4111111111111111", "4242424242424242"]

    def _is_valid_username(self, username):
        return re.match('^[A-Za-z0-9_\\-]{4,15}$', username)

    def _charge_credit_card(self, credit_card_number):
        print(f"Charging credit card {credit_card_number} for {self.username}")

class MiniVenmo:
    feed = []

    def __init__(self):
        self.users = []

    def create_user(self, username, balance, credit_card_number):
        print(f"Creating user: {username}")
        new_user = User(username)
        new_user.add_to_balance(balance)
        new_user.add_credit_card(credit_card_number)
        self.users.append(new_user)
        return new_user

    def render_feed(self, feed):
        print("Rendering feed:")
        for entry in feed:
            if isinstance(entry, Payment):
                print(f"{entry.actor.username} paid {entry.target.username} ${entry.amount:.2f} for {entry.note}")
            else:
                print(entry)

    @classmethod
    def run(cls):
        print("Starting MiniVenmo")
        venmo = cls()
        bobby = venmo.create_user("Bobby", 5.00, "4111111111111111")
        carol = venmo.create_user("Carol", 10.00, "4242424242424242")

        try:
            bobby.pay(carol, 5.00, "Coffee")
            carol.pay(bobby, 15.00, "Lunch")
        except PaymentException as e:
            print(f"Payment error: {e}")

        feed = bobby.retrieve_feed()
        venmo.render_feed(feed)

        bobby.add_friend(carol)

if __name__ == '__main__':
    MiniVenmo.run()




