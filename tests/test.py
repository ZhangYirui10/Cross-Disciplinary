with open('../data/field.txt', 'r') as field_fin:
    for line in field_fin:
        row = line.strip().split('\t')
        print(row)