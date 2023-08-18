from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Tuple
import re

import db

class QueryKind(StrEnum):
    unset = "unset"
    select = "select"
    insert = "insert"
    update = "update"

@dataclass
class QueryBuilder:
    _kind: QueryKind = QueryKind.unset
    _parts: list = field(default_factory=list)  #statement parts
    _bindings: list = field(default_factory=list)  #statement bindings

    _table_parts: str = ''
    _select_parts: list = field(default_factory=list) 
    _update_parts: list = field(default_factory=list)
    _join_parts: list = field(default_factory=list)
    _where_parts: list = field(default_factory=list)
    _groupby_parts: list = field(default_factory=list)
    _having_parts: list = field(default_factory=list)
    _orderby_parts: list = field(default_factory=list)
    _extra_parts: list = field(default_factory=list)
    _union_parts: list = field(default_factory=list)

    @classmethod
    def new(cls):
        return cls()

    def table(self, table: str):
        self._table_parts = table
        return self
    
    def select(self, columns: str|list):
        self._kind = QueryKind.select
        t = type(columns)
        if t == list:
            self._select_parts.extend(columns)
        else:
            self._select_parts.append(columns)

        return self

    def update(self, field: str, value: Any = []):
        query = f'SET {field} = %s'
        self.update_raw(query, value)
        return self

    def update_raw(self, query: str, value:Any = []):
        self._kind = QueryKind.update
        if type(value) != list:
            value = [value]
        self._update_parts.append((query, value))
        return self        

    def join(self, table: str, on: str, op='join'):
        self._join_parts.append((table, on, op))
        return self

    def leftjoin(self, table: str, on: str, op='left join'):
        self._join_parts.append((table, on, op))
        return self

    def rightjoin(self, table: str, on: str, op='right join'):
        self._join_parts.append((table, on, op))
        return self        
    
    def where(self, field: str, op: Any='raw', value: Any=[], bool_op: str = 'and'):
        if op == 'raw': #raw query
            self._where_parts.append((field, 'raw', value, bool_op))
        elif value == []:
            self._where_parts.append((field, '=', op, bool_op))
        else: 
            self._where_parts.append((field, op, value, bool_op))
            
        return self


    def where_or(self, field: str, op='raw', value: Any=[], bool_op: str = 'or'):
        self.where(field, op, value, bool_op)
        return self

    def where_raw(self, query: str, value: Any=[], bool_op: str = 'and'):
        if type(value) != list:
            value = [value]
        self.where(query, 'raw', value, bool_op)
        return self

    def where_in(self, field: str, values, bool_op = 'and'):
        query = f'{field} IN ('
        query += ', '.join(['%s'] * len(values))
        query += ')'
        self.where_raw(query, values, bool_op)
        return self

    def where_not_in(self, field: str, values, bool_op = 'and'):
        query = f'{field} NOT IN ('
        query += ', '.join(['%s'] * len(values))
        query += ')'
        self.where_raw(query, values, bool_op)
        return self        

    def where_null(self, field: str, bool_op = 'and'):
        self.where_raw(field + ' IS NULL', [], bool_op)
        return self

    def where_not_null(self, field: str, bool_op = 'and'):
        self.where_raw(field + ' IS NOT NULL', [], bool_op)
        return self

    def where_between(self, field: str, value1: Any, value2: Any, bool_op = 'and'):
        self.where_raw(field + ' BETWEEN %s AND %s', [value1, value2], bool_op)
        return self

    def where_not_between(self, field: str, value1: Any, value2: Any, bool_op = 'and'):
        self.where_raw(field + ' NOT BETWEEN %s AND %s', [value1, value2], bool_op)
        return self

    def union(self, query: str, values: list = [], op = 'union'):
        self._union_parts.append((query, values, op))
        return self

    def union_all(self, query: str, values: list = [], op = 'union all'):
        self._union_parts.append((query, values, op))
        return self

    def group_by(self, query: str|list):
        t = type(query)
        if t == list:
            self._groupby_parts.extend(query)
        else:
            self._groupby_parts.append(query)
        return self

    def having(self, query: str, value: Any = [], bool_op: str = 'and'):
        if type(value) != list:
            value = [value]
        self._having_parts.append((query, value, bool_op))
        return self

    def order_by(self, query: str|list):
        t = type(query)
        if t == list:
            self._orderby_parts.extend(query)
        else:
            self._orderby_parts.append(query)
        return self

    def order_by_rand(self):
        self.order_by('RAND()')
        return self
    
    def limit(self, num: int):
        query = f'LIMIT {num}'
        self._extra_parts.append(query)
        return self

    def offset(self, num: int):
        query = f'OFFSET {num}'
        self._extra_parts.append(query)
        return self

    def _build_select(self):
        if self._kind != QueryKind.select:
            return self      
        fields = ', '.join(self._select_parts) if self._select_parts else '*'
        query = f'SELECT {fields} FROM {self._table_parts}'
        self._parts.append(query)
        return self

    def _build_update(self):
        if self._kind != QueryKind.update:
            return self
        if not self._update_parts:
            return self
        query = ''
        is_first = True
        for part, values in self._update_parts:
            if is_first:
                is_first = False
                query += f'UPDATE {self._table_parts} {part}'
            else:
                query += f', {part}'
            self._bindings.extend(values)

        self._parts.append(query)
        return self;

    def _build_join(self):
        if not self._join_parts:
            return self
        for table, on, op in self._join_parts:
            query = f'{op.upper()} {table} ON {on}'
            self._parts.append(query)
        return self

    def _build_where(self):
        if not self._where_parts:
            self._parts.append('WHERE 1')
        if self._where_parts:
            query = ''
            is_first = True
            for column, op, value, bool_op in self._where_parts:
                part = ''
                if op == 'raw': #raw query
                    part = column
                    self._bindings.extend(value)
                else:
                    part = f'{column} {op} %s'
                    self._bindings.append(value)

                if is_first:
                    is_first = False
                    query += f'WHERE {part}'
                else:
                    query += f' {bool_op.upper()} {part}'
            self._parts.append(query)

        return self

    def _build_union(self):
        if not self._union_parts:
            return self
        for query, values, op in self._union_parts:
            query = f'{op.upper()} {query}'
            self._parts.append(query)
            self._bindings.extend(values)
        return self

    def _build_groupby(self):
        if not self._groupby_parts:
            return self
        query = 'GROUP BY ' + ', '.join(self._groupby_parts)
        self._parts.append(query)
        return self

    def _build_having(self):
        if not self._having_parts:
            return self

        query = ''
        is_first = True
        for part, values, bool_op in self._having_parts:
            if is_first:
                is_first = False
                query += f'HAVING {part}'
            else:
                query += f' {bool_op.upper()} {part}'
            self._bindings.extend(values)

        self._parts.append(query)

        return self

    def _build_orderby(self):
        if not self._orderby_parts:
            return self
        query = 'ORDER BY ' + ', '.join(self._orderby_parts)
        self._parts.append(query)
        return self

    def _build_extra(self):
        if not self._extra_parts:
            return self
        query = ' '.join(self._extra_parts)
        self._parts.append(query)
        return self

    def build(self) -> Tuple[str, list]:
        self._parts = []
        self._bindings = []
        (self
            ._build_select()
            ._build_update()
            ._build_join()
            ._build_where()
            ._build_groupby()
            ._build_having()
            ._build_orderby()
            ._build_extra()
            ._build_union() #stay at bottom
        )

        return ' '.join(self._parts), self._bindings

    def dump_build(self):
        p, v = self.build()
        print(p)
        print(v)
        return self
    

    def build_fake_sql(self) -> str:
        escapes = {
            "'" : "\\'",
            "\\" : "\\\\"
        }

        def escape_string(value):
            escaped = []
            for char in value:
                if char in escapes:
                    escaped.append(escapes[char])
                else:
                    escaped.append(char)
            return "".join(escaped)

        def quote_str(value):
            if isinstance(value, str):
                return f"'{escape_string(value)}'"
            return str(value)

        query, values = self.build()
        query = re.sub(r'%s', lambda x: quote_str(values.pop(0)), query)
        return query

    def dump_fake_sql(self):
        s = self.build_fake_sql()
        print(s)
        return self        

    async def get_one(self, to: Any, pool_fn = db.get_pool):
        query, values = self.build()
        res = await db.select_one(query, *values, pool_fn=pool_fn, to=to)
        return res

    async def get_all(self, to: Any, pool_fn = db.get_pool):
        query, values = self.build()
        res = await db.select(query, *values, pool_fn=pool_fn, to=to)
        return res

if __name__ == "__main__":
    (QueryBuilder().new()
        .table('users as u') 
        .join('user_ext as e', 'e.uid = u.user_id')
        .select(['id', 'name'])
        .select("created_at")
        .where('u.id', 1) 
        .where("aBcD=123") 
        .where_raw('FGHI=%s', 'BNMV')
        .where('type', '<>', 'bid')
        .where_between('age', 12, 20)
        .where_in('pet', ['dog', 'cat', 'bird'])
        .where_null('note')
        .where_or('dd', '>=', 15)
        .group_by(['age', 'score'])
        .having('avg(age) > %s', 10)
        .having('sum(age) < %s', [10000])
        # .order_by_rand()
        .order_by('age desc')
        .order_by(['score desc', 'create_at desc'])
        .offset(99)
        .limit(20)
        .union("select * from my_ext_users where my_uid=%s and tag=%s", [890, 'ext_user'])
        .dump_build()
        .dump_fake_sql()
        .build()
    )
    print('----update----')
    (QueryBuilder().new()
        .table('users')
        .update('notes', 'my notes')
        .update('score', 50)
        .update_raw('set age = %s', 22)
        .where('id', 123)
        .limit(1)
        .dump_build()
        .dump_fake_sql()
        .build()
    )


