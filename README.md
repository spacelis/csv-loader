CSV Loader
==========

This tool aims at loading general CSV files into db tables. It will detect the types
and headers of the CSV file and generate a plan for the layout in the database.
Users can change the layout accordingly and the loading command will adjust to the plan.


Usage
=====

First run 
```
python structing.py <plan.py> file1.csv [file2.csv [...]]
``` 
to generate a plan.
Then make any modification to the plan accordingly, such as adjust the names and types.
Then run 
```
python dataloader.py [-f] [-b BUFFERSIZE] <plan.py> <postgresql://...>
``` 
to load the tables to the database given the URL.`-f` means recreate all tables, this
may be useful if you need to re-upload after editing the table structures.

This tool is based on SQLAlchemy which allow it to be used for different database management system,
such as PostgreSQL, MySQL, SQLite.


LICENSE
=======
The MIT License (MIT)

Copyright (c) 2016 Wen Li

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
