
# # Exone parser  
  
**Exone Parser** created to parse vacancies data from https://www.exone.de/karriere/jobs/stellenangebote 
  
  
## Used packages  
- PyQuery  
- requests  
- splinter
  
## Files  
**exone_parser.py** include main parsing functions

**exchanger.py** include main exchange functions
  
  
## Installation  
  
    $ make venv
    $ source venv/bin/activate  
    $ make requirements

## Run parsing:
    $ python exone_parser.py 

## Run exchange:
    $ python exchanger.py 