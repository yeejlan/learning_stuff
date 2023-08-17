from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

class QueryBuilderException(Exception):
    pass

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
    _join_parts: list = field(default_factory=list)
    _where_parts: list = field(default_factory=list)
    _groupby_parts: list = field(default_factory=list)
    _having_parts: list = field(default_factory=list)
    _order_parts: list = field(default_factory=list)
    _union_parts: list = field(default_factory=list)
    _unionorder_parts: list = field(default_factory=list)

    def table(self, table: str):
        self._table_parts = table
        return self
    
    def select(self, columns: str|list):
        self._kind = QueryKind.select
        t = type(columns)
        if t == list:
            self._select_parts.extend(columns)
        elif t == str:
            self._select_parts.append(columns)
        else:
            raise QueryBuilderException('select params not supported')
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
    
    def where(self, field: str, op=None, value=None, bool_op: str = 'and'):
        if op is None and value is None: #raw query
            self._where_parts.append((field, 'raw', [], bool_op))
        elif value is None:
            self._where_parts.append((field, '=', op, bool_op))
        else: 
            self._where_parts.append((field, op, value, bool_op))
            
        return self


    def where_or(self, field: str, op=None, value=None, bool_op: str = 'or'):
        self.where(field, op, value, bool_op)
        return self

    def where_raw(self, query: str, values: list = [], bool_op: str = 'and'):
        self.where(query, 'raw', values, bool_op)
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

    def _build_select(self):
        if not self._table_parts:
            raise QueryBuilderException('table is missing')
        
        fields = ', '.join(self._select_parts) if self._select_parts else '*'
        query = f'SELECT {fields} FROM {self._table_parts}'
        self._parts.append(query)
        return self

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

    def build(self):
        (self
            ._build_select()
            ._build_join()
            ._build_where()
        )

        return ' '.join(self._parts), self._bindings
    
    def build_fake_sql(self):
        pass


if __name__ == "__main__":
    qb = QueryBuilder()
    q = (qb
        .table('users as u') 
        .join('user_ext as e', 'e.uid = u.user_id')
        .select(['id', 'name'])
        .select("created_at")
        .where('id', 1) 
        .where("aBcD=123") 
        .where('cc', 2)
        .where_between('age', 12, 20)
        .where_in('pet', ['dog', 'cat'])
        .where_null('haha')
        .where_or('dd', '>=', 15)
    )

    query, values = q.build()

    print(query) 
    print(values)
