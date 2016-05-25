# How much money am I spending?

This is a Dockerized web interface (demo) that does the following:

- Loads a user's transactions from the GetAllTransactions endpoint
- Determines how much money the user spends and makes in each of the months for which we have data, and in the "average" month.

The applications output these numbers in the following format:


      {"2014-10": {"spent": "$200.00", "income": "$500.00"},
      "2014-11": {"spent": "$1510.05", "income": "$1000.00"},
      "2015-04": {"spent": "$300.00", "income": "$500.00"},
      "average": {"spent": "$750.00", "income": "$950.00"}}

This information is represented in an interactive data table, and downloadable by the user as a json file.

### Additional features
- **ignoredonuts** the user can select to not include donuts. This could easily be extended to take in a custom query string by the user for transactions to filter, and currently is implemented as an "Ignore Donuts" and "Account Donuts" button.
- **crystal ball** the user can choose to produce data for predicted spending with the "Crystal Ball" button.

I did not implement ignoring credit card payments because I need to get back to work. :)


# Application instructions

First, download the code repo:

     git clone https://www.github.com/vsoch/levelmoney
     cd levelmoney

You can run the application locally doing the following:

     python index.py

And open up to `127.0.0.1:5000` This assumes that you have all dependencies (numpy, etc) installed. You can also run the application via it's docker container:

     docker-compose up -d

The container image will be downloaded to your computer via DockerHub. If you want to build locally, first do:

     docker build -t vanessa/levelmoney . 
     docker-compose up -d 

Then you will need to find the address of the container:

      docker inspect levelmoney_web_1 |grep "IPAddress"

And it should be repeated twice (will have better solution for this). Then go to ${IPADDRESS}:5000 in your browser.


# Usage

This is a demo, so the "authentication" is just entering an institution ID into the login box that is then passed around between the views. There is no password. The tool does its initial query of transaction data using the API at application start, and this works for the demo but would not be an ideal strategy for an actual implementation (when the data would likely change). Finally, all functions are separated in sections in the equivalent [index.py](index.py) file, and this would be sub optimal for a more complex application.

To use, you can either enter the demo institution ID into the box `42069000` or click the "Demo ID" in the upper right to have the application do it for you.
