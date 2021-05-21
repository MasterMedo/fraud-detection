"""Generates a dataset viable for fraud detection.

Assumes all accounts are a part of a single bank.
Creates B business accounts.
Creates P personal accounts 5 to 10 years old.
Creates T transactions 1 month old at most.

Accounts
    - id: str
    - created: float
    - identification: Identification
    - location: Location
    - phone number: Phone
    - credit card: CreditCard

Identification
    - id: str
    - name: str
    - birthday: float

Location
    - id: str
    - state: str
    - city: str
    - zipcode: str
    - latitude: float
    - longitude: float

Phone
    - id: str
    - number: str

Credit card
    - id: str
    - number: str
    - type: str

Transaction
    - id: str
    - amount: float
    - latitude: float
    - longitude: float
    - created: float
"""
import os
import random
import barnum
from collections import defaultdict
from functools import partial

B = 100
P = 1000
T = 10000


class Account:
    def __init__(self, type_, created, name, coordinates):
        self.id = get_random_id()
        self.type = type_
        self.created = created
        self.card = barnum.create_cc_number()
        self.phone = barnum.create_phone()
        self.identification = [
            get_random_id(),
            name,
            barnum.create_birthday(18, 80).toordinal()
        ]

        zipcode, city, state = barnum.create_city_state_zip()
        longitude, latitude = coordinates[zipcode]
        self.location = [
            zipcode,
            city,
            state,
            longitude,
            latitude
        ]


def get_random_id():
    global all_ids
    while (id_ := hex(random.getrandbits(64))[2:]) in all_ids:
        pass

    all_ids.add(id_)
    return id_


all_ids = set()
if __name__ == '__main__':
    with open('zip-codes.txt') as f:
        lines = [line.split(',') for line in f]
        coordinates = {
            row[0][1:-1]: (float(row[1][1:-1]), float(row[2][1:-1]))
            for row in lines
            if row[1] and row[2]
        }

    date_bank_created = barnum.create_birthday(5, 10).toordinal()
    business_accounts = []
    grid = defaultdict(list)
    # ########################## Business accounts ###########################
    while len(business_accounts) < B:
        try:
            account = Account(
                type_='business',
                created=date_bank_created,
                name=barnum.create_company_name(),
                coordinates=coordinates,
            )
        except Exception:  # barnum has internal bugs
            continue

        n = random.random()
        if n < 0.03:
            account.random_expense = partial(random.gauss, 10000, 3000)
        elif n < 0.1:
            account.random_expense = partial(random.gauss, 3000, 1000)
        elif n < 0.4:
            account.random_expense = partial(random.choice, [20, 30, 50, 100, 200, 500, 1000])
            account.identification[1] += ' ATM'
        else:
            account.random_expense = partial(random.gauss, 50, 30)
            account.identification[1] += random.choice(['Shop', 'Bar', 'Food', 'Store'])

        longitude, latitude = account.location[-2:]
        grid[
            int((longitude + 67) / 10),
            int((latitude - 25) / 5),
        ].append(len(business_accounts))
        business_accounts.append(account)

    current_time = date_bank_created
    accounts = []
    transactions = []
    compromised_indexes = []
    compromiseable_attributes = ['identification', 'phone', 'location']
    while len(transactions) < T:
        current_time += random.random() * date_bank_created / T
        # ######################### Personal Accounts ########################
        if len(accounts) < P and random.random() < 0.1:
            try:
                account = Account(
                    type_='personal',
                    created=current_time,
                    name=' '.join(barnum.create_name()),
                    coordinates=coordinates,
                )
            except Exception:  # barnum has internal bugs
                continue

            account.location = random.choice(business_accounts).location
            d = 0.4  # geographical coordinates maximal offset
            account.location[-1] += random.random()*d - d/2
            account.location[-2] += random.random()*d - d/2

            # modify created account with a compromised field
            if compromised_indexes and random.random() < 0.05:
                attribute = random.choice(compromiseable_attributes)
                compromised_index = random.choice(compromised_indexes)
                compromised_account = accounts[compromised_index]
                compromised_attribute = getattr(compromised_account, attribute)
                setattr(account, attribute, compromised_attribute)

            # compromise an account
            if accounts and random.random() < 0.05:
                compromised_indexes.append(random.randint(0, len(accounts)-1))

            accounts.append(account)

        # ######################### Transactions ############################
        if accounts and len(transactions) < T:
            person = random.choice(accounts)
            if random.random() < 0.995:
                longitude, latitude = person.location[-2:]
                longitude = int((longitude + 67) / 10)
                latitude = int((latitude - 25) / 5)
                if (longitude, latitude) not in grid:
                    continue

                business = business_accounts[random.choice(grid[
                    longitude,
                    latitude,
                ])]
            else:
                business = random.choice(business_accounts)

            transaction_id = get_random_id()
            created = current_time
            amount = abs(business.random_expense())

            transactions.append((
                transaction_id,
                person.card[1][0],
                business.card[1][0],
                created,
                round(amount, 2)
            ))

    dirname = os.path.dirname(os.path.realpath(__file__))
    with open(dirname + '/accounts.csv', 'w') as f:
        print(
            'account_id,'
            'account_type,'
            'created,'
            'identification_id,'
            'name,'
            'birthday,'
            'zipcode,'
            'city,'
            'state,'
            'latitude,'
            'longitude,'
            'card_type,'
            'card_number,'
            'phone',
            file=f
        )
        for account in accounts + business_accounts:
            print(
                ','.join(map(str, [
                    account.id,
                    account.type,
                    account.created,
                    *account.identification,
                    *account.location,
                    account.card[0],
                    account.card[1][0],
                    account.phone
                ])),
                file=f
            )

    with open(dirname + '/transactions.csv', 'w') as f:
        print(
            'id,'
            'from,'
            'to,'
            'created,'
            'amount',
            file=f
        )
        for transaction in transactions:
            print(
                ','.join(map(str, transaction)),
                file=f
            )
