import aiomysql
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Callable, Tuple, Union
import re
from datetime import datetime, timezone

from core import db_mysql
from core.time_util import now_as_mysql_datetime

class QueryKind(StrEnum):
    select = "select"
    insert = "insert"
    update = "update"
    delete = "delete"

@dataclass
class QueryBuilder:
    _kind: QueryKind = QueryKind.select
    _parts: list = field(default_factory=list)  #statement parts
    _bindings: list = field(default_factory=list)  #statement bindings

    _table_parts: str = ''
    _select_for_update = False
    _select_parts: list = field(default_factory=list)
    _update_parts: list = field(default_factory=list)
    _insert_parts: list = field(default_factory=list)
    _join_parts: list = field(default_factory=list)
    _where_parts: list = field(default_factory=list)
    _groupby_parts: list = field(default_factory=list)
    _having_parts: list = field(default_factory=list)
    _orderby_parts: list = field(default_factory=list)
    _extra_parts: list = field(default_factory=list)
    _union_parts: list = field(default_factory=list)

    _auto_insert_update_predefined_columns = True
    _predefined_columns_auto_updated = False

    _conn_or_pool: Any = None
    _map_to_model: Any = None

    @classmethod
    def new(cls):
        return cls()
    
    def set_conn_or_pool(self, conn_or_pool: Union[aiomysql.Connection, aiomysql.Pool]):
        self._conn_or_pool = conn_or_pool
        return self
    
    def get_conn_or_pool(self) -> Union[aiomysql.Connection, aiomysql.Pool]:
        return self._conn_or_pool
    
    def auto_insert_update_predefined_columns(self, enabled: bool = True):
        self._auto_insert_update_predefined_columns = enabled
        return self

    def map_query_to_model(self, model:Any):
        self._map_to_model = model
        return self

    def table(self, table: str):
        self._table_parts = table
        return self
    
    def lock_for_update(self):
        self._select_for_update = True
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
        query = f'{field} = %s'
        self.update_raw(query, value)
        return self

    def update_timestamp(self):
        now = now_as_mysql_datetime()
        if not self._predefined_columns_auto_updated:
            self.update('updated_at', now)
            self._predefined_columns_auto_updated = True
        return self

    def update_raw(self, query: str, value:Any = []):
        self._kind = QueryKind.update
        if type(value) != list:
            value = [value]
        self._update_parts.append((query, value))
        return self

    def insert(self, dict_data: Any):
        self._kind = QueryKind.insert

        if type(dict_data) == dict:
            dict_data = [dict_data]

        if self._auto_insert_update_predefined_columns:
            dd = []
            now = now_as_mysql_datetime()
            for one in dict_data:
                one['created_at'] = now
                one['updated_at'] = now
                dd.append(one)
            dict_data = dd

        for one in dict_data:
            placeholders = ', '.join(['%s'] * len(one))
            columns = ', '.join(one.keys())
            sql = "INSERT INTO " + self._table_parts +" ({}) VALUES ({})".format(columns, placeholders)
            self._insert_parts.append((sql, list(one.values())))
        return self

    def delete(self):
        self._kind = QueryKind.delete
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

    def where_in(self, field: str, values: list[Any], bool_op = 'and'):
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
    
    def where_or_group(self, group_callback):
        return self.where_group(group_callback, bool_op='or')

    def where_group(self, group_callback, bool_op='and', default_inner_bool_op='and'):
        group = WhereGroup(default_bool_op=default_inner_bool_op)
        group_callback(group)
        
        def process_group(group):
            conditions = []
            bindings = []
            for i, (field, op, value, inner_bool_op) in enumerate(group.conditions):
                if op == 'raw':
                    conditions.append(f"{inner_bool_op.upper() if i > 0 else ''} {field}")
                    bindings.extend(value)
                elif op == 'group':
                    sub_conditions, sub_bindings = process_group(field)
                    conditions.append(f"{inner_bool_op.upper() if i > 0 else ''} ({sub_conditions})")
                    bindings.extend(sub_bindings)
                else:
                    conditions.append(f"{inner_bool_op.upper() if i > 0 else ''} {field} {op} %s")
                    bindings.append(value)
            return " ".join(conditions), bindings

        grouped_condition, bindings = process_group(group)
        self._where_parts.append((f"({grouped_condition})", 'raw', bindings, bool_op))
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
        for_update_parts = ''
        if self._select_for_update:
            for_update_parts = ' FOR UPDATE'
        query = f'SELECT {fields} FROM {self._table_parts}{for_update_parts}'
        self._parts.append(query)
        return self

    def _build_update(self):
        if self._kind != QueryKind.update:
            return self
        if not self._update_parts:
            return self
        if self._auto_insert_update_predefined_columns:
                self.update_timestamp()

        query = ''
        is_first = True
        for part, values in self._update_parts:
            if is_first:
                is_first = False
                query += f'UPDATE {self._table_parts} SET {part}'
            else:
                query += f', {part}'
            self._bindings.extend(values)

        self._parts.append(query)
        return self

    def _build_delete(self):
        if self._kind != QueryKind.delete:
            return self
        query = f'DELETE FROM {self._table_parts}'
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
            ._build_delete()
            ._build_join()
            ._build_where()
            ._build_groupby()
            ._build_having()
            ._build_orderby()
            ._build_extra()
            ._build_union() #stay at bottom
        )

        return ' '.join(self._parts), self._bindings

    @staticmethod
    def build_from_list(query_list):
        """
        Builds a SQL query from a list.

        Example:
            q = [
                ['SELECT * FROM users'],
                ['WHERE id = ? AND name = ?', (1, 'nana')],
            ]

            sql, args = QueryBuilder.build_from_list(q)

            print(sql)   # Output: SELECT * FROM users WHERE id = ? AND name = ?
            print(args)  # Output: (1, 'nana')

        """
        sql_parts = []
        args = []
        
        for part in query_list:
            sql_parts.append(part[0].strip())
            if len(part) > 1:
                if isinstance(part[1], (list, tuple)):
                    args.extend(part[1])
                else:
                    args.extend(part[1:])
        
        sql = ' '.join(sql_parts)
        return sql, tuple(args)

    def dump_build(self):
        if self._kind == QueryKind.insert:
            for sql, values in self._insert_parts:
                print(sql)
                print(values)
            return self
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

        if self._kind == QueryKind.insert:
            queries = []
            for sql, values in self._insert_parts:
                query = re.sub(r'%s', lambda x: quote_str(values.pop(0)), sql)
                queries.append(query)
            return "\n".join(queries)

        query, values = self.build()
        query = re.sub(r'%s', lambda x: quote_str(values.pop(0)), query)
        return query

    def dump_fake_sql(self):
        s = self.build_fake_sql()
        print(s)
        return self
    
    def print_separator(self):
        print('--------')
        return self

    async def dump_only(self) -> Any:
        self.dump_build()
        self.print_separator()    
        self.dump_fake_sql()
        return None

    async def exec_select_one(self, query_: str = "", values_: list[Any] = []):
        if query_:
            query = query_
            values = values_
        else:
            query, values = self.build()
        res = await db_mysql.select_one(query, tuple(values), conn_or_pool=self._conn_or_pool, to=self._map_to_model)
        return res

    async def exec_select(self, query_: str = "", values_: list[Any] = []):
        if query_:
            query = query_
            values = values_
        else:
            query, values = self.build()
        res = await db_mysql.select(query, tuple(values), conn_or_pool=self._conn_or_pool, to=self._map_to_model)
        return res

    async def exec_update(self, query_: str = "", values_: list[Any] = []) -> int:
        if query_:
            query = query_
            values = values_
        else:
            query, values = self.build()
        res = await db_mysql.update(query, tuple(values), conn_or_pool=self._conn_or_pool)
        return res

    async def exec_insert(self, query_: str = "", values_: list[Any] = []) -> int:
        if query_:
            res = await db_mysql.insert(query_, tuple(values_), conn_or_pool=self._conn_or_pool)
        else:
            res = 0
            for query, values in self._insert_parts:
                res = await db_mysql.insert(query, tuple(values), conn_or_pool=self._conn_or_pool)
        return res

    async def exec_insert_and_retrieve(self, primary_key='id') -> Any:
        insert_id = await self.exec_insert()
        if insert_id < 1:
            return None
        one = await self.select('*').where(primary_key, insert_id).exec_select_one()
        return one

    async def exec_delete(self, query_: str = "", values_: list[Any] = []) -> int:
        if query_:
            res = await db_mysql.update(query_, tuple(values_), conn_or_pool=self._conn_or_pool)
        else:
            res = await self.exec_update()
        return res
    
    async def transaction(self, operations: Callable[[aiomysql.Connection], Any]) -> Any:
        return await db_mysql.transaction(operations, conn_or_pool=self._conn_or_pool)


