import re

paragraph = 'Сх 81 зарядить АКБ  - мойка'
scheme_number = re.search("Сх ", paragraph)
print(paragraph.split()[1])