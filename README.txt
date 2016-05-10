INSTALL
-----------------
$ pip install -r requirements.txt


CONFIGURE
-----------------
- Edit config.py (editable options)
    + PREMIUM_BRANDS: List of premium brands
    + BUDGET_BRANDS: List of budget brands
    + OUTPUT_PATH: Absolute path to output directory


RUN
-----------------
$ python convert.py [path/to/xml_file_name]

Example:
--------
$ python convert.py ranking2/154_2015-07-27.xml
>> RUNNING convert.py ranking2/154_2015-07-27.xml
>> Start generating data from file:  ranking2/154_2015-07-27.xml
>> Generated successfully. All output are in ./html_files/154_2015-07-27_report.html

------->
All results will be in ./html_files/154_2015-07-27_report.html
