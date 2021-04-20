import os
import random
import barnum
from randomtimestamp import randomtimestamp
# import time
# from geopy.geocoders import Nominatim


class Account:
    def __init__(self, account_id, bank_name, geolocator=None):
        self.account_id = account_id
        self.account_type = 'personal'
        self.bank_name = bank_name
        self.identification = [
            random.randint(452358123, 973821648),
            ' '.join(barnum.create_name()),
            barnum.create_birthday(18, 80)
        ]
        zipcode, city, state = barnum.create_city_state_zip()
        # location = geolocator.geocode({
        #     'postalcode': zipcode,
        #     'countryRegion': 'United States'
        # })
        self.location = (
            zipcode,
            city,
            state,
            0,  # location.longitude,
            0,  # location.latitude
        )
        self.card = barnum.create_cc_number()
        self.phone = barnum.create_phone()


if __name__ == '__main__':
    bank_names = [barnum.create_nouns().title() + ' Bank' for _ in range(10)]
    compromiseable_attributes = ['identification', 'phone', 'location']

    accounts = {}
    compromised_account_ids = set()
    # geolocator = Nominatim(user_agent='fraud-detection-data-generator')
    for _ in range(10000):
        account_id = hex(random.getrandbits(64))[2:]
        try:
            account = Account(
                account_id,
                random.choice(bank_names),
                # geolocator
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
        try:
            account = Account(
                account_id,
                random.choice(bank_names),
                # geolocator
            )
        except Exception:
            continue

        account.account_type = 'business'
        account.identification[1] = barnum.create_company_name()
        business_accounts[account_id] = account

    accounts = list(accounts.values())
    business_accounts = list(business_accounts.values())
    transactions = []
    for _ in range(10000):
        account = random.choice(accounts)
        business_account = random.choice(business_accounts)
        transaction_id = hex(random.getrandbits(64))[2:]
        timestamp = randomtimestamp(start_year=2020)
        if random.random() < 0.001:
            amount = random.gauss(10000, 3000)
        elif random.random() < 0.01:
            amount = random.gauss(3000, 1000)
        else:
            amount = random.gauss(100, 30) * random.lognormvariate(0, 2)

        transactions.append((
            transaction_id,
            account.card[1][0],
            business_account.card[1][0],
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
            'longitude,'
            'latitude,'
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
