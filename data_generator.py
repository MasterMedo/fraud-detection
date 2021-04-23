import os
import random
import barnum
import geopy
from datetime import datetime


class Account:
    def __init__(self, account_id, bank_name, coordinates):
        self.account_id = account_id
        self.account_type = 'personal'
        self.bank_name = bank_name
        self.identification = [
            hex(random.getrandbits(64))[2:],
            ' '.join(barnum.create_name()),
            float(barnum.create_birthday(18, 80))
        ]

        zipcode, city, state = barnum.create_city_state_zip()
        longitude, latitude = coordinates[zipcode]
        longitude += random.random() / 5 * 2 - 0.2
        latitude += random.random() / 5 * 2 - 0.2
        self.location = (
            zipcode,
            city,
            state,
            longitude,
            latitude
        )
        self.card = barnum.create_cc_number()
        self.phone = barnum.create_phone()


if __name__ == '__main__':
    bank_names = [barnum.create_nouns().title() + ' Bank' for _ in range(10)]
    compromiseable_attributes = ['identification', 'phone', 'location']
    with open('zip-codes.txt') as f:
        lines = [line.split(',') for line in f]
        coordinates = {
            row[0][1:-1]: (float(row[1][1:-1]), float(row[2][1:-1]))
            for row in lines
            if row[1] and row[2]
        }

    accounts = {}
    compromised_account_ids = set()
    for _ in range(1000):
        account_id = hex(random.getrandbits(64))[2:]
        try:
            account = Account(
                account_id,
                random.choice(bank_names),
                coordinates
            )
        except Exception:
            continue

        if compromised_account_ids and random.random() < 0.05:
            attribute = random.choice(compromiseable_attributes)
            compromised_id = random.choice(list(compromised_account_ids))
            compromised_account = accounts[compromised_id]
            compromised_attribute = getattr(compromised_account, attribute)
            setattr(account, attribute, compromised_attribute)

        if accounts and random.random() < 0.05:
            compromised_account_ids.add(random.choice(list(accounts.keys())))

        accounts[account_id] = account

    business_accounts = {}
    for _ in range(100):
        account_id = hex(random.getrandbits(64))[2:]
        if account_id in accounts:
            continue
        try:
            account = Account(
                account_id,
                random.choice(bank_names),
                coordinates
            )
        except Exception:
            continue

        account.account_type = 'business'
        account.identification[1] = barnum.create_company_name()
        business_accounts[account_id] = account

    accounts = list(accounts.values())
    business_accounts = list(business_accounts.values())
    transactions = []
    while len(transactions) != 10000:
        person = random.choice(accounts)
        business = random.choice(business_accounts)
        if (
            geopy.distance.distance(
                (person.longitude, person.latitude),
                (business.longitude, business.latitude)).km < 400
            or random.random() < 0.99
        ):
            continue
        transaction_id = hex(random.getrandbits(64))[2:]
        timestamp = random.uniform(datetime.now() - 2678400, datetime.now())
        if random.random() < 0.001:
            amount = random.gauss(10000, 3000)
        elif random.random() < 0.01:
            amount = random.gauss(3000, 1000)
        else:
            amount = random.gauss(100, 30) * random.lognormvariate(0, 2)

        transactions.append((
            transaction_id,
            person.card[1][0],
            business.card[1][0],
            timestamp,
            round(amount, 2)
        ))

    dirname = os.path.dirname(os.path.realpath(__file__))
    with open(dirname + '/accounts.csv', 'w') as f:
        print(
            'account_id,'
            'account_type,'
            'bank_name,'
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
                    account.account_id,
                    account.account_type,
                    account.bank_name,
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
            'timestamp,'
            'amount',
            file=f
        )
        for transaction in transactions:
            print(
                ','.join(map(str, transaction)),
                file=f
            )
