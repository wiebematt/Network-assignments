# Network-assignments

threaded-echo-server.py
    - handler: reads the message sent and extract the expressions to evaluate. 
    - math_handler: uses the parser class to evaluate the expressions and
        and return the answer byte message.
      
simple-echo-client.py
    - main: use the mutable_bytes variable (an list of byte counts and expressions)
        and calls package_data and send the result to the server
    - package_data: takes the list of values and converts it into a string
    - report_data: takes the server response and prints out the resulting
        answers
        
Parser.py
    - parses string-based math equations (parenthesis are not handled)
    
Run Instructions
    Run threaded-echo-server.py
    Call main in simple-echo-client.py with an list of the values to be sent
        (e.g mutable_bytes = [3, 10, "100*10/5-2", 10, "40/2*20+20", 11, "1000+1000*2"])
        Easiest just to do this at the end of the file.