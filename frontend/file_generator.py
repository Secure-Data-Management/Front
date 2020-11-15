import csv
from pathlib import Path
from random import randrange
import datetime
import os

names = ['Michael', 'Jones', 'Williams', 'John', 'Rose', 'Daniel', 'Jonathan', 'Donald', 'Julia', 'Stephanie', 'Karl', 'Laura']
banks = ['ABN AMRO', 'Rabobank', 'ING', 'bunq', 'SNS Bank']
fieldnames = ['transaction_type', 'destination', 'transaction', 'transaction_date', 'bank']


def random_date():
    # This function will return a random datetime between two datetime

    start_date = datetime.date(2000, 1, 1)
    end_date = datetime.date(2020, 1, 1)

    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = randrange(days_between_dates)
    random_date = start_date + datetime.timedelta(days=random_number_of_days)
    return random_date


def generate_record(filename, amount_transaction_max=1000):
    with open("./frontend/data_user/" + filename + ".csv", 'w') as new_file:
        # Generate csv file with the following fields corresponding to the record of a client

        csv_writer = csv.DictWriter(new_file, delimiter='\t', fieldnames=fieldnames)

        csv_writer.writeheader()

        amount_transaction = randrange(amount_transaction_max)

        n_name = randrange(len(names))  # Random destination
        transaction = randrange(amount_transaction)  # Random amount of transaction
        n_bank = randrange(len(banks))  # Random choice of bank
        b = randrange(2)  # Credit or Debit
        if b:
            transaction_type = 'Credit'
        else:
            transaction_type = 'Debit'
        csv_writer.writerow({'transaction_type': transaction_type, 'destination': names[n_name], 'transaction': transaction, 'transaction_date': random_date(), 'bank': banks[n_bank]})


def get_keywords(filename: str):  # return keywords from a specific file
    with open("./frontend/data_user/" + filename + ".csv", 'r') as f:
        reader = csv.DictReader(f, delimiter='\t', fieldnames=fieldnames)
        keywords = []
        next(reader, None)
        for row in reader:
            for keyword_type in fieldnames:
                keywords.append(row[keyword_type]) if row[keyword_type] not in keywords else keywords
    with open("./frontend/data_user/" + filename + "_keywords.csv", 'w') as new_file:
        writer = csv.writer(new_file, delimiter=',')
        writer.writerow(keywords)

    return keywords


def generate_files():  # each file contains one transaction
    path = Path('./frontend/data_user')
    path.mkdir(parents=True)
    filename = 'File'
    generate_record(filename)
    print(str(filename) + ".csv generated")
    get_keywords(filename)
    print(str(filename) + "_keywords.csv generated")

