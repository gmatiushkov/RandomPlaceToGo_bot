from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

main_menu = InlineKeyboardMarkup(row_width=1)
btn_random_place = InlineKeyboardButton("Место 📍", callback_data="random_place")
btn_random_station = InlineKeyboardButton("Станция Ⓜ️", callback_data="random_station")
btn_direction = InlineKeyboardButton("Направление 🧭", callback_data="direction")
main_menu.add(btn_random_place, btn_random_station, btn_direction)

direction_menu = InlineKeyboardMarkup(row_width=1)
btn_left_right = InlineKeyboardButton("⬅️ или ➡️", callback_data="left_right")
btn_all_directions = InlineKeyboardButton("⬆️⬇️➡️⬅️", callback_data="all_directions")
btn_back = InlineKeyboardButton("⬅️ Назад", callback_data="back_to_menu")
direction_menu.add(btn_left_right, btn_all_directions, btn_back)

metro_menu = InlineKeyboardMarkup(row_width=3)
colors = ["🔴", "🔵", "🟢", "🟠", "🟣"]
for color in colors:
    metro_menu.add(InlineKeyboardButton(color, callback_data=f"metro_{color}"))
metro_menu.add(InlineKeyboardButton("Все 🌈", callback_data="metro_all"))
metro_menu.add(InlineKeyboardButton("⬅️ Назад", callback_data="back_to_menu"))

place_type_menu = InlineKeyboardMarkup(row_width=1)
btn_random_place = InlineKeyboardButton("Случайное", callback_data="random_place_type")
btn_green_place = InlineKeyboardButton("С растительностью 🌿", callback_data="green_place_type")
btn_water_place = InlineKeyboardButton("У воды 🌊", callback_data="water_place_type")
btn_back = InlineKeyboardButton("⬅️ Назад", callback_data="back_to_menu")
place_type_menu.add(btn_random_place, btn_green_place, btn_water_place, btn_back)
