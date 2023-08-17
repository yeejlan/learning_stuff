from dataclasses import dataclass, field
from enum import StrEnum

class QueryBuilderException(Exception):
    pass

class QueryKind(StrEnum):
    select = "select"
    insert = "insert"
    update = "update"

@dataclass
class QueryBuilder:
    kind: QueryKind = QueryKind.select
    parts: list = field(default_factory=list)  #statement parts
    bindings: list = field(default_factory=list)  #statement bindings

    table_parts: str = ''
    select_parts: list = field(default_factory=list) 
    join_parts: list = field(default_factory=list)
    where_parts: list = field(default_factory=list)
    groupby_parts: list = field(default_factory=list)
    having_parts: list = field(default_factory=list)
    order_parts: list = field(default_factory=list)
    union_parts: list = field(default_factory=list)
    unionorder_parts: list = field(default_factory=list)


    def table(self, parts):
        self.table_parts = parts
        return self
    
    def select(self, parts):
        self.kind = QueryKind.select
        t = type(parts)
        if t == tuple or t == list:
            self.select_parts.append(', '.join(parts))
        elif t == str:
            self.select_parts.append(parts)
        else:
            raise QueryBuilderException('not supported select params')
        return self
    
    def where(self, field, op=None, value=None, bool_op = 'and'):
        if op is None and value is None: #raw query
            self.where_parts.append((field, None, None, bool_op))
        elif value is None:
            self.where_parts.append((field, '=', op, bool_op))
        else: 
            self.where_parts.append((field, op, value, bool_op))
            
        return self


    def where_or(self, field, op=None, value=None, bool_op = 'or'):
        self.where(field, op, value, bool_op)
        return self

    def _build_select(self):
        if not self.table_parts:
            raise QueryBuilderException('table is missing')
        
        fields = ' '.join(self.select_parts) if self.select_parts else '*'
        query = f'SELECT {fields} FROM {self.table_parts}'
        self.parts.append(query)
        return self

    def _build_where(self):
        if not self.where_parts:
            self.parts.append('WHERE 1')
        if self.where_parts:
            query = ''
            is_first = True
            for column, op, value, bool_op in self.where_parts:
                part = ''
                if op is None and value is None: #raw query
                    part = column
                else:
                    part = f'{column} {op} %s'
                    self.bindings.append(value)

                if is_first:
                    is_first = False
                    query += f'WHERE {part}'
                else:
                    query += f' {bool_op.upper()} {part}'
            self.parts.append(query)

        return self

    def build(self):
        self._build_select() \
            ._build_where()

        return ' '.join(self.parts), self.bindings
    
    def build_fake_sql(self):
        pass
        
qb = QueryBuilder()
query, values = (qb.table('users') 
    .select(['id', 'name']) 
    .where('id', 1) 
    .where("niasasww") 
    .where('cc', 2) 
    .where_or('dd', '>=', 15)
    .build()
)

print(query) 
# SELECT id,name FROM  WHERE user_id = %s
print(values)
# (1,)