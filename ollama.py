# Author: Pablo Moreno
# Date: 2024-05-15
# Description: This script is used to collect data from the Ollama API and save it to a file.

import requests
import json

URL_Ollama = "http://localhost:11434/"

def banner():
    print("""                                                                                                          
                 .!JJ!.              .7YY7.                 
                :B@@@@B~            ^#@@@@B:                
               .B@#^^B@&:          :#@G::#@G                
               7@@?  !@@Y:!J5PP5J!:Y@@~  ?@@!               
               Y@@~  .&@@@@#GPPG#@@@@#.  ~@@J               
               7@@Y!7?@@B?^      :?B@&?7!Y@@?               
              .5@@@@&#G7            ?B#&@@@@5.              
             ?&@#J~:.                 .:^7P&@#7             
            Y@@J.                          :Y@@J            
           ~@@5              ..              5@@^           
           ?@@?    ?P5^ :?5GGGGGG5?: ^GBY.   7@@!           
           ~@@B.  :G##JJ&G?~::::~?G&J~B&B:  .B@&:           
            5@@P.   . ?@J   ~##~   J@? .   .G@@?            
            !@@@^     7@P.   ~!.  .P@7     :#@&:            
            G@&~       !G#5?!~~!?5#G!       ^&@P            
           :@@5          ^7J5PP5J7^          5@@^           
           ^@@Y                              5@@^           
            B@&^                            :&@B.           
            !@@#^                          :B@&~            
            .#@@^                          ^@@B             
            7@@J                            ?@@?            
            B@@^                            :&@#            
            7PB.                            .BG7            
              .                              .                                                                               
    """)

def main():
    banner()

    # Get the list of alerts from the Ollama API

if __name__ == "__main__":
    main()