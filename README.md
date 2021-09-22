# Stock Analysis	

<h1>Stock Analysis</h1>

<img src="https://github.com/eilon1996/stock-analysis/blob/master/stock.png" width="768" height="380"/>

<h4>Stock Analysis will help you find and compare stocks and other finance products</h4>
<h4>you can filter the best stock for you out of 12861 options based on:</h4>

<h4>for the remote conrol:  </h4>
<ul>
  <li>yields in a specific time</li>
  <li>dividend distribution</li>
  <li>PE ratio  </li>
  <li>and much more </li>
</ul>

 
the Python script collected the data from all USA stocks, by calling a google cloud function using multi thread.
and store the data in firebase realtime database.

get_data_google_cloud.py is the function that found in the google cloud that collecting the data
send_request_thread, colling the google cloud function in multi thread with all the stocks symbols
raw_data.json where the data store as json objects
json_to_csv.py convert the data from json form to array form and storing it in data.csv
data.csv to easily convert the data into numpy array.
main.py - where all the action is happening containing a user console interface, and the filter and compare functions described above.
in calculation.py there are all the often used and not so pretty functions, that allow better handling and representing of the data.

-currently not in use-
data_sorted.csv is the same as data.csv but for every data field column there is an index column,
for time efficient sorting the data with masking
database_handler.py used to handle a sql database
