from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

main_menu = InlineKeyboardMarkup(row_width=2)
btn_random_place = InlineKeyboardButton("Случайное место", callback_data="random_place")
btn_random_station = InlineKeyboardButton("Случайная станция", callback_data="random_station")
main_menu.add(btn_random_place, btn_random_station)

metro_menu = InlineKeyboardMarkup(row_width=3)
colors = ["🟥", "🟦", "🟩", "🟧", "🟪"]
for color in colors:
    metro_menu.add(InlineKeyboardButton(color, callback_data=f"metro_{color}"))
metro_menu.add(InlineKeyboardButton("Все станции", callback_data="metro_all"))
