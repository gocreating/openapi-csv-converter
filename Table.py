import csv

BASE_DIR = 'build'

class Table():
    def __init__(self, table_name, columns):
        self.table_name = table_name
        self.columns = [column.strip() for column in columns.split(',')]
        self.rows = []
        self.auto_increment_number = 0

    def find(self, **kwargs):
        rows = []
        for row in self.rows:
            dict_row = self.toDict(row)
            matched = all(dict_row[find_name] == find_value for find_name, find_value in kwargs.items())
            if matched:
                rows.append(row)
        return rows

    def findDict(self, **kwargs):
        return [self.toDict(row) for row in self.find(**kwargs)]

    def findById(self, id):
        for row in self.rows:
            if row[0] == id:
                return row

    def findDictById(self, id):
        row = self.findById(id)
        return self.toDict(row)

    def toDict(self, row):
        d = {}
        for i in range(len(self.columns)):
            column_name = self.columns[i]
            d[column_name] = row[i]
        return d

    def add(self, **kwargs):
        row = [kwargs.get(self.columns[i]) for i in range(len(self.columns))]
        if kwargs.get('id') is None:
            row[0] = self.auto_increment_number
        self.rows.append(row)
        self.auto_increment_number += 1
        return row[0]

    def load(self):
        with open(f'{BASE_DIR}/{self.table_name}.csv', 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            next(reader) # skip header
            self.rows = [row for row in reader]

    def persist(self):
        with open(f'{BASE_DIR}/{self.table_name}.csv', 'w', newline='') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerow(self.columns)
            writer.writerows(self.rows)