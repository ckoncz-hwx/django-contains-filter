# Django "contains" field lookup issue with Oracle

The "contains" field lookup is supposed to generate a `WHERE` clause performing a case-sensitive containment test: https://docs.djangoproject.com/en/6.0/ref/models/querysets/#std-fieldlookup-contains.

When using an Oracle database this seems to work only for TextFields that contain at most 2000 characters. The steps to reproduce the error when a TextField is 2001 characters long are below.

## Steps

### start an Oracle database:
```
docker run --name oracle-db-free -d \
  -p 1521:1521 \
  -e ORACLE_PASSWORD=django \
  gvenzl/oracle-free:23.26.1-slim

```

### create a Python virtual environment

Clone the current repo, then:
```
python3.12 -m venv venv

# activate it
source ./venv/bin/activate

# install packages
pip install -r requirements.txt
```

### Execute tests
```
cd djangotutorial

python manage.py test --noinput --debug-mode test_filtering.TestLogEntry.test_log_filtering_2001
```

### Result:
```
======================================================================
ERROR: test_log_filtering_2001 (test_filtering.TestLogEntry.test_log_filtering_2001)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/csaba/django-contains-filter/venv/lib/python3.12/site-packages/django/db/backends/utils.py", line 105, in _execute
    return self.cursor.execute(sql, params)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/csaba/django-contains-filter/venv/lib/python3.12/site-packages/django/db/backends/oracle/base.py", line 628, in execute
    return self.cursor.execute(query, self._param_generator(params))
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/csaba/django-contains-filter/venv/lib/python3.12/site-packages/oracledb/cursor.py", line 859, in execute
    impl.execute(self)
  File "src/oracledb/impl/thin/cursor.pyx", line 279, in oracledb.thin_impl.ThinCursorImpl.execute
  File "src/oracledb/impl/thin/protocol.pyx", line 501, in oracledb.thin_impl.Protocol._process_single_message
  File "src/oracledb/impl/thin/protocol.pyx", line 502, in oracledb.thin_impl.Protocol._process_single_message
  File "src/oracledb/impl/thin/protocol.pyx", line 494, in oracledb.thin_impl.Protocol._process_message
  File "src/oracledb/impl/thin/messages/base.pyx", line 102, in oracledb.thin_impl.Message._check_and_raise_exception
oracledb.exceptions.DatabaseError: ORA-06502: PL/SQL: value or conversion error: character string buffer too small
ORA-06512: at line 1
Help: https://docs.oracle.com/error-help/db/ora-06502/

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/home/csaba/django-contains-filter/djangotutorial/test_filtering.py", line 14, in test_log_filtering_2001
    self.assertEqual(len(LogEntry.objects.only('id').filter(change_message__contains='a')), 1)
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/csaba/django-contains-filter/venv/lib/python3.12/site-packages/django/db/models/query.py", line 372, in __len__
    self._fetch_all()
  File "/home/csaba/django-contains-filter/venv/lib/python3.12/site-packages/django/db/models/query.py", line 2000, in _fetch_all
    self._result_cache = list(self._iterable_class(self))
                         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/csaba/django-contains-filter/venv/lib/python3.12/site-packages/django/db/models/query.py", line 95, in __iter__
    results = compiler.execute_sql(
              ^^^^^^^^^^^^^^^^^^^^^
  File "/home/csaba/django-contains-filter/venv/lib/python3.12/site-packages/django/db/models/sql/compiler.py", line 1624, in execute_sql
    cursor.execute(sql, params)
  File "/home/csaba/django-contains-filter/venv/lib/python3.12/site-packages/django/db/backends/utils.py", line 122, in execute
    return super().execute(sql, params)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/csaba/django-contains-filter/venv/lib/python3.12/site-packages/django/db/backends/utils.py", line 79, in execute
    return self._execute_with_wrappers(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/csaba/django-contains-filter/venv/lib/python3.12/site-packages/django/db/backends/utils.py", line 92, in _execute_with_wrappers
    return executor(sql, params, many, context)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/csaba/django-contains-filter/venv/lib/python3.12/site-packages/django/db/backends/utils.py", line 100, in _execute
    with self.db.wrap_database_errors:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/csaba/django-contains-filter/venv/lib/python3.12/site-packages/django/db/utils.py", line 94, in __exit__
    raise dj_exc_value.with_traceback(traceback) from exc_value
  File "/home/csaba/django-contains-filter/venv/lib/python3.12/site-packages/django/db/backends/utils.py", line 105, in _execute
    return self.cursor.execute(sql, params)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/csaba/django-contains-filter/venv/lib/python3.12/site-packages/django/db/backends/oracle/base.py", line 628, in execute
    return self.cursor.execute(query, self._param_generator(params))
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/csaba/django-contains-filter/venv/lib/python3.12/site-packages/oracledb/cursor.py", line 859, in execute
    impl.execute(self)
  File "src/oracledb/impl/thin/cursor.pyx", line 279, in oracledb.thin_impl.ThinCursorImpl.execute
  File "src/oracledb/impl/thin/protocol.pyx", line 501, in oracledb.thin_impl.Protocol._process_single_message
  File "src/oracledb/impl/thin/protocol.pyx", line 502, in oracledb.thin_impl.Protocol._process_single_message
  File "src/oracledb/impl/thin/protocol.pyx", line 494, in oracledb.thin_impl.Protocol._process_message
  File "src/oracledb/impl/thin/messages/base.pyx", line 102, in oracledb.thin_impl.Message._check_and_raise_exception
django.db.utils.DatabaseError: ORA-06502: PL/SQL: value or conversion error: character string buffer too small
ORA-06512: at line 1
Help: https://docs.oracle.com/error-help/db/ora-06502/

----------------------------------------------------------------------
Ran 1 test in 0.171s

FAILED (errors=1)
```

The generated SQL that fails is the following:
```
SELECT "DJANGO_ADMIN_LOG"."ID" FROM "DJANGO_ADMIN_LOG" WHERE DBMS_LOB.SUBSTR("DJANGO_ADMIN_LOG"."CHANGE_MESSAGE") LIKE TRANSLATE(%a% USING NCHAR_CS) ESCAPE TRANSLATE('\' USING NCHAR_CS) ORDER BY "DJANGO_ADMIN_LOG"."ACTION_TIME" DESC;
```

Case insensitive contaiment check (`icontains`) works OK.