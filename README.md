# Stock Analysis	

Stock Analysis will help you check out stocks, compare them or even filter them.
from 10367 finance products you can choose the best suited for you based on yields of price or dividend in specific years,
PE ratio or the profitability of the company.
compare visual graphs of any stacks and export the data in to excel file.

2 shorts video (less then 3o seconds) that show the script in action

https://www.youtube.com/watch?v=GIDT-iHpExc&ab_channel=eilontoledano

https://www.youtube.com/watch?v=5dSntCRkA6c&ab_channel=eilontoledano
 
the Python script collected the data from all USA stocks, by calling a google cloud function using multi thread.
and store the data in firebase realtime database.

get_data_google_cloud.py is the function that found in the google cloud that collecting the data
send_request_thread, colling the google cloud function in multi thread with all the stocks symbols
raw_data.json where the data store as json objects
json_to_csv.py convert the data from json form to array form and storing it in data.csv
data.csv to easily convert the data into numpy array.
main.py - where all the action is happening containing a user console interface, and the filter and compare functions described above.
in calculation.py there are all the often used and not so pretty functions, that allow better handling and representing of the data.
req.sh this will help you to install al the necessary python packages (for linux)

-currently not in use-
data_sorted.csv is the same as data.csv but for every data field column there is an index column,
for time efficient sorting the data with masking
database_handler.py used to handle a sql database
