# stock-code
this program will help you analyse any stock you want and compare it to any other option
farther more it will let you dicover new stocks and etf that will stand in the paramaters that you choose, even those you didnt know exist!

some basic knoladge before we dive to the code
stock is a share in a company (a tiny part of it) thats mean that your one of her (many) owners
yeald is how mach the stock price rised 
dividend is a part of the revenue the company did that go to the owners (the stock holders)
bond is a loan that you can give to a company or a state 
etf is a  banch of stock or bonds (or both)

the main file is where the user begin, and this file use the others to handle everything
finance_product: is the main object that we work with
stock, etf: are an objects that are being used as a field in the finance prudact 
database_handler: where we use mysql to save our data
calculation: from there we import information that is relevent to several files
test is for experement somethings in a clean envairment brfore integrate them to the file

req.sh this will help you to install al the necessery python packages
I guese that you are using windows so you will need to change the end to .bat end the pip3 to pip and run through the CMD
or just downlload them one by one