class WhereGroup:
    def __init__(self, default_bool_op='and'):
        self.conditions = []
        self.default_bool_op = default_bool_op
    
    def _add_condition(self, field, op_or_value, value=None, bool_op='and'):
        if value is None:
            op, value = '=', op_or_value
        else:
            op, value = op_or_value, value
        self.conditions.append((field, op, value, bool_op))
        return self

    def where(self, field, op_or_value, value=None):
        return self._add_condition(field, op_or_value, value, 'and')

    def where_or(self, field, op_or_value, value=None):
        return self._add_condition(field, op_or_value, value, 'or')

    def where_raw(self, query, value=[], bool_op=None):
        bool_op = bool_op or self.default_bool_op
        self.conditions.append((query, 'raw', value, bool_op))
        return self

    def where_group(self, group_callback, bool_op=None):
        bool_op = bool_op or self.default_bool_op
        subgroup = WhereGroup(default_bool_op=self.default_bool_op)
        group_callback(subgroup)
        self.conditions.append((subgroup, 'group', None, bool_op))
        return self

    def where_or_group(self, group_callback):
        return self.where_group(group_callback, bool_op='or')


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
        .where_group(lambda g: g
            .where('abc', '>', 1)
            .where('def', 5)
        )
        .where_group(lambda g: g
            .where_group(lambda sg1: sg1
                .where('b', '>', 1)
                .where('e', '<', 5)
            )
            .where_or_group(lambda sg2: sg2
                .where('c', 2)
                .where_or('d', '<', 3)
            )
        )        
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
        .print_separator()
        .dump_fake_sql()
        .build()
    )
    print('----update----')
    (QueryBuilder().new()
        .table('users')
        .update('notes', 'my notes')
        .update('score', 50)
        .update_raw('score=score+1')
        .update_raw('age = %s', 22)
        .where('id', 123)
        .limit(1)
        .dump_build()
        .print_separator()
        .dump_fake_sql()
        .build()
    )
    print('----insert----')
    user1 = {
        'id':1,
        'name': 'nana',
    }
    user2 = {
        'id':2,
        'name': 'choi'
    }
    user3 = {
        'id':3,
        'name': 'allen'
    }    
    (QueryBuilder().new()
        .table('users')
        .insert(user1) #insert one record
        .insert([user2, user3]) #insert multi records
        .dump_build()
        .print_separator()
        .dump_fake_sql()
        .build()
    )
    print('----delete----')
    (QueryBuilder().new()
        .table('users')
        .delete()
        .where('age', '<', 15)
        .where_not_null('score')
        .order_by('score DESC')
        .limit(5)
        .dump_build()
        .print_separator()
        .dump_fake_sql()
        .build()
    )

    print('----raw sql----')
    q = [
        ['SELECT * FROM users'],
        ['WHERE id = ? AND name = ?', (1, 'nana')],
    ]

    sql, args = QueryBuilder.build_from_list(q)

    print(sql)   # Output: SELECT * FROM users WHERE id = ? AND name = ?
    print(args)  # Output: (1, 'nana')