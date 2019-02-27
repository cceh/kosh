# Kosh - APIs for Dictionaries

For sample datasets, see: <https://github.com/cceh/kosh_data>


How to run Kosh (Linux, OSX) with the above sample data:

1. [elasticsearch](https://www.elastic.co/downloads/elasticsearch) running
2. `git clone https://github.com/cceh/kosh`
3. `git clone https://github.com/cceh/kosh_data`
4. go to kosh's dir and type: `make`
5. start kosh:

    on Linux:  
    `kosh --log_level DEBUG --data_root ../kosh_data --data_host localhost`
    
    on OSX: 
    `kosh --log_level DEBUG --data_root ../kosh_data --data_host localhost --data_sync off`

