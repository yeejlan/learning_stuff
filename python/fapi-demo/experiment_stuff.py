
from core.querybuilder import QueryBuilder


q = [
    ['SELECT * FROM users'],
    ['WHERE id = ? AND name = ?', (1, 'nana')],
]

sql, args = QueryBuilder.build_from_list(q)

print(sql)   # Output: SELECT * FROM users WHERE id = ? AND name = ?
print(args)  # Output: (1, 'nana')