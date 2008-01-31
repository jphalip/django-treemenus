
def clean_ranks(menu_items):
    rank = 0
    for menu_item in menu_items:
        menu_item.rank = rank
        menu_item.save()
        rank += 1