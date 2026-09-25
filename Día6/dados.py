import random
import time


while True:
    dado1 = random.randint(1,6) 
    dado2 = random.randint(1,6)
    if dado1 == dado2:
        print(f"Doble {dado1} - {dado2} ")
        break
    else:
        print(f"{dado1} - {dado2}")

    time.sleep(2)