import random
def bus_game(seat_num):
    seat_list, open_seats = generate_seats(seat_num)
    


def generate_seats(seat_num):
    seats = [False for _ in range(seat_num)] # false for empty, true for full
    seats_tb_filled = random.randint(1, seat_num-1)
    open_seats = seat_num-seats_tb_filled
    while seats_tb_filled > 0:
        index = random.randint(0, seat_num-1)
        if not seats[index]:
            seats[index] = True
            seats_tb_filled -= 1
    return seats, open_seats